"""
Demo Content Population Script for HMLR Showcase

Creates aligned platform content (Meetings, Tasks, Agents, Decisions, Budgets)
that corresponds with HMLR memory data, enabling coherent AI Guide demos.

Usage:
    python scripts/populate_demo_content.py

This script uses the backend API to create content, ensuring proper indexing
in Azure AI Search.
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = "http://localhost:8000"

# Track created IDs for linking
created_ids = {
    "meetings": {},
    "tasks": {},
    "agents": {},
    "decisions": {},
    "budgets": {},
}


async def create_meeting(client: httpx.AsyncClient, meeting: dict) -> Optional[str]:
    """Create a meeting and return its ID."""
    try:
        response = await client.post(f"{API_BASE}/api/meetings", json=meeting)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"  Created meeting: {meeting['title']}")
            return data.get("id")
        else:
            print(f"  Failed to create meeting {meeting['title']}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating meeting {meeting['title']}: {e}")
        return None


async def create_task(client: httpx.AsyncClient, task: dict) -> Optional[str]:
    """Create a task and return its ID."""
    try:
        response = await client.post(f"{API_BASE}/api/tasks", json=task)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"  Created task: {task['title']}")
            return data.get("id")
        else:
            print(f"  Failed to create task {task['title']}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating task {task['title']}: {e}")
        return None


async def create_agent(client: httpx.AsyncClient, agent: dict) -> Optional[str]:
    """Create an agent and return its ID."""
    try:
        response = await client.post(f"{API_BASE}/api/agents", json=agent)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"  Created agent: {agent['name']}")
            return data.get("id")
        else:
            print(f"  Failed to create agent {agent['name']}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating agent {agent['name']}: {e}")
        return None


async def create_decision(client: httpx.AsyncClient, decision: dict) -> Optional[str]:
    """Create a decision and return its ID."""
    try:
        response = await client.post(f"{API_BASE}/api/decisions", json=decision)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"  Created decision: {decision['title']}")
            return data.get("id")
        else:
            print(f"  Failed to create decision {decision['title']}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating decision {decision['title']}: {e}")
        return None


async def create_budget(client: httpx.AsyncClient, budget: dict) -> Optional[str]:
    """Create a budget and return its ID."""
    try:
        response = await client.post(f"{API_BASE}/api/budget/budgets", json=budget)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"  Created budget: {budget['name']}")
            return data.get("id")
        else:
            print(f"  Failed to create budget {budget['name']}: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Error creating budget {budget['name']}: {e}")
        return None


async def populate_meetings(client: httpx.AsyncClient):
    """Create demo meetings."""
    print("\n=== Creating Meetings ===")

    now = datetime.utcnow()

    meetings = [
        {
            "title": "AI Architect Weekly Sync",
            "date": (now - timedelta(days=2)).isoformat(),
            "type": "AI Architect",
            "facilitator": "David Hayes",
            "attendees": ["David Hayes", "Sarah Chen", "Marcus Williams", "Elena Rodriguez"],
            "agenda": "1. Agent deployment pipeline updates\n2. HMLR memory system progress\n3. Governance framework review\n4. Budget tracking feature status",
            "summary": "Discussed progress on key AI platform initiatives. HMLR memory system is 80% complete with test suite in progress. Agent deployment pipeline needs GitHub Actions configuration finalized. Budget tracking Azure Cost API integration is underway. Agreed to prioritize Enterprise tier approval workflow.",
            "topics": ["HMLR", "agent deployment", "governance", "budget tracking"],
            "status": "Completed",
        },
        {
            "title": "HMLR System Design Review",
            "date": (now - timedelta(days=5)).isoformat(),
            "type": "Technical",
            "facilitator": "David Hayes",
            "attendees": ["David Hayes", "Platform Engineering Team", "Alex Kumar"],
            "agenda": "1. Bridge Block architecture review\n2. Governor routing scenarios\n3. Cross-session memory design\n4. Suggestion personalization approach",
            "summary": "Deep-dive into HMLR (Hierarchical Memory Lookup and Routing) system architecture. Agreed to use CosmosDB for Bridge Blocks storage. Implemented 4-scenario Governor routing: continuation, resumption, new topic, and topic shift. Cross-session memory will use recency decay for priority scoring.",
            "topics": ["HMLR", "CosmosDB", "memory architecture", "Governor routing"],
            "status": "Completed",
        },
        {
            "title": "Budget & Cost Tracking Planning",
            "date": (now - timedelta(days=7)).isoformat(),
            "type": "Governance",
            "facilitator": "David Hayes",
            "attendees": ["David Hayes", "Finance Team", "IT Operations", "James Mitchell"],
            "agenda": "1. Azure cost visibility requirements\n2. License tracking needs\n3. Budget alert thresholds\n4. Resource group cost allocation",
            "summary": "Planned the budget and cost tracking feature for AI platform. Decided to use Azure Cost Management API for cost data. License tracking dashboard design is pending UX input. Set up budget alert thresholds at 75% (warning) and 90% (critical). Will allocate costs by resource group for granular tracking.",
            "topics": ["budget tracking", "Azure costs", "license management", "cost allocation"],
            "status": "Completed",
        },
        {
            "title": "Agent Tier Governance Framework",
            "date": (now - timedelta(days=10)).isoformat(),
            "type": "Governance",
            "facilitator": "David Hayes",
            "attendees": ["David Hayes", "AI Architect Committee", "Compliance Team", "Rachel Foster"],
            "agenda": "1. Tier definition review\n2. Approval workflow design\n3. Enterprise tier requirements\n4. Compliance checklist",
            "summary": "Established the 3-tier agent governance model. Tier 1 (Individual) requires minimal oversight. Tier 2 (Department) needs department head approval. Tier 3 (Enterprise) requires AI Architect Committee approval. Created compliance checklist covering data handling, security, and integration requirements.",
            "topics": ["governance", "agent tiers", "compliance", "approval workflow"],
            "status": "Completed",
        },
        {
            "title": "Q1 Platform Roadmap Review",
            "date": (now + timedelta(days=3)).isoformat(),
            "type": "Review",
            "facilitator": "David Hayes",
            "attendees": ["David Hayes", "Leadership Team", "AI Architect Team", "Product Management"],
            "agenda": "1. Feature prioritization for Q1\n2. Resource allocation review\n3. Key milestones and dependencies\n4. Risk assessment",
            "status": "Scheduled",
        },
    ]

    for meeting in meetings:
        meeting_id = await create_meeting(client, meeting)
        if meeting_id:
            created_ids["meetings"][meeting["title"]] = meeting_id


async def populate_agents(client: httpx.AsyncClient):
    """Create demo agents."""
    print("\n=== Creating Agents ===")

    agents = [
        {
            "name": "AI Guide",
            "description": "AI-powered assistant for Fourth Platform navigation and data insights. Uses RAG (Retrieval Augmented Generation) with Azure AI Search and HMLR (Hierarchical Memory Lookup and Routing) for personalized, context-aware responses. Helps users navigate tasks, meetings, agents, and governance items.",
            "tier": "Tier3_Enterprise",
            "status": "Production",
            "owner": "David Hayes",
            "department": "AI Architecture",
            "data_sources": ["CosmosDB", "Azure AI Search", "Platform Documentation", "Meeting Transcripts"],
            "use_case": "Platform navigation, data queries, cross-session memory, personalized suggestions",
            "integration_status": "Fully Integrated",
            "integration_notes": "Fully integrated with all platform modules. HMLR memory system enables topic tracking and personalized suggestions.",
            "next_milestone": "HMLR v2.0 with enhanced fact extraction",
            "team": "Platform Engineering",
        },
        {
            "name": "Transcript Processor",
            "description": "Automated meeting transcript processor that extracts action items, decisions, and key topics from meeting recordings. Uses Azure Speech Services for transcription and GPT-4 for summarization.",
            "tier": "Tier2_Department",
            "status": "Testing",
            "owner": "Platform Team",
            "department": "AI Architecture",
            "data_sources": ["Azure Blob Storage", "Meeting Recordings"],
            "use_case": "Automated meeting summarization, action item extraction, decision capture",
            "integration_status": "In Progress",
            "integration_notes": "Testing with sample transcripts. Integration with Meetings module 70% complete.",
            "deployment_blockers": ["Azure Speech Services quota approval pending"],
            "next_milestone": "Production rollout to AI Architect meetings",
            "team": "Platform Engineering",
        },
        {
            "name": "Cost Analyzer",
            "description": "Analyzes Azure cloud costs across resource groups and services. Generates budget reports, identifies cost anomalies, and provides optimization recommendations.",
            "tier": "Tier2_Department",
            "status": "Development",
            "owner": "Finance",
            "department": "IT Operations",
            "data_sources": ["Azure Cost Management API", "Resource Group Metadata"],
            "use_case": "Cost tracking, budget monitoring, optimization recommendations",
            "integration_status": "Not Started",
            "integration_notes": "Development in progress. Will integrate with Budget module for automated alerts.",
            "next_milestone": "MVP with basic cost breakdown by resource group",
            "team": "Finance Technology",
        },
        {
            "name": "Governance Reviewer",
            "description": "Reviews agent proposals for compliance with governance framework. Suggests required approvals, identifies potential risks, and ensures adherence to tier-specific requirements.",
            "tier": "Tier1_Individual",
            "status": "Idea",
            "owner": "Compliance",
            "department": "Governance",
            "data_sources": ["Proposals Database", "Governance Policies"],
            "use_case": "Automated compliance checking, risk assessment, approval routing",
            "integration_status": "Not Started",
            "integration_notes": "Concept phase. Will integrate with Proposals and Governance modules.",
            "next_milestone": "Requirements gathering with Compliance team",
            "team": "Compliance",
        },
    ]

    for agent in agents:
        agent_id = await create_agent(client, agent)
        if agent_id:
            created_ids["agents"][agent["name"]] = agent_id


async def populate_tasks(client: httpx.AsyncClient):
    """Create demo tasks."""
    print("\n=== Creating Tasks ===")

    now = datetime.utcnow()
    ai_guide_id = created_ids["agents"].get("AI Guide")

    tasks = [
        # HMLR Memory System Tasks
        {
            "title": "Complete HMLR test suite",
            "description": "Finish comprehensive test suite for HMLR memory system including Governor routing scenarios, cross-session memory retrieval, and suggestion personalization. Current coverage at 85%, target 95%.",
            "status": "In-Progress",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "related_agent": ai_guide_id,
            "notes": "Test files: test_governor_boundaries.py, test_cross_session_memory.py, test_suggestion_edge_cases.py",
            "team": "Platform Engineering",
        },
        {
            "title": "Test personalized suggestions on frontend",
            "description": "Verify that personalized suggestions from HMLR appear correctly in the AI Guide widget. Test suggestion chips, open loop resumption, and user profile integration.",
            "status": "In-Progress",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "related_agent": ai_guide_id,
            "notes": "Frontend integration complete. Testing with david.hayes user profile.",
            "team": "Platform Engineering",
        },
        {
            "title": "Implement Governor 4-scenario routing",
            "description": "Implement the Governor component with 4 routing scenarios: Topic Continuation (similarity >= 0.7), Topic Resumption (matching paused block), New Topic (first query), Topic Shift (low similarity).",
            "status": "Done",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "related_agent": ai_guide_id,
            "notes": "Completed and tested. All 4 scenarios working with similarity threshold at 0.7.",
            "team": "Platform Engineering",
        },
        {
            "title": "Cross-session memory retrieval optimization",
            "description": "Optimize cross-session memory retrieval for open loops. Implement recency decay (base 80, -0.5/hour first 24h, -0.3/hour after). Maximum 5 open loops, exclude items older than 168 hours.",
            "status": "In-Progress",
            "priority": "Medium",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "related_agent": ai_guide_id,
            "notes": "Recency decay implemented. Testing priority sorting.",
            "team": "Platform Engineering",
        },
        {
            "title": "Document HMLR architecture for team",
            "description": "Create comprehensive documentation of HMLR system architecture including Bridge Blocks, Governor routing, Hydrator context assembly, and fact extraction. Target audience: AI Architect team.",
            "status": "Pending",
            "priority": "Medium",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "related_agent": ai_guide_id,
            "notes": "Will include architecture diagrams and code examples.",
            "team": "Platform Engineering",
        },

        # Agent Deployment Pipeline Tasks
        {
            "title": "Configure GitHub Actions for AI Guide deployment",
            "description": "Set up GitHub Actions workflow for automated AI Guide deployment to Azure Container Apps. Include build, test, and deploy stages with environment-specific configurations.",
            "status": "In-Progress",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "Platform Team",
            "related_agent": ai_guide_id,
            "notes": "Workflow file created. Testing deployment to staging environment.",
            "team": "DevOps",
        },
        {
            "title": "Define Azure Container Apps scaling rules",
            "description": "Configure auto-scaling rules for Azure Container Apps hosting AI agents. Define min/max replicas, CPU/memory thresholds, and HTTP request-based scaling for the AI Guide.",
            "status": "Pending",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "notes": "Need to analyze current load patterns. Target: handle 100 concurrent users.",
            "team": "Platform Engineering",
        },
        {
            "title": "Set up staging environment for agent testing",
            "description": "Create staging environment in Azure for testing AI agents before production deployment. Include separate CosmosDB, Azure AI Search, and Azure OpenAI instances.",
            "status": "Done",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "DevOps",
            "notes": "Staging environment ready at agent-arch-staging.azurecontainerapps.io",
            "team": "DevOps",
        },
        {
            "title": "Create deployment runbook for Enterprise agents",
            "description": "Document step-by-step deployment process for Tier 3 (Enterprise) agents including pre-deployment checklist, approval workflow, deployment steps, and rollback procedures.",
            "status": "Pending",
            "priority": "Medium",
            "category": "Governance",
            "assigned_to": "David Hayes",
            "notes": "Will align with governance framework requirements.",
            "team": "Platform Engineering",
        },
        {
            "title": "Implement deployment approval workflow",
            "description": "Build automated approval workflow for agent deployments. Tier 2 requires department head approval, Tier 3 requires AI Architect Committee approval. Integrate with Teams notifications.",
            "status": "Blocked",
            "priority": "High",
            "category": "Governance",
            "assigned_to": "Governance",
            "notes": "Blocked: Waiting for Enterprise tier approval process definition.",
            "dependencies": [],
            "team": "Governance",
        },

        # Budget & Cost Tracking Tasks
        {
            "title": "Integrate Azure Cost Management API",
            "description": "Implement integration with Azure Cost Management API to retrieve cost data by resource group, service, and time period. Enable daily cost aggregation and trend analysis.",
            "status": "In-Progress",
            "priority": "High",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "notes": "API authentication configured. Building cost aggregation service.",
            "team": "Platform Engineering",
        },
        {
            "title": "Design license tracking dashboard",
            "description": "Design UX for license tracking dashboard showing software licenses, usage, renewal dates, and costs. Include filtering by vendor, department, and license type.",
            "status": "Pending",
            "priority": "Medium",
            "category": "Technical",
            "assigned_to": "UX Team",
            "notes": "Waiting for UX team capacity. Initial wireframes needed.",
            "team": "Product Design",
        },
        {
            "title": "Set up budget alert thresholds",
            "description": "Configure budget alert thresholds at 75% (warning) and 90% (critical) for each resource group budget. Send notifications to budget owners via email and Teams.",
            "status": "Done",
            "priority": "Medium",
            "category": "Technical",
            "assigned_to": "IT Ops",
            "notes": "Alerts configured for rg-agent-architecture, rg-ai-services, rg-dev-test.",
            "team": "IT Operations",
        },
        {
            "title": "Create cost allocation model for agent tiers",
            "description": "Define cost allocation model that distributes Azure costs to agent tiers based on resource consumption. Enable chargeback reporting for department budgets.",
            "status": "Pending",
            "priority": "Medium",
            "category": "Governance",
            "assigned_to": "Finance",
            "notes": "Finance team to define allocation rules.",
            "team": "Finance",
        },
        {
            "title": "Document Azure resource cost breakdown",
            "description": "Create documentation mapping Azure resources to AI platform components. Include cost drivers, optimization opportunities, and reserved instance recommendations.",
            "status": "In-Progress",
            "priority": "Low",
            "category": "Technical",
            "assigned_to": "David Hayes",
            "notes": "Analyzing current month costs. Top cost drivers: Azure OpenAI, CosmosDB.",
            "team": "Platform Engineering",
        },

        # Governance Framework Tasks
        {
            "title": "Define Enterprise tier approval process",
            "description": "Document the complete approval process for Tier 3 (Enterprise) agents. Include committee composition, review criteria, voting process, and escalation paths.",
            "status": "In-Progress",
            "priority": "Critical",
            "category": "Governance",
            "assigned_to": "Governance",
            "notes": "Draft process reviewed by AI Architect Committee. Finalizing committee charter.",
            "team": "Governance",
        },
        {
            "title": "Create agent compliance checklist",
            "description": "Develop comprehensive compliance checklist for AI agents covering data handling, security requirements, integration standards, and documentation requirements.",
            "status": "Done",
            "priority": "High",
            "category": "Governance",
            "assigned_to": "Compliance",
            "notes": "Checklist approved. Integrated into agent registration workflow.",
            "team": "Compliance",
        },
        {
            "title": "Review AI Guide v2.0 proposal",
            "description": "Review and approve proposal for AI Guide v2.0 including enhanced HMLR features, multi-agent orchestration, and advanced intent classification.",
            "status": "Pending",
            "priority": "High",
            "category": "AI Architect",
            "assigned_to": "AI Architect Committee",
            "related_agent": ai_guide_id,
            "notes": "Scheduled for Q1 Platform Roadmap Review meeting.",
            "team": "AI Architecture",
        },
    ]

    for task in tasks:
        task_id = await create_task(client, task)
        if task_id:
            created_ids["tasks"][task["title"]] = task_id


async def populate_decisions(client: httpx.AsyncClient):
    """Create demo decisions."""
    print("\n=== Creating Decisions ===")

    now = datetime.utcnow()

    decisions = [
        {
            "title": "Adopt 3-tier agent governance model",
            "description": "Approved the 3-tier agent governance model: Tier 1 (Individual) - minimal oversight, Tier 2 (Department) - department head approval, Tier 3 (Enterprise) - AI Architect Committee approval. This provides appropriate governance without hindering innovation.",
            "category": "Governance",
            "decision_date": (now - timedelta(days=10)).isoformat(),
            "decision_maker": "AI Architect Committee",
            "rationale": "Balances governance requirements with agility. Lower tiers enable rapid experimentation while Enterprise tier ensures proper oversight for organization-wide agents.",
            "impact": "All new agents must be classified into tiers. Existing agents to be reviewed and classified within 30 days.",
        },
        {
            "title": "Use CosmosDB for HMLR Bridge Blocks",
            "description": "Selected Azure Cosmos DB as the storage solution for HMLR Bridge Blocks (conversation topic units). Using SQL API with partition key on user_id for efficient per-user queries.",
            "category": "Architecture",
            "decision_date": (now - timedelta(days=5)).isoformat(),
            "decision_maker": "David Hayes",
            "rationale": "CosmosDB provides global distribution, automatic scaling, and flexible schema for Bridge Block documents. SQL API enables rich queries for Governor routing.",
            "impact": "Bridge Blocks, user profiles, and facts stored in dedicated containers. Estimated cost: ~$100/month for current scale.",
        },
        {
            "title": "GitHub Actions for agent CI/CD",
            "description": "Selected GitHub Actions as the CI/CD platform for AI agent deployment pipelines. Integrates with Azure Container Apps for automated deployment.",
            "category": "Architecture",
            "decision_date": (now - timedelta(days=7)).isoformat(),
            "decision_maker": "Platform Team",
            "rationale": "GitHub Actions provides native integration with our repository, good Azure support, and familiar workflow syntax for the team.",
            "impact": "All agent deployments will use GitHub Actions workflows. Legacy Jenkins pipelines to be migrated within 60 days.",
        },
        {
            "title": "Azure Cost Management API for budget tracking",
            "description": "Selected Azure Cost Management API as the data source for budget tracking feature. Will provide resource group costs, service breakdown, and trend analysis.",
            "category": "Budget",
            "decision_date": (now - timedelta(days=7)).isoformat(),
            "decision_maker": "IT Operations",
            "rationale": "Native Azure integration, comprehensive cost data, and API access included in our Enterprise Agreement.",
            "impact": "Budget module will retrieve daily cost data. Historical data available for 13 months.",
        },
        {
            "title": "Enterprise tier requires committee approval",
            "description": "Established that all Tier 3 (Enterprise) agent deployments require AI Architect Committee approval before production deployment. Approval requires majority vote with quorum of 3 members.",
            "category": "Governance",
            "decision_date": (now - timedelta(days=10)).isoformat(),
            "decision_maker": "Leadership",
            "rationale": "Enterprise agents have organization-wide impact. Committee review ensures proper security, compliance, and architectural alignment.",
            "impact": "Enterprise agent deployments require 3-5 business days for committee review. Emergency process available for critical deployments.",
        },
    ]

    for decision in decisions:
        decision_id = await create_decision(client, decision)
        if decision_id:
            created_ids["decisions"][decision["title"]] = decision_id


async def populate_budgets(client: httpx.AsyncClient):
    """Create demo budget entries."""
    print("\n=== Creating Budgets ===")

    budgets = [
        {
            "name": "AI Platform Infrastructure",
            "category": "Azure Service",
            "resource_groups": ["rg-agent-architecture"],
            "amount": 5000.0,
            "currency": "USD",
            "period": "monthly",
            "threshold_warning": 75.0,
            "threshold_critical": 90.0,
            "notes": "Covers Azure Container Apps, CosmosDB, Azure AI Search for AI Guide and other platform agents.",
            "owner": "David Hayes",
        },
        {
            "name": "AI Services & Cognitive",
            "category": "Azure Service",
            "resource_groups": ["rg-ai-services"],
            "azure_service_type": "Azure OpenAI Service",
            "amount": 3000.0,
            "currency": "USD",
            "period": "monthly",
            "threshold_warning": 75.0,
            "threshold_critical": 90.0,
            "notes": "Azure OpenAI API costs for AI Guide, Transcript Processor, and other AI-powered features. Includes GPT-4 and embedding model usage.",
            "owner": "AI Architecture",
        },
        {
            "name": "Development & Testing",
            "category": "Custom Allocation",
            "resource_groups": ["rg-dev-test"],
            "amount": 1500.0,
            "currency": "USD",
            "period": "monthly",
            "threshold_warning": 80.0,
            "threshold_critical": 95.0,
            "notes": "Development and staging environments for AI platform. Includes separate CosmosDB and Azure OpenAI instances for testing.",
            "owner": "Platform Engineering",
        },
    ]

    for budget in budgets:
        budget_id = await create_budget(client, budget)
        if budget_id:
            created_ids["budgets"][budget["name"]] = budget_id


async def update_hmlr_memories(client: httpx.AsyncClient):
    """Update HMLR memories to align with created platform content."""
    print("\n=== Updating HMLR Memories ===")

    from datetime import timezone

    # Import HMLR components
    try:
        from src.hmlr.service import HMLRService
        from src.hmlr.models import BridgeBlock, Turn
        from src.database import Database
        from src.config import settings

        if not settings.hmlr_enabled:
            print("  HMLR is disabled in settings. Skipping memory update.")
            return

        db = Database()
        await db.initialize()

        hmlr = HMLRService()
        await hmlr.initialize()

        user_id = "david.hayes"
        now = datetime.now(timezone.utc)

        # Create aligned Bridge Blocks
        blocks = [
            {
                "user_id": user_id,
                "session_id": f"session_{user_id}_demo_hmlr",
                "topic_label": "HMLR Memory System Development",
                "keywords": ["HMLR", "memory", "Governor", "Bridge Blocks", "personalization", "suggestions"],
                "summary": "Working on HMLR memory system including test suite completion, frontend integration, and Governor routing optimization.",
                "open_loops": [
                    "Complete HMLR test suite - currently at 85% coverage",
                    "Test personalized suggestions on frontend with david.hayes profile",
                ],
                "decisions": ["Use CosmosDB for Bridge Blocks", "Implement 4-scenario Governor routing"],
                "status": "PAUSED",
                "last_activity": now - timedelta(hours=2),
            },
            {
                "user_id": user_id,
                "session_id": f"session_{user_id}_demo_deployment",
                "topic_label": "Agent Deployment Pipeline",
                "keywords": ["deployment", "CI/CD", "GitHub Actions", "Azure Container Apps", "staging"],
                "summary": "Setting up deployment pipeline for AI agents using GitHub Actions and Azure Container Apps.",
                "open_loops": [
                    "Configure GitHub Actions for AI Guide deployment",
                    "Define Azure Container Apps scaling rules",
                ],
                "decisions": ["GitHub Actions for CI/CD", "Staging environment at agent-arch-staging"],
                "status": "PAUSED",
                "last_activity": now - timedelta(hours=6),
            },
            {
                "user_id": user_id,
                "session_id": f"session_{user_id}_demo_budget",
                "topic_label": "Budget Tracking Feature",
                "keywords": ["budget", "costs", "Azure Cost Management", "tracking", "licenses"],
                "summary": "Building budget and cost tracking feature using Azure Cost Management API.",
                "open_loops": [
                    "Integrate Azure Cost Management API - authentication configured",
                    "Design license tracking dashboard - waiting for UX input",
                ],
                "decisions": ["Azure Cost Management API for budget data", "Alert thresholds at 75% and 90%"],
                "status": "PAUSED",
                "last_activity": now - timedelta(days=1),
            },
            {
                "user_id": user_id,
                "session_id": f"session_{user_id}_demo_governance",
                "topic_label": "Governance Framework",
                "keywords": ["governance", "tiers", "compliance", "Enterprise", "approval"],
                "summary": "Establishing agent governance framework with 3-tier model and compliance requirements.",
                "open_loops": [
                    "Define Enterprise tier approval process",
                    "Review AI Guide v2.0 proposal",
                ],
                "decisions": ["3-tier governance model adopted", "Enterprise tier requires committee approval"],
                "status": "PAUSED",
                "last_activity": now - timedelta(days=2),
            },
        ]

        # Store blocks
        for block_data in blocks:
            block = BridgeBlock(
                user_id=block_data["user_id"],
                session_id=block_data["session_id"],
                topic_label=block_data["topic_label"],
                keywords=block_data["keywords"],
                summary=block_data["summary"],
                open_loops=block_data["open_loops"],
                decisions=block_data["decisions"],
                status=block_data["status"],
                last_activity=block_data["last_activity"],
            )

            await hmlr.block_manager.create_block(block)
            print(f"  Created Bridge Block: {block_data['topic_label']}")

        # Update user profile
        profile_update = {
            "common_queries": [
                "What was I working on?",
                "Show me blocked tasks",
                "What decisions were made recently?",
                "Show agent deployment status",
                "What's the budget status?",
                "Show me the governance framework",
                "What tasks are assigned to me?",
                "What meetings are coming up?",
            ],
            "known_entities": [
                {"name": "AI Guide", "type": "agent"},
                {"name": "HMLR", "type": "system"},
                {"name": "Cost Analyzer", "type": "agent"},
                {"name": "Governance Reviewer", "type": "agent"},
                {"name": "Azure Container Apps", "type": "technology"},
                {"name": "CosmosDB", "type": "technology"},
                {"name": "GitHub Actions", "type": "technology"},
            ],
            "preferences": {
                "response_style": "concise",
                "expertise_areas": ["AI/ML", "Azure", "Architecture", "Governance"],
                "notification_preferences": {"email": True, "teams": True},
            },
            "interaction_patterns": {
                "total_queries": 175,
                "technical_queries": 140,
                "governance_queries": 25,
                "reporting_queries": 10,
            },
        }

        await hmlr.update_user_profile(user_id, profile_update)
        print(f"  Updated user profile for {user_id}")

        # Add aligned facts
        facts = [
            ("AI Guide status", "AI Guide is in Production status, fully integrated with all platform modules", "Entity"),
            ("Enterprise approval", "Enterprise tier agents require AI Architect Committee approval with majority vote", "Policy"),
            ("CI/CD platform", "GitHub Actions is the chosen CI/CD platform for agent deployment", "Technology"),
            ("Budget data source", "Azure Cost Management API provides budget and cost tracking data", "Technology"),
            ("Governance model", "3-tier agent governance model: Individual, Department, Enterprise", "Policy"),
            ("HMLR storage", "HMLR Bridge Blocks are stored in CosmosDB with user_id partition key", "Architecture"),
        ]

        for key, value, category in facts:
            await hmlr.store_fact(user_id, key, value, category, verified=True)
            print(f"  Stored fact: {key}")

        print("  HMLR memories updated successfully!")

    except Exception as e:
        print(f"  Error updating HMLR memories: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main population routine."""
    print("=" * 60)
    print("HMLR Demo Content Population Script")
    print("=" * 60)
    print("\nThis script creates aligned platform content for AI Guide demo.")
    print("Make sure the backend is running at http://localhost:8000\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check backend is running
        try:
            response = await client.get(f"{API_BASE}/health")
            if response.status_code != 200:
                print("ERROR: Backend is not healthy. Please start the backend first.")
                return
            print("Backend is healthy. Starting content population...\n")
        except Exception as e:
            print(f"ERROR: Cannot connect to backend at {API_BASE}: {e}")
            return

        # Populate in order (respecting dependencies)
        await populate_agents(client)
        await populate_meetings(client)
        await populate_tasks(client)
        await populate_decisions(client)
        await populate_budgets(client)
        await update_hmlr_memories(client)

        print("\n" + "=" * 60)
        print("Content Population Complete!")
        print("=" * 60)
        print("\nCreated content summary:")
        print(f"  Meetings: {len(created_ids['meetings'])}")
        print(f"  Agents: {len(created_ids['agents'])}")
        print(f"  Tasks: {len(created_ids['tasks'])}")
        print(f"  Decisions: {len(created_ids['decisions'])}")
        print(f"  Budgets: {len(created_ids['budgets'])}")
        print("\nDemo scenarios ready to test:")
        print('  1. "What was I working on with HMLR?"')
        print('  2. "Show me tasks related to agent deployment"')
        print('  3. "What\'s the status of budget tracking?"')
        print('  4. "What decisions were made in recent meetings?"')
        print('  5. "What do I have pending?"')


if __name__ == "__main__":
    asyncio.run(main())
