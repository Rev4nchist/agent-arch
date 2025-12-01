"""Transcript upload and processing endpoints."""
from fastapi import APIRouter, File, UploadFile, HTTPException
from azure.storage.blob import BlobServiceClient
from src.config import settings
from src.ai_client import ai_client
from src.database import db
import logging
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])

# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".md", ".docx"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

class TranscriptBlobService:
    """Blob service specifically for transcript files."""

    def __init__(self):
        """Initialize with transcripts container."""
        self.client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.container_name = "transcripts"
        self._ensure_container_exists()

    def _ensure_container_exists(self):
        """Ensure transcripts container exists."""
        try:
            container_client = self.client.get_container_client(self.container_name)
            if not container_client.exists():
                self.client.create_container(self.container_name)
                logger.info(f"Created container '{self.container_name}'")
        except Exception as e:
            logger.error(f"Container creation error: {e}")
            raise

    async def upload_transcript(
        self,
        file_content: bytes,
        file_name: str,
        meeting_id: Optional[str] = None
    ) -> dict:
        """Upload transcript to blob storage."""
        try:
            # Generate blob name with meeting_id prefix if provided
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            if meeting_id:
                blob_name = f"{meeting_id}/{timestamp}_{file_name}"
            else:
                blob_name = f"{timestamp}_{file_name}"

            blob_client = self.client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Upload with metadata
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                metadata={
                    "meeting_id": meeting_id or "",
                    "upload_timestamp": datetime.utcnow().isoformat(),
                    "original_filename": file_name
                }
            )

            blob_url = blob_client.url
            logger.info(f"Uploaded transcript to {blob_url}")

            return {
                "blob_url": blob_url,
                "file_name": file_name,
                "file_size": len(file_content),
                "upload_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Transcript upload error: {e}")
            raise

# Global instance
transcript_blob_service = TranscriptBlobService()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check file extension
    file_ext = None
    if file.filename:
        file_ext = "." + file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    # Check content type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type: {file.content_type}"
        )


@router.post("/upload")
async def upload_transcript(
    file: UploadFile = File(...),
    meeting_id: Optional[str] = None
):
    """
    Upload transcript file to Azure Blob Storage.

    - **file**: Transcript file (.txt, .md, .docx)
    - **meeting_id**: Optional meeting ID to link transcript to

    Returns upload metadata including blob URL.
    """
    try:
        # Validate file type
        validate_file(file)

        # Read file content
        file_content = await file.read()

        # Check file size
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
            )

        # Check if file is empty
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )

        # Upload to blob storage
        result = await transcript_blob_service.upload_transcript(
            file_content=file_content,
            file_name=file.filename or "transcript.txt",
            meeting_id=meeting_id
        )

        logger.info(f"Successfully uploaded transcript: {file.filename}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


class ProcessRequest(BaseModel):
    """Request model for transcript processing."""
    meeting_id: str
    blob_url: str


@router.post("/process")
async def process_transcript(request: ProcessRequest):
    """
    Process uploaded transcript to extract meeting insights.

    - **meeting_id**: ID of the meeting
    - **blob_url**: Blob storage URL of the transcript file

    Returns extracted summary, action items, decisions, and topics.
    """
    try:
        logger.info(f"Processing transcript for meeting {request.meeting_id}")

        # Download transcript from blob storage
        blob_name = request.blob_url.split("/")[-1]
        container_name = request.blob_url.split("/")[-2]

        blob_client = transcript_blob_service.client.get_blob_client(
            container=container_name,
            blob=blob_name
        )

        # Download and decode transcript
        download_stream = blob_client.download_blob()
        transcript_bytes = download_stream.readall()
        transcript_text = transcript_bytes.decode('utf-8')

        logger.info(f"Downloaded transcript ({len(transcript_text)} characters)")

        # Process with AI
        result = await ai_client.process_transcript(transcript_text)

        logger.info(f"Extracted {len(result.get('action_items', []))} action items, "
                   f"{len(result.get('decisions', []))} decisions, "
                   f"{len(result.get('topics', []))} topics")

        # Create tasks from action items
        tasks_container = db.get_container("tasks")
        task_ids = []

        for action_item in result.get("action_items", []):
            try:
                task_doc = {
                    "id": str(uuid.uuid4()),
                    "title": action_item.get("title", "Untitled Task"),
                    "description": action_item.get("description"),
                    "status": "Pending",
                    "priority": action_item.get("priority", "Medium"),
                    "assigned_to": action_item.get("assigned_to"),
                    "due_date": action_item.get("due_date"),
                    "created_from_meeting": request.meeting_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }

                tasks_container.create_item(task_doc)
                task_ids.append(task_doc["id"])
                logger.info(f"Created task: {task_doc['title']}")

            except Exception as task_error:
                logger.error(f"Failed to create task: {task_error}")
                # Continue with other tasks

        logger.info(f"Created {len(task_ids)} tasks from action items")

        # Create decisions from extracted decisions
        decisions_container = db.get_container("decisions")
        decision_ids = []

        for decision in result.get("decisions", []):
            try:
                decision_doc = {
                    "id": str(uuid.uuid4()),
                    "title": decision.get("title", "Untitled Decision"),
                    "description": decision.get("description", ""),
                    "category": decision.get("category", "Architecture"),
                    "decision_date": datetime.utcnow().isoformat(),
                    "decision_maker": decision.get("decision_maker", ""),
                    "rationale": decision.get("rationale", ""),
                    "meeting": request.meeting_id,
                    "created_at": datetime.utcnow().isoformat()
                }

                decisions_container.create_item(decision_doc)
                decision_ids.append(decision_doc["id"])
                logger.info(f"Created decision: {decision_doc['title']}")

            except Exception as decision_error:
                logger.error(f"Failed to create decision: {decision_error}")
                # Continue with other decisions

        logger.info(f"Created {len(decision_ids)} decisions")

        # Update meeting record in Cosmos DB
        meetings_container = db.get_container("meetings")

        try:
            # Get existing meeting
            meeting = meetings_container.read_item(
                item=request.meeting_id,
                partition_key=request.meeting_id
            )

            # Update with extracted data
            meeting["summary"] = result.get("summary", "")
            meeting["action_items"] = task_ids  # Store task IDs
            meeting["decisions"] = decision_ids  # Store decision IDs
            meeting["topics"] = result.get("topics", [])
            meeting["transcript_url"] = request.blob_url
            meeting["transcript_text"] = transcript_text
            meeting["status"] = "Completed"
            meeting["updated_at"] = datetime.utcnow().isoformat()

            # Save updated meeting
            meetings_container.upsert_item(meeting)

            logger.info(f"Updated meeting {request.meeting_id} with extracted data")

        except Exception as db_error:
            logger.warning(f"Could not update meeting in DB: {db_error}")
            # Continue anyway - return results even if DB update fails

        return {
            "meeting_id": request.meeting_id,
            "summary": result.get("summary", ""),
            "action_items": result.get("action_items", []),
            "decisions": result.get("decisions", []),
            "topics": result.get("topics", []),
            "tasks_created": len(task_ids),
            "task_ids": task_ids,
            "decisions_created": len(decision_ids),
            "decision_ids": decision_ids,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Transcript processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )
