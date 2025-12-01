# MSFT Agent Architecture Guide - Backend

FastAPI backend for the MSFT Agent Architecture Guide project management site.

## Tech Stack

- **Framework:** FastAPI
- **Database:** Azure Cosmos DB
- **AI:** Azure AI Foundry Model Router
- **Search:** Azure AI Search
- **Deployment:** Azure Container Apps

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your Azure credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `COSMOS_ENDPOINT` - Azure Cosmos DB endpoint
- `COSMOS_KEY` - Azure Cosmos DB key
- `AZURE_AI_FOUNDRY_ENDPOINT` - Azure AI Foundry endpoint
- `AZURE_AI_FOUNDRY_API_KEY` - Azure AI Foundry API key
- Other Azure service credentials

### 3. Run Locally

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

API will be available at: http://localhost:8000

API documentation: http://localhost:8000/docs

## API Endpoints

### Health Check
- `GET /health` - Health check

### Meetings
- `GET /api/meetings` - Get all meetings
- `GET /api/meetings/{id}` - Get meeting by ID
- `POST /api/meetings` - Create meeting
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting

### Tasks
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{id}` - Get task by ID
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Agents
- `GET /api/agents` - Get all agents
- `GET /api/agents/{id}` - Get agent by ID
- `POST /api/agents` - Create agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Decisions
- `GET /api/decisions` - Get all decisions
- `POST /api/decisions` - Create decision

### Resources
- `GET /api/resources` - Get all resources
- `POST /api/resources` - Create resource
- `DELETE /api/resources/{id}` - Delete resource

### Tech Radar
- `GET /api/tech-radar` - Get all tech radar items
- `POST /api/tech-radar` - Create tech radar item
- `PUT /api/tech-radar/{id}` - Update tech radar item

### Code Patterns
- `GET /api/code-patterns` - Get all code patterns
- `POST /api/code-patterns` - Create code pattern

### AI Features
- `POST /api/transcripts/process` - Process transcript (extract tasks/decisions)
- `POST /api/agent/query` - Query Fourth AI Guide

## Deployment to Azure

### Build Docker Image

```bash
cd backend
docker build -t agent-architecture-backend .
```

### Deploy to Azure Container Apps

```bash
# Create resource group
az group create --name rg-agent-architecture --location northeurope

# Create Azure Container Apps environment
az containerapp env create --name agent-architecture-env --resource-group rg-agent-architecture --location northeurope

# Deploy container
az containerapp create \
  --name agent-architecture-backend \
  --resource-group rg-agent-architecture \
  --environment agent-architecture-env \
  --image agent-architecture-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    COSMOS_ENDPOINT=$COSMOS_ENDPOINT \
    COSMOS_KEY=$COSMOS_KEY \
    AZURE_AI_FOUNDRY_ENDPOINT=$AZURE_AI_FOUNDRY_ENDPOINT \
    AZURE_AI_FOUNDRY_API_KEY=$AZURE_AI_FOUNDRY_API_KEY
```

## Database Initialization

The database and containers are automatically created on first run. The following Cosmos DB containers will be created:

- `meetings` - Meeting records
- `tasks` - Task records
- `agents` - Agent portfolio
- `decisions` - Governance decisions
- `resources` - Resource library
- `tech_radar_items` - Tech radar items
- `code_patterns` - Code patterns

## Development

### Run Tests

```bash
pytest
```

### Format Code

```bash
black src/
```

### Lint Code

```bash
pylint src/
```
# Backend deployment trigger - Mon, Dec  1, 2025 11:34:27 AM
