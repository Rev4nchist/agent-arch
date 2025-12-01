# Deployment Guide - Azure Resources Setup

## Prerequisites

- Azure CLI installed and logged in: `az login`
- Azure subscription active
- Python 3.11+ installed
- Node.js 18+ installed

---

## Step 1: Create Azure Cosmos DB

### Option A: Azure CLI (Fastest)

```bash
# Set variables
RESOURCE_GROUP="rg-agent-architecture"
LOCATION="northeurope"
COSMOS_ACCOUNT="agent-architecture-cosmos"

# Create resource group (if not exists)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Cosmos DB account (NoSQL API)
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$LOCATION \
  --default-consistency-level Session \
  --enable-free-tier false

# Get connection details
az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint \
  --output tsv

# Get primary key
az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey \
  --output tsv
```

**Copy these values:**
- `COSMOS_ENDPOINT`: (from first command output)
- `COSMOS_KEY`: (from second command output)

### Option B: Azure Portal

1. Go to: https://portal.azure.com
2. Click "Create a resource" → "Azure Cosmos DB"
3. Select **"Azure Cosmos DB for NoSQL"**
4. Fill in:
   - Resource Group: `rg-agent-architecture` (create new)
   - Account Name: `agent-architecture-cosmos`
   - Location: `North Europe`
   - Capacity mode: `Provisioned throughput`
5. Click "Review + Create" → "Create"
6. After deployment, go to resource → **"Keys"** section
7. Copy:
   - URI → `COSMOS_ENDPOINT`
   - PRIMARY KEY → `COSMOS_KEY`

**Time:** ~5 minutes

---

## Step 2: Create Azure Blob Storage

### Option A: Azure CLI (Fastest)

```bash
# Set variables
STORAGE_ACCOUNT="agentarchstorage"  # Must be lowercase, no hyphens
CONTAINER_NAME="resources"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --output tsv

# Create blob container
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --public-access off
```

**Copy this value:**
- `AZURE_STORAGE_CONNECTION_STRING`: (from connection string command)

### Option B: Azure Portal

1. Go to: https://portal.azure.com
2. Click "Create a resource" → "Storage account"
3. Fill in:
   - Resource Group: `rg-agent-architecture`
   - Storage account name: `agentarchstorage`
   - Location: `North Europe`
   - Performance: `Standard`
   - Redundancy: `Locally-redundant storage (LRS)`
4. Click "Review + Create" → "Create"
5. After deployment, go to resource → **"Access keys"** section
6. Click "Show" next to `key1`
7. Copy **"Connection string"** → `AZURE_STORAGE_CONNECTION_STRING`
8. Go to **"Containers"** → Click "+ Container"
9. Name: `resources`, Private access level
10. Click "Create"

**Time:** ~3 minutes

---

## Step 3: Get Azure AI Foundry Model Router API Key

### Option A: Azure AI Foundry Portal

1. Go to: https://ai.azure.com
2. Navigate to your project: https://ai.azure.com/nextgen/r/yb7SAsShQ-mSLZo42Wb4Pg
3. Click **"Deployments"** in left sidebar
4. Find **"model-router"** (or create if not exists):
   - Click "+ Create deployment"
   - Select "Model Router" (2025-11-18 version)
   - Deployment name: `model-router`
   - Click "Deploy"
5. Click on the deployment → **"Keys and Endpoint"**
6. Copy:
   - `Endpoint` → `AZURE_AI_FOUNDRY_ENDPOINT`
   - `Key` → `AZURE_AI_FOUNDRY_API_KEY`

### Option B: Use Existing Azure OpenAI (Fallback)

If Model Router is not available, you can temporarily use your existing Azure OpenAI:

```bash
# From your Agent-Framework-Test project
AZURE_AI_FOUNDRY_ENDPOINT="<your-azure-openai-endpoint>"
AZURE_AI_FOUNDRY_API_KEY="<your-azure-openai-key>"
MODEL_ROUTER_DEPLOYMENT="gpt-4o"  # Use your existing deployment
```

**Time:** ~2 minutes

---

## Step 4: Reuse Existing Azure OpenAI & Search

From your **Agent-Framework-Test** project, copy these values:

```bash
# Azure OpenAI (from Agent-Framework-Test backend/.env)
AZURE_OPENAI_ENDPOINT="<your-existing-endpoint>"
AZURE_OPENAI_API_KEY="<your-existing-key>"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT="text-embedding-ada-002"

# Azure AI Search (from Agent-Framework-Test backend/.env)
AZURE_SEARCH_ENDPOINT="<your-existing-endpoint>"
AZURE_SEARCH_API_KEY="<your-existing-key>"
AZURE_SEARCH_INDEX_NAME="transcripts"  # New index for this project
```

---

## Step 5: Create Local .env File

```bash
cd backend

# Create .env from template
cp .env.example .env

# Edit .env with your values (use your favorite editor)
# On Windows:
notepad .env

# On Mac/Linux:
nano .env
```

**Fill in all values from Steps 1-4:**

```bash
# Azure Cosmos DB (Step 1)
COSMOS_ENDPOINT=https://agent-architecture-cosmos.documents.azure.com:443/
COSMOS_KEY=<your-cosmos-primary-key>
COSMOS_DATABASE_NAME=agent-architecture-db

# Azure Blob Storage (Step 2)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=agentarchstorage;AccountKey=...
AZURE_STORAGE_CONTAINER_NAME=resources

# Azure OpenAI (Step 4 - Reuse)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure AI Search (Step 4 - Reuse)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=<your-key>
AZURE_SEARCH_INDEX_NAME=transcripts

# Azure AI Foundry Model Router (Step 3)
AZURE_AI_FOUNDRY_ENDPOINT=https://ai.azure.com/...
AZURE_AI_FOUNDRY_API_KEY=<your-key>
MODEL_ROUTER_DEPLOYMENT=model-router

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# Authentication (Shared Access Key)
API_ACCESS_KEY=dev-test-key-123
```

---

## Step 6: Install Backend Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Time:** ~2 minutes

---

## Step 7: Run Backend Locally

```bash
# Make sure you're in the backend directory with venv activated
cd backend

# Run the server
uvicorn src.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database 'agent-architecture-db' ready
INFO:     Container 'meetings' ready
INFO:     Container 'tasks' ready
INFO:     Container 'agents' ready
INFO:     Container 'decisions' ready
INFO:     Container 'resources' ready
INFO:     Container 'tech_radar_items' ready
INFO:     Container 'code_patterns' ready
INFO:     Application startup complete.
```

---

## Step 8: Test API Endpoints

### Health Check

Open browser: http://localhost:8000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Interactive API Docs

Open browser: http://localhost:8000/docs

**Test endpoints:**
1. Click "GET /api/meetings" → "Try it out" → "Execute"
2. Should return: `[]` (empty array - no meetings yet)

### Test Authentication

```bash
# Try without API key (should fail)
curl http://localhost:8000/api/meetings

# Expected: 401 Unauthorized

# Try with API key (should succeed)
curl -H "Authorization: Bearer dev-test-key-123" http://localhost:8000/api/meetings

# Expected: []
```

### Test Cosmos DB Connection

```bash
# Create a test meeting
curl -X POST http://localhost:8000/api/meetings \
  -H "Authorization: Bearer dev-test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "title": "Test Meeting",
    "date": "2025-11-20T10:00:00Z",
    "type": "Governance",
    "facilitator": "David Hayes",
    "attendees": ["David Hayes", "Mark Beynon"],
    "status": "Scheduled"
  }'

# Verify it was created
curl -H "Authorization: Bearer dev-test-key-123" http://localhost:8000/api/meetings

# Should return the meeting in an array
```

### Test Blob Storage Connection

```bash
# Create a test resource (will store metadata, file URL would be from blob)
curl -X POST http://localhost:8000/api/resources \
  -H "Authorization: Bearer dev-test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-resource-1",
    "title": "Test Document",
    "type": "PDF",
    "category": "Governance",
    "tags": ["test"],
    "file_url": "https://example.com/test.pdf",
    "uploaded_by": "David Hayes"
  }'

# Verify
curl -H "Authorization: Bearer dev-test-key-123" http://localhost:8000/api/resources
```

---

## Step 9: Test AI Features (Optional)

### Test Transcript Processing

```bash
curl -X POST http://localhost:8000/api/transcripts/process \
  -H "Authorization: Bearer dev-test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_text": "Meeting notes: David will schedule the governance session by Nov 25. Mark approved the three-tier agent framework. Denis agreed to lead the security review.",
    "meeting_id": "test-1"
  }'

# Should return extracted action items and decisions
```

### Test Fourth AI Guide Query

```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Authorization: Bearer dev-test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What meetings are scheduled?",
    "context": "Test Meeting is scheduled for Nov 20"
  }'

# Should return AI-generated response
```

---

## Troubleshooting

### Issue: "Database initialization error"

**Cause:** Invalid Cosmos DB credentials

**Fix:**
1. Verify `COSMOS_ENDPOINT` and `COSMOS_KEY` in `.env`
2. Check Cosmos DB account is running in Azure Portal

### Issue: "Blob Service initialization failed"

**Cause:** Invalid Blob Storage connection string

**Fix:**
1. Verify `AZURE_STORAGE_CONNECTION_STRING` in `.env`
2. Ensure storage account exists in Azure Portal

### Issue: "AI Foundry endpoint not reachable"

**Cause:** Invalid Model Router endpoint or key

**Fix:**
1. Verify `AZURE_AI_FOUNDRY_ENDPOINT` and `AZURE_AI_FOUNDRY_API_KEY`
2. Alternatively, use Azure OpenAI endpoint as fallback

### Issue: "Module not found" errors

**Cause:** Missing dependencies

**Fix:**
```bash
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Fix:**
```bash
# Use different port
uvicorn src.main:app --reload --port 8001
```

---

## Next Steps After Local Testing

Once local testing is successful:

1. ✅ Backend working locally
2. ✅ All Azure connections verified
3. ✅ API endpoints responding
4. → **Proceed to frontend development** (Day 2)
5. → **Deploy to Azure Container Apps** (Day 4)

---

## Quick Command Reference

```bash
# Start backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000

# Test health
curl http://localhost:8000/health

# Test with auth
curl -H "Authorization: Bearer dev-test-key-123" http://localhost:8000/api/meetings

# View API docs
open http://localhost:8000/docs
```

---

**Estimated Total Time:** 15-20 minutes
**Status:** Ready for Day 2 (Frontend Development)
