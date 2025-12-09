"""
Populate HMLR Test Data for David Hayes.

This script creates test data in the HMLR system to test personalized suggestions:
- User profile with preferences, common queries, topic interests
- Bridge blocks with open loops
- Facts about known entities

Usage:
    cd backend
    python -m scripts.populate_hmlr_test_data
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.database import db
from src.hmlr.models import UserProfile, Fact, BridgeBlock, Turn, BlockStatus, FactCategory
from src.hmlr.sql_client import HMLRSQLClient
from src.hmlr.bridge_block_mgr import BridgeBlockManager

USER_ID = "David.Hayes"  # Must match MSAL auth format: user?.username?.split('@')[0]
DISPLAY_NAME = "David Hayes"


async def create_user_profile(sql_client: HMLRSQLClient):
    """Create user profile with preferences and patterns."""
    print(f"Creating user profile for {USER_ID}...")

    profile = UserProfile(
        user_id=USER_ID,
        preferences={
            "response_style": "detailed",
            "preferred_format": "markdown",
            "show_sources": True,
            # Topic interests - extracted by memory_accessor._extract_topic_interests()
            "preferred_topics": [
                "governance",
                "agent development",
                "enterprise architecture",
                "HMLR memory system",
                "platform administration"
            ]
        },
        common_queries=[
            "What tasks are blocked?",
            "Show agent development status",
            "How many agents are in each tier?",
            "What's the status of HMLR implementation?",
            "Show recent meeting action items",
            "What governance proposals need review?"
        ],
        known_entities=[
            {"name": "AI Guide", "type": "project", "context": "Main project David works on"},
            {"name": "HMLR", "type": "system", "context": "Memory system being implemented"},
            {"name": "Fourth Platform", "type": "platform", "context": "Enterprise agent platform"},
            {"name": "Dashboard Agent", "type": "agent", "context": "Enterprise tier agent"},
            {"name": "Governance Committee", "type": "team", "context": "Decision-making body"}
        ],
        interaction_patterns={
            "peak_hours": ["09:00-12:00", "14:00-17:00"],
            "common_intents": ["status_check", "aggregation", "list"],
            "average_session_length": 15,
            "queries_per_session": 5,
            # These determine expertise level via memory_accessor._determine_expertise()
            # >100 total + >60% technical = expert
            "total_queries": 150,
            "technical_queries": 100,
            # Topic frequency - also extracted by _extract_topic_interests()
            "topic_frequency": {
                "governance": 45,
                "agent development": 38,
                "tasks": 32,
                "HMLR": 25,
                "meetings": 10
            }
        }
    )

    success = await sql_client.save_user_profile(profile)
    if success:
        print(f"  [OK] Created user profile with {len(profile.common_queries)} common queries")
        print(f"  [OK] Added {len(profile.known_entities)} known entities")
        print(f"  [OK] Set {len(profile.preferences.get('preferred_topics', []))} preferred topics")
        print(f"  [OK] Expertise level will resolve to: expert (150 total, 100 technical)")
    else:
        print("  [FAIL] Failed to create user profile")
    return success


async def create_facts(sql_client: HMLRSQLClient):
    """Create facts about David's known entities and preferences."""
    print(f"Creating facts for {USER_ID}...")

    facts = [
        Fact(
            user_id=USER_ID,
            key="AI Guide",
            value="AI-powered assistant for Fourth Platform, uses RAG and intent classification",
            category=FactCategory.ENTITY,
            confidence=0.95,
            evidence_snippet="David is lead developer of AI Guide project"
        ),
        Fact(
            user_id=USER_ID,
            key="HMLR",
            value="Hierarchical Memory Lookup & Routing - persistent memory system",
            category=FactCategory.ACRONYM,
            confidence=0.98,
            evidence_snippet="HMLR implementation in progress"
        ),
        Fact(
            user_id=USER_ID,
            key="Enterprise Tier",
            value="Highest agent tier with full governance, requires approval committee",
            category=FactCategory.DEFINITION,
            confidence=0.9,
            evidence_snippet="Agent governance documentation"
        ),
        Fact(
            user_id=USER_ID,
            key="RAG",
            value="Retrieval Augmented Generation - technique for grounding LLM responses",
            category=FactCategory.ACRONYM,
            confidence=0.98,
            evidence_snippet="Technical architecture documentation"
        ),
        Fact(
            user_id=USER_ID,
            key="Bridge Block",
            value="Topic-based conversation unit in HMLR system",
            category=FactCategory.DEFINITION,
            confidence=0.95,
            evidence_snippet="HMLR design document"
        ),
        Fact(
            user_id=USER_ID,
            key="Preferred Response Format",
            value="Detailed markdown with sources and action items",
            category=FactCategory.DEFINITION,
            confidence=0.85,
            evidence_snippet="Inferred from interaction patterns"
        )
    ]

    created = 0
    for fact in facts:
        try:
            await sql_client.save_fact(fact)
            created += 1
        except Exception as e:
            print(f"  [FAIL] Failed to create fact '{fact.key}': {e}")

    print(f"  [OK] Created {created}/{len(facts)} facts")
    return created


async def create_bridge_blocks(block_manager: BridgeBlockManager):
    """Create bridge blocks with open loops for testing."""
    print(f"Creating bridge blocks for {USER_ID}...")

    now = datetime.utcnow()

    blocks_data = [
        {
            "session_id": f"session_{USER_ID}_current",
            "topic_label": "HMLR Implementation Progress",
            "turns": [
                Turn(
                    index=0,
                    query="What's the status of HMLR implementation?",
                    response_summary="HMLR is 80% complete. Memory accessor and suggestion providers are done.",
                    intent="status_check",
                    entities=["HMLR"],
                    timestamp=now - timedelta(minutes=30)
                ),
                Turn(
                    index=1,
                    query="What's left to do?",
                    response_summary="Remaining: test suite completion and frontend integration testing.",
                    intent="status_check",
                    entities=["HMLR", "tests"],
                    timestamp=now - timedelta(minutes=25)
                )
            ],
            "open_loops": [
                "Complete the HMLR test suite",
                "Test personalized suggestions on frontend"
            ],
            "age": timedelta(minutes=30)
        },
        {
            "session_id": f"session_{USER_ID}_yesterday",
            "topic_label": "Agent Governance Review",
            "turns": [
                Turn(
                    index=0,
                    query="What governance proposals are pending?",
                    response_summary="3 proposals pending: AI Guide v2.0, Dashboard Enhancement, Security Audit.",
                    intent="list",
                    entities=["proposals"],
                    timestamp=now - timedelta(hours=20)
                )
            ],
            "open_loops": [
                "Review AI Guide v2.0 proposal",
                "Schedule governance committee meeting"
            ],
            "age": timedelta(hours=20)
        },
        {
            "session_id": f"session_{USER_ID}_oldwork",
            "topic_label": "Task Prioritization",
            "turns": [
                Turn(
                    index=0,
                    query="What are my high priority tasks?",
                    response_summary="Found 5 high priority tasks including HMLR integration.",
                    intent="list",
                    entities=["tasks"],
                    timestamp=now - timedelta(days=2)
                )
            ],
            "open_loops": [
                "Discuss task dependencies with team"
            ],
            "age": timedelta(days=2)
        }
    ]

    created = 0
    for bd in blocks_data:
        try:
            block = BridgeBlock(
                id=f"bb_test_{created}_{now.strftime('%H%M%S')}",
                session_id=bd["session_id"],
                user_id=USER_ID,
                topic_label=bd["topic_label"],
                turns=bd["turns"],
                open_loops=bd["open_loops"],
                status=BlockStatus.PAUSED if bd["age"] > timedelta(hours=1) else BlockStatus.ACTIVE,
                created_at=now - bd["age"],
                last_activity=now - bd["age"]
            )

            block_manager.container.upsert_item(body=block.model_dump(mode='json'))
            created += 1
            print(f"  [OK] Created block: {bd['topic_label']} ({len(bd['open_loops'])} open loops)")

        except Exception as e:
            print(f"  [FAIL] Failed to create block '{bd['topic_label']}': {e}")

    print(f"  Total: {created}/{len(blocks_data)} bridge blocks created")
    return created


async def verify_data(sql_client: HMLRSQLClient, block_manager: BridgeBlockManager):
    """Verify the test data was created correctly."""
    print("\nVerifying test data...")

    profile = await sql_client.get_user_profile(USER_ID)
    if profile:
        print(f"  [OK] User profile: {len(profile.common_queries)} queries, {len(profile.known_entities)} entities")
    else:
        print("  [FAIL] User profile not found")

    facts = await sql_client.get_facts_by_user(USER_ID, limit=20)
    print(f"  [OK] Facts: {len(facts)} facts found")

    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{USER_ID}'"
        blocks = list(block_manager.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        total_open_loops = sum(len(b.get('open_loops', [])) for b in blocks)
        print(f"  [OK] Bridge blocks: {len(blocks)} blocks, {total_open_loops} total open loops")
    except Exception as e:
        print(f"  [FAIL] Failed to query bridge blocks: {e}")


async def main():
    print("=" * 60)
    print("HMLR Test Data Population Script")
    print("=" * 60)
    print(f"User: {DISPLAY_NAME} ({USER_ID})")
    print(f"HMLR Enabled: {settings.hmlr_enabled}")
    print()

    if not settings.hmlr_enabled:
        print("WARNING: HMLR is disabled in settings. Data will be created but won't be used.")

    print("Initializing database...")
    db.initialize()
    print("Database initialized.\n")

    sql_client = HMLRSQLClient()
    block_manager = BridgeBlockManager()

    try:
        await create_user_profile(sql_client)
        print()

        await create_facts(sql_client)
        print()

        await create_bridge_blocks(block_manager)
        print()

        await verify_data(sql_client, block_manager)

        print()
        print("=" * 60)
        print("Test data creation complete!")
        print()
        print("To test personalized suggestions:")
        print(f"  curl 'http://localhost:8000/api/guide/suggestions?page_type=dashboard&user_id={USER_ID}'")
        print()
        print("Expected behavior:")
        print("  - Open loops should appear as 'Continue:' suggestions")
        print("  - Common queries should be adapted to expertise level")
        print("  - Known entities should generate 'Update on' suggestions")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sql_client.close()


if __name__ == "__main__":
    asyncio.run(main())
