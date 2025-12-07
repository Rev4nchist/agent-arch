"""Suggestion Providers for personalized suggestions."""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from src.hmlr.suggestion_models import (
    PersonalizedSuggestion,
    SuggestionSource,
    SuggestionData
)

logger = logging.getLogger(__name__)

MAX_OPEN_LOOPS_DISPLAY = 3
MAX_COMMON_QUERIES_INPUT = 5
MAX_COMMON_QUERIES_OUTPUT = 3
MAX_TOPIC_INTERESTS_DISPLAY = 3
MAX_ENTITIES_DISPLAY = 2
MAX_CONTEXT_FACTS_DISPLAY = 2
TEXT_DISPLAY_LENGTH = 40
TEXT_TRUNCATE_LENGTH = 37
CROSS_SESSION_TEXT_LENGTH = 30
MIN_QUERY_LENGTH = 5
MIN_TOPIC_LENGTH = 3
MIN_ENTITY_NAME_LENGTH = 2
MIN_FACT_KEY_LENGTH = 3
STATIC_PRIORITY = 40
HIGH_PRIORITY_THRESHOLD = 70

VALID_PAGE_TYPES = frozenset({
    "dashboard", "meetings", "tasks", "agents", "decisions",
    "governance", "budget", "resources", "tech-radar",
    "architecture", "guide", "unknown", "followup"
})

PAGE_STATIC_SUGGESTIONS: Dict[str, List[str]] = {
    "dashboard": [
        "What can I ask you about?",
        "What are my most urgent tasks?",
        "Summarize recent meeting outcomes",
        "Show agents needing attention",
    ],
    "meetings": [
        "What topics were discussed in recent meetings?",
        "Find action items from governance meetings",
        "Who facilitated the most meetings?",
        "Show meetings with unprocessed transcripts",
    ],
    "tasks": [
        "What high priority tasks are pending?",
        "Show blocked tasks needing resolution",
        "Find tasks due this week",
        "Which tasks are assigned to me?",
    ],
    "agents": [
        "Which agents are in development?",
        "Show enterprise tier agents",
        "Find agents related to governance",
        "What agents need testing?",
    ],
    "decisions": [
        "What can I ask you about?",
        "What proposals are awaiting review?",
        "Show recent architecture decisions",
        "Find licensing-related proposals",
    ],
    "governance": [
        "What are the key governance policies?",
        "Show compliance requirements",
        "Find security guidelines",
        "What approval thresholds exist?",
    ],
    "budget": [
        "What is the current budget allocation?",
        "Show active licenses",
        "Find cost optimization opportunities",
        "What are the licensing constraints?",
    ],
    "resources": [
        "Find documents about agent frameworks",
        "Show governance resources",
        "What technical guides are available?",
        "Find architecture documentation",
    ],
    "tech-radar": [
        "What technologies should we adopt?",
        "Show technologies on hold",
        "Find tools being assessed",
        "What teams are using which technologies?",
    ],
    "architecture": [
        "Show code patterns for agents",
        "Find deployment guides",
        "What architecture patterns exist?",
        "Show hybrid deployment options",
    ],
    "guide": [
        "What can I ask you about?",
        "Help me understand the agent tiers",
        "Summarize platform activity this week",
        "How do I create a new agent?",
    ],
    "unknown": [
        "What can I help you with?",
        "Show me recent activity",
        "Find pending tasks",
        "Summarize recent meetings",
    ],
}


class SuggestionProvider(ABC):
    @abstractmethod
    def get_suggestions(self, **kwargs) -> List[PersonalizedSuggestion]:
        pass


class MemorySuggestionProvider(SuggestionProvider):
    def get_suggestions(
        self,
        data: SuggestionData,
        page_type: str = "unknown",
        **kwargs
    ) -> List[PersonalizedSuggestion]:
        suggestions = []
        suggestions.extend(self._from_open_loops(data.open_loops))
        suggestions.extend(self._from_common_queries(data.common_queries, data.expertise_level))
        suggestions.extend(self._from_topic_interests(data.topic_interests))
        suggestions.extend(self._from_entities(data.known_entities))
        suggestions.extend(self._from_context_facts(data.relevant_facts))
        return suggestions

    def _from_open_loops(self, open_loops: List[Dict[str, Any]]) -> List[PersonalizedSuggestion]:
        suggestions = []
        for loop in open_loops[:MAX_OPEN_LOOPS_DISPLAY]:
            text = loop.get("text", "")
            topic = loop.get("topic", "")
            priority = loop.get("priority", 100)
            is_current = loop.get("is_current_session", False)

            if text:
                display = f"Continue: {text}" if len(text) < TEXT_DISPLAY_LENGTH else f"Continue: {text[:TEXT_TRUNCATE_LENGTH]}..."
                if topic and not is_current:
                    display = f"Resume: {topic} - {text[:CROSS_SESSION_TEXT_LENGTH]}..."

                suggestions.append(PersonalizedSuggestion(
                    text=display,
                    source=SuggestionSource.OPEN_LOOP,
                    priority=priority,
                    confidence=0.9 if is_current else 0.7,
                    metadata={
                        "original_text": text,
                        "topic": topic,
                        "block_id": loop.get("block_id"),
                        "is_current_session": is_current
                    }
                ))
        return suggestions

    def _from_common_queries(
        self,
        queries: List[str],
        expertise: str
    ) -> List[PersonalizedSuggestion]:
        suggestions = []
        seen = set()

        for query in queries[:MAX_COMMON_QUERIES_INPUT]:
            normalized = query.lower().strip()
            if normalized in seen or len(normalized) < MIN_QUERY_LENGTH:
                continue
            seen.add(normalized)

            adapted = self._adapt_for_expertise(query, expertise)
            suggestions.append(PersonalizedSuggestion(
                text=adapted,
                source=SuggestionSource.COMMON_QUERY,
                priority=80,
                confidence=0.8,
                metadata={"original_query": query, "expertise": expertise}
            ))
        return suggestions[:MAX_COMMON_QUERIES_OUTPUT]

    def _adapt_for_expertise(self, query: str, expertise: str) -> str:
        if expertise == "beginner" and "how" not in query.lower():
            return f"Help me understand: {query}"
        if expertise == "expert" and "advanced" not in query.lower():
            return query.replace("How do I", "Show advanced options for")
        return query

    def _from_topic_interests(self, topics: List[str]) -> List[PersonalizedSuggestion]:
        suggestions = []
        for topic in topics[:MAX_TOPIC_INTERESTS_DISPLAY]:
            if len(topic) < MIN_TOPIC_LENGTH:
                continue
            suggestions.append(PersonalizedSuggestion(
                text=f"Explore more about {topic}",
                source=SuggestionSource.TOPIC_INTEREST,
                priority=80,
                confidence=0.75,
                metadata={"topic": topic}
            ))
        return suggestions

    def _from_entities(self, entities: List[Dict[str, str]]) -> List[PersonalizedSuggestion]:
        suggestions = []
        for entity in entities[:MAX_ENTITIES_DISPLAY]:
            name = entity.get("name", entity.get("key", ""))
            etype = entity.get("type", entity.get("category", "item"))
            if not name or len(name) < MIN_ENTITY_NAME_LENGTH:
                continue

            if etype.lower() in ["project", "agent", "team"]:
                text = f"Update on {name} {etype.lower()}"
            else:
                text = f"Tell me about {name}"

            suggestions.append(PersonalizedSuggestion(
                text=text,
                source=SuggestionSource.ENTITY,
                priority=60,
                confidence=0.7,
                metadata={"entity": name, "type": etype}
            ))
        return suggestions

    def _from_context_facts(self, facts: List[Dict[str, Any]]) -> List[PersonalizedSuggestion]:
        suggestions = []
        for fact in facts[:MAX_CONTEXT_FACTS_DISPLAY]:
            key = fact.get("key", "")
            category = fact.get("category", "")
            if not key or len(key) < MIN_FACT_KEY_LENGTH:
                continue

            category_lower = category.lower() if category else ""
            if category_lower in ["definition", "acronym"]:
                text = f"Explain more about {key}"
            elif category_lower == "entity":
                text = f"Details on {key}"
            else:
                continue

            suggestions.append(PersonalizedSuggestion(
                text=text,
                source=SuggestionSource.CONTEXT,
                priority=60,
                confidence=0.65,
                metadata={"fact_key": key, "category": category}
            ))
        return suggestions


class StaticSuggestionProvider(SuggestionProvider):
    def get_suggestions(
        self,
        page_type: str = "unknown",
        **kwargs
    ) -> List[PersonalizedSuggestion]:
        texts = PAGE_STATIC_SUGGESTIONS.get(page_type, PAGE_STATIC_SUGGESTIONS["unknown"])
        return [
            PersonalizedSuggestion(
                text=text,
                source=SuggestionSource.STATIC,
                priority=STATIC_PRIORITY,
                confidence=1.0,
                metadata={"page_type": page_type}
            )
            for text in texts
        ]


class IntentSuggestionProvider(SuggestionProvider):
    def get_suggestions(
        self,
        intent: str,
        response_text: Optional[str] = None,
        data: Optional[SuggestionData] = None,
        **kwargs
    ) -> List[PersonalizedSuggestion]:
        suggestions = []
        intent_suggestions = self._get_intent_suggestions(intent)

        for text, priority in intent_suggestions:
            suggestions.append(PersonalizedSuggestion(
                text=text,
                source=SuggestionSource.INTENT,
                priority=priority,
                confidence=0.85,
                metadata={"intent": intent}
            ))

        if data and data.open_loops:
            for loop in data.open_loops[:1]:
                if loop.get("priority", 0) > HIGH_PRIORITY_THRESHOLD:
                    suggestions.append(PersonalizedSuggestion(
                        text=f"Return to: {loop.get('topic', 'previous topic')}",
                        source=SuggestionSource.OPEN_LOOP,
                        priority=70,
                        confidence=0.75,
                        metadata={"from_followup": True}
                    ))
        return suggestions

    def _get_intent_suggestions(self, intent: str) -> List[tuple]:
        mappings = {
            "task_query": [
                ("Show all my pending tasks", 75),
                ("Find blocked tasks", 70),
                ("Tasks due this week", 70),
            ],
            "meeting_query": [
                ("Recent meeting summaries", 75),
                ("Pending action items", 70),
                ("Who attended recent meetings?", 65),
            ],
            "agent_query": [
                ("Agents in development", 75),
                ("Show agent tier breakdown", 70),
                ("Find similar agents", 65),
            ],
            "navigation": [
                ("What can I do here?", 70),
                ("Show me the main features", 65),
            ],
            "platform_help": [
                ("How do I create a task?", 75),
                ("Navigate to agents", 70),
                ("Platform overview", 65),
            ],
            "data_query": [
                ("Show recent activity", 70),
                ("Platform statistics", 65),
            ],
        }
        return mappings.get(intent, [("What else would you like to know?", 60)])
