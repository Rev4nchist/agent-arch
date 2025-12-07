"""Bridge Block Manager - Cosmos DB Operations.

Manages Bridge Blocks stored in Cosmos DB. Bridge Blocks are
topic-based conversation units that organize turns within a session.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.hmlr.models import BridgeBlock, Turn, BlockStatus
from src.database import db

logger = logging.getLogger(__name__)


class BridgeBlockManager:
    """Manages Bridge Block CRUD operations in Cosmos DB."""

    CONTAINER_NAME = "bridge_blocks"

    def __init__(self):
        """Initialize manager with Cosmos DB container."""
        self._container = None

    @property
    def container(self):
        """Lazy load container to ensure db is initialized."""
        if self._container is None:
            self._container = db.get_container(self.CONTAINER_NAME)
        return self._container

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    async def create_block(
        self,
        session_id: str,
        user_id: str,
        topic_label: str,
        first_turn: Optional[Turn] = None
    ) -> BridgeBlock:
        """Create a new Bridge Block.

        Args:
            session_id: Session identifier (partition key)
            user_id: User identifier
            topic_label: AI-generated topic label
            first_turn: Optional first turn to include

        Returns:
            Created BridgeBlock
        """
        block_id = f"bb_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        block = BridgeBlock(
            id=block_id,
            session_id=session_id,
            user_id=user_id,
            topic_label=topic_label,
            status=BlockStatus.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        if first_turn:
            block.turns.append(first_turn)

        try:
            self.container.create_item(body=block.model_dump(mode='json'))
            logger.info(f"Created Bridge Block: {block_id} for session {session_id}")
            return block

        except Exception as e:
            logger.error(f"Failed to create Bridge Block: {e}")
            raise

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    async def get_block(self, block_id: str, session_id: str) -> Optional[BridgeBlock]:
        """Get a specific Bridge Block.

        Args:
            block_id: Block identifier
            session_id: Session identifier (partition key)

        Returns:
            BridgeBlock if found, None otherwise
        """
        try:
            item = self.container.read_item(item=block_id, partition_key=session_id)
            return BridgeBlock(**item)
        except Exception as e:
            logger.warning(f"Block {block_id} not found: {e}")
            return None

    async def get_session_blocks(self, session_id: str) -> List[BridgeBlock]:
        """Get all blocks for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of BridgeBlocks ordered by last_activity DESC
        """
        try:
            query = """
                SELECT * FROM c
                WHERE c.session_id = @session_id
                ORDER BY c.last_activity DESC
            """
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@session_id", "value": session_id}],
                enable_cross_partition_query=False
            ))
            return [BridgeBlock(**item) for item in items]

        except Exception as e:
            logger.error(f"Failed to get session blocks: {e}")
            return []

    async def get_active_block(self, session_id: str) -> Optional[BridgeBlock]:
        """Get the currently active block for a session.

        Only ONE block should be ACTIVE at a time per session.

        Args:
            session_id: Session identifier

        Returns:
            Active BridgeBlock if exists, None otherwise
        """
        try:
            query = """
                SELECT * FROM c
                WHERE c.session_id = @session_id AND c.status = 'ACTIVE'
            """
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@session_id", "value": session_id}],
                enable_cross_partition_query=False
            ))

            if items:
                return BridgeBlock(**items[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get active block: {e}")
            return None

    async def get_paused_blocks(self, session_id: str) -> List[BridgeBlock]:
        """Get all paused blocks for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of paused BridgeBlocks
        """
        try:
            query = """
                SELECT * FROM c
                WHERE c.session_id = @session_id AND c.status = 'PAUSED'
                ORDER BY c.last_activity DESC
            """
            items = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@session_id", "value": session_id}],
                enable_cross_partition_query=False
            ))
            return [BridgeBlock(**item) for item in items]

        except Exception as e:
            logger.error(f"Failed to get paused blocks: {e}")
            return []

    async def get_user_blocks_with_open_loops(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[BridgeBlock]:
        """Get blocks with open loops for a user across all sessions.

        Used for cross-session open loop retrieval in suggestions.

        Args:
            user_id: User identifier
            limit: Maximum blocks to return

        Returns:
            List of BridgeBlocks with open_loops, ordered by last_activity DESC
        """
        try:
            query = """
                SELECT * FROM c
                WHERE c.user_id = @user_id
                  AND ARRAY_LENGTH(c.open_loops) > 0
                ORDER BY c.last_activity DESC
                OFFSET 0 LIMIT @limit
            """
            items = list(self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@user_id", "value": user_id},
                    {"name": "@limit", "value": limit}
                ],
                enable_cross_partition_query=True
            ))
            return [BridgeBlock(**item) for item in items]

        except Exception as e:
            logger.error(f"Failed to get user blocks with open loops: {e}")
            return []

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    async def add_turn(
        self,
        block_id: str,
        session_id: str,
        turn: Turn
    ) -> Optional[BridgeBlock]:
        """Add a turn to a Bridge Block.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            turn: Turn to add

        Returns:
            Updated BridgeBlock
        """
        block = await self.get_block(block_id, session_id)
        if not block:
            logger.error(f"Block {block_id} not found")
            return None

        turn.index = len(block.turns)
        block.turns.append(turn)
        block.last_activity = datetime.utcnow()

        try:
            self.container.replace_item(item=block_id, body=block.model_dump(mode='json'))
            logger.info(f"Added turn {turn.index} to block {block_id}")
            return block

        except Exception as e:
            logger.error(f"Failed to add turn: {e}")
            return None

    async def update_block(
        self,
        block_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[BridgeBlock]:
        """Update block fields.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            updates: Dict of fields to update

        Returns:
            Updated BridgeBlock
        """
        block = await self.get_block(block_id, session_id)
        if not block:
            return None

        for key, value in updates.items():
            if hasattr(block, key):
                setattr(block, key, value)

        block.last_activity = datetime.utcnow()

        try:
            self.container.replace_item(item=block_id, body=block.model_dump(mode='json'))
            return block

        except Exception as e:
            logger.error(f"Failed to update block: {e}")
            return None

    async def update_summary(
        self,
        block_id: str,
        session_id: str,
        summary: str
    ) -> bool:
        """Update block summary.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            summary: New summary text

        Returns:
            True if updated successfully
        """
        result = await self.update_block(block_id, session_id, {"summary": summary})
        return result is not None

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
            True if added successfully
        """
        block = await self.get_block(block_id, session_id)
        if not block:
            return False

        if open_loop not in block.open_loops:
            block.open_loops.append(open_loop)
            result = await self.update_block(block_id, session_id, {"open_loops": block.open_loops})
            return result is not None
        return True

    async def add_decision(
        self,
        block_id: str,
        session_id: str,
        decision: str
    ) -> bool:
        """Add a decision to a block.

        Args:
            block_id: Block identifier
            session_id: Session identifier
            decision: Decision text

        Returns:
            True if added successfully
        """
        block = await self.get_block(block_id, session_id)
        if not block:
            return False

        if decision not in block.decisions_made:
            block.decisions_made.append(decision)
            result = await self.update_block(block_id, session_id, {"decisions_made": block.decisions_made})
            return result is not None
        return True

    # =========================================================================
    # STATUS OPERATIONS
    # =========================================================================

    async def pause_block(self, block_id: str, session_id: str) -> bool:
        """Pause a block (set status to PAUSED).

        Args:
            block_id: Block identifier
            session_id: Session identifier

        Returns:
            True if paused successfully
        """
        result = await self.update_block(block_id, session_id, {"status": BlockStatus.PAUSED})
        if result:
            logger.info(f"Paused block {block_id}")
        return result is not None

    async def resume_block(self, block_id: str, session_id: str) -> Optional[BridgeBlock]:
        """Resume a paused block (set status to ACTIVE).

        Also pauses any currently active block first.

        Args:
            block_id: Block to resume
            session_id: Session identifier

        Returns:
            Resumed BridgeBlock
        """
        # Pause current active block if exists
        active = await self.get_active_block(session_id)
        if active and active.id != block_id:
            await self.pause_block(active.id, session_id)

        # Resume the target block
        result = await self.update_block(block_id, session_id, {"status": BlockStatus.ACTIVE})
        if result:
            logger.info(f"Resumed block {block_id}")
        return result

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    async def delete_block(self, block_id: str, session_id: str) -> bool:
        """Delete a Bridge Block.

        Args:
            block_id: Block identifier
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        try:
            self.container.delete_item(item=block_id, partition_key=session_id)
            logger.info(f"Deleted block {block_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete block: {e}")
            return False

    async def delete_session_blocks(self, session_id: str) -> int:
        """Delete all blocks for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of blocks deleted
        """
        blocks = await self.get_session_blocks(session_id)
        deleted = 0

        for block in blocks:
            if await self.delete_block(block.id, session_id):
                deleted += 1

        return deleted
