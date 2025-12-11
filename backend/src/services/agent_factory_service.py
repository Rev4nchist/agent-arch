"""Agent Factory Service - Mock implementation for provisioning Azure AI agents."""
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ProvisionStatus(str, Enum):
    PROVISIONING = "provisioning"
    READY = "ready"
    ERROR = "error"


class IndexingStatus(str, Enum):
    INDEXING = "indexing"
    READY = "ready"
    MOCK_INDEXED = "mock_indexed"


@dataclass
class ProvisionedAgent:
    agent_id: str
    name: str
    status: ProvisionStatus
    created_at: datetime
    instructions: str
    tools: List[str] = field(default_factory=list)
    connectors: List[str] = field(default_factory=list)
    vector_store_id: Optional[str] = None
    governance: Dict[str, Any] = field(default_factory=dict)
    progress: int = 0
    message: Optional[str] = None


class AgentFactoryService:
    """
    Mock Agent Factory Service for development.

    In production, this would integrate with:
    - Azure AI Foundry Agent Service SDK
    - Azure Blob Storage for file uploads
    - Azure AI Search for vector stores
    - Microsoft Entra ID for OBO token flows
    """

    def __init__(self):
        self._provisioned_agents: Dict[str, ProvisionedAgent] = {}
        self._knowledge_stores: Dict[str, Dict[str, Any]] = {}
        logger.info("AgentFactoryService initialized (MOCK MODE)")

    async def provision_agent(
        self,
        name: str,
        description: str,
        department: str,
        owner: str,
        instructions: str,
        tools: List[str],
        connectors: List[str],
        knowledge_file_ids: List[str],
        governance: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Provision a new Azure AI Agent (mock implementation).

        In production, this would:
        1. Validate user entitlements (RBAC)
        2. Create agent in Azure AI Foundry
        3. Attach tools and connectors
        4. Link vector stores
        5. Apply governance tags
        """
        agent_id = str(uuid.uuid4())

        agent = ProvisionedAgent(
            agent_id=agent_id,
            name=name,
            status=ProvisionStatus.READY,
            created_at=datetime.utcnow(),
            instructions=instructions,
            tools=tools,
            connectors=connectors,
            vector_store_id=f"vs-{agent_id[:8]}" if knowledge_file_ids else None,
            governance=governance,
            progress=100,
            message="Agent provisioned successfully (mock)",
        )

        self._provisioned_agents[agent_id] = agent

        logger.info(f"[MOCK] Provisioned agent: {agent_id} - {name}")

        return {
            "agent_id": agent_id,
            "status": agent.status.value,
            "message": agent.message,
        }

    async def get_provision_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the provisioning status of an agent."""
        if agent_id not in self._provisioned_agents:
            return {
                "status": ProvisionStatus.ERROR.value,
                "progress": 0,
                "message": "Agent not found",
            }

        agent = self._provisioned_agents[agent_id]
        return {
            "status": agent.status.value,
            "progress": agent.progress,
            "message": agent.message,
        }

    async def attach_knowledge(
        self,
        agent_id: str,
        files: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Attach knowledge files to an agent (mock implementation).

        In production, this would:
        1. Upload files to Azure Blob Storage
        2. Create/update vector store in Azure AI Search
        3. Process and index documents
        4. Link vector store to agent
        """
        file_ids = [str(uuid.uuid4()) for _ in files]
        store_id = f"vs-{agent_id[:8]}" if agent_id else str(uuid.uuid4())

        self._knowledge_stores[store_id] = {
            "agent_id": agent_id,
            "file_ids": file_ids,
            "file_count": len(files),
            "status": IndexingStatus.MOCK_INDEXED.value,
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"[MOCK] Attached {len(files)} files to agent {agent_id}")

        return {
            "files_received": len(files),
            "file_ids": file_ids,
            "vector_store_id": store_id,
            "status": IndexingStatus.MOCK_INDEXED.value,
        }

    async def create_thread(self, agent_id: str) -> Dict[str, Any]:
        """
        Create a new conversation thread (mock implementation).

        In production, this would create a thread in Azure AI Foundry.
        """
        thread_id = f"thread-{uuid.uuid4().hex[:16]}"

        logger.info(f"[MOCK] Created thread {thread_id} for agent {agent_id}")

        return {
            "thread_id": thread_id,
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
        }

    async def execute_run(
        self,
        agent_id: str,
        thread_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Execute an agent run (mock implementation).

        In production, this would:
        1. Create a message in the thread
        2. Start a run with the agent
        3. Stream events back to the client
        4. Handle tool calls with OBO token exchange
        """
        run_id = f"run-{uuid.uuid4().hex[:16]}"

        mock_response = f"[MOCK RESPONSE] I received your message: '{message}'. In production, I would process this using Azure AI Foundry and potentially call tools on your behalf."

        logger.info(f"[MOCK] Executed run {run_id} for thread {thread_id}")

        return {
            "run_id": run_id,
            "thread_id": thread_id,
            "status": "completed",
            "response": mock_response,
        }


agent_factory_service = AgentFactoryService()
