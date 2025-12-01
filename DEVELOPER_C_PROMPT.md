# Developer C - Resource Library Track (Dual-Section Architecture)

## Your Mission
You are Developer C working on the **Resource Library Track** - implementing the **dual-section Resource Library** with Azure Cloud Asset Inventory and Educational Resource Library (Tasks 8-9). This is a MEDIUM-PRIORITY feature that provides infrastructure visibility and knowledge management.

## Project Context
- **Project:** Agent Architecture Guide (Microsoft Agent Ecosystem Portal)
- **Location:** `c:\agent-arch`
- **Your Role:** Lead developer for resource management features
- **Working in Parallel With:**
  - Developer A: AI Transcript Processing (Tasks 1-4)
  - Developer B: Microsoft SSO Authentication (Task 13)

## Task Master Integration

### Your Tasks (Both Independent - Can Work in Any Order)
```
Task #8: Azure Cloud Asset Inventory
  - 5 subtasks (backend + frontend)
  - Real-time Azure resource tracking via API

Task #9: Educational Resource Library
  - 8 subtasks (backend + frontend + preview system)
  - Document and link management with rich preview
```

### Getting Started
```bash
cd c:\agent-arch

# View your tasks
task-master show 8
task-master show 9

# Choose which to start with (recommendation: Task 8 first)
task-master set-status --id=8 --status=in-progress

# Task 8 has 5 subtasks (already generated)
# Task 9 has 8 subtasks (already generated)
```

### Tracking Your Progress
```bash
# Log progress regularly
task-master update-subtask --id=8.1 --prompt="Integrated Azure Resource Graph API, caching working"

# Mark subtasks done
task-master set-status --id=8.1 --status=done
```

## Comprehensive Technical Specifications

**PRIMARY REFERENCE DOCUMENT:**
`c:\agent-arch\Resource-Library-Enhancement-Proposal.md`

This 1000+ line proposal contains complete specifications for both sections. Read it carefully before starting!

## Section 1: Azure Cloud Asset Inventory (Task #8)

### Overview
Build real-time Azure resource tracking using Azure SDK APIs. Display live infrastructure with filtering, cost attribution, and drill-down capabilities.

### Backend Architecture (Task 8.1-8.3)

**Install Azure SDK Dependencies:**
```bash
cd backend
pip install azure-identity azure-mgmt-resource azure-mgmt-costmanagement azure-mgmt-monitor
```

**Create Azure Resource Module:**

File: `backend/src/azure_resources.py`
```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta
import os

class AzureResourceService:
    def __init__(self):
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        credential = DefaultAzureCredential()

        self.resource_client = ResourceManagementClient(credential, subscription_id)
        self.cost_client = CostManagementClient(credential)
        self.monitor_client = MonitorManagementClient(credential, subscription_id)

        # Cache
        self.resource_cache = {}
        self.resource_cache_expiry = None
        self.cost_cache = {}
        self.cost_cache_expiry = None

    def list_resources(self, force_refresh=False):
        """List all Azure resources with caching (5 min)"""
        if not force_refresh and self.resource_cache_expiry and datetime.utcnow() < self.resource_cache_expiry:
            return self.resource_cache

        resources = []
        for resource in self.resource_client.resources.list():
            resources.append({
                "id": resource.id,
                "name": resource.name,
                "type": resource.type,
                "location": resource.location,
                "resource_group": resource.id.split('/')[4],
                "tags": resource.tags or {},
                "properties": resource.properties
            })

        self.resource_cache = resources
        self.resource_cache_expiry = datetime.utcnow() + timedelta(minutes=5)

        return resources

    def get_resource_cost(self, resource_id):
        """Get current month cost for specific resource"""
        # Use Cost Management API
        # ... implementation
        pass

    def get_resource_metrics(self, resource_id):
        """Get metrics for specific resource (CPU, memory, requests, etc.)"""
        # Use Monitor API
        # ... implementation
        pass
```

**API Endpoints:**

File: `backend/src/routers/azure_resources.py`
```python
from fastapi import APIRouter, Query
from src.azure_resources import AzureResourceService

router = APIRouter(prefix="/api/azure", tags=["azure-resources"])
azure_service = AzureResourceService()

@router.get("/resources")
async def list_resources(
    type_filter: str = Query(None),
    region: str = Query(None),
    status: str = Query(None),
    force_refresh: bool = False
):
    """List all Azure resources with optional filtering"""
    resources = azure_service.list_resources(force_refresh=force_refresh)

    # Apply filters
    if type_filter:
        resources = [r for r in resources if type_filter in r["type"]]
    if region:
        resources = [r for r in resources if r["location"] == region]

    return resources

@router.get("/resources/{resource_id:path}")
async def get_resource(resource_id: str):
    """Get detailed resource information"""
    resources = azure_service.list_resources()
    resource = next((r for r in resources if r["id"] == resource_id), None)

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Enrich with cost and metrics
    resource["current_month_cost"] = azure_service.get_resource_cost(resource_id)
    resource["metrics"] = azure_service.get_resource_metrics(resource_id)

    return resource

@router.get("/resources/summary")
async def get_summary():
    """Get aggregation statistics"""
    resources = azure_service.list_resources()

    return {
        "total_resources": len(resources),
        "running_services": len([r for r in resources if "Running" in str(r.get("properties", {}))]),
        "regions": len(set(r["location"] for r in resources)),
        "resource_groups": len(set(r["resource_group"] for r in resources))
    }

@router.post("/resources/refresh")
async def refresh_cache():
    """Force refresh resource cache"""
    resources = azure_service.list_resources(force_refresh=True)
    return {"message": "Cache refreshed", "count": len(resources)}
```

### Frontend Components (Task 8.4-8.5)

**Main Page:**

File: `frontend/app/resources/inventory/page.tsx`
```typescript
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface AzureResource {
  id: string;
  name: string;
  type: string;
  location: string;
  resource_group: string;
  tags: Record<string, string>;
  current_month_cost?: number;
  status?: string;
}

export default function AzureInventoryPage() {
  const [resources, setResources] = useState<AzureResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ type: 'all', region: 'all' });

  useEffect(() => {
    loadResources();
  }, [filters]);

  async function loadResources() {
    const params = new URLSearchParams();
    if (filters.type !== 'all') params.set('type_filter', filters.type);
    if (filters.region !== 'all') params.set('region', filters.region);

    const response = await fetch(`/api/azure/resources?${params}`);
    const data = await response.json();
    setResources(data);
    setLoading(false);
  }

  async function handleRefresh() {
    setLoading(true);
    await fetch('/api/azure/resources/refresh', { method: 'POST' });
    loadResources();
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Azure Cloud Inventory</h1>
            <p className="text-gray-600">Real-time infrastructure tracking</p>
          </div>
          <Button onClick={handleRefresh}>Refresh</Button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {/* Total Resources, Running Services, Cost, Regions */}
        </div>

        {/* Filters */}
        <div className="mb-6 flex gap-4">
          {/* Type filter, Region filter */}
        </div>

        {/* Resource Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.map((resource) => (
            <Card key={resource.id}>
              <CardHeader>
                <CardTitle className="text-sm">{resource.name}</CardTitle>
                <p className="text-xs text-gray-600">{resource.type}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge>{resource.location}</Badge>
                    {resource.current_month_cost && (
                      <span className="text-sm font-semibold">
                        ${resource.current_month_cost.toFixed(2)}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500">
                    RG: {resource.resource_group}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Key Features to Implement

**Filtering System:**
- By resource type (AI Services, Data & Storage, Compute, Networking, Security)
- By region (North Europe, North America, etc.)
- By environment (via tags: Production, Non-Production, Sandbox)
- By cost tier (High >$1000, Medium $100-1000, Low <$100)

**Resource Detail Modal:**
- Full ARM JSON (collapsible)
- Cost trend chart (last 30 days)
- Related resources
- Quick actions: "View in Portal", "View Metrics", "View Logs"

**Summary Statistics:**
- Total resources
- Running services
- Current month cost
- Number of regions

## Section 2: Educational Resource Library (Task #9)

### Overview
Document and link management system with rich preview functionality. Support PDFs, Markdown, Office docs, and web links.

### Backend Architecture (Task 9.1-9.5)

**Install Dependencies:**
```bash
pip install pdf2image pillow python-magic beautifulsoup4 requests
```

**Resource Upload Endpoint:**

File: `backend/src/routers/resources.py`
```python
from fastapi import APIRouter, UploadFile, File, Form
from azure.storage.blob import BlobServiceClient
from pdf2image import convert_from_path
import uuid

router = APIRouter(prefix="/api/resources", tags=["resources"])

@router.post("/")
async def upload_resource(
    file: UploadFile = File(None),
    url: str = Form(None),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    tags: str = Form("[]")
):
    """Upload document or add web link"""

    resource_id = str(uuid.uuid4())

    if file:
        # Upload to Blob Storage
        blob_service = BlobServiceClient.from_connection_string(...)
        container = blob_service.get_container_client("resources")

        blob_name = f"{resource_id}/{file.filename}"
        blob_client = container.upload_blob(name=blob_name, data=file.file)
        blob_url = blob_client.url

        # Generate thumbnail for PDF
        if file.filename.endswith('.pdf'):
            thumbnail_url = await generate_pdf_thumbnail(file, resource_id)
        else:
            thumbnail_url = None

        resource_doc = {
            "id": resource_id,
            "type": "document",
            "title": title,
            "description": description,
            "category": category,
            "tags": json.loads(tags),
            "file_type": file.filename.split('.')[-1],
            "file_size_bytes": file.size,
            "blob_url": blob_url,
            "thumbnail_url": thumbnail_url,
            "uploaded_by": "system",  # TODO: Use authenticated user
            "uploaded_at": datetime.utcnow().isoformat(),
            "view_count": 0
        }

    elif url:
        # Fetch OpenGraph metadata
        og_metadata = await fetch_og_metadata(url)

        resource_doc = {
            "id": resource_id,
            "type": "link",
            "title": title or og_metadata.get("title"),
            "description": description or og_metadata.get("description"),
            "category": category,
            "tags": json.loads(tags),
            "url": url,
            "og_image": og_metadata.get("image"),
            "uploaded_by": "system",
            "uploaded_at": datetime.utcnow().isoformat(),
            "view_count": 0
        }

    # Store in Cosmos DB
    resources_container.create_item(resource_doc)

    return resource_doc

async def generate_pdf_thumbnail(file, resource_id):
    """Generate thumbnail from first page of PDF"""
    # Save file temporarily
    temp_path = f"/tmp/{resource_id}.pdf"
    with open(temp_path, 'wb') as f:
        f.write(await file.read())

    # Convert first page to image
    images = convert_from_path(temp_path, first_page=1, last_page=1)
    thumbnail = images[0].resize((300, 400))

    # Upload thumbnail to Blob Storage
    thumbnail_path = f"/tmp/{resource_id}_thumb.png"
    thumbnail.save(thumbnail_path)

    blob_service = BlobServiceClient.from_connection_string(...)
    container = blob_service.get_container_client("resources")
    blob_client = container.upload_blob(
        name=f"{resource_id}/thumbnail.png",
        data=open(thumbnail_path, 'rb')
    )

    return blob_client.url

async def fetch_og_metadata(url):
    """Fetch OpenGraph metadata from URL"""
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')

    metadata = {
        'title': soup.find('meta', property='og:title'),
        'description': soup.find('meta', property='og:description'),
        'image': soup.find('meta', property='og:image')
    }

    return {k: v['content'] if v else None for k, v in metadata.items()}
```

**Search and Filter Endpoints:**
```python
@router.get("/")
async def list_resources(
    category: str = Query(None),
    tags: str = Query(None),
    search: str = Query(None),
    type: str = Query(None)
):
    """List resources with filtering"""
    query = "SELECT * FROM c WHERE 1=1"
    parameters = []

    if category:
        query += " AND c.category = @category"
        parameters.append({"name": "@category", "value": category})

    if search:
        query += " AND (CONTAINS(c.title, @search) OR CONTAINS(c.description, @search))"
        parameters.append({"name": "@search", "value": search})

    resources = list(resources_container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))

    return resources

@router.get("/{resource_id}/preview")
async def get_preview(resource_id: str):
    """Get preview data for resource"""
    resource = resources_container.read_item(resource_id, resource_id)

    if resource["type"] == "document" and resource["file_type"] == "pdf":
        # Extract first 500 characters of text
        preview_text = await extract_pdf_text_preview(resource["blob_url"])
        return {"preview_text": preview_text, "thumbnail_url": resource["thumbnail_url"]}

    elif resource["type"] == "link":
        return {"og_metadata": resource.get("og_image")}

@router.post("/{resource_id}/view")
async def increment_view_count(resource_id: str):
    """Increment view count when resource is accessed"""
    resource = resources_container.read_item(resource_id, resource_id)
    resource["view_count"] += 1
    resource["last_accessed"] = datetime.utcnow().isoformat()
    resources_container.upsert_item(resource)
    return {"view_count": resource["view_count"]}
```

### Frontend Components (Task 9.6-9.8)

**Main Page:**

File: `frontend/app/resources/library/page.tsx`
```typescript
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent } from '@/components/ui/dialog';

interface Resource {
  id: string;
  type: 'document' | 'link';
  title: string;
  description: string;
  category: string;
  tags: string[];
  thumbnail_url?: string;
  url?: string;
  blob_url?: string;
  view_count: number;
}

export default function ResourceLibraryPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  async function handlePreview(resource: Resource) {
    setSelectedResource(resource);
    setPreviewOpen(true);

    // Increment view count
    await fetch(`/api/resources/${resource.id}/view`, { method: 'POST' });
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Educational Resource Library</h1>

        {/* Search and Filters */}
        <div className="mb-6 flex gap-4">
          {/* Search bar, Category filter, Tag filter */}
        </div>

        {/* Resource Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {resources.map((resource) => (
            <Card key={resource.id} className="cursor-pointer hover:shadow-lg">
              <CardContent className="p-4" onClick={() => handlePreview(resource)}>
                {resource.thumbnail_url && (
                  <img src={resource.thumbnail_url} alt={resource.title} className="w-full h-48 object-cover rounded mb-3" />
                )}
                <h3 className="font-semibold mb-2">{resource.title}</h3>
                <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                  {resource.description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {resource.tags.map(tag => (
                    <Badge key={tag} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Preview Modal */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-w-4xl h-[80vh]">
          {selectedResource && (
            <div className="grid grid-cols-[2fr_1fr] gap-4 h-full">
              <div className="overflow-auto">
                {/* Document/link preview */}
              </div>
              <div>
                {/* Metadata panel */}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

## Tab Navigation Between Sections

**Unified Resource Library Page:**

File: `frontend/app/resources/page.tsx`
```typescript
'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AzureInventoryPage from './inventory/page';
import ResourceLibraryPage from './library/page';

export default function ResourcesPage() {
  return (
    <Tabs defaultValue="library" className="w-full">
      <TabsList className="mb-6">
        <TabsTrigger value="library">Educational Library</TabsTrigger>
        <TabsTrigger value="inventory">Azure Cloud Inventory</TabsTrigger>
      </TabsList>

      <TabsContent value="library">
        <ResourceLibraryPage />
      </TabsContent>

      <TabsContent value="inventory">
        <AzureInventoryPage />
      </TabsContent>
    </Tabs>
  );
}
```

## Environment Variables

```bash
# Backend .env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_RESOURCES_CONTAINER=resources
```

## Success Criteria

✅ **Task 8 Complete When:**
- Azure resources displayed in real-time
- Filtering works (type, region, status)
- Summary statistics calculated
- Resource detail modal functional
- Cost data displayed per resource

✅ **Task 9 Complete When:**
- Documents upload to Blob Storage
- PDF thumbnails generated
- Web links with OpenGraph metadata
- Preview modal shows 80% of content
- Search and filtering works
- Categories and tags functional
- View count tracking working

## Estimated Timeline

- **Task 8:** 10-14 hours (Azure Inventory)
- **Task 9:** 14-18 hours (Educational Library)

**Total: 24-32 hours (approximately 4-5 days of full-time work)**

## Coordination

**With Developers A & B:**
- After SSO complete: Add `uploaded_by` user context
- Resources may link to meetings (after transcript processing)
- Independent otherwise

## Key Resources

**Primary Reference:**
`c:\agent-arch\Resource-Library-Enhancement-Proposal.md` (READ THIS FIRST!)

**Good luck building the resource management system! 📚**
