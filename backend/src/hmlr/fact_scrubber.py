"""Fact Scrubber - LLM-Based Fact Extraction.

Extracts hard facts from conversations using AI:
- Definitions: "X is Y", "X means Y"
- Acronyms: "X stands for Y", "X (Y)"
- Entities: "David owns X", "Contact Y"
- Secrets: API keys, passwords, user preferences
"""

import json
import logging
import time
from typing import List, Optional, Any

from src.hmlr.models import Fact, FactCategory, FactExtractionResult
from src.hmlr.sql_client import HMLRSQLClient
from src.config import settings

logger = logging.getLogger(__name__)


EXTRACTION_PROMPT = """Extract ONLY hard facts from this conversation turn.

CATEGORIES (only use these):
- Definition: "X is Y", "X means Y", explicit definitions
- Acronym: "X stands for Y", "X (abbreviation)", acronym expansions
- Secret: API keys, passwords, credentials, sensitive user preferences
- Entity: Named entities with relationships ("David owns backend", "Contact Sarah for X")

RULES:
1. Extract ONLY explicit, stated facts - no inferences
2. Each fact must have clear evidence in the text
3. Skip opinions, questions, and uncertain statements
4. Keep values concise but complete
5. Confidence: 1.0 for explicit statements, 0.8 for strong implications

Return JSON format:
{
  "facts": [
    {
      "key": "short_identifier",
      "value": "the fact content",
      "category": "Definition|Acronym|Secret|Entity",
      "evidence_snippet": "exact text from input that supports this fact",
      "confidence": 0.8-1.0
    }
  ]
}

If no facts found, return: {"facts": []}

TEXT TO ANALYZE:
"""


class FactScrubber:
    """Extracts and persists facts from conversation turns."""

    def __init__(
        self,
        sql_client: HMLRSQLClient,
        ai_client: Any = None
    ):
        """Initialize FactScrubber.

        Args:
            sql_client: SQL client for fact persistence
            ai_client: AI client for LLM extraction (optional)
        """
        self.sql_client = sql_client
        self.ai_client = ai_client

    async def extract_facts(
        self,
        text: str,
        user_id: str,
        block_id: Optional[str] = None
    ) -> FactExtractionResult:
        """Extract facts from text using LLM.

        Args:
            text: Text to analyze
            user_id: User identifier
            block_id: Source block ID (optional)

        Returns:
            FactExtractionResult with extracted facts
        """
        start_time = time.time()

        if not text or len(text.strip()) < 10:
            return FactExtractionResult(
                facts=[],
                extraction_method="skip_short",
                processing_time_ms=0
            )

        try:
            facts = await self._llm_extract(text, user_id, block_id)
            processing_time = int((time.time() - start_time) * 1000)

            return FactExtractionResult(
                facts=facts,
                extraction_method="llm",
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            facts = self._regex_extract(text, user_id, block_id)
            processing_time = int((time.time() - start_time) * 1000)

            return FactExtractionResult(
                facts=facts,
                extraction_method="regex_fallback",
                processing_time_ms=processing_time
            )

    async def extract_and_save(
        self,
        user_id: str,
        block_id: str,
        text: str
    ) -> List[Fact]:
        """Extract facts from text and save to database.

        Main entry point for background fact extraction.

        Args:
            user_id: User identifier
            block_id: Source block ID
            text: Text to analyze

        Returns:
            List of saved Fact objects
        """
        if not settings.hmlr_fact_extraction_enabled:
            return []

        result = await self.extract_facts(text, user_id, block_id)

        saved_facts = []
        for fact in result.facts:
            try:
                fact_id = await self.sql_client.save_fact(fact)
                fact.fact_id = fact_id
                saved_facts.append(fact)
                logger.info(f"Saved fact: {fact.key} ({fact.category})")
            except Exception as e:
                logger.error(f"Failed to save fact {fact.key}: {e}")

        logger.info(
            f"Fact extraction complete: {len(saved_facts)} facts saved "
            f"({result.extraction_method}, {result.processing_time_ms}ms)"
        )

        return saved_facts

    async def _llm_extract(
        self,
        text: str,
        user_id: str,
        block_id: Optional[str]
    ) -> List[Fact]:
        """Extract facts using LLM.

        Args:
            text: Text to analyze
            user_id: User identifier
            block_id: Source block ID

        Returns:
            List of extracted Fact objects

        Raises:
            ValueError: If no AI client configured (caller should use regex)
        """
        if not self.ai_client:
            logger.warning("No AI client configured, using regex fallback")
            raise ValueError("No AI client configured")

        prompt = EXTRACTION_PROMPT + text

        try:
            response = await self.ai_client.complete(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.1
            )

            response_text = response.get("content", "")
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                logger.warning("No JSON found in LLM response")
                return []

            facts = []
            for item in data.get("facts", []):
                try:
                    category = self._parse_category(item.get("category", "Entity"))
                    fact = Fact(
                        user_id=user_id,
                        key=item.get("key", "unknown"),
                        value=item.get("value", ""),
                        category=category,
                        source_block_id=block_id,
                        evidence_snippet=item.get("evidence_snippet"),
                        confidence=float(item.get("confidence", 0.8))
                    )
                    facts.append(fact)
                except Exception as e:
                    logger.warning(f"Failed to parse fact: {e}")

            return facts

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return []
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return []

    def _regex_extract(
        self,
        text: str,
        user_id: str,
        block_id: Optional[str]
    ) -> List[Fact]:
        """Fallback regex-based fact extraction.

        Simple pattern matching for common fact patterns.

        Args:
            text: Text to analyze
            user_id: User identifier
            block_id: Source block ID

        Returns:
            List of extracted Fact objects
        """
        import re
        facts = []
        text_lower = text.lower()

        definition_patterns = [
            r"(\w+(?:\s+\w+)?)\s+(?:is|means|refers to)\s+(.+?)(?:\.|$)",
            r"(\w+(?:\s+\w+)?)\s*[:=]\s*(.+?)(?:\.|$)",
        ]

        for pattern in definition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for key, value in matches[:3]:
                if len(key) > 2 and len(value) > 3:
                    facts.append(Fact(
                        user_id=user_id,
                        key=key.strip().lower().replace(" ", "_"),
                        value=value.strip(),
                        category=FactCategory.DEFINITION,
                        source_block_id=block_id,
                        evidence_snippet=f"{key} is {value}",
                        confidence=0.6
                    ))

        acronym_patterns = [
            r"(\b[A-Z]{2,6}\b)\s+(?:stands for|means)\s+(.+?)(?:\.|$)",
            r"(\b[A-Z]{2,6}\b)\s*\(([^)]+)\)",
        ]

        for pattern in acronym_patterns:
            matches = re.findall(pattern, text)
            for acronym, expansion in matches[:3]:
                facts.append(Fact(
                    user_id=user_id,
                    key=acronym.upper(),
                    value=expansion.strip(),
                    category=FactCategory.ACRONYM,
                    source_block_id=block_id,
                    evidence_snippet=f"{acronym} ({expansion})",
                    confidence=0.7
                ))

        secret_patterns = [
            r"(?:api[_\s]?key|token|password|secret)[:\s]+([^\s]+)",
        ]

        for pattern in secret_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for value in matches[:2]:
                if len(value) > 5:
                    facts.append(Fact(
                        user_id=user_id,
                        key="detected_secret",
                        value="[REDACTED - Secret detected]",
                        category=FactCategory.SECRET,
                        source_block_id=block_id,
                        evidence_snippet="Secret value detected",
                        confidence=0.5
                    ))

        seen_keys = set()
        unique_facts = []
        for fact in facts:
            if fact.key not in seen_keys:
                seen_keys.add(fact.key)
                unique_facts.append(fact)

        return unique_facts[:10]

    def _parse_category(self, category_str: str) -> FactCategory:
        """Parse category string to FactCategory enum.

        Args:
            category_str: Category string from LLM

        Returns:
            FactCategory enum value
        """
        category_map = {
            "definition": FactCategory.DEFINITION,
            "acronym": FactCategory.ACRONYM,
            "secret": FactCategory.SECRET,
            "entity": FactCategory.ENTITY,
        }
        return category_map.get(category_str.lower(), FactCategory.ENTITY)

    async def get_user_facts(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Fact]:
        """Get all facts for a user.

        Args:
            user_id: User identifier
            limit: Maximum facts to return

        Returns:
            List of Fact objects
        """
        return await self.sql_client.get_facts_by_user(user_id, limit)

    async def search_facts(
        self,
        user_id: str,
        keywords: List[str],
        limit: int = 10
    ) -> List[Fact]:
        """Search facts by keywords.

        Args:
            user_id: User identifier
            keywords: Search keywords
            limit: Maximum results

        Returns:
            List of matching Fact objects
        """
        return await self.sql_client.search_facts(user_id, keywords, limit)

    async def delete_fact(self, fact_id: int) -> bool:
        """Delete a specific fact.

        Args:
            fact_id: Fact identifier

        Returns:
            True if deleted successfully
        """
        return await self.sql_client.delete_fact(fact_id)
