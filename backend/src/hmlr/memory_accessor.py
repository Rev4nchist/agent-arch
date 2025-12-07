"""HMLR Memory Accessor for suggestion personalization."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone

from src.hmlr.suggestion_models import SuggestionData
from src.hmlr.models import BridgeBlock, UserProfile, Fact, BlockStatus
from src.config import settings

logger = logging.getLogger(__name__)

MAX_OPEN_LOOPS = 5
MAX_COMMON_QUERIES = 10
MAX_KNOWN_ENTITIES = 10
MAX_FACTS = 10
MAX_RECENT_TOPICS = 5
MAX_TOPIC_INTERESTS = 8
MAX_FREQUENCY_TOPICS = 5
CROSS_SESSION_HOURS_CUTOFF = 168
MIN_PRIORITY = 40
EXPERTISE_BEGINNER_THRESHOLD = 10
EXPERTISE_EXPERT_QUERIES = 100
EXPERTISE_EXPERT_RATIO = 0.6
EXPERTISE_ADVANCED_QUERIES = 50
EXPERTISE_ADVANCED_RATIO = 0.3


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class HMLRMemoryAccessor:
    def __init__(self, hmlr_service):
        self.hmlr = hmlr_service
        self._enabled = settings.hmlr_enabled

    async def get_suggestion_data(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        include_cross_session: bool = True
    ) -> SuggestionData:
        if not self._enabled or not self.hmlr:
            return SuggestionData()

        try:
            profile = await self.hmlr.get_user_profile(user_id)
            facts = await self.hmlr.get_user_facts(user_id, limit=20)
            open_loops = await self._get_open_loops(
                user_id, session_id, include_cross_session
            )
            recent_topics = await self._get_recent_topics(user_id, session_id)

            return SuggestionData(
                open_loops=open_loops,
                common_queries=profile.common_queries[:MAX_COMMON_QUERIES] if profile.common_queries else [],
                topic_interests=self._extract_topic_interests(profile),
                known_entities=profile.known_entities[:MAX_KNOWN_ENTITIES] if profile.known_entities else [],
                expertise_level=self._determine_expertise(profile),
                recent_topics=recent_topics,
                relevant_facts=self._format_facts(facts)
            )
        except Exception as e:
            logger.error(f"Error getting suggestion data: {e}")
            return SuggestionData()

    async def _get_open_loops(
        self,
        user_id: str,
        session_id: Optional[str],
        include_cross_session: bool
    ) -> List[Dict[str, Any]]:
        open_loops = []
        now = datetime.now(timezone.utc)

        if session_id:
            try:
                session_blocks = await self.hmlr.get_session_blocks(session_id)
                for block in session_blocks:
                    for loop in block.open_loops:
                        last_activity = _ensure_utc(block.last_activity)
                        age_hours = (now - last_activity).total_seconds() / 3600
                        priority = self._calculate_recency_priority(age_hours, is_current_session=True)
                        open_loops.append({
                            "text": loop,
                            "topic": block.topic_label,
                            "block_id": block.id,
                            "is_current_session": True,
                            "priority": priority,
                            "age_hours": age_hours
                        })
            except Exception as e:
                logger.warning(f"Error getting session blocks: {e}")

        if include_cross_session:
            try:
                all_blocks = await self._get_user_blocks_with_open_loops(user_id)
                for block in all_blocks:
                    if session_id and block.session_id == session_id:
                        continue
                    for loop in block.open_loops:
                        last_activity = _ensure_utc(block.last_activity)
                        age_hours = (now - last_activity).total_seconds() / 3600
                        if age_hours > CROSS_SESSION_HOURS_CUTOFF:
                            continue
                        priority = self._calculate_recency_priority(age_hours, is_current_session=False)
                        open_loops.append({
                            "text": loop,
                            "topic": block.topic_label,
                            "block_id": block.id,
                            "is_current_session": False,
                            "priority": priority,
                            "age_hours": age_hours
                        })
            except Exception as e:
                logger.warning(f"Error getting cross-session blocks: {e}")

        open_loops.sort(key=lambda x: x["priority"], reverse=True)
        return open_loops[:MAX_OPEN_LOOPS]

    def _calculate_recency_priority(self, age_hours: float, is_current_session: bool) -> int:
        base = 100 if is_current_session else 80
        if age_hours < 1:
            decay = 0
        elif age_hours < 24:
            decay = int(age_hours * 0.5)
        elif age_hours < 72:
            decay = 12 + int((age_hours - 24) * 0.3)
        else:
            decay = 26 + int((age_hours - 72) * 0.2)
        return max(MIN_PRIORITY, base - decay)

    async def _get_user_blocks_with_open_loops(self, user_id: str) -> List[BridgeBlock]:
        try:
            if hasattr(self.hmlr.block_manager, 'get_user_blocks_with_open_loops'):
                return await self.hmlr.block_manager.get_user_blocks_with_open_loops(user_id)
            return []
        except Exception:
            return []

    async def _get_recent_topics(
        self,
        user_id: str,
        session_id: Optional[str]
    ) -> List[str]:
        topics = []
        try:
            if session_id:
                blocks = await self.hmlr.get_session_blocks(session_id)
                topics = [b.topic_label for b in blocks if b.topic_label]
        except Exception as e:
            logger.warning(f"Error getting recent topics: {e}")
        return topics[:MAX_RECENT_TOPICS]

    def _extract_topic_interests(self, profile: UserProfile) -> List[str]:
        interests = []
        if profile.interaction_patterns:
            freq = profile.interaction_patterns.get("topic_frequency", {})
            sorted_topics = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            interests = [t[0] for t in sorted_topics[:MAX_FREQUENCY_TOPICS]]
        if profile.preferences:
            pref_topics = profile.preferences.get("preferred_topics", [])
            for t in pref_topics:
                if t not in interests:
                    interests.append(t)
        return interests[:MAX_TOPIC_INTERESTS]

    def _determine_expertise(self, profile: UserProfile) -> str:
        if not profile.interaction_patterns:
            return "intermediate"
        patterns = profile.interaction_patterns
        total = patterns.get("total_queries", 0)
        technical = patterns.get("technical_queries", 0)

        if total < EXPERTISE_BEGINNER_THRESHOLD:
            return "beginner"
        if total > EXPERTISE_EXPERT_QUERIES and technical / max(total, 1) > EXPERTISE_EXPERT_RATIO:
            return "expert"
        if total > EXPERTISE_ADVANCED_QUERIES or technical / max(total, 1) > EXPERTISE_ADVANCED_RATIO:
            return "advanced"
        return "intermediate"

    def _format_facts(self, facts: List[Fact]) -> List[Dict[str, Any]]:
        return [
            {
                "key": f.key,
                "value": f.value,
                "category": f.category,
                "confidence": f.confidence
            }
            for f in facts[:MAX_FACTS]
        ]
