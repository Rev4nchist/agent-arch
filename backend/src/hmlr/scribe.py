"""Scribe - Async User Profile Updates.

The Scribe agent learns from conversations and updates
user profiles over time:
- Preferences detection
- Interaction pattern learning
- Entity relationship tracking
- Common query patterns
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.hmlr.models import (
    BridgeBlock,
    UserProfile,
    Turn,
    ScribeUpdate
)
from src.hmlr.sql_client import HMLRSQLClient
from src.config import settings

logger = logging.getLogger(__name__)


class Scribe:
    """Async agent for learning and updating user profiles."""

    def __init__(self, sql_client: HMLRSQLClient, ai_client: Any = None):
        """Initialize Scribe.

        Args:
            sql_client: SQL client for profile persistence
            ai_client: AI client for preference extraction (optional)
        """
        self.sql_client = sql_client
        self.ai_client = ai_client

    async def process_turn(
        self,
        user_id: str,
        block: BridgeBlock,
        turn: Turn
    ) -> Optional[ScribeUpdate]:
        """Process a conversation turn for profile updates.

        Called asynchronously after each turn to learn from interactions.

        Args:
            user_id: User identifier
            block: Current bridge block
            turn: The turn to process

        Returns:
            ScribeUpdate if updates were made, None otherwise
        """
        if not settings.hmlr_profile_update_enabled:
            return None

        updates = {}

        query_update = self._extract_query_pattern(turn.query)
        if query_update:
            updates["common_queries"] = query_update

        entity_updates = self._extract_entities(turn)
        if entity_updates:
            updates["known_entities"] = entity_updates

        pattern_updates = self._analyze_interaction_pattern(turn)
        if pattern_updates:
            updates["interaction_patterns"] = pattern_updates

        if not updates:
            return None

        try:
            for field, value in updates.items():
                await self.sql_client.update_profile_field(user_id, field, value)

            logger.info(f"Scribe updated profile for {user_id}: {list(updates.keys())}")

            return ScribeUpdate(
                user_id=user_id,
                updates=updates,
                source_block_id=block.id,
                timestamp=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Scribe profile update failed: {e}")
            return None

    async def process_block_completion(
        self,
        user_id: str,
        block: BridgeBlock
    ) -> Optional[ScribeUpdate]:
        """Process a completed block for aggregate insights.

        Called when a block is paused or session ends.

        Args:
            user_id: User identifier
            block: Completed bridge block

        Returns:
            ScribeUpdate if updates were made
        """
        if not block.turns:
            return None

        updates = {}

        topic_preference = self._analyze_topic_engagement(block)
        if topic_preference:
            updates["preferences"] = {"topic_interests": topic_preference}

        decisions = block.decisions_made
        if decisions:
            updates["interaction_patterns"] = {
                "decision_making_style": self._classify_decision_style(decisions)
            }

        if updates:
            try:
                for field, value in updates.items():
                    await self.sql_client.update_profile_field(user_id, field, value)

                return ScribeUpdate(
                    user_id=user_id,
                    updates=updates,
                    source_block_id=block.id
                )
            except Exception as e:
                logger.error(f"Block completion update failed: {e}")

        return None

    def _extract_query_pattern(self, query: str) -> Optional[str]:
        """Extract query pattern for common queries tracking.

        Args:
            query: User query

        Returns:
            Normalized query pattern or None
        """
        query_lower = query.lower().strip()

        patterns = [
            ("how do i", "how-to"),
            ("what is", "definition"),
            ("show me", "retrieval"),
            ("create", "creation"),
            ("update", "modification"),
            ("delete", "deletion"),
            ("find", "search"),
            ("list", "listing"),
            ("help", "assistance"),
            ("why", "explanation"),
        ]

        for trigger, pattern_type in patterns:
            if query_lower.startswith(trigger):
                return f"{pattern_type}:{query_lower[:50]}"

        if len(query_lower) > 20:
            return query_lower[:50]

        return None

    def _extract_entities(self, turn: Turn) -> Optional[List[Dict[str, str]]]:
        """Extract entity mentions from turn.

        Args:
            turn: Conversation turn

        Returns:
            List of entity dictionaries or None
        """
        if not turn.entities:
            return None

        entities = []
        for entity in turn.entities[:5]:
            entities.append({
                "name": entity,
                "context": turn.query[:50],
                "intent": turn.intent or "general"
            })

        return entities if entities else None

    def _analyze_interaction_pattern(self, turn: Turn) -> Optional[Dict[str, Any]]:
        """Analyze interaction patterns from turn.

        Args:
            turn: Conversation turn

        Returns:
            Pattern updates or None
        """
        patterns = {}

        query_len = len(turn.query)
        if query_len < 20:
            patterns["query_style"] = "brief"
        elif query_len > 200:
            patterns["query_style"] = "detailed"
        else:
            patterns["query_style"] = "moderate"

        technical_terms = [
            "api", "database", "function", "class", "method",
            "deploy", "container", "kubernetes", "azure", "aws"
        ]
        query_lower = turn.query.lower()
        tech_count = sum(1 for term in technical_terms if term in query_lower)

        if tech_count >= 3:
            patterns["expertise_level"] = "advanced"
        elif tech_count >= 1:
            patterns["expertise_level"] = "intermediate"

        return patterns if patterns else None

    def _analyze_topic_engagement(self, block: BridgeBlock) -> Optional[Dict[str, Any]]:
        """Analyze topic engagement from completed block.

        Args:
            block: Completed bridge block

        Returns:
            Topic engagement data or None
        """
        if not block.turns:
            return None

        turn_count = len(block.turns)
        engagement_level = "high" if turn_count > 5 else "medium" if turn_count > 2 else "low"

        return {
            "topic": block.topic_label,
            "engagement": engagement_level,
            "turn_count": turn_count
        }

    def _classify_decision_style(self, decisions: List[str]) -> str:
        """Classify decision-making style from decisions made.

        Args:
            decisions: List of decisions made in block

        Returns:
            Decision style classification
        """
        if not decisions:
            return "exploratory"

        if len(decisions) >= 3:
            return "decisive"
        elif len(decisions) == 1:
            return "focused"
        else:
            return "balanced"

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get user profile or create if not exists.

        Args:
            user_id: User identifier

        Returns:
            UserProfile object
        """
        profile = await self.sql_client.get_user_profile(user_id)

        if not profile:
            profile = UserProfile(
                user_id=user_id,
                preferences={},
                common_queries=[],
                known_entities=[],
                interaction_patterns={},
                last_updated=datetime.utcnow()
            )
            await self.sql_client.save_user_profile(profile)

        return profile

    async def update_preference(
        self,
        user_id: str,
        key: str,
        value: Any
    ) -> bool:
        """Update a specific user preference.

        Args:
            user_id: User identifier
            key: Preference key
            value: Preference value

        Returns:
            True if updated successfully
        """
        return await self.sql_client.update_profile_field(
            user_id, "preferences", {key: value}
        )

    async def add_known_entity(
        self,
        user_id: str,
        name: str,
        role: str,
        context: str = ""
    ) -> bool:
        """Add a known entity to user profile.

        Args:
            user_id: User identifier
            name: Entity name
            role: Entity role/relationship
            context: Additional context

        Returns:
            True if added successfully
        """
        entity = {"name": name, "role": role, "context": context}
        return await self.sql_client.update_profile_field(
            user_id, "known_entities", [entity]
        )
