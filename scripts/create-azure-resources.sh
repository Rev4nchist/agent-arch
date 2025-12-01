#!/bin/bash

# Azure Resources Creation Script for Agent Architecture Guide
# Run this script to create all required Azure resources

set -e  # Exit on error

echo "🚀 Creating Azure resources for Agent Architecture Guide..."
echo ""

# Configuration
RESOURCE_GROUP="rg-agent-architecture"
LOCATION="northeurope"
COSMOS_ACCOUNT="agent-architecture-cosmos"
STORAGE_ACCOUNT="agentarchstorage"
CONTAINER_NAME="resources"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Running 'az login'..."
    az login
fi

echo "✅ Azure CLI authenticated"
echo ""

# Create Resource Group
echo "📦 Creating resource group: $RESOURCE_GROUP..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output table

echo "✅ Resource group created"
echo ""

# Create Cosmos DB
echo "🗄️  Creating Cosmos DB account: $COSMOS_ACCOUNT..."
echo "   (This may take 3-5 minutes...)"
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$LOCATION \
  --default-consistency-level Session \
  --enable-free-tier false \
  --output table

echo "✅ Cosmos DB created"
echo ""

# Get Cosmos DB details
echo "📋 Getting Cosmos DB connection details..."
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint \
  --output tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey \
  --output tsv)

echo "✅ Cosmos DB Endpoint: $COSMOS_ENDPOINT"
echo ""

# Create Storage Account
echo "💾 Creating storage account: $STORAGE_ACCOUNT..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2 \
  --output table

echo "✅ Storage account created"
echo ""

# Get Storage connection string
echo "📋 Getting storage connection string..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --output tsv)

echo "✅ Storage connection string retrieved"
echo ""

# Create blob container
echo "📁 Creating blob container: $CONTAINER_NAME..."
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --public-access off \
  --output table

echo "✅ Blob container created"
echo ""

# Generate .env file
echo "📝 Generating .env file..."

cat > ../backend/.env << EOF
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
EOF

echo "✅ .env file created at: ../backend/.env"
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════"
echo "🎉 Azure resources created successfully!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Created Resources:"
echo "   • Resource Group: $RESOURCE_GROUP"
echo "   • Cosmos DB: $COSMOS_ACCOUNT"
echo "   • Storage Account: $STORAGE_ACCOUNT"
echo "   • Blob Container: $CONTAINER_NAME"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit backend/.env and fill in the remaining values:"
echo "   - AZURE_OPENAI_* (copy from Agent-Framework-Test)"
echo "   - AZURE_SEARCH_* (copy from Agent-Framework-Test)"
echo "   - AZURE_AI_FOUNDRY_* (get from ai.azure.com)"
echo ""
echo "2. Install backend dependencies:"
echo "   cd ../backend"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Run backend locally:"
echo "   uvicorn src.main:app --reload --port 8000"
echo ""
echo "4. Test health endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
echo "════════════════════════════════════════════════════════════════"
