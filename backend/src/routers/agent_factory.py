"""Agent Factory Router - Endpoints for provisioning and managing Azure AI agents."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents/factory", tags=["agent-factory"])


class DataClassification(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"


class GovernanceConfig(BaseModel):
    classification: DataClassification = DataClassification.INTERNAL
    cost_center: Optional[str] = None
    requires_approval: bool = False


class AgentProvisionRequest(BaseModel):
    name: str
    description: str
    department: str
    owner: str
    instructions: str
    tools: List[str] = []
    connectors: List[str] = []
    knowledge_file_ids: List[str] = []
    governance: GovernanceConfig = GovernanceConfig()


class AgentProvisionResponse(BaseModel):
    agent_id: str
    status: str
    message: Optional[str] = None


class ProvisionStatusResponse(BaseModel):
    status: str
    progress: int
    message: Optional[str] = None


class AttachKnowledgeResponse(BaseModel):
    files_received: int
    file_ids: List[str]
    vector_store_id: str
    status: str


class CreateThreadResponse(BaseModel):
    thread_id: str
    agent_id: str
    created_at: str


class RunMessageRequest(BaseModel):
    message: str


class RunResponse(BaseModel):
    run_id: str
    thread_id: str
    status: str
    response: str


@router.post("/provision", response_model=AgentProvisionResponse)
async def provision_agent(request: AgentProvisionRequest):
    """
    Provision a new Azure AI Agent.

    This endpoint creates an agent in Azure AI Foundry with the specified
    configuration, tools, and governance settings.

    In mock mode, this returns immediately with a mock agent ID.
    In production, this would trigger the full provisioning workflow.
    """
    try:
        from src.services.agent_factory_service import agent_factory_service

        result = await agent_factory_service.provision_agent(
            name=request.name,
            description=request.description,
            department=request.department,
            owner=request.owner,
            instructions=request.instructions,
            tools=request.tools,
            connectors=request.connectors,
            knowledge_file_ids=request.knowledge_file_ids,
            governance=request.governance.model_dump(),
        )

        return AgentProvisionResponse(**result)
    except Exception as e:
        logger.error(f"Error provisioning agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status", response_model=ProvisionStatusResponse)
async def get_provision_status(agent_id: str):
    """
    Get the provisioning status of an agent.

    Returns the current status, progress percentage, and any status messages.
    """
    try:
        from src.services.agent_factory_service import agent_factory_service

        result = await agent_factory_service.get_provision_status(agent_id)
        return ProvisionStatusResponse(**result)
    except Exception as e:
        logger.error(f"Error getting provision status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/knowledge", response_model=AttachKnowledgeResponse)
async def attach_knowledge(
    agent_id: str,
    files: List[UploadFile] = File(...),
):
    """
    Attach knowledge files to an agent.

    Files are uploaded to Azure Blob Storage and indexed into a vector store
    for semantic search. The agent can then use these documents to answer questions.

    Supported file types: PDF, DOC, DOCX, TXT, MD, JSON, CSV, XLSX
    Maximum file size: 50MB per file
    Maximum files: 10 per request
    """
    try:
        from src.services.agent_factory_service import agent_factory_service

        file_info = [
            {
                "filename": f.filename,
                "content_type": f.content_type,
                "size": f.size,
            }
            for f in files
        ]

        result = await agent_factory_service.attach_knowledge(
            agent_id=agent_id,
            files=file_info,
        )

        return AttachKnowledgeResponse(**result)
    except Exception as e:
        logger.error(f"Error attaching knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/threads", response_model=CreateThreadResponse)
async def create_thread(agent_id: str):
    """
    Create a new conversation thread with an agent.

    Threads maintain conversation history and context for multi-turn interactions.
    """
    try:
        from src.services.agent_factory_service import agent_factory_service

        result = await agent_factory_service.create_thread(agent_id)
        return CreateThreadResponse(**result)
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/threads/{thread_id}/runs", response_model=RunResponse)
async def execute_run(
    agent_id: str,
    thread_id: str,
    request: RunMessageRequest,
):
    """
    Send a message and execute an agent run.

    The agent will process the message using its instructions and tools,
    then return a response. Tool calls are executed using OBO (On-Behalf-Of)
    authentication to maintain user context.
    """
    try:
        from src.services.agent_factory_service import agent_factory_service

        result = await agent_factory_service.execute_run(
            agent_id=agent_id,
            thread_id=thread_id,
            message=request.message,
        )

        return RunResponse(**result)
    except Exception as e:
        logger.error(f"Error executing run: {e}")
        raise HTTPException(status_code=500, detail=str(e))
