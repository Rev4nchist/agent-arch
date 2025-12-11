"""Governor - Conversation Routing Logic.

The Governor is the "brain" of HMLR routing, implementing 4 scenarios:
1. Topic Continuation - Same block, continue conversation
2. Topic Resumption - Reactivate paused block
3. New Topic Creation - First topic today (no active blocks)
4. Topic Shift - New topic, pause current block

The Governor runs 3 parallel tasks for each routing decision:
1. Get session blocks from Cosmos DB
2. Lookup relevant facts from Azure SQL
3. Retrieve memories via LatticeCrawler (semantic vector search)

Key 1: LatticeCrawler performs vector search to find raw candidates
Key 2: Governor applies contextual filtering on returned candidates
"""

import asyncio
import logging
import numpy as np
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta

from src.hmlr.models import (
    BridgeBlock,
    Fact,
    GovernorDecision,
    RoutingScenario,
    Turn,
    CandidateMemory,
    MemoryType,
)
from src.hmlr.bridge_block_mgr import BridgeBlockManager
from src.hmlr.sql_client import HMLRSQLClient
from src.hmlr.cache import TTLLRUCache
from src.config import settings

if TYPE_CHECKING:
    from src.hmlr.lattice_crawler import LatticeCrawler

logger = logging.getLogger(__name__)


class Governor:
    """Routes conversations to appropriate Bridge Blocks.

    Implements the HMLR 4-scenario routing pattern:
    - SCENARIO 1: Topic Continuation (similarity > threshold)
    - SCENARIO 2: Topic Resumption (paused block matches)
    - SCENARIO 3: New Topic (no active blocks)
    - SCENARIO 4: Topic Shift (new topic, pause current)

    Uses LatticeCrawler for semantic memory retrieval (Key 1)
    and applies contextual filtering (Key 2) on candidates.
    """

    def __init__(
        self,
        block_manager: BridgeBlockManager,
        sql_client: HMLRSQLClient,
        lattice_crawler: Optional["LatticeCrawler"] = None,
        ai_client: Any = None
    ):
        """Initialize Governor.

        Args:
            block_manager: Bridge Block manager instance
            sql_client: SQL client for fact lookup
            lattice_crawler: LatticeCrawler for semantic memory retrieval
            ai_client: AI client for topic similarity (optional)
        """
        self.block_manager = block_manager
        self.sql_client = sql_client
        self.lattice_crawler = lattice_crawler
        self.ai_client = ai_client
        self.similarity_threshold = settings.hmlr_topic_similarity_threshold
        self._embedding_cache = TTLLRUCache(
            maxsize=settings.hmlr_embedding_cache_size,
            ttl_minutes=settings.hmlr_embedding_cache_ttl_minutes
        )

    async def route(
        self,
        user_id: str,
        session_id: str,
        query: str,
        intent: Optional[str] = None,
        entities: Optional[List[str]] = None
    ) -> GovernorDecision:
        """Route a conversation turn to the appropriate Bridge Block.

        Runs 3 parallel tasks:
        1. Get session blocks
        2. Lookup relevant facts
        3. Retrieve memories (placeholder)

        Then determines 1 of 4 routing scenarios.

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User's query
            intent: Classified intent (optional)
            entities: Extracted entities (optional)

        Returns:
            GovernorDecision with routing details
        """
        logger.info(f"Governor routing for session {session_id}: {query[:50]}...")

        # Extract keywords from query for fact lookup
        keywords = self._extract_keywords(query, entities or [])

        # Run 3 parallel tasks (key HMLR pattern)
        blocks_task = self.block_manager.get_session_blocks(session_id)
        facts_task = self._lookup_facts(user_id, keywords)
        memories_task = self._retrieve_memories(user_id, query)

        blocks, facts, memories = await asyncio.gather(
            blocks_task, facts_task, memories_task
        )

        # Find active and paused blocks
        active_block = None
        paused_blocks = []

        for block in blocks:
            if block.status == "ACTIVE":
                active_block = block
            else:
                paused_blocks.append(block)

        # Compute topic similarity if active block exists
        topic_similarity = 0.0
        if active_block:
            topic_similarity = await self._compute_topic_similarity(
                query, active_block
            )

        # Determine routing scenario
        decision = await self._determine_scenario(
            query=query,
            user_id=user_id,
            session_id=session_id,
            active_block=active_block,
            paused_blocks=paused_blocks,
            facts=facts,
            memories=memories,
            topic_similarity=topic_similarity,
            intent=intent
        )

        logger.info(
            f"Governor decision: Scenario {decision.scenario}, "
            f"block={decision.matched_block_id}, new_topic={decision.is_new_topic}"
        )

        return decision

    async def _determine_scenario(
        self,
        query: str,
        user_id: str,
        session_id: str,
        active_block: Optional[BridgeBlock],
        paused_blocks: List[BridgeBlock],
        facts: List[Fact],
        memories: List[Dict],
        topic_similarity: float,
        intent: Optional[str]
    ) -> GovernorDecision:
        """Determine which of 4 scenarios applies.

        SCENARIO 1: Topic Continuation
            - Active block exists AND similarity > threshold

        SCENARIO 2: Topic Resumption
            - Paused block matches query better than active block

        SCENARIO 3: New Topic Creation (first today)
            - No active block AND no matching paused blocks

        SCENARIO 4: Topic Shift
            - Active block exists BUT query is new topic
        """

        # Generate topic label from query (for new blocks)
        suggested_label = await self._generate_topic_label(query, intent)

        # SCENARIO 3: No active block and nothing matches
        if not active_block:
            # Check if any paused block matches
            matching_paused = await self._find_matching_paused(query, paused_blocks)

            if matching_paused:
                # SCENARIO 2: Resumption
                return GovernorDecision(
                    scenario=RoutingScenario.TOPIC_RESUMPTION,
                    matched_block_id=matching_paused.id,
                    is_new_topic=False,
                    suggested_label=matching_paused.topic_label,
                    active_block=matching_paused,
                    relevant_facts=facts,
                    memories=memories,
                    topic_similarity=topic_similarity
                )
            else:
                # SCENARIO 3: New Topic (first)
                return GovernorDecision(
                    scenario=RoutingScenario.NEW_TOPIC_FIRST,
                    matched_block_id=None,
                    is_new_topic=True,
                    suggested_label=suggested_label,
                    active_block=None,
                    relevant_facts=facts,
                    memories=memories,
                    topic_similarity=0.0
                )

        # Active block exists - check similarity
        if topic_similarity >= self.similarity_threshold:
            # SCENARIO 1: Topic Continuation
            return GovernorDecision(
                scenario=RoutingScenario.TOPIC_CONTINUATION,
                matched_block_id=active_block.id,
                is_new_topic=False,
                suggested_label=active_block.topic_label,
                active_block=active_block,
                relevant_facts=facts,
                memories=memories,
                topic_similarity=topic_similarity
            )

        # Topic seems different - check paused blocks
        matching_paused = await self._find_matching_paused(query, paused_blocks)

        if matching_paused:
            # SCENARIO 2: Topic Resumption
            return GovernorDecision(
                scenario=RoutingScenario.TOPIC_RESUMPTION,
                matched_block_id=matching_paused.id,
                is_new_topic=False,
                suggested_label=matching_paused.topic_label,
                active_block=matching_paused,
                relevant_facts=facts,
                memories=memories,
                topic_similarity=topic_similarity
            )

        # SCENARIO 4: Topic Shift
        return GovernorDecision(
            scenario=RoutingScenario.TOPIC_SHIFT,
            matched_block_id=None,
            is_new_topic=True,
            suggested_label=suggested_label,
            active_block=active_block,  # Current block (to be paused)
            relevant_facts=facts,
            memories=memories,
            topic_similarity=topic_similarity
        )

    async def _compute_topic_similarity(
        self,
        query: str,
        block: BridgeBlock
    ) -> float:
        """Compute semantic similarity between query and block.

        Uses embedding-based cosine similarity when LatticeCrawler is available,
        falls back to keyword overlap otherwise.

        Args:
            query: User's query
            block: Bridge Block to compare

        Returns:
            Similarity score (0.0 - 1.0)
        """
        if self.lattice_crawler and settings.hmlr_vector_search_enabled:
            try:
                return await self._compute_embedding_similarity(query, block)
            except Exception as e:
                logger.warning(f"Embedding similarity failed, using keyword fallback: {e}")

        return self._compute_keyword_similarity(query, block)

    async def _compute_embedding_similarity(
        self,
        query: str,
        block: BridgeBlock
    ) -> float:
        """Compute cosine similarity using embeddings.

        Args:
            query: User's query
            block: Bridge Block to compare

        Returns:
            Cosine similarity score (0.0 - 1.0)
        """
        query_embedding = self.lattice_crawler.generate_embedding(query)

        block_content = self._get_block_content_for_embedding(block)
        cache_key = f"block_{block.id}"

        cached_embedding = self._embedding_cache.get(cache_key)
        if cached_embedding is not None:
            block_embedding = cached_embedding
            logger.debug(f"Embedding cache HIT for block {block.id}")
        else:
            block_embedding = self.lattice_crawler.generate_embedding(block_content)
            self._embedding_cache.set(cache_key, block_embedding)
            logger.debug(f"Embedding cache MISS for block {block.id}")

        similarity = self._cosine_similarity(query_embedding, block_embedding)
        return max(0.0, min(1.0, similarity))

    def _get_block_content_for_embedding(self, block: BridgeBlock) -> str:
        """Generate content string for block embedding.

        Args:
            block: Bridge Block

        Returns:
            Content string for embedding
        """
        parts = [f"Topic: {block.topic_label}"]

        if block.keywords:
            parts.append(f"Keywords: {', '.join(block.keywords)}")

        if block.summary:
            parts.append(f"Summary: {block.summary}")

        if block.turns:
            recent_queries = [t.query for t in block.turns[-3:]]
            parts.append(f"Recent queries: {' | '.join(recent_queries)}")

        return ". ".join(parts)

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (-1.0 to 1.0, typically 0.0 to 1.0 for embeddings)
        """
        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _compute_keyword_similarity(
        self,
        query: str,
        block: BridgeBlock
    ) -> float:
        """Compute similarity using keyword overlap (fallback).

        Args:
            query: User's query
            block: Bridge Block to compare

        Returns:
            Similarity score (0.0 - 1.0)
        """
        if not block.keywords:
            return 0.3

        query_lower = query.lower()
        query_words = set(query_lower.split())

        block_keywords = set(k.lower() for k in block.keywords)
        matches = query_words.intersection(block_keywords)

        if block.topic_label.lower() in query_lower:
            matches.add("_topic_match_")

        if block.turns:
            last_turn = block.turns[-1]
            if any(word in last_turn.query.lower() for word in query_words):
                matches.add("_turn_match_")

        if not block_keywords:
            return 0.3

        similarity = len(matches) / max(len(block_keywords), len(query_words))
        return min(similarity * 1.5, 1.0)

    async def _find_matching_paused(
        self,
        query: str,
        paused_blocks: List[BridgeBlock]
    ) -> Optional[BridgeBlock]:
        """Find a paused block that matches the query.

        Args:
            query: User's query
            paused_blocks: List of paused blocks

        Returns:
            Best matching paused block, or None
        """
        if not paused_blocks:
            return None

        best_match = None
        best_score = self.similarity_threshold * 0.8  # Slightly lower threshold

        for block in paused_blocks:
            score = await self._compute_topic_similarity(query, block)
            if score > best_score:
                best_score = score
                best_match = block

        return best_match

    async def _lookup_facts(
        self,
        user_id: str,
        keywords: List[str]
    ) -> List[Fact]:
        """Lookup relevant facts for keywords.

        Args:
            user_id: User identifier
            keywords: Keywords to search

        Returns:
            List of relevant facts
        """
        if not keywords:
            return []

        try:
            return await self.sql_client.search_facts(user_id, keywords, limit=5)
        except Exception as e:
            logger.error(f"Fact lookup failed: {e}")
            return []

    async def _retrieve_memories(
        self,
        user_id: str,
        query: str
    ) -> List[Dict]:
        """Retrieve relevant memories via LatticeCrawler (Key 1).

        Performs semantic vector search and applies Key 2 contextual filtering.

        Args:
            user_id: User identifier
            query: Query for semantic search

        Returns:
            List of filtered memory dictionaries
        """
        if not self.lattice_crawler or not settings.hmlr_vector_search_enabled:
            logger.debug("LatticeCrawler not available, skipping memory retrieval")
            return []

        try:
            candidates = await self.lattice_crawler.crawl(
                user_id=user_id,
                query=query,
                top_k=settings.hmlr_max_candidates,
                min_score=settings.hmlr_min_similarity_score,
            )

            filtered = self._filter_candidates(candidates)

            memories = [
                {
                    "id": c.id,
                    "content": c.content,
                    "type": c.memory_type,
                    "source_id": c.source_id,
                    "score": c.score,
                    "category": c.category,
                    "topic_label": c.topic_label,
                }
                for c in filtered
            ]

            logger.info(
                f"Retrieved {len(memories)} memories for user {user_id} "
                f"(from {len(candidates)} candidates)"
            )
            return memories

        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []

    def _filter_candidates(
        self,
        candidates: List[CandidateMemory]
    ) -> List[CandidateMemory]:
        """Apply Key 2 contextual filtering on raw candidates.

        Filters candidates based on:
        - Recency (prefer recent memories)
        - Confidence (for facts)
        - Topic isolation (avoid cross-topic leakage)

        Args:
            candidates: Raw candidates from LatticeCrawler

        Returns:
            Filtered list of candidates
        """
        if not candidates:
            return []

        filtered = []
        seen_topics = set()

        for candidate in candidates:
            if candidate.memory_type == MemoryType.FACT:
                if candidate.confidence and candidate.confidence < 0.5:
                    continue

            if candidate.memory_type == MemoryType.BLOCK_SUMMARY:
                if candidate.topic_label:
                    topic_key = candidate.topic_label.lower()[:20]
                    if topic_key in seen_topics:
                        continue
                    seen_topics.add(topic_key)

            filtered.append(candidate)

        filtered.sort(key=lambda c: c.score, reverse=True)

        return filtered[:settings.hmlr_max_candidates]

    def _extract_keywords(
        self,
        query: str,
        entities: List[str]
    ) -> List[str]:
        """Extract keywords from query and entities.

        Simple extraction based on significant words.

        Args:
            query: User's query
            entities: Extracted entities

        Returns:
            List of keywords
        """
        # Start with entities
        keywords = list(entities) if entities else []

        # Extract significant words from query
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
            'until', 'while', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'i', 'me', 'my', 'we',
            'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
            'it', 'its', 'they', 'them', 'their'
        }

        words = query.lower().split()
        for word in words:
            word = word.strip('.,!?;:"\'()[]{}')
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)

        return list(set(keywords))[:10]  # Dedupe and limit

    async def _generate_topic_label(
        self,
        query: str,
        intent: Optional[str]
    ) -> str:
        """Generate a topic label for a new block.

        Simple heuristic: First few significant words + intent.
        Future: Use LLM for better labels.

        Args:
            query: User's query
            intent: Classified intent

        Returns:
            Topic label string
        """
        keywords = self._extract_keywords(query, [])[:3]

        if intent:
            label = f"{intent.replace('_', ' ').title()}: {' '.join(keywords)}"
        else:
            label = ' '.join(keywords).title()

        return label[:50]  # Limit length
