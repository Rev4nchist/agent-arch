"""Populate test memory data for HMLR personalized suggestions testing."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import db
from src.hmlr.models import BridgeBlock, BlockStatus, Fact, FactCategory, UserProfile


async def populate_test_data(user_id: str = "david.hayes"):
    """Populate comprehensive test data for a user."""

    print(f"\n{'='*60}")
    print(f"Populating HMLR test data for: {user_id}")
    print(f"{'='*60}\n")

    # Initialize database first
    print("Initializing database...")
    db.initialize()

    # 1. Create Bridge Blocks with Open Loops (across different sessions)
    print("1. Creating Bridge Blocks with Open Loops...")

    blocks_container = db.get_container("bridge_blocks")
    now = datetime.now(timezone.utc)

    test_blocks = [
        {
            "id": f"bb_test_session1_{now.strftime('%Y%m%d')}",
            "session_id": "test-session-001",
            "user_id": user_id,
            "topic_label": "Agent Deployment Pipeline",
            "status": "PAUSED",
            "created_at": (now - timedelta(hours=2)).isoformat(),
            "last_activity": (now - timedelta(hours=1)).isoformat(),
            "turns": [],
            "open_loops": [
                "CI/CD configuration for AI Guide needs review",
                "Azure Container Apps scaling rules need to be defined"
            ],
            "decisions_made": ["Use GitHub Actions for deployment"],
            "summary": "Discussed deployment pipeline options for AI agents"
        },
        {
            "id": f"bb_test_session2_{now.strftime('%Y%m%d')}",
            "session_id": "test-session-002",
            "user_id": user_id,
            "topic_label": "HMLR Memory System",
            "status": "PAUSED",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "last_activity": (now - timedelta(days=1)).isoformat(),
            "turns": [],
            "open_loops": [
                "Cross-session memory retrieval optimization pending"
            ],
            "decisions_made": [],
            "summary": "Working on HMLR memory system improvements"
        },
        {
            "id": f"bb_test_session3_{now.strftime('%Y%m%d')}",
            "session_id": "test-session-003",
            "user_id": user_id,
            "topic_label": "Budget Tracking Feature",
            "status": "PAUSED",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "last_activity": (now - timedelta(days=2)).isoformat(),
            "turns": [],
            "open_loops": [
                "Azure cost API integration not yet complete",
                "License tracking dashboard design needs input"
            ],
            "decisions_made": ["Use Azure Cost Management API"],
            "summary": "Budget and license tracking feature design"
        }
    ]

    for block in test_blocks:
        try:
            blocks_container.upsert_item(body=block)
            print(f"   [OK] Created block: {block['topic_label']} ({len(block['open_loops'])} open loops)")
        except Exception as e:
            print(f"   [ERR] Error creating block: {e}")

    # 2. Update User Profile
    print("\n2. Updating User Profile...")

    profiles_container = db.get_container("user_profiles")

    profile_data = {
        "id": user_id,
        "user_id": user_id,
        "preferences": {
            "response_style": "concise",
            "expertise_areas": ["AI/ML", "Azure", "Architecture"],
            "preferred_formats": ["markdown", "diagrams"],
            "communication_style": "technical"
        },
        "common_queries": [
            "What tasks are blocked?",
            "Show agent development status",
            "What decisions need to be made?",
            "Show me the tech radar",
            "What meetings are scheduled this week?",
            "Show deployment status",
            "What are the open action items?",
            "Show budget utilization"
        ],
        "known_entities": [
            {"name": "AI Guide", "type": "project"},
            {"name": "HMLR", "type": "system"},
            {"name": "Agent Architecture Portal", "type": "application"},
            {"name": "David Hayes", "type": "person"},
            {"name": "Fourth", "type": "organization"},
            {"name": "Azure OpenAI", "type": "technology"},
            {"name": "CosmosDB", "type": "technology"}
        ],
        "interaction_patterns": {
            "total_queries": 150,
            "technical_queries": 120,
            "governance_queries": 20,
            "reporting_queries": 10,
            "peak_hours": ["09:00", "14:00", "16:00"],
            "topics_by_frequency": {
                "agent development": 45,
                "governance": 30,
                "architecture": 25,
                "deployment": 20,
                "budget": 15,
                "meetings": 10,
                "security": 5
            }
        },
        "last_updated": now.isoformat()
    }

    try:
        profiles_container.upsert_item(body=profile_data)
        print(f"   [OK] Updated profile with {len(profile_data['common_queries'])} common queries")
        print(f"   [OK] Added {len(profile_data['known_entities'])} known entities")
    except Exception as e:
        print(f"   [ERR] Error updating profile: {e}")

    # 3. Add Facts
    print("\n3. Adding User Facts...")

    facts_container = db.get_container("user_facts")

    test_facts = [
        {
            "id": f"fact_{user_id}_1",
            "user_id": user_id,
            "key": "Preferred Response Format",
            "value": "Concise bullet points with code examples",
            "category": "Definition",
            "source": "user_stated",
            "verified": True,
            "created_at": now.isoformat()
        },
        {
            "id": f"fact_{user_id}_2",
            "user_id": user_id,
            "key": "Primary Focus Area",
            "value": "Agent Architecture and AI Development",
            "category": "Entity",
            "source": "inferred",
            "verified": True,
            "created_at": now.isoformat()
        },
        {
            "id": f"fact_{user_id}_3",
            "user_id": user_id,
            "key": "HMLR",
            "value": "Hierarchical Memory Lookup and Routing - the memory system for AI Guide",
            "category": "Acronym",
            "source": "extracted",
            "verified": True,
            "created_at": now.isoformat()
        },
        {
            "id": f"fact_{user_id}_4",
            "user_id": user_id,
            "key": "Tech Stack",
            "value": "Next.js frontend, FastAPI backend, CosmosDB, Azure OpenAI",
            "category": "Definition",
            "source": "inferred",
            "verified": True,
            "created_at": now.isoformat()
        },
        {
            "id": f"fact_{user_id}_5",
            "user_id": user_id,
            "key": "Deployment Target",
            "value": "Azure Static Web Apps for frontend, Azure Container Apps for backend",
            "category": "Entity",
            "source": "extracted",
            "verified": True,
            "created_at": now.isoformat()
        }
    ]

    for fact in test_facts:
        try:
            facts_container.upsert_item(body=fact)
            print(f"   [OK] Added fact: {fact['key']}")
        except Exception as e:
            print(f"   [ERR] Error adding fact: {e}")

    print(f"\n{'='*60}")
    print("Test data population complete!")
    print(f"{'='*60}\n")

    # Summary
    print("Summary of test data created:")
    print(f"  • Bridge Blocks: {len(test_blocks)} (with {sum(len(b['open_loops']) for b in test_blocks)} total open loops)")
    print(f"  • Common Queries: {len(profile_data['common_queries'])}")
    print(f"  • Known Entities: {len(profile_data['known_entities'])}")
    print(f"  • Facts: {len(test_facts)}")
    print(f"\nYou can now test suggestions at:")
    print(f"  curl 'http://localhost:8080/api/guide/suggestions?page_type=dashboard&user_id={user_id}'")


if __name__ == "__main__":
    asyncio.run(populate_test_data())
