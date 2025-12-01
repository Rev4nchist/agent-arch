# MSFT Agent Architecture Guide

**Project Management site for Fourth's Microsoft Agent Ecosystem adoption**

## Overview

Comprehensive project management web application serving as the **single source of truth** for Fourth's AI Architect Team to track the Microsoft Agent Ecosystem implementation journey.

## Project Structure

```
MSFT-agent-architecture-guide/
├── frontend/               # Next.js 16 + Shadcn UI
│   ├── app/               # Next.js app directory
│   ├── components/        # React components
│   │   └── ui/           # Shadcn UI components
│   ├── lib/              # Utility functions
│   └── package.json
│
├── backend/               # FastAPI + Azure services
│   ├── src/
│   │   ├── main.py       # FastAPI application
│   │   ├── config.py     # Settings & environment
│   │   ├── database.py   # Cosmos DB client
│   │   ├── blob_service.py  # Azure Blob Storage
│   │   ├── ai_client.py  # Azure AI Foundry Model Router
│   │   ├── auth.py       # Shared access key auth
│   │   └── models.py     # Pydantic data models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docs/                 # Documentation
└── README.md            # This file
```

## Tech Stack

### Frontend
- **Framework:** Next.js 16 (TypeScript)
- **UI Library:** Shadcn CLI components
- **Styling:** Tailwind CSS
- **Deployment:** Azure Static Web Apps

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** Azure Cosmos DB
- **File Storage:** Azure Blob Storage (for transcripts, PDFs)
- **AI Services:** Azure AI Foundry Model Router
- **Search:** Azure AI Search
- **Auth:** Shared Access Key (MVP)
- **Deployment:** Azure Container Apps

## Critical Design Decisions

### 1. Azure Blob Storage (Not Cosmos DB Embedding)

**Problem:** Cosmos DB has a 2MB document limit. Meeting transcripts and PDFs exceed this.

**Solution:** Store files in Azure Blob Storage, metadata in Cosmos DB.

```python
# Resources stored as:
{
  "id": "uuid",
  "title": "AI Governance Framework",
  "type": "PDF",
  "blob_url": "https://storage.../file.pdf",  # ← Blob Storage URL
  "tags": ["governance", "policy"]
}
```

### 2. Shared Access Key Authentication (MVP)

**Rationale:** Entra ID setup takes 2-4 hours. For internal team of 6, shared key is faster.

**Implementation:**
```bash
# .env
API_ACCESS_KEY=your-shared-secret-key-change-in-production

# Frontend request
Authorization: Bearer {API_ACCESS_KEY}
```

**Post-MVP:** Upgrade to Entra ID with MSAL.

### 3. Simplified UI Components

**Tech Radar:** Grouped card grid (not visual quadrant chart)
**Tasks:** List + Simple Kanban (not Gantt chart)
**Agenda:** Markdown editor (not rich text WYSIWYG)

**Time Saved:** 5-8 hours

### 4. Transcript Chunking

**Problem:** Long meetings (1+ hours) can exceed 15k token limits.

**Solution:** Automatic chunking in `ai_client.py`:
- Transcripts >15k tokens split into 10k token chunks
- Each chunk processed separately
- Results deduplicated and merged

## Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Azure subscription with:
  - Cosmos DB account
  - Blob Storage account
  - AI Foundry Model Router access
  - AI Search service

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# Run locally
uvicorn src.main:app --reload --port 8000
```

API Docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run locally
npm run dev
```

Frontend: http://localhost:3000

## Key Features

### 1. Meetings Hub
- Session planner with pre-work checklists
- Attendee role management (RACI)
- Markdown agenda builder
- **Transcript upload panel** with AI extraction
- Auto-generate tasks and decisions from transcripts

### 2. Task Management
- Personal task list (My Tasks)
- List view (sortable by status, priority, due date)
- Simple Kanban board (Pending | In-Progress | Done)
- Dependencies tracking
- Auto-generated from meetings

### 3. Agent Portfolio
- Agent cards by tier (Individual | Department | Enterprise)
- Filter by status (Idea → Production)
- Agent request form
- Related tasks tracking

### 4. Governance Tracking
- 6-week framework timeline
- Policy document repository
- Decision log with rationale
- Compliance dashboard

### 5. Budget & Licensing
- License inventory (ChatGPT, Claude, Copilot, Azure OpenAI)
- Budget vs. actual tracking
- Optimization opportunities ($150K+ target)
- 2026 spend forecast

### 6. Resources Library
- Upload PDFs, documents, links
- Tag and categorize resources
- Search functionality
- Storage in Azure Blob Storage

### 7. Architecture & Build Lab
- **Tech Radar:** Grouped by category (Adopt, Trial, Assess, Hold)
- **Code Patterns:** Repository of approved patterns (Code-First vs. Low-Code)
- **Deployment Guides:** Step-by-step Azure deployment instructions

### 8. Fourth AI Guide (Built-in Agent)
- Query meeting transcripts
- Track tasks and responsibilities
- Agent status lookups
- Governance policy searches
- Budget queries

## API Endpoints

**Health:**
- `GET /health` - Health check

**Meetings:**
- `GET /api/meetings` - List all
- `POST /api/meetings` - Create
- `PUT /api/meetings/{id}` - Update
- `DELETE /api/meetings/{id}` - Delete

**Tasks:**
- `GET /api/tasks` - List all
- `POST /api/tasks` - Create
- `PUT /api/tasks/{id}` - Update

**Agents:**
- `GET /api/agents` - List all
- `POST /api/agents` - Create
- `PUT /api/agents/{id}` - Update

**AI Features:**
- `POST /api/transcripts/process` - Extract tasks/decisions from transcript
- `POST /api/agent/query` - Query Fourth AI Guide

(See [backend/README.md](backend/README.md) for complete API documentation)

## Deployment

### Backend to Azure Container Apps

```bash
cd backend

# Build Docker image
docker build -t agent-architecture-backend .

# Tag for Azure Container Registry
docker tag agent-architecture-backend your-acr.azurecr.io/agent-architecture-backend:latest

# Push to ACR
az acr login --name your-acr
docker push your-acr.azurecr.io/agent-architecture-backend:latest

# Deploy to Container Apps
az containerapp create \
  --name agent-architecture-backend \
  --resource-group rg-agent-architecture \
  --environment agent-architecture-env \
  --image your-acr.azurecr.io/agent-architecture-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    COSMOS_ENDPOINT=$COSMOS_ENDPOINT \
    COSMOS_KEY=$COSMOS_KEY \
    AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING \
    AZURE_AI_FOUNDRY_ENDPOINT=$AZURE_AI_FOUNDRY_ENDPOINT \
    AZURE_AI_FOUNDRY_API_KEY=$AZURE_AI_FOUNDRY_API_KEY \
    API_ACCESS_KEY=$API_ACCESS_KEY
```

### Frontend to Azure Static Web Apps

```bash
cd frontend

# Build for production
npm run build

# Deploy using Azure CLI
az staticwebapp create \
  --name agent-architecture-frontend \
  --resource-group rg-agent-architecture \
  --location northeurope

# Get deployment token and deploy
# (Or use GitHub Actions for CI/CD)
```

## Data Model

**Core Entities:**

| Entity | Collection | Key Fields |
|--------|-----------|------------|
| Meetings | `meetings` | title, date, type, facilitator, attendees, transcript |
| Tasks | `tasks` | title, status, priority, assigned_to, dependencies |
| Agents | `agents` | name, tier, status, owner, data_sources |
| Decisions | `decisions` | title, decision_maker, category, rationale |
| Resources | `resources` | title, type, blob_url, tags |
| Tech Radar | `tech_radar_items` | tool_name, category, recommendation |
| Code Patterns | `code_patterns` | title, pattern_type, code_snippet |

## Development Timeline

**Day 1:** Backend + Frontend foundation ✅
**Day 2:** Dashboard + Meetings Hub + Tasks Page
**Day 3:** Agents + Governance + Resources + Architecture Lab
**Day 4:** Fourth AI Guide + Data migration + Polish + Deploy

## Security Notes

**Current (MVP):**
- Shared API Access Key
- Internal team only (6 members)
- HTTPS in production

**Post-MVP Upgrades:**
- Entra ID integration (MSAL)
- Role-based access control (RBAC)
- Audit logging
- SOC2/GDPR compliance features

## Environment Variables

### Backend (.env)

```bash
# Azure Cosmos DB
COSMOS_ENDPOINT=https://...
COSMOS_KEY=...
COSMOS_DATABASE_NAME=agent-architecture-db

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=resources

# Azure AI Foundry Model Router
AZURE_AI_FOUNDRY_ENDPOINT=https://ai.azure.com/...
AZURE_AI_FOUNDRY_API_KEY=...
MODEL_ROUTER_DEPLOYMENT=model-router

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://...
AZURE_SEARCH_API_KEY=...

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend.azurestaticapps.net
API_ACCESS_KEY=your-shared-secret-key
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend.azurecontainerapps.io
NEXT_PUBLIC_API_KEY=your-shared-secret-key
```

## Support

**AI Architect Team:**
- David Hayes (AI Enablement Lead)
- Mark Beynon (Cloud Architecture)
- Boyan Asenov (Agent Development)
- Lucas (Agent Development)
- Dimitar Stoynev (Data Engineering)
- Ivan Georgiev (Development)

**Microsoft Partnership:**
- Julia Hilfrich (AI Business Process Specialist)
- Josh Rogers (Solution Engineer)
- Helen Foy (Purview Specialist)

## License

Internal Fourth project - Not for external distribution

---

**Version:** 1.0.0 (MVP)
**Last Updated:** 2025-11-20
**Status:** In Development (Day 1 Complete)
