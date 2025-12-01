"""Data indexing utilities for Azure AI Search."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.database import db
from src.search_service import get_search_service

logger = logging.getLogger(__name__)


def chunk_text(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for better search coverage.

    Args:
        text: Text to chunk
        max_chunk_size: Maximum characters per chunk
        overlap: Character overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for period, question mark, or exclamation within last 200 chars
            chunk_text = text[start:end]
            last_sentence = max(
                chunk_text.rfind('. '),
                chunk_text.rfind('? '),
                chunk_text.rfind('! ')
            )
            if last_sentence > max_chunk_size - 200:
                end = start + last_sentence + 2

        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else end

    return chunks


def index_meetings(limit: Optional[int] = None) -> Dict[str, int]:
    """
    Index all meetings from Cosmos DB to Azure AI Search.
    Long transcripts are chunked into segments.

    Args:
        limit: Optional limit on number of meetings to index

    Returns:
        Dict with success/failed counts
    """
    try:
        search_service = get_search_service()
        container = db.get_container("meetings")

        # Query all meetings
        query = "SELECT * FROM c"
        if limit:
            query += f" OFFSET 0 LIMIT {limit}"

        meetings = list(container.query_items(query=query, enable_cross_partition_query=True))

        logger.info(f"Found {len(meetings)} meetings to index")

        documents = []
        for meeting in meetings:
            transcript = meeting.get("transcript", "")

            # Skip if no transcript content
            if not transcript or not transcript.strip():
                logger.warning(f"Skipping meeting {meeting.get('id')} - no transcript content")
                continue

            # Chunk transcript if it's long
            if len(transcript) > 1000:
                chunks = chunk_text(transcript, max_chunk_size=1000)
                logger.info(f"Chunked meeting {meeting['id']} into {len(chunks)} segments")

                # Create document for each chunk
                for i, chunk in enumerate(chunks):
                    doc = {
                        "id": f"{meeting['id']}_chunk_{i}",
                        "content": chunk,
                        "type": "meeting",
                        "title": f"{meeting.get('title', 'Meeting')} (Part {i+1}/{len(chunks)})",
                        "metadata": {
                            "meeting_id": meeting["id"],
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "date": meeting.get("date"),
                            "facilitator": meeting.get("facilitator"),
                            "participants": meeting.get("participants", []),
                        },
                        "status": meeting.get("status", "Completed"),
                    }
                    documents.append(doc)
            else:
                # Single document for short transcripts
                doc = {
                    "id": meeting["id"],
                    "content": transcript,
                    "type": "meeting",
                    "title": meeting.get("title", "Meeting"),
                    "metadata": {
                        "date": meeting.get("date"),
                        "facilitator": meeting.get("facilitator"),
                        "participants": meeting.get("participants", []),
                    },
                    "status": meeting.get("status", "Completed"),
                }
                documents.append(doc)

        # Batch upload
        if documents:
            result = search_service.upload_documents_batch(documents)
            logger.info(f"Indexed {result['success']} meeting documents, {result['failed']} failed")
            return result
        else:
            logger.info("No meeting documents to index")
            return {"success": 0, "failed": 0}

    except Exception as e:
        logger.error(f"Error indexing meetings: {str(e)}")
        raise


def index_tasks(limit: Optional[int] = None) -> Dict[str, int]:
    """
    Index all tasks from Cosmos DB to Azure AI Search.

    Args:
        limit: Optional limit on number of tasks to index

    Returns:
        Dict with success/failed counts
    """
    try:
        search_service = get_search_service()
        container = db.get_container("tasks")

        # Query all tasks
        query = "SELECT * FROM c"
        if limit:
            query += f" OFFSET 0 LIMIT {limit}"

        tasks = list(container.query_items(query=query, enable_cross_partition_query=True))

        logger.info(f"Found {len(tasks)} tasks to index")

        documents = []
        for task in tasks:
            # Skip if no description
            if not task.get("description") or not task.get("description").strip():
                logger.warning(f"Skipping task {task.get('id')} - no description")
                continue

            # Combine description and acceptance criteria for content
            content_parts = [task.get("description", "")]
            if task.get("acceptance_criteria"):
                content_parts.append(f"Acceptance Criteria: {task['acceptance_criteria']}")

            content = " ".join(content_parts)

            doc = {
                "id": task["id"],
                "content": content,
                "type": "task",
                "title": task.get("title", "Task"),
                "metadata": {
                    "assigned_to": task.get("assigned_to"),
                    "due_date": task.get("due_date"),
                    "estimated_hours": task.get("estimated_hours"),
                    "tags": task.get("tags", []),
                },
                "status": task.get("status", "Pending"),
                "priority": task.get("priority", "Medium"),
            }
            documents.append(doc)

        # Batch upload
        if documents:
            result = search_service.upload_documents_batch(documents)
            logger.info(f"Indexed {result['success']} task documents, {result['failed']} failed")
            return result
        else:
            logger.info("No task documents to index")
            return {"success": 0, "failed": 0}

    except Exception as e:
        logger.error(f"Error indexing tasks: {str(e)}")
        raise


def index_agents(limit: Optional[int] = None) -> Dict[str, int]:
    """
    Index all agents from Cosmos DB to Azure AI Search.

    Args:
        limit: Optional limit on number of agents to index

    Returns:
        Dict with success/failed counts
    """
    try:
        search_service = get_search_service()
        container = db.get_container("agents")

        # Query all agents
        query = "SELECT * FROM c"
        if limit:
            query += f" OFFSET 0 LIMIT {limit}"

        agents = list(container.query_items(query=query, enable_cross_partition_query=True))

        logger.info(f"Found {len(agents)} agents to index")

        documents = []
        for agent in agents:
            # Skip if no description
            if not agent.get("description") or not agent.get("description").strip():
                logger.warning(f"Skipping agent {agent.get('id')} - no description")
                continue

            # Combine description and capabilities for content
            content_parts = [agent.get("description", "")]
            if agent.get("capabilities"):
                capabilities_text = ", ".join(agent["capabilities"])
                content_parts.append(f"Capabilities: {capabilities_text}")
            if agent.get("use_cases"):
                use_cases_text = ", ".join(agent["use_cases"])
                content_parts.append(f"Use Cases: {use_cases_text}")

            content = " ".join(content_parts)

            doc = {
                "id": agent["id"],
                "content": content,
                "type": "agent",
                "title": agent.get("name", "Agent"),
                "metadata": {
                    "tier": agent.get("tier"),
                    "development_status": agent.get("development_status"),
                    "tools": agent.get("tools", []),
                    "repositories": agent.get("repositories", []),
                },
                "status": agent.get("development_status", "Proposed"),
                "category": agent.get("tier", "Unknown"),
            }
            documents.append(doc)

        # Batch upload
        if documents:
            result = search_service.upload_documents_batch(documents)
            logger.info(f"Indexed {result['success']} agent documents, {result['failed']} failed")
            return result
        else:
            logger.info("No agent documents to index")
            return {"success": 0, "failed": 0}

    except Exception as e:
        logger.error(f"Error indexing agents: {str(e)}")
        raise


def index_governance(limit: Optional[int] = None) -> Dict[str, int]:
    """
    Index governance items (proposals and decisions) from Cosmos DB to Azure AI Search.

    Args:
        limit: Optional limit on number of items to index

    Returns:
        Dict with success/failed counts
    """
    try:
        search_service = get_search_service()

        documents = []

        # Index proposals
        proposals_container = db.get_container("proposals")
        query = "SELECT * FROM c"
        if limit:
            query += f" OFFSET 0 LIMIT {limit // 2}"

        proposals = list(proposals_container.query_items(query=query, enable_cross_partition_query=True))
        logger.info(f"Found {len(proposals)} proposals to index")

        for proposal in proposals:
            # Skip if no description
            if not proposal.get("description") or not proposal.get("description").strip():
                logger.warning(f"Skipping proposal {proposal.get('id')} - no description")
                continue

            content_parts = [proposal.get("description", "")]
            if proposal.get("rationale"):
                content_parts.append(f"Rationale: {proposal['rationale']}")
            if proposal.get("impact"):
                content_parts.append(f"Impact: {proposal['impact']}")

            content = " ".join(content_parts)

            doc = {
                "id": proposal["id"],
                "content": content,
                "type": "governance",
                "title": proposal.get("title", "Proposal"),
                "metadata": {
                    "proposed_by": proposal.get("proposed_by"),
                    "proposed_date": proposal.get("proposed_date"),
                    "voting_deadline": proposal.get("voting_deadline"),
                    "votes": proposal.get("votes", {}),
                },
                "status": proposal.get("status", "Proposed"),
                "category": "proposal",
            }
            documents.append(doc)

        # Index decisions
        decisions_container = db.get_container("decisions")
        query = "SELECT * FROM c"
        if limit:
            query += f" OFFSET 0 LIMIT {limit // 2}"

        decisions = list(decisions_container.query_items(query=query, enable_cross_partition_query=True))
        logger.info(f"Found {len(decisions)} decisions to index")

        for decision in decisions:
            # Skip if no description
            if not decision.get("description") or not decision.get("description").strip():
                logger.warning(f"Skipping decision {decision.get('id')} - no description")
                continue

            content_parts = [decision.get("description", "")]
            if decision.get("rationale"):
                content_parts.append(f"Rationale: {decision['rationale']}")
            if decision.get("alternatives_considered"):
                content_parts.append(f"Alternatives: {decision['alternatives_considered']}")

            content = " ".join(content_parts)

            doc = {
                "id": decision["id"],
                "content": content,
                "type": "governance",
                "title": decision.get("title", "Decision"),
                "metadata": {
                    "decision_date": decision.get("decision_date"),
                    "decided_by": decision.get("decided_by"),
                    "impact": decision.get("impact"),
                },
                "status": "Approved",
                "category": "decision",
            }
            documents.append(doc)

        # Batch upload
        if documents:
            result = search_service.upload_documents_batch(documents)
            logger.info(f"Indexed {result['success']} governance documents, {result['failed']} failed")
            return result
        else:
            logger.info("No governance documents to index")
            return {"success": 0, "failed": 0}

    except Exception as e:
        logger.error(f"Error indexing governance: {str(e)}")
        raise


def index_all_data(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Index all data from Cosmos DB to Azure AI Search.

    Args:
        limit: Optional limit per container

    Returns:
        Dict with results for each data type
    """
    logger.info("Starting bulk indexing of all data...")

    results = {
        "meetings": {"success": 0, "failed": 0},
        "tasks": {"success": 0, "failed": 0},
        "agents": {"success": 0, "failed": 0},
        "governance": {"success": 0, "failed": 0},
    }

    try:
        results["meetings"] = index_meetings(limit)
    except Exception as e:
        logger.error(f"Failed to index meetings: {str(e)}")

    try:
        results["tasks"] = index_tasks(limit)
    except Exception as e:
        logger.error(f"Failed to index tasks: {str(e)}")

    try:
        results["agents"] = index_agents(limit)
    except Exception as e:
        logger.error(f"Failed to index agents: {str(e)}")

    try:
        results["governance"] = index_governance(limit)
    except Exception as e:
        logger.error(f"Failed to index governance: {str(e)}")

    # Calculate totals
    total_success = sum(r["success"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())

    logger.info(f"Bulk indexing complete: {total_success} succeeded, {total_failed} failed")

    results["total"] = {"success": total_success, "failed": total_failed}
    return results
