"""Suggestion Orchestrator - Ranks and diversifies suggestions."""

import logging
from typing import List, Optional, Dict, Any
from collections import defaultdict

from src.hmlr.suggestion_models import (
    PersonalizedSuggestion,
    SuggestionSource,
    SuggestionData,
    SuggestionResponse
)
from src.hmlr.suggestion_providers import (
    MemorySuggestionProvider,
    StaticSuggestionProvider,
    IntentSuggestionProvider
)
from src.hmlr.memory_accessor import HMLRMemoryAccessor
from src.config import settings

logger = logging.getLogger(__name__)


class SuggestionOrchestrator:
    MAX_SUGGESTIONS = 6

    DIVERSITY_LIMITS = {
        SuggestionSource.OPEN_LOOP: 2,
        SuggestionSource.COMMON_QUERY: 2,
        SuggestionSource.TOPIC_INTEREST: 2,
        SuggestionSource.ENTITY: 1,
        SuggestionSource.CONTEXT: 2,
        SuggestionSource.STATIC: 3,
        SuggestionSource.INTENT: 2,
    }

    def __init__(self, hmlr_service=None):
        self.hmlr_service = hmlr_service
        self.memory_accessor = HMLRMemoryAccessor(hmlr_service) if hmlr_service else None
        self.memory_provider = MemorySuggestionProvider()
        self.static_provider = StaticSuggestionProvider()
        self.intent_provider = IntentSuggestionProvider()
        self._hmlr_enabled = settings.hmlr_enabled and self.memory_accessor is not None

    async def get_initial_suggestions(
        self,
        user_id: Optional[str],
        page_type: str,
        session_id: Optional[str] = None
    ) -> SuggestionResponse:
        if not user_id or not self._is_hmlr_enabled():
            return self._static_fallback(page_type, "no_user")

        try:
            data = await self.memory_accessor.get_suggestion_data(
                user_id=user_id,
                session_id=session_id,
                include_cross_session=True
            )

            if self._is_empty_memory(data):
                return self._static_fallback(page_type, "empty_memory")

            memory_suggestions = self.memory_provider.get_suggestions(
                data=data,
                page_type=page_type
            )
            static_suggestions = self.static_provider.get_suggestions(
                page_type=page_type
            )

            all_suggestions = memory_suggestions + static_suggestions
            ranked = self._rank_and_diversify(all_suggestions)

            return SuggestionResponse(
                suggestions=ranked,
                is_personalized=len(memory_suggestions) > 0,
                user_id=user_id,
                page_type=page_type
            )

        except Exception as e:
            logger.error(f"Error getting initial suggestions: {e}")
            return self._static_fallback(page_type, f"error: {str(e)}")

    async def get_followup_suggestions(
        self,
        user_id: Optional[str],
        intent: str,
        response_text: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[PersonalizedSuggestion]:
        data = None
        if user_id and self._is_hmlr_enabled() and self.memory_accessor:
            try:
                data = await self.memory_accessor.get_suggestion_data(
                    user_id=user_id,
                    session_id=session_id,
                    include_cross_session=True
                )
            except Exception as e:
                logger.warning(f"Error getting memory data for followup: {e}")

        intent_suggestions = self.intent_provider.get_suggestions(
            intent=intent,
            response_text=response_text,
            data=data
        )

        if data:
            memory_suggestions = self.memory_provider.get_suggestions(
                data=data,
                page_type="followup"
            )
            open_loop_suggestions = [
                s for s in memory_suggestions
                if s.source == SuggestionSource.OPEN_LOOP
            ][:2]
            all_suggestions = intent_suggestions + open_loop_suggestions
        else:
            all_suggestions = intent_suggestions

        return self._rank_and_diversify(all_suggestions, max_count=4)

    def _rank_and_diversify(
        self,
        suggestions: List[PersonalizedSuggestion],
        max_count: Optional[int] = None
    ) -> List[PersonalizedSuggestion]:
        if not suggestions:
            return []

        max_count = max_count or self.MAX_SUGGESTIONS
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (s.priority, s.confidence),
            reverse=True
        )

        source_counts: Dict[SuggestionSource, int] = defaultdict(int)
        seen_texts: set = set()
        result: List[PersonalizedSuggestion] = []

        for suggestion in sorted_suggestions:
            if len(result) >= max_count:
                break

            normalized_text = suggestion.text.lower().strip()
            if normalized_text in seen_texts:
                continue

            source = SuggestionSource(suggestion.source)
            limit = self.DIVERSITY_LIMITS.get(source, 2)
            if source_counts[source] >= limit:
                continue

            result.append(suggestion)
            source_counts[source] += 1
            seen_texts.add(normalized_text)

        return result

    def _static_fallback(
        self,
        page_type: str,
        reason: str
    ) -> SuggestionResponse:
        static_suggestions = self.static_provider.get_suggestions(page_type=page_type)
        return SuggestionResponse(
            suggestions=static_suggestions[:self.MAX_SUGGESTIONS],
            is_personalized=False,
            fallback_reason=reason,
            page_type=page_type
        )

    def _is_hmlr_enabled(self) -> bool:
        return self._hmlr_enabled

    def _is_empty_memory(self, data: SuggestionData) -> bool:
        return (
            not data.open_loops and
            not data.common_queries and
            not data.topic_interests and
            not data.known_entities
        )
