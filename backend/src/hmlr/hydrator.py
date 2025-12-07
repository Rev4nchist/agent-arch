"""Context Hydrator - Assembles Context for LLM Prompts.

The Hydrator combines multiple memory sources into a coherent
context string that gets prepended to LLM prompts:
- Active/resumed block history
- Relevant facts for the query
- User profile and preferences
- Open loops from paused blocks
"""

import logging
from typing import List, Optional

from src.hmlr.models import (
    BridgeBlock,
    Fact,
    UserProfile,
    HydratedContext,
    GovernorDecision
)

logger = logging.getLogger(__name__)

TOKENS_PER_CHAR = 0.25
MAX_CONTEXT_TOKENS = 4000


class ContextHydrator:
    """Assembles context from HMLR memory components."""

    def __init__(self, max_turns: int = 5, max_facts: int = 10):
        """Initialize Hydrator.

        Args:
            max_turns: Maximum turns to include from block history
            max_facts: Maximum facts to include
        """
        self.max_turns = max_turns
        self.max_facts = max_facts

    async def hydrate(
        self,
        decision: GovernorDecision,
        profile: Optional[UserProfile] = None,
        query: str = ""
    ) -> HydratedContext:
        """Assemble full context from Governor decision.

        Args:
            decision: GovernorDecision with block and facts
            profile: User profile (optional)
            query: Current user query

        Returns:
            HydratedContext with assembled context
        """
        block = decision.active_block
        facts = decision.relevant_facts
        memories = decision.memories

        block_summary = self._build_block_summary(block)
        block_history = self._build_block_history(block)
        facts_text = self._build_facts_text(facts)
        prefs_text = self._build_preferences_text(profile)
        loops_text = self._build_open_loops_text(block)

        full_context = self._assemble_full_context(
            block_summary=block_summary,
            block_history=block_history,
            facts_text=facts_text,
            prefs_text=prefs_text,
            loops_text=loops_text,
            scenario=decision.scenario
        )

        token_estimate = int(len(full_context) * TOKENS_PER_CHAR)

        return HydratedContext(
            block_summary=block_summary,
            block_history=block_history,
            relevant_facts_text=facts_text,
            user_preferences_text=prefs_text,
            open_loops_text=loops_text,
            full_context=full_context,
            token_estimate=token_estimate
        )

    def _build_block_summary(self, block: Optional[BridgeBlock]) -> str:
        """Build summary of the active block.

        Args:
            block: Active BridgeBlock

        Returns:
            Block summary string
        """
        if not block:
            return ""

        parts = [f"Current Topic: {block.topic_label}"]

        if block.summary:
            parts.append(f"Summary: {block.summary}")

        if block.keywords:
            parts.append(f"Keywords: {', '.join(block.keywords[:5])}")

        if block.decisions_made:
            recent = block.decisions_made[-3:]
            parts.append(f"Recent Decisions: {'; '.join(recent)}")

        return "\n".join(parts)

    def _build_block_history(self, block: Optional[BridgeBlock]) -> str:
        """Build conversation history from block turns.

        Args:
            block: Active BridgeBlock

        Returns:
            Conversation history string
        """
        if not block or not block.turns:
            return ""

        recent_turns = block.turns[-self.max_turns:]
        history_parts = []

        for turn in recent_turns:
            history_parts.append(f"User: {turn.query}")
            if turn.response_summary:
                history_parts.append(f"Assistant: {turn.response_summary}")

        return "\n".join(history_parts)

    def _build_facts_text(self, facts: List[Fact]) -> str:
        """Build relevant facts text.

        Args:
            facts: List of relevant facts

        Returns:
            Facts text string
        """
        if not facts:
            return ""

        limited_facts = facts[:self.max_facts]
        fact_lines = []

        for fact in limited_facts:
            if fact.category == "Secret":
                fact_lines.append(f"- {fact.key}: [SENSITIVE - Available on request]")
            else:
                fact_lines.append(f"- {fact.key}: {fact.value}")

        return "Known Facts:\n" + "\n".join(fact_lines)

    def _build_preferences_text(self, profile: Optional[UserProfile]) -> str:
        """Build user preferences text.

        Args:
            profile: User profile

        Returns:
            Preferences text string
        """
        if not profile:
            return ""

        parts = []

        if profile.preferences:
            prefs = []
            for key, value in list(profile.preferences.items())[:5]:
                prefs.append(f"{key}: {value}")
            if prefs:
                parts.append("Preferences: " + "; ".join(prefs))

        if profile.known_entities:
            entities = []
            for entity in profile.known_entities[:5]:
                if isinstance(entity, dict):
                    name = entity.get("name", "")
                    role = entity.get("role", "")
                    if name:
                        entities.append(f"{name} ({role})" if role else name)
            if entities:
                parts.append("Known Entities: " + ", ".join(entities))

        if profile.interaction_patterns:
            patterns = profile.interaction_patterns
            if patterns.get("preferred_response_length"):
                parts.append(f"Response Style: {patterns['preferred_response_length']}")
            if patterns.get("expertise_level"):
                parts.append(f"Expertise: {patterns['expertise_level']}")

        return "\n".join(parts)

    def _build_open_loops_text(self, block: Optional[BridgeBlock]) -> str:
        """Build open loops text (unresolved items).

        Args:
            block: Active BridgeBlock

        Returns:
            Open loops text string
        """
        if not block or not block.open_loops:
            return ""

        loops = block.open_loops[-5:]
        return "Open Items:\n- " + "\n- ".join(loops)

    def _assemble_full_context(
        self,
        block_summary: str,
        block_history: str,
        facts_text: str,
        prefs_text: str,
        loops_text: str,
        scenario: int
    ) -> str:
        """Assemble all context parts into final string.

        Args:
            block_summary: Block summary
            block_history: Conversation history
            facts_text: Relevant facts
            prefs_text: User preferences
            loops_text: Open loops
            scenario: Routing scenario (1-4)

        Returns:
            Full assembled context string
        """
        sections = []

        scenario_labels = {
            1: "Continuing conversation on same topic",
            2: "Resuming previous topic",
            3: "Starting new conversation",
            4: "Shifting to new topic"
        }
        sections.append(f"[Context: {scenario_labels.get(scenario, 'Unknown')}]")

        if block_summary:
            sections.append(f"\n{block_summary}")

        if prefs_text:
            sections.append(f"\n{prefs_text}")

        if facts_text:
            sections.append(f"\n{facts_text}")

        if loops_text:
            sections.append(f"\n{loops_text}")

        if block_history:
            sections.append(f"\nRecent Conversation:\n{block_history}")

        full_context = "\n".join(sections)

        max_chars = int(MAX_CONTEXT_TOKENS / TOKENS_PER_CHAR)
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n[Context truncated]"

        return full_context

    def hydrate_minimal(
        self,
        block: Optional[BridgeBlock],
        facts: List[Fact]
    ) -> str:
        """Quick minimal context for simple queries.

        Args:
            block: Active block
            facts: Relevant facts

        Returns:
            Minimal context string
        """
        parts = []

        if block:
            parts.append(f"Topic: {block.topic_label}")
            if block.turns:
                last_turn = block.turns[-1]
                parts.append(f"Last: {last_turn.query[:100]}")

        if facts:
            fact_strs = [f"{f.key}={f.value}" for f in facts[:3]]
            parts.append(f"Facts: {'; '.join(fact_strs)}")

        return " | ".join(parts)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return int(len(text) * TOKENS_PER_CHAR)
