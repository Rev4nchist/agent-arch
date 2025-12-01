# Azure Resources Creation Script for Agent Architecture Guide (PowerShell)
# Run this script to create all required Azure resources

$ErrorActionPreference = "Stop"

Write-Host "🚀 Creating Azure resources for Agent Architecture Guide..." -ForegroundColor Green
Write-Host ""

# Configuration
$RESOURCE_GROUP = "rg-agent-architecture"
$LOCATION = "northeurope"
$COSMOS_ACCOUNT = "agent-architecture-cosmos"
$STORAGE_ACCOUNT = "agentarchstorage"
$CONTAINER_NAME = "resources"

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
Write-Host "🔐 Checking Azure login status..." -ForegroundColor Cyan
try {
    az account show | Out-Null
    Write-Host "✅ Azure CLI authenticated" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure. Running 'az login'..." -ForegroundColor Red
    az login
}
Write-Host ""

# Create Resource Group
Write-Host "📦 Creating resource group: $RESOURCE_GROUP..." -ForegroundColor Cyan
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION `
  --output table

Write-Host "✅ Resource group created" -ForegroundColor Green
Write-Host ""

# Create Cosmos DB
Write-Host "🗄️  Creating Cosmos DB account: $COSMOS_ACCOUNT..." -ForegroundColor Cyan
Write-Host "   (This may take 3-5 minutes...)" -ForegroundColor Yellow
az cosmosdb create `
  --name $COSMOS_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --locations regionName=$LOCATION `
  --default-consistency-level Session `
  --enable-free-tier false `
  --output table

Write-Host "✅ Cosmos DB created" -ForegroundColor Green
Write-Host ""

# Get Cosmos DB details
Write-Host "📋 Getting Cosmos DB connection details..." -ForegroundColor Cyan
$COSMOS_ENDPOINT = az cosmosdb show `
  --name $COSMOS_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --query documentEndpoint `
  --output tsv

$COSMOS_KEY = az cosmosdb keys list `
  --name $COSMOS_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --query primaryMasterKey `
  --output tsv

Write-Host "✅ Cosmos DB Endpoint: $COSMOS_ENDPOINT" -ForegroundColor Green
Write-Host ""

# Create Storage Account
Write-Host "💾 Creating storage account: $STORAGE_ACCOUNT..." -ForegroundColor Cyan
az storage account create `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2 `
  --output table

Write-Host "✅ Storage account created" -ForegroundColor Green
Write-Host ""

# Get Storage connection string
Write-Host "📋 Getting storage connection string..." -ForegroundColor Cyan
$STORAGE_CONNECTION_STRING = az storage account show-connection-string `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --output tsv

Write-Host "✅ Storage connection string retrieved" -ForegroundColor Green
Write-Host ""

# Create blob container
Write-Host "📁 Creating blob container: $CONTAINER_NAME..." -ForegroundColor Cyan
az storage container create `
  --name $CONTAINER_NAME `
  --account-name $STORAGE_ACCOUNT `
  --public-access off `
  --output table

Write-Host "✅ Blob container created" -ForegroundColor Green
Write-Host ""

# Generate .env file
Write-Host "📝 Generating .env file..." -ForegroundColor Cyan

$envContent = @"
# Azure Cosmos DB
COSMOS_ENDPOINT=$COSMOS_ENDPOINT
COSMOS_KEY=$COSMOS_KEY
COSMOS_DATABASE_NAME=agent-architecture-db

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING
AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME

# Azure OpenAI (FILL IN YOUR VALUES FROM Agent-Framework-Test)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure AI Search (FILL IN YOUR VALUES FROM Agent-Framework-Test)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
AZURE_SEARCH_INDEX_NAME=transcripts

# Azure AI Foundry Model Router (FILL IN YOUR VALUES)
AZURE_AI_FOUNDRY_ENDPOINT=https://ai.azure.com/...
AZURE_AI_FOUNDRY_API_KEY=your-foundry-key
MODEL_ROUTER_DEPLOYMENT=model-router

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# Authentication (Shared Access Key)
API_ACCESS_KEY=dev-test-key-123
"@

$envPath = Join-Path $PSScriptRoot "..\backend\.env"
Set-Content -Path $envPath -Value $envContent -Encoding UTF8

Write-Host "✅ .env file created at: backend\.env" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "🎉 Azure resources created successfully!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""
Write-Host "📋 Created Resources:" -ForegroundColor Cyan
Write-Host "   • Resource Group: $RESOURCE_GROUP"
Write-Host "   • Cosmos DB: $COSMOS_ACCOUNT"
Write-Host "   • Storage Account: $STORAGE_ACCOUNT"
Write-Host "   • Blob Container: $CONTAINER_NAME"
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Edit backend\.env and fill in the remaining values:"
Write-Host "   - AZURE_OPENAI_* (copy from Agent-Framework-Test)"
Write-Host "   - AZURE_SEARCH_* (copy from Agent-Framework-Test)"
Write-Host "   - AZURE_AI_FOUNDRY_* (get from ai.azure.com)"
Write-Host ""
Write-Host "2. Install backend dependencies:"
Write-Host "   cd backend"
Write-Host "   python -m venv venv"
Write-Host "   venv\Scripts\activate"
Write-Host "   pip install -r requirements.txt"
Write-Host ""
Write-Host "3. Run backend locally:"
Write-Host "   uvicorn src.main:app --reload --port 8000"
Write-Host ""
Write-Host "4. Test health endpoint:"
Write-Host "   curl http://localhost:8000/health"
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
