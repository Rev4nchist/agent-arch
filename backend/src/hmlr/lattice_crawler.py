"""LatticeCrawler - Vector Search Layer for HMLR Memory Retrieval.

The LatticeCrawler performs semantic search (Key 1) to find candidate memories,
which are then passed to the Governor for contextual filtering (Key 2).

This implements the missing "lattice" layer from the original HMLR architecture.

SECURITY NOTES:
- user_id is validated and escaped before use in OData filters
- Secrets (FactCategory.SECRET) are NEVER indexed in vector store
- All inputs are validated for length and format
- Error messages are sanitized to prevent information disclosure
"""

import logging
import re
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from src.hmlr.models import (
    CandidateMemory,
    MemoryType,
    Fact,
    BridgeBlock,
    FactCategory,
)
from src.config import settings

logger = logging.getLogger(__name__)

# Security constants
MAX_USER_ID_LENGTH = 256
MAX_QUERY_LENGTH = 10000
MAX_TOP_K = 100
MIN_SCORE_FLOOR = 0.0
MAX_SCORE_CEILING = 1.0
USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-@.]+$')


class SecurityValidationError(Exception):
    """Raised when security validation fails."""
    pass


def _validate_user_id(user_id: str) -> str:
    """Validate and sanitize user_id for safe use in OData filters.

    Args:
        user_id: Raw user identifier

    Returns:
        Validated user_id

    Raises:
        SecurityValidationError: If user_id is invalid
    """
    if not user_id:
        raise SecurityValidationError("user_id cannot be empty")

    if len(user_id) > MAX_USER_ID_LENGTH:
        raise SecurityValidationError(f"user_id exceeds maximum length of {MAX_USER_ID_LENGTH}")

    if not USER_ID_PATTERN.match(user_id):
        raise SecurityValidationError("user_id contains invalid characters")

    if "'" in user_id or '"' in user_id or "\\" in user_id:
        raise SecurityValidationError("user_id contains forbidden characters")

    return user_id


def _escape_odata_string(value: str) -> str:
    """Escape a string for safe use in OData filter expressions.

    Args:
        value: Raw string value

    Returns:
        Escaped string safe for OData filters
    """
    return value.replace("'", "''")


def _sanitize_log_message(message: str, max_length: int = 500) -> str:
    """Sanitize a message for safe logging.

    Args:
        message: Raw message
        max_length: Maximum length to log

    Returns:
        Sanitized message
    """
    sanitized = str(message)[:max_length]
    sanitized = re.sub(r'(api[_-]?key|token|password|secret)[=:]\s*\S+',
                       r'\1=[REDACTED]', sanitized, flags=re.IGNORECASE)
    return sanitized


class LatticeCrawler:
    """Vector search layer for HMLR memory retrieval.

    Manages a dedicated index for HMLR memories (facts + block summaries)
    and provides semantic search capabilities for the Governor.
    """

    def __init__(
        self,
        index_name: str = None,
        endpoint: str = None,
        api_key: str = None,
    ):
        """Initialize LatticeCrawler.

        Args:
            index_name: Azure AI Search index name (default: hmlr-memories)
            endpoint: Azure AI Search endpoint
            api_key: Azure AI Search API key
        """
        self.endpoint = endpoint or settings.azure_search_endpoint
        self.api_key = api_key or settings.azure_search_api_key
        self.index_name = index_name or getattr(
            settings, 'hmlr_search_index_name', 'hmlr-memories'
        )

        self.credential = AzureKeyCredential(self.api_key)

        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )

        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self.embeddings_deployment = settings.azure_openai_embeddings_deployment

    def _create_index_schema(self) -> SearchIndex:
        """Create the HMLR memories index schema.

        Schema fields:
        - id: Unique identifier (user_id + memory_type + source_id)
        - user_id: User identifier (filterable)
        - content: Text content for search
        - content_vector: 1536-dim embedding vector
        - memory_type: fact | block_summary
        - source_id: fact_id or block_id
        - category: Fact category (for facts)
        - topic_label: Block topic (for block summaries)
        - confidence: Fact confidence score
        - created_at: Timestamp
        """
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="hmlr-vector-profile",
                    algorithm_configuration_name="hmlr-vector-algorithm",
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hmlr-vector-algorithm",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ],
        )

        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SimpleField(
                name="user_id",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                analyzer_name="en.microsoft",
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="hmlr-vector-profile",
            ),
            SimpleField(
                name="memory_type",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="source_id",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="category",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SearchableField(
                name="topic_label",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
            ),
            SimpleField(
                name="confidence",
                type=SearchFieldDataType.Double,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="created_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),
        ]

        return SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )

    def create_or_update_index(self) -> None:
        """Create or update the HMLR memories index."""
        try:
            index = self._create_index_schema()
            self.index_client.create_or_update_index(index)
            logger.info(f"Created/updated HMLR index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error creating HMLR index: {e}")
            raise

    def index_exists(self) -> bool:
        """Check if the HMLR index exists."""
        try:
            self.index_client.get_index(self.index_name)
            return True
        except Exception:
            return False

    def ensure_index_exists(self) -> None:
        """Ensure the HMLR index exists, creating if needed."""
        if not self.index_exists():
            logger.info(f"HMLR index {self.index_name} not found, creating...")
            self.create_or_update_index()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector
        """
        try:
            max_chars = 32000
            if len(text) > max_chars:
                text = text[:max_chars]
                logger.warning(f"Text truncated to {max_chars} chars for embedding")

            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embeddings_deployment
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def crawl(
        self,
        user_id: str,
        query: str,
        top_k: int = 10,
        memory_type: Optional[MemoryType] = None,
        min_score: float = 0.5,
    ) -> List[CandidateMemory]:
        """Crawl the lattice for candidate memories (Key 1).

        Performs vector search filtered by user_id to find semantically
        relevant memories for the Governor to filter (Key 2).

        SECURITY: user_id is validated and escaped to prevent OData injection.

        Args:
            user_id: User identifier (validated)
            query: Search query (length-bounded)
            top_k: Maximum candidates to return (bounded to MAX_TOP_K)
            memory_type: Optional filter by memory type
            min_score: Minimum similarity score threshold (bounded)

        Returns:
            List of CandidateMemory objects ranked by relevance

        Raises:
            SecurityValidationError: If user_id validation fails
        """
        validated_user_id = _validate_user_id(user_id)

        if not query:
            return []
        if len(query) > MAX_QUERY_LENGTH:
            query = query[:MAX_QUERY_LENGTH]
            logger.warning("Query truncated for security")

        top_k = min(max(1, top_k), MAX_TOP_K)
        min_score = max(MIN_SCORE_FLOOR, min(min_score, MAX_SCORE_CEILING))

        try:
            query_vector = self.generate_embedding(query)

            safe_user_id = _escape_odata_string(validated_user_id)
            filter_expr = f"user_id eq '{safe_user_id}'"
            if memory_type:
                filter_expr += f" and memory_type eq '{memory_type.value}'"

            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top_k,
                fields="content_vector"
            )

            results = self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                filter=filter_expr,
                top=top_k,
                select=[
                    "id", "user_id", "content", "memory_type",
                    "source_id", "category", "topic_label",
                    "confidence", "created_at"
                ],
            )

            candidates = []
            for result in results:
                if result.get("user_id") != validated_user_id:
                    logger.warning("User isolation violation detected - skipping result")
                    continue

                score = result.get("@search.score", 0)
                if score < min_score:
                    continue

                created_at = result.get("created_at")
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                    except ValueError:
                        created_at = None

                candidate = CandidateMemory(
                    id=result["id"],
                    user_id=result["user_id"],
                    content=result["content"],
                    memory_type=MemoryType(result["memory_type"]),
                    source_id=result["source_id"],
                    score=score,
                    category=result.get("category"),
                    topic_label=result.get("topic_label"),
                    confidence=result.get("confidence"),
                    created_at=created_at,
                )
                candidates.append(candidate)

            logger.info(f"LatticeCrawler found {len(candidates)} candidates")
            return candidates

        except SecurityValidationError:
            raise
        except Exception as e:
            logger.error(f"LatticeCrawler.crawl error: {_sanitize_log_message(str(e))}")
            return []

    async def index_fact(self, fact: Fact) -> bool:
        """Index a fact in the lattice.

        SECURITY: Secrets (FactCategory.SECRET) are NEVER indexed to prevent
        exposure through vector search. Only the fact key is stored with a
        placeholder value.

        Args:
            fact: Fact to index

        Returns:
            True if indexed successfully
        """
        try:
            validated_user_id = _validate_user_id(fact.user_id)

            fact_category = fact.category
            if isinstance(fact_category, str):
                try:
                    fact_category = FactCategory(fact_category)
                except ValueError:
                    fact_category = FactCategory.ENTITY

            if fact_category == FactCategory.SECRET:
                content = f"{fact.key}: [SECURE_VALUE_NOT_INDEXED]"
                logger.info(f"Secret fact '{fact.key}' indexed without value for security")
            else:
                content = f"{fact.key}: {fact.value}"
                if fact.evidence_snippet:
                    content += f" (Evidence: {fact.evidence_snippet})"

            doc_id = f"fact_{validated_user_id}_{fact.fact_id or fact.key}"
            doc_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_id)

            embedding = self.generate_embedding(content)

            document = {
                "id": doc_id,
                "user_id": validated_user_id,
                "content": content,
                "content_vector": embedding,
                "memory_type": MemoryType.FACT.value,
                "source_id": str(fact.fact_id) if fact.fact_id else fact.key,
                "category": fact_category.value if hasattr(fact_category, 'value') else str(fact_category),
                "confidence": fact.confidence,
                "created_at": (
                    fact.created_at.isoformat() + "Z"
                    if fact.created_at else datetime.utcnow().isoformat() + "Z"
                ),
            }

            self.search_client.upload_documents(documents=[document])
            logger.debug(f"Indexed fact {doc_id}")
            return True

        except SecurityValidationError as e:
            logger.error(f"Security validation failed for fact: {e}")
            return False
        except Exception as e:
            logger.error(f"Error indexing fact: {_sanitize_log_message(str(e))}")
            return False

    async def index_block_summary(self, block: BridgeBlock) -> bool:
        """Index a bridge block summary in the lattice.

        SECURITY: User ID is validated before indexing.

        Args:
            block: Bridge block to index

        Returns:
            True if indexed successfully
        """
        try:
            validated_user_id = _validate_user_id(block.user_id)

            content_parts = [f"Topic: {block.topic_label}"]
            if block.summary:
                content_parts.append(f"Summary: {block.summary}")
            if block.keywords:
                content_parts.append(f"Keywords: {', '.join(block.keywords)}")
            if block.open_loops:
                content_parts.append(f"Open loops: {', '.join(block.open_loops)}")
            if block.decisions_made:
                content_parts.append(f"Decisions: {', '.join(block.decisions_made)}")

            content = ". ".join(content_parts)

            doc_id = f"block_{validated_user_id}_{block.id}"
            doc_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_id)

            embedding = self.generate_embedding(content)

            document = {
                "id": doc_id,
                "user_id": validated_user_id,
                "content": content,
                "content_vector": embedding,
                "memory_type": MemoryType.BLOCK_SUMMARY.value,
                "source_id": block.id,
                "topic_label": block.topic_label,
                "created_at": (
                    block.created_at.isoformat() + "Z"
                    if block.created_at else datetime.utcnow().isoformat() + "Z"
                ),
            }

            self.search_client.upload_documents(documents=[document])
            logger.debug(f"Indexed block summary {doc_id}")
            return True

        except SecurityValidationError as e:
            logger.error(f"Security validation failed for block: {e}")
            return False
        except Exception as e:
            logger.error(f"Error indexing block summary: {_sanitize_log_message(str(e))}")
            return False

    async def update_block_embedding(self, block: BridgeBlock) -> bool:
        """Update an existing block's embedding in the lattice.

        Called when a block is updated (new turns, decisions, etc.)

        Args:
            block: Updated bridge block

        Returns:
            True if updated successfully
        """
        return await self.index_block_summary(block)

    async def delete_fact(self, user_id: str, fact_id: str) -> bool:
        """Delete a fact from the lattice.

        SECURITY: User ID is validated before constructing document ID.

        Args:
            user_id: User identifier
            fact_id: Fact identifier

        Returns:
            True if deleted successfully
        """
        try:
            validated_user_id = _validate_user_id(user_id)
            doc_id = f"fact_{validated_user_id}_{fact_id}"
            doc_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_id)
            self.search_client.delete_documents(documents=[{"id": doc_id}])
            logger.debug(f"Deleted fact from lattice")
            return True
        except SecurityValidationError as e:
            logger.error(f"Security validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting fact from lattice: {_sanitize_log_message(str(e))}")
            return False

    async def delete_block(self, user_id: str, block_id: str) -> bool:
        """Delete a block summary from the lattice.

        SECURITY: User ID is validated before constructing document ID.

        Args:
            user_id: User identifier
            block_id: Block identifier

        Returns:
            True if deleted successfully
        """
        try:
            validated_user_id = _validate_user_id(user_id)
            doc_id = f"block_{validated_user_id}_{block_id}"
            doc_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_id)
            self.search_client.delete_documents(documents=[{"id": doc_id}])
            logger.debug(f"Deleted block from lattice")
            return True
        except SecurityValidationError as e:
            logger.error(f"Security validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting block from lattice: {_sanitize_log_message(str(e))}")
            return False

    async def delete_user_memories(self, user_id: str) -> int:
        """Delete all memories for a user (GDPR compliance).

        SECURITY: User ID is validated and escaped to prevent OData injection.

        Args:
            user_id: User identifier

        Returns:
            Number of documents deleted
        """
        try:
            validated_user_id = _validate_user_id(user_id)
            safe_user_id = _escape_odata_string(validated_user_id)

            results = self.search_client.search(
                search_text="*",
                filter=f"user_id eq '{safe_user_id}'",
                select=["id", "user_id"],
                top=1000,
            )

            doc_ids = []
            for result in results:
                if result.get("user_id") == validated_user_id:
                    doc_ids.append({"id": result["id"]})
                else:
                    logger.warning("User isolation violation in delete - skipping")

            if doc_ids:
                self.search_client.delete_documents(documents=doc_ids)
                logger.info(f"Deleted {len(doc_ids)} memories for user")
                return len(doc_ids)

            return 0

        except SecurityValidationError as e:
            logger.error(f"Security validation failed: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error deleting user memories: {_sanitize_log_message(str(e))}")
            return 0

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about the HMLR index."""
        try:
            stats = self.index_client.get_index_statistics(self.index_name)
            return {
                "index_name": self.index_name,
                "document_count": stats.get("document_count", 0),
                "storage_size": stats.get("storage_size", 0),
            }
        except Exception as e:
            return {
                "index_name": self.index_name,
                "document_count": 0,
                "error": str(e)
            }


_lattice_crawler: Optional[LatticeCrawler] = None


def get_lattice_crawler() -> LatticeCrawler:
    """Get or create the global LatticeCrawler instance."""
    global _lattice_crawler
    if _lattice_crawler is None:
        _lattice_crawler = LatticeCrawler()
    return _lattice_crawler


def initialize_lattice() -> None:
    """Initialize the lattice on application startup."""
    try:
        crawler = get_lattice_crawler()
        crawler.ensure_index_exists()
        stats = crawler.get_index_statistics()
        logger.info(f"Lattice initialized: {stats}")
    except Exception as e:
        logger.error(f"Failed to initialize lattice: {e}")
        raise
