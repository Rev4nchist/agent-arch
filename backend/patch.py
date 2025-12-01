import sys

with open('src/main.py', 'r') as f:
    content = f.read()

old = '''@app.put("/api/meetings/{meeting_id}", response_model=Meeting)
async def update_meeting(meeting_id: str, meeting: Meeting):
    """Update meeting."""
    try:
        meeting.id = meeting_id
        meeting.updated_at = datetime.utcnow()

        container = db.get_container("meetings")
        container.upsert_item(body=meeting.model_dump(mode='json'))
        return jsonable_encoder(meeting)'''

new = '''@app.put("/api/meetings/{meeting_id}", response_model=Meeting)
async def update_meeting(meeting_id: str, meeting: Meeting):
    """Update meeting. Auto-sets status to Completed when transcript is added."""
    try:
        meeting.id = meeting_id
        meeting.updated_at = datetime.utcnow()

        # Auto-transition to Completed when transcript is added
        if (meeting.transcript or meeting.transcript_text or meeting.transcript_url):
            from src.models import MeetingStatus
            if meeting.status != MeetingStatus.CANCELLED:
                meeting.status = MeetingStatus.COMPLETED
                logger.info(f"Meeting {meeting_id} auto-transitioned to Completed (transcript added)")

        container = db.get_container("meetings")
        container.upsert_item(body=meeting.model_dump(mode='json'))
        return jsonable_encoder(meeting)'''

if old in content:
    content = content.replace(old, new)
    with open('src/main.py', 'w') as f:
        f.write(content)
    print("Patch applied")
else:
    print("ERROR: Pattern not found")
    sys.exit(1)
