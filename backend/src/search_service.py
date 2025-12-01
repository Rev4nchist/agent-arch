"""Azure AI Search service for RAG functionality."""
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
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from typing import List, Dict, Any, Optional
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for Azure AI Search operations."""

    def __init__(self):
        """Initialize Azure AI Search clients and Azure OpenAI client for embeddings."""
        self.endpoint = settings.azure_search_endpoint
        self.api_key = settings.azure_search_api_key
        self.index_name = settings.azure_search_index_name

        # Create credentials
        self.credential = AzureKeyCredential(self.api_key)

        # Initialize search clients
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )

        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        # Initialize Azure OpenAI client for embeddings
        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self.embeddings_deployment = settings.azure_openai_embeddings_deployment

    def _create_index_schema(self) -> SearchIndex:
        """
        Create the index schema with all required fields.

        Schema includes:
        - id: Unique identifier
        - content: Main searchable text content
        - content_vector: Embedding vector for semantic search
        - type: Document type (meeting|task|agent|governance)
        - title: Document title
        - metadata: Additional structured data (JSON)
        - created_at: Timestamp
        """
        # Define vector search configuration
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="vector-algorithm",
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="vector-algorithm",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ],
        )

        # Define index fields
        fields = [
            # Core fields
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
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
                vector_search_dimensions=1536,  # text-embedding-ada-002 dimensions
                vector_search_profile_name="vector-profile",
            ),

            # Metadata fields
            SimpleField(
                name="type",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),

            SearchableField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
            ),

            # Additional metadata as JSON string
            SearchableField(
                name="metadata",
                type=SearchFieldDataType.String,
                searchable=True,
            ),

            # Timestamp
            SimpleField(
                name="created_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),

            # Specific type-based fields
            SimpleField(
                name="status",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),

            SimpleField(
                name="priority",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),

            SimpleField(
                name="category",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
        ]

        # Create the index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )

        return index

    def create_or_update_index(self) -> None:
        """Create or update the search index."""
        try:
            index = self._create_index_schema()
            self.index_client.create_or_update_index(index)
            logger.info(f"Successfully created/updated index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error creating/updating index: {str(e)}")
            raise

    def index_exists(self) -> bool:
        """Check if the index exists."""
        try:
            self.index_client.get_index(self.index_name)
            return True
        except Exception:
            return False

    def delete_index(self) -> None:
        """Delete the search index."""
        try:
            self.index_client.delete_index(self.index_name)
            logger.info(f"Successfully deleted index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            raise

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        try:
            index = self.index_client.get_index(self.index_name)
            stats = self.index_client.get_index_statistics(self.index_name)

            return {
                "index_name": self.index_name,
                "document_count": stats.get("document_count", 0),
                "storage_size": stats.get("storage_size", 0),
                "field_count": len(index.fields),
            }
        except Exception as e:
            logger.error(f"Error getting index statistics: {str(e)}")
            return {
                "index_name": self.index_name,
                "document_count": 0,
                "error": str(e)
            }

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for the given text using Azure OpenAI.

        Args:
            text: Text content to generate embedding for

        Returns:
            List of floats representing the 1536-dimensional embedding vector

        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Clean and truncate text if needed (embeddings have token limits)
            # text-embedding-ada-002 has a limit of 8191 tokens (~32k characters)
            max_chars = 32000
            if len(text) > max_chars:
                text = text[:max_chars]
                logger.warning(f"Text truncated to {max_chars} characters for embedding generation")

            # Generate embedding
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embeddings_deployment
            )

            # Extract embedding vector
            embedding = response.data[0].embedding

            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of text content to generate embeddings for

        Returns:
            List of embedding vectors

        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Clean and prepare texts
            prepared_texts = []
            for text in texts:
                # Truncate if needed
                max_chars = 32000
                if len(text) > max_chars:
                    text = text[:max_chars]
                prepared_texts.append(text)

            # Generate embeddings in batch
            # Azure OpenAI supports batch embedding generation
            response = self.openai_client.embeddings.create(
                input=prepared_texts,
                model=self.embeddings_deployment
            )

            # Extract embedding vectors
            embeddings = [item.embedding for item in response.data]

            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings batch: {str(e)}")
            raise

    def upload_document(
        self,
        doc_id: str,
        content: str,
        doc_type: str,
        title: str,
        metadata: Dict[str, Any],
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        """
        Upload a single document to the search index with embedding.

        Args:
            doc_id: Unique document identifier
            content: Text content to index
            doc_type: Document type (meeting|task|agent|governance)
            title: Document title
            metadata: Additional metadata as dict (will be JSON serialized)
            status: Optional status field
            priority: Optional priority field
            category: Optional category field

        Raises:
            Exception: If upload fails
        """
        try:
            import json
            from datetime import datetime

            # Generate embedding for content
            content_vector = self.generate_embedding(content)

            # Prepare document
            document = {
                "id": doc_id,
                "content": content,
                "content_vector": content_vector,
                "type": doc_type,
                "title": title,
                "metadata": json.dumps(metadata),
                "created_at": datetime.utcnow().isoformat() + "Z",
            }

            # Add optional fields
            if status:
                document["status"] = status
            if priority:
                document["priority"] = priority
            if category:
                document["category"] = category

            # Upload to index
            result = self.search_client.upload_documents(documents=[document])

            logger.info(f"Uploaded document {doc_id} to index")

        except Exception as e:
            logger.error(f"Error uploading document {doc_id}: {str(e)}")
            raise

    def upload_documents_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Upload multiple documents to the search index in batch.

        Args:
            documents: List of document dicts with keys:
                - id: Document ID
                - content: Text content
                - type: Document type
                - title: Title
                - metadata: Dict of metadata
                - status, priority, category (optional)

        Returns:
            Dict with counts: {"success": int, "failed": int}

        Raises:
            Exception: If batch upload fails
        """
        try:
            import json
            from datetime import datetime

            # Extract content for batch embedding generation
            contents = [doc["content"] for doc in documents]

            # Generate embeddings in batch
            embeddings = self.generate_embeddings_batch(contents)

            # Prepare documents with embeddings
            prepared_docs = []
            for i, doc in enumerate(documents):
                prepared_doc = {
                    "id": doc["id"],
                    "content": doc["content"],
                    "content_vector": embeddings[i],
                    "type": doc["type"],
                    "title": doc["title"],
                    "metadata": json.dumps(doc.get("metadata", {})),
                    "created_at": datetime.utcnow().isoformat() + "Z",
                }

                # Add optional fields
                if "status" in doc:
                    prepared_doc["status"] = doc["status"]
                if "priority" in doc:
                    prepared_doc["priority"] = doc["priority"]
                if "category" in doc:
                    prepared_doc["category"] = doc["category"]

                prepared_docs.append(prepared_doc)

            # Upload batch
            results = self.search_client.upload_documents(documents=prepared_docs)

            # Count successes and failures
            success_count = sum(1 for r in results if r.succeeded)
            failed_count = len(results) - success_count

            logger.info(f"Batch upload: {success_count} succeeded, {failed_count} failed")

            return {"success": success_count, "failed": failed_count}

        except Exception as e:
            logger.error(f"Error in batch upload: {str(e)}")
            raise

    def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        """
        Update an existing document in the search index.

        Args:
            doc_id: Document ID to update
            content: New content (if provided, will regenerate embedding)
            title: New title
            metadata: New metadata
            status, priority, category: Optional field updates

        Raises:
            Exception: If update fails
        """
        try:
            import json

            # Build update document
            update_doc = {"id": doc_id}

            # If content changed, regenerate embedding
            if content is not None:
                update_doc["content"] = content
                update_doc["content_vector"] = self.generate_embedding(content)

            # Update other fields
            if title is not None:
                update_doc["title"] = title
            if metadata is not None:
                update_doc["metadata"] = json.dumps(metadata)
            if status is not None:
                update_doc["status"] = status
            if priority is not None:
                update_doc["priority"] = priority
            if category is not None:
                update_doc["category"] = category

            # Merge update
            result = self.search_client.merge_documents(documents=[update_doc])

            logger.info(f"Updated document {doc_id}")

        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {str(e)}")
            raise

    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the search index.

        Args:
            doc_id: Document ID to delete

        Raises:
            Exception: If deletion fails
        """
        try:
            result = self.search_client.delete_documents(documents=[{"id": doc_id}])

            logger.info(f"Deleted document {doc_id}")

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise

    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        top: int = 10,
        use_semantic_search: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search the index using text and/or semantic (vector) search.

        Args:
            query: Search query text
            doc_type: Optional filter by document type
            top: Number of results to return
            use_semantic_search: Whether to use vector search

        Returns:
            List of search results with relevance scores

        Raises:
            Exception: If search fails
        """
        try:
            from azure.search.documents.models import VectorizedQuery

            # Prepare search options
            search_options = {
                "top": top,
                "select": ["id", "content", "type", "title", "metadata", "status", "priority", "category"],
                "include_total_count": True,
            }

            # Add type filter if specified
            if doc_type:
                search_options["filter"] = f"type eq '{doc_type}'"

            # Add vector search if enabled
            if use_semantic_search:
                query_vector = self.generate_embedding(query)
                vector_query = VectorizedQuery(
                    vector=query_vector,
                    k_nearest_neighbors=top,
                    fields="content_vector"
                )
                search_options["vector_queries"] = [vector_query]

            # Perform search
            results = self.search_client.search(
                search_text=query if not use_semantic_search else None,
                **search_options
            )

            # Format results
            formatted_results = []
            for result in results:
                import json

                formatted_result = {
                    "id": result["id"],
                    "title": result["title"],
                    "content": result["content"],
                    "type": result["type"],
                    "score": result.get("@search.score", 0),
                }

                # Parse metadata JSON
                if "metadata" in result:
                    try:
                        formatted_result["metadata"] = json.loads(result["metadata"])
                    except:
                        formatted_result["metadata"] = {}

                # Add optional fields
                for field in ["status", "priority", "category"]:
                    if field in result:
                        formatted_result[field] = result[field]

                formatted_results.append(formatted_result)

            logger.info(f"Search returned {len(formatted_results)} results")

            return formatted_results

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise


# Global instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create the global SearchService instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


def initialize_search_index() -> None:
    """Initialize the search index on application startup."""
    try:
        service = get_search_service()

        if not service.index_exists():
            logger.info(f"Index {service.index_name} does not exist. Creating...")
            service.create_or_update_index()
        else:
            logger.info(f"Index {service.index_name} already exists.")

        # Log index statistics
        stats = service.get_index_statistics()
        logger.info(f"Index statistics: {stats}")

    except Exception as e:
        logger.error(f"Failed to initialize search index: {str(e)}")
        raise
