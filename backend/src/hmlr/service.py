"""HMLR Service - Main Orchestrator.

The HMLRService is the main entry point for the HMLR memory system.
It orchestrates all components:
- Governor: Routing decisions
- BridgeBlockManager: Topic organization
- FactScrubber: Fact extraction
- Hydrator: Context assembly
- Scribe: Profile updates
- LatticeCrawler: Vector search for semantic memory retrieval
"""

import asyncio
import logging
from typing import Optional, Any, List

from src.hmlr.models import (
    BridgeBlock,
    Fact,
    UserProfile,
    GovernorDecision,
    HydratedContext,
    Turn,
    RoutingScenario
)
from src.hmlr.governor import Governor
from src.hmlr.bridge_block_mgr import BridgeBlockManager
from src.hmlr.fact_scrubber import FactScrubber
from src.hmlr.hydrator import ContextHydrator
from src.hmlr.scribe import Scribe
from src.hmlr.sql_client import HMLRSQLClient
from src.hmlr.lattice_crawler import LatticeCrawler
from src.config import settings

logger = logging.getLogger(__name__)


class HMLRService:
    """Main orchestrator for HMLR memory system.

    Provides high-level API for memory operations:
    - route_query: Get routing decision and hydrated context
    - store_turn: Store conversation turn and trigger background tasks
    - get_context: Get context for current conversation
    """

    def __init__(
        self,
        ai_client: Any = None,
        sql_connection_string: Optional[str] = None
    ):
        """Initialize HMLR Service.

        Args:
            ai_client: AI client for LLM operations
            sql_connection_string: Azure SQL connection string
        """
        self.sql_client = HMLRSQLClient(
            sql_connection_string or settings.hmlr_sql_connection_string
        )

        self.lattice_crawler = None
        if settings.hmlr_vector_search_enabled:
            try:
                self.lattice_crawler = LatticeCrawler()
                self.lattice_crawler.ensure_index_exists()
                logger.info("LatticeCrawler initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LatticeCrawler: {e}. Vector search disabled.")
                self.lattice_crawler = None

        self.block_manager = BridgeBlockManager(
            lattice_crawler=self.lattice_crawler
        )
        self.governor = Governor(
            block_manager=self.block_manager,
            sql_client=self.sql_client,
            lattice_crawler=self.lattice_crawler,
            ai_client=ai_client
        )
        self.fact_scrubber = FactScrubber(
            sql_client=self.sql_client,
            lattice_crawler=self.lattice_crawler,
            ai_client=ai_client
        )
        self.hydrator = ContextHydrator()
        self.scribe = Scribe(
            sql_client=self.sql_client,
            ai_client=ai_client
        )
        self.ai_client = ai_client
        self._enabled = settings.hmlr_enabled

    async def route_query(
        self,
        user_id: str,
        session_id: str,
        query: str,
        intent: Optional[str] = None,
        entities: Optional[List[str]] = None
    ) -> tuple[GovernorDecision, HydratedContext]:
        """Route query and get hydrated context.

        Main entry point for the query pipeline.

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User's query
            intent: Classified intent (optional)
            entities: Extracted entities (optional)

        Returns:
            Tuple of (GovernorDecision, HydratedContext)
        """
        if not self._enabled:
            return self._empty_decision(), HydratedContext()

        decision = await self.governor.route(
            user_id=user_id,
            session_id=session_id,
            query=query,
            intent=intent,
            entities=entities
        )

        profile = await self.scribe.get_or_create_profile(user_id)

        context = await self.hydrator.hydrate(
            decision=decision,
            profile=profile,
            query=query
        )

        logger.info(
            f"HMLR route: scenario={decision.scenario}, "
            f"block={decision.matched_block_id}, "
            f"tokens={context.token_estimate}"
        )

        return decision, context

    async def store_turn(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: str,
        decision: GovernorDecision,
        intent: Optional[str] = None,
        entities: Optional[List[str]] = None
    ) -> Optional[BridgeBlock]:
        """Store a conversation turn.

        Creates/updates blocks based on Governor decision and
        triggers background tasks for fact extraction and profile updates.

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User's query
            response: AI response
            decision: Governor's routing decision
            intent: Classified intent
            entities: Extracted entities

        Returns:
            Updated BridgeBlock
        """
        if not self._enabled:
            return None

        turn = Turn(
            index=0,
            query=query,
            response_summary=self._summarize_response(response),
            intent=intent,
            entities=entities or []
        )

        block = await self._handle_routing_scenario(
            decision=decision,
            user_id=user_id,
            session_id=session_id,
            turn=turn
        )

        if block:
            logger.info(
                f"HMLR turn stored: block={block.id}, "
                f"topic={block.topic_label}, turns={len(block.turns)}"
            )
            asyncio.create_task(self._background_processing(
                user_id=user_id,
                block=block,
                turn=turn,
                response=response
            ))

        return block

    async def _handle_routing_scenario(
        self,
        decision: GovernorDecision,
        user_id: str,
        session_id: str,
        turn: Turn
    ) -> Optional[BridgeBlock]:
        """Handle the routing scenario to create/update blocks.

        Args:
            decision: Governor's decision
            user_id: User identifier
            session_id: Session identifier
            turn: Turn to add

        Returns:
            Updated or created BridgeBlock
        """
        scenario = decision.scenario

        if scenario == RoutingScenario.TOPIC_CONTINUATION:
            if decision.matched_block_id:
                return await self.block_manager.add_turn(
                    block_id=decision.matched_block_id,
                    session_id=session_id,
                    turn=turn
                )

        elif scenario == RoutingScenario.TOPIC_RESUMPTION:
            if decision.matched_block_id:
                block = await self.block_manager.resume_block(
                    block_id=decision.matched_block_id,
                    session_id=session_id
                )
                if block:
                    return await self.block_manager.add_turn(
                        block_id=block.id,
                        session_id=session_id,
                        turn=turn
                    )

        elif scenario == RoutingScenario.NEW_TOPIC_FIRST:
            return await self.block_manager.create_block(
                session_id=session_id,
                user_id=user_id,
                topic_label=decision.suggested_label,
                first_turn=turn
            )

        elif scenario == RoutingScenario.TOPIC_SHIFT:
            if decision.active_block:
                await self.block_manager.pause_block(
                    block_id=decision.active_block.id,
                    session_id=session_id
                )

            return await self.block_manager.create_block(
                session_id=session_id,
                user_id=user_id,
                topic_label=decision.suggested_label,
                first_turn=turn
            )

        return None

    async def _background_processing(
        self,
        user_id: str,
        block: BridgeBlock,
        turn: Turn,
        response: str
    ):
        """Background processing for fact extraction and profile updates.

        Args:
            user_id: User identifier
            block: Current block
            turn: Current turn
            response: AI response
        """
        try:
            if settings.hmlr_fact_extraction_enabled:
                combined_text = f"User: {turn.query}\nAssistant: {response}"
                await self.fact_scrubber.extract_and_save(
                    user_id=user_id,
                    block_id=block.id,
                    text=combined_text
                )

            if settings.hmlr_profile_update_enabled:
                await self.scribe.process_turn(
                    user_id=user_id,
                    block=block,
                    turn=turn
                )

        except Exception as e:
            logger.error(f"Background processing error: {e}")

    def _summarize_response(self, response: str, max_length: int = 200) -> str:
        """Summarize response for turn storage.

        Args:
            response: Full AI response
            max_length: Maximum summary length

        Returns:
            Summarized response
        """
        if len(response) <= max_length:
            return response

        return response[:max_length - 3] + "..."

    def _empty_decision(self) -> GovernorDecision:
        """Create empty decision when HMLR is disabled.

        Returns:
            Empty GovernorDecision
        """
        return GovernorDecision(
            scenario=RoutingScenario.NEW_TOPIC_FIRST,
            matched_block_id=None,
            is_new_topic=True,
            suggested_label="",
            active_block=None,
            relevant_facts=[],
            memories=[],
            topic_similarity=0.0
        )

    async def get_context(
        self,
        user_id: str,
        session_id: str,
        query: str
    ) -> str:
        """Get context string for a query (simplified API).

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User's query

        Returns:
            Context string for LLM
        """
        decision, context = await self.route_query(
            user_id=user_id,
            session_id=session_id,
            query=query
        )
        return context.full_context

    async def get_user_facts(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Fact]:
        """Get all facts for a user.

        Args:
            user_id: User identifier
            limit: Maximum facts

        Returns:
            List of Fact objects
        """
        return await self.fact_scrubber.get_user_facts(user_id, limit)

    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile.

        Args:
            user_id: User identifier

        Returns:
            UserProfile object
        """
        return await self.scribe.get_or_create_profile(user_id)

    async def get_session_blocks(self, session_id: str) -> List[BridgeBlock]:
        """Get all blocks for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of BridgeBlock objects
        """
        return await self.block_manager.get_session_blocks(session_id)

    async def add_open_loop(
        self,
        block_id: str,
        session_id: str,
        open_loop: str
    ) -> bool:
        """Add an open loop to a block.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            open_loop: Open loop text

        Returns:
            True if added
        """
        return await self.block_manager.add_open_loop(
            block_id=block_id,
            session_id=session_id,
            open_loop=open_loop
        )

    async def add_decision(
        self,
        block_id: str,
        session_id: str,
        decision_text: str
    ) -> bool:
        """Add a decision to a block.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            decision_text: Decision text

        Returns:
            True if added
        """
        return await self.block_manager.add_decision(
            block_id=block_id,
            session_id=session_id,
            decision=decision_text
        )

    async def end_session(self, session_id: str, user_id: str):
        """Clean up when session ends.

        Triggers block completion processing.

        Args:
            session_id: Session identifier
            user_id: User identifier
        """
        blocks = await self.block_manager.get_session_blocks(session_id)

        for block in blocks:
            if block.status == "ACTIVE":
                await self.block_manager.pause_block(block.id, session_id)
                await self.scribe.process_block_completion(user_id, block)

        logger.info(f"Session {session_id} ended, processed {len(blocks)} blocks")

    def close(self):
        """Close database connections."""
        self.sql_client.close()

    @property
    def enabled(self) -> bool:
        """Check if HMLR is enabled."""
        return self._enabled

    def enable(self):
        """Enable HMLR."""
        self._enabled = True
        logger.info("HMLR enabled")

    def disable(self):
        """Disable HMLR."""
        self._enabled = False
        logger.info("HMLR disabled")
