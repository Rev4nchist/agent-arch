"""Add Proposal endpoints to main.py."""
import re

with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Proposal to imports
old_imports = '''from src.models import (
    Meeting,
    Task,
    Agent,
    Decision,
    Resource,
    TechRadarItem,
    CodePattern,
    TranscriptProcessRequest,
    TranscriptProcessResponse,
    AgentQueryRequest,
    AgentQueryResponse,
)'''

new_imports = '''from src.models import (
    Meeting,
    Task,
    Agent,
    Proposal,
    Decision,
    Resource,
    TechRadarItem,
    CodePattern,
    TranscriptProcessRequest,
    TranscriptProcessResponse,
    AgentQueryRequest,
    AgentQueryResponse,
)'''

content = content.replace(old_imports, new_imports)

# Add proposal endpoints before decisions endpoints
proposal_endpoints = '''

# Proposals endpoints
@app.get("/api/proposals", response_model=List[Proposal])
async def get_proposals():
    """Get all proposals."""
    try:
        container = db.get_container("proposals")
        items = list(container.read_all_items())
        return [Proposal(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/proposals/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: str):
    """Get proposal by ID."""
    try:
        container = db.get_container("proposals")
        item = container.read_item(item=proposal_id, partition_key=proposal_id)
        return Proposal(**item)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Proposal not found")


@app.post("/api/proposals", response_model=Proposal)
async def create_proposal(proposal: Proposal):
    """Create new proposal."""
    try:
        if not proposal.id:
            proposal.id = str(uuid.uuid4())
        proposal.created_at = datetime.utcnow()
        proposal.updated_at = datetime.utcnow()

        container = db.get_container("proposals")
        container.create_item(body=proposal.model_dump(mode='json'))
        return jsonable_encoder(proposal)
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/proposals/{proposal_id}", response_model=Proposal)
async def update_proposal(proposal_id: str, proposal: Proposal):
    """Update proposal (partial update)."""
    try:
        proposal.id = proposal_id
        proposal.updated_at = datetime.utcnow()

        container = db.get_container("proposals")
        container.upsert_item(body=proposal.model_dump(mode='json'))
        return jsonable_encoder(proposal)
    except Exception as e:
        logger.error(f"Error updating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """Delete proposal."""
    try:
        container = db.get_container("proposals")
        container.delete_item(item=proposal_id, partition_key=proposal_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Proposal not found")


'''

# Insert proposal endpoints before decisions endpoints
content = content.replace(
    '# Decisions endpoints',
    proposal_endpoints + '# Decisions endpoints'
)

# Add createFromProposal endpoint after create_decision
create_from_proposal_endpoint = '''


@app.post("/api/decisions/from-proposal", response_model=Decision)
async def create_decision_from_proposal(data: dict):
    """Create decision from approved proposal."""
    try:
        proposal_id = data.get("proposal_id")
        if not proposal_id:
            raise HTTPException(status_code=400, detail="proposal_id is required")

        # Get proposal
        proposals_container = db.get_container("proposals")
        try:
            proposal_item = proposals_container.read_item(item=proposal_id, partition_key=proposal_id)
            proposal = Proposal(**proposal_item)
        except Exception:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Create decision from proposal
        decision = Decision(
            id=str(uuid.uuid4()),
            title=data.get("title", proposal.title),
            description=data.get("description", proposal.description),
            category=data.get("category", "Governance"),
            decision_date=datetime.utcnow(),
            decision_maker=data.get("decision_maker", proposal.proposer),
            rationale=data.get("rationale", proposal.rationale),
            impact=data.get("impact", proposal.impact),
            proposal_id=proposal_id,
        )
        decision.created_at = datetime.utcnow()

        container = db.get_container("decisions")
        container.create_item(body=decision.model_dump(mode='json'))
        return jsonable_encoder(decision)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating decision from proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))'''

# Insert after create_decision endpoint
content = content.replace(
    '# Resources endpoints',
    create_from_proposal_endpoint + '\n\n\n# Resources endpoints'
)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added Proposal endpoints to main.py")
