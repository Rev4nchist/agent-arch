# Developer A - AI Features Track (Transcript Processing)

## Your Mission
You are Developer A working on the **AI Features Track** - specifically implementing the **Meeting Transcript Processing System** (Tasks 1-4). This is a HIGH-PRIORITY feature that enables automated extraction of action items, decisions, and topics from meeting transcripts using Azure AI.

## Project Context
- **Project:** Agent Architecture Guide (Microsoft Agent Ecosystem Portal)
- **Location:** `c:\agent-arch`
- **Your Role:** Lead developer for AI-powered transcript processing
- **Working in Parallel With:**
  - Developer B: Microsoft SSO Authentication (Task 13)
  - Developer C: Resource Library dual-section (Tasks 8-9)

## Task Master Integration
You have Task Master CLI available for tracking your work.

### Your Task Chain (Sequential Dependencies)
```
Task #1: Implement Transcript File Upload Backend (START HERE)
    ↓
Task #2: Build AI Transcript Processing Pipeline
    ↓
Task #3: Implement Auto-Task Creation from Transcripts
    ↓
Task #4: Connect Frontend Upload Dialog to Backend
```

### Getting Started
```bash
cd c:\agent-arch

# View your task details
task-master show 1

# Start working on Task 1
task-master set-status --id=1 --status=in-progress

# View Task 1 subtasks (already expanded with 5 subtasks)
# 1.1: Set up Azure Blob Storage client
# 1.2: Create file upload endpoint with validation
# 1.3: Store validated files in Azure Blob Storage
# 1.4: Return upload metadata as JSON response
# 1.5: Implement error handling and logging
```

### Tracking Your Progress
```bash
# After completing each subtask
task-master set-status --id=1.1 --status=done
task-master update-subtask --id=1.1 --prompt="Set up BlobServiceClient with connection string, created 'transcripts' container"

# When Task 1 is complete
task-master set-status --id=1 --status=done

# Move to Task 2
task-master set-status --id=2 --status=in-progress
```

## Technical Specifications

### Task #1: Transcript File Upload Backend (6-8 hours)

**What You're Building:**
Backend endpoint that accepts transcript file uploads, validates them, stores in Azure Blob Storage, and returns metadata.

**Backend Endpoint:**
```python
# File: backend/src/main.py or backend/src/routers/transcripts.py

POST /api/transcripts/upload
- Accepts: multipart/form-data with file (.txt, .md, .docx)
- Maximum file size: 10MB
- Returns: { blob_url, file_name, file_size, upload_timestamp }
```

**Azure Blob Storage Setup:**
```python
from azure.storage.blob import BlobServiceClient

# Connection string from environment variable
blob_service = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

# Container: "transcripts"
container_client = blob_service.get_container_client("transcripts")
```

**File Validation:**
- Check file extension: `.txt`, `.md`, `.docx` only
- Check file size: Max 10MB
- Use `python-magic` for MIME type validation
- Return 400 error for invalid files

**Key Files to Create/Modify:**
- `backend/src/routers/transcripts.py` (new)
- `backend/src/blob_service.py` (may already exist, extend it)
- `backend/requirements.txt` (add azure-storage-blob, python-magic)

### Task #2: AI Transcript Processing Pipeline (8-10 hours)

**What You're Building:**
Process uploaded transcripts with Azure AI Foundry to extract action items, decisions, topics, and summary.

**Backend Endpoint:**
```python
POST /api/transcripts/process
Body: {
  "meeting_id": "meeting-uuid",
  "blob_url": "https://storage.../transcript.txt"
}
Returns: {
  "summary": "2-3 sentence summary",
  "action_items": ["Task 1", "Task 2"],
  "decisions": ["Decision 1", "Decision 2"],
  "topics": ["topic1", "topic2", "topic3"]
}
```

**Chunking Strategy:**
- If transcript > 15,000 tokens → split into 10,000 token chunks
- Process each chunk separately
- Deduplicate and merge results

**Azure AI Integration:**
```python
from azure.ai.foundry import ModelRouterClient

# Use Model Router for GPT-4o
router_client = ModelRouterClient(
    endpoint=os.getenv("AZURE_AI_FOUNDRY_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_FOUNDRY_API_KEY")
)

# Prompt for extraction
prompt = f"""
Extract the following from this meeting transcript:
1. Summary (2-3 sentences)
2. Action items (list of tasks mentioned)
3. Key decisions made
4. Main topics discussed

Transcript:
{transcript_text}

Return JSON format.
"""
```

**Update Meeting Record:**
After processing, update the meeting in Cosmos DB:
```python
meeting_doc = {
    "id": meeting_id,
    "summary": extracted_summary,
    "action_items": extracted_action_items,
    "decisions": extracted_decisions,
    "topics": extracted_topics,
    "status": "Completed",  # Change from "Scheduled"
    "transcript_text": transcript_text,
    "updated_at": datetime.utcnow().isoformat()
}
```

### Task #3: Auto-Task Creation (4-6 hours)

**What You're Building:**
Automatically create tasks in Cosmos DB for each extracted action item.

**Logic:**
```python
for action_item in extracted_action_items:
    task_doc = {
        "id": str(uuid.uuid4()),
        "title": action_item["title"],
        "description": action_item["description"],
        "status": "Pending",
        "priority": detect_priority(action_item),  # Check for "urgent", "critical", "ASAP"
        "assigned_to": extract_assignee(action_item),  # If name mentioned
        "created_from_meeting": meeting_id,
        "created_at": datetime.utcnow().isoformat()
    }

    # Insert into Cosmos DB tasks collection
    tasks_container.create_item(task_doc)
```

**Priority Detection:**
- If action item contains "urgent", "critical", "ASAP" → Priority: High
- If contains "important" → Priority: Medium
- Otherwise → Priority: Low

**Assignee Detection:**
- If action item mentions "David", "Mark", "Boyan", etc. → assigned_to: name
- Otherwise → assigned_to: null (unassigned)

### Task #4: Frontend Connection (3-4 hours)

**What You're Building:**
Connect the existing upload dialog in `app/meetings/page.tsx` to your backend endpoints.

**Frontend Changes:**
```typescript
// In app/meetings/page.tsx

const handleTranscriptUpload = async (meetingId: string, file: File) => {
  // Step 1: Upload file
  const formData = new FormData();
  formData.append('file', file);

  const uploadResponse = await fetch('/api/transcripts/upload', {
    method: 'POST',
    body: formData
  });

  const { blob_url } = await uploadResponse.json();

  // Step 2: Process transcript
  setProcessingStatus('Processing transcript...');

  const processResponse = await fetch('/api/transcripts/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id: meetingId, blob_url })
  });

  const results = await processResponse.json();

  // Step 3: Show success
  toast.success(`Extracted ${results.action_items.length} action items, ${results.decisions.length} decisions`);

  // Step 4: Refresh meetings list
  loadMeetings();
};
```

**UI States:**
- Uploading: Show progress bar
- Processing: Show "Extracting action items..." spinner
- Complete: Show success message with counts
- Error: Show user-friendly error message

## Testing Strategy

### Unit Tests
- Test file validation (valid/invalid types, size limits)
- Test chunking logic for large transcripts
- Test priority detection from action items
- Test assignee extraction

### Integration Tests
- Upload transcript → Verify stored in Blob Storage
- Process transcript → Verify meeting updated in Cosmos DB
- Auto-create tasks → Verify tasks created with correct linking

### Manual Testing Checklist
```
[ ] Upload .txt transcript < 10MB → Success
[ ] Upload .pdf transcript → Rejected (invalid type)
[ ] Upload 15MB file → Rejected (too large)
[ ] Process short transcript → Extract action items
[ ] Process long transcript (>15k tokens) → Chunking works
[ ] Create meeting with transcript → Status changes to "Completed"
[ ] Extract action items → Tasks auto-created in Cosmos DB
[ ] Extracted tasks linked to meeting → created_from_meeting field set
[ ] Frontend upload dialog → Works end-to-end
```

## Environment Variables Required

Add to `backend/.env`:
```bash
# Already exist
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_AI_FOUNDRY_ENDPOINT=...
AZURE_AI_FOUNDRY_API_KEY=...

# May need to add
AZURE_STORAGE_TRANSCRIPTS_CONTAINER=transcripts
MAX_TRANSCRIPT_SIZE_MB=10
TRANSCRIPT_CHUNK_SIZE_TOKENS=10000
```

## Success Criteria

✅ **Task 1 Complete When:**
- Files upload successfully to Blob Storage
- Metadata returned correctly
- Invalid files rejected with clear errors

✅ **Task 2 Complete When:**
- Transcripts processed with Azure AI
- Action items, decisions, topics extracted
- Meeting status updated to "Completed"
- Large transcripts chunked and processed

✅ **Task 3 Complete When:**
- Tasks auto-created for each action item
- Priority and assignee detected correctly
- Tasks linked to originating meeting

✅ **Task 4 Complete When:**
- Upload dialog functional in UI
- Processing status shown to user
- Success/error messages displayed
- Meeting list refreshes after processing

## Key Technical Decisions

**File Storage:**
- Use Azure Blob Storage (already configured)
- Container: `transcripts`
- Blob name format: `{meeting_id}/{timestamp}_{filename}`

**AI Processing:**
- Use Azure AI Foundry Model Router
- Model: GPT-4o (already deployed)
- Chunking threshold: 15,000 tokens
- Chunk size: 10,000 tokens with 500 token overlap

**Task Creation:**
- Create immediately after extraction (not async)
- Link with `created_from_meeting` field
- Default status: "Pending"
- Auto-detect priority and assignee (best effort)

## Coordination with Other Developers

**With Developer B (SSO):**
- Currently using shared API key authentication
- Developer B will implement user context
- Your code should use `created_by` field (set to "system" for now)
- After SSO is complete, update to use authenticated user

**With Developer C (Resources):**
- No direct dependencies
- Both working independently on different features
- May need to coordinate on Azure Blob Storage container usage

## Getting Help

**Documentation:**
- Azure SDK: `c:\agent-arch\Resource-Library-Enhancement-Proposal.md`
- Project README: `c:\agent-arch\README.md`
- Current state: `c:\agent-arch\CURRENT_STATE_AND_TODO.md`

**API Reference:**
- Backend API: Check `backend/src/main.py` for existing endpoints
- Frontend API client: `frontend/lib/api.ts`

**Task Master Commands:**
```bash
task-master list              # View all tasks
task-master show <id>         # View task details
task-master next              # Get next task recommendation
task-master update-subtask --id=1.1 --prompt="notes"  # Log progress
```

## Estimated Timeline

- **Task 1:** 6-8 hours (File upload backend)
- **Task 2:** 8-10 hours (AI processing pipeline)
- **Task 3:** 4-6 hours (Auto-task creation)
- **Task 4:** 3-4 hours (Frontend connection)

**Total: 21-28 hours (approximately 3-4 days of full-time work)**

## Final Notes

- **Start with Task 1.1** (Azure Blob Storage setup)
- **Test frequently** - don't wait until the end
- **Log your progress** in Task Master (`update-subtask`)
- **Ask questions** if blocked - don't spin your wheels
- **Coordinate** with Developers B and C on shared resources

**Good luck! You're building a critical AI feature for the team! 🚀**
