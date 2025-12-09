"""Azure SQL Client for HMLR Fact Store.

Handles all Azure SQL operations for persistent fact storage
and user profiles.
"""

import pyodbc
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.hmlr.models import Fact, UserProfile, FactCategory
from src.config import settings

logger = logging.getLogger(__name__)


class HMLRSQLClient:
    """Azure SQL client for fact store and user profiles."""

    def __init__(self, connection_string: Optional[str] = None):
        """Initialize SQL client.

        Args:
            connection_string: Azure SQL connection string.
                             If None, uses settings.hmlr_sql_connection_string
        """
        self.connection_string = connection_string or settings.hmlr_sql_connection_string
        self._connection: Optional[pyodbc.Connection] = None

    def _get_connection(self) -> pyodbc.Connection:
        """Get or create database connection."""
        if self._connection is None or self._connection.closed:
            if not self.connection_string:
                raise ValueError("HMLR SQL connection string not configured")
            self._connection = pyodbc.connect(self.connection_string)
        return self._connection

    def close(self):
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    # =========================================================================
    # FACT OPERATIONS
    # =========================================================================

    async def save_fact(self, fact: Fact) -> int:
        """Save or update a fact using upsert stored procedure.

        Args:
            fact: Fact to save

        Returns:
            fact_id of saved fact
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """EXEC upsert_fact
                   @user_id=?, @fact_key=?, @value=?, @category=?,
                   @source_block_id=?, @source_chunk_id=?,
                   @evidence_snippet=?, @confidence=?""",
                fact.user_id,
                fact.key,
                fact.value,
                fact.category.value if isinstance(fact.category, FactCategory) else fact.category,
                fact.source_block_id,
                fact.source_chunk_id,
                fact.evidence_snippet,
                fact.confidence
            )
            conn.commit()

            # Get the fact_id
            cursor.execute(
                "SELECT fact_id FROM fact_store WHERE user_id=? AND [key]=?",
                fact.user_id, fact.key
            )
            row = cursor.fetchone()
            return row[0] if row else 0

        except Exception as e:
            logger.error(f"Failed to save fact: {e}")
            raise

    async def get_facts_by_user(
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
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """SELECT fact_id, user_id, [key], value, category,
                          source_block_id, source_chunk_id, evidence_snippet,
                          confidence, verified, created_at
                   FROM fact_store
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY""",
                user_id, limit
            )

            facts = []
            for row in cursor.fetchall():
                facts.append(Fact(
                    fact_id=row[0],
                    user_id=row[1],
                    key=row[2],
                    value=row[3],
                    category=row[4],
                    source_block_id=row[5],
                    source_chunk_id=row[6],
                    evidence_snippet=row[7],
                    confidence=row[8],
                    verified=bool(row[9]),
                    created_at=row[10]
                ))
            return facts

        except Exception as e:
            logger.error(f"Failed to get facts for user {user_id}: {e}")
            return []

    async def search_facts(
        self,
        user_id: str,
        keywords: List[str],
        limit: int = 10
    ) -> List[Fact]:
        """Search facts by keywords.

        Args:
            user_id: User identifier
            keywords: Keywords to search for
            limit: Maximum results

        Returns:
            List of matching Fact objects
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            keywords_str = ",".join(keywords)
            cursor.execute(
                "EXEC get_facts_by_keywords @user_id=?, @keywords=?",
                user_id, keywords_str
            )

            facts = []
            for row in cursor.fetchall():
                facts.append(Fact(
                    fact_id=row[0],
                    user_id=row[1],
                    key=row[2],
                    value=row[3],
                    category=row[4],
                    evidence_snippet=row[5],
                    confidence=row[6],
                    created_at=row[7]
                ))
            return facts[:limit]

        except Exception as e:
            logger.error(f"Failed to search facts: {e}")
            return []

    async def get_fact_by_key(
        self,
        user_id: str,
        key: str
    ) -> Optional[Fact]:
        """Get a specific fact by exact key match.

        Args:
            user_id: User identifier
            key: Exact fact key

        Returns:
            Fact if found, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """SELECT fact_id, user_id, [key], value, category,
                          source_block_id, source_chunk_id, evidence_snippet,
                          confidence, verified, created_at
                   FROM fact_store
                   WHERE user_id = ? AND [key] = ?""",
                user_id, key
            )

            row = cursor.fetchone()
            if not row:
                return None

            return Fact(
                fact_id=row[0],
                user_id=row[1],
                key=row[2],
                value=row[3],
                category=row[4],
                source_block_id=row[5],
                source_chunk_id=row[6],
                evidence_snippet=row[7],
                confidence=row[8],
                verified=bool(row[9]),
                created_at=row[10]
            )

        except Exception as e:
            logger.error(f"Failed to get fact by key: {e}")
            return None

    async def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact.

        Args:
            fact_id: Fact identifier

        Returns:
            True if deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fact_store WHERE fact_id = ?", fact_id)
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to delete fact: {e}")
            return False

    async def delete_fact_for_user(self, fact_id: int, user_id: str) -> bool:
        """Delete a fact only if it belongs to the user.

        Args:
            fact_id: Fact identifier
            user_id: User identifier for authorization

        Returns:
            True if deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM fact_store WHERE fact_id = ? AND user_id = ?",
                fact_id, user_id
            )
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to delete fact: {e}")
            return False

    async def verify_fact(self, fact_id: int, user_id: str) -> bool:
        """Mark a fact as verified.

        Args:
            fact_id: Fact identifier
            user_id: User identifier for authorization

        Returns:
            True if updated, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fact_store SET verified = 1 WHERE fact_id = ? AND user_id = ?",
                fact_id, user_id
            )
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Failed to verify fact: {e}")
            return False

    # =========================================================================
    # USER PROFILE OPERATIONS
    # =========================================================================

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile.

        Args:
            user_id: User identifier

        Returns:
            UserProfile if exists, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """SELECT user_id, preferences, common_queries,
                          known_entities, interaction_patterns, last_updated
                   FROM user_profiles
                   WHERE user_id = ?""",
                user_id
            )

            row = cursor.fetchone()
            if not row:
                return None

            return UserProfile(
                user_id=row[0],
                preferences=json.loads(row[1]) if row[1] else {},
                common_queries=json.loads(row[2]) if row[2] else [],
                known_entities=json.loads(row[3]) if row[3] else [],
                interaction_patterns=json.loads(row[4]) if row[4] else {},
                last_updated=row[5]
            )

        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None

    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Save or update user profile.

        Args:
            profile: UserProfile to save

        Returns:
            True if saved successfully
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """EXEC upsert_user_profile
                   @user_id=?, @preferences=?, @common_queries=?,
                   @known_entities=?, @interaction_patterns=?""",
                profile.user_id,
                json.dumps(profile.preferences),
                json.dumps(profile.common_queries),
                json.dumps(profile.known_entities),
                json.dumps(profile.interaction_patterns)
            )
            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            return False

    async def update_profile_field(
        self,
        user_id: str,
        field: str,
        value: Any
    ) -> bool:
        """Update a specific profile field.

        Args:
            user_id: User identifier
            field: Field name (preferences, common_queries, etc.)
            value: New value

        Returns:
            True if updated successfully
        """
        try:
            # Get current profile
            profile = await self.get_user_profile(user_id)
            if not profile:
                profile = UserProfile(user_id=user_id)

            # Update field
            if field == "preferences":
                profile.preferences.update(value)
            elif field == "common_queries":
                if isinstance(value, list):
                    profile.common_queries.extend(value)
                else:
                    profile.common_queries.append(value)
                profile.common_queries = list(set(profile.common_queries))[-20:]
            elif field == "known_entities":
                if isinstance(value, list):
                    profile.known_entities.extend(value)
                else:
                    profile.known_entities.append(value)
            elif field == "interaction_patterns":
                profile.interaction_patterns.update(value)

            profile.last_updated = datetime.utcnow()
            return await self.save_user_profile(profile)

        except Exception as e:
            logger.error(f"Failed to update profile field: {e}")
            return False
