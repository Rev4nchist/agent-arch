# Resource Library Enhancement Proposal
## Dual-Section Architecture for AI Portal

**Date:** November 24, 2025
**Project:** Agent Architecture Guide (C:\agent-arch)
**Purpose:** Expand Resource Library into comprehensive asset tracking and knowledge management system
**Stakeholders:** Mark Beynon, David Hayes, Boyan, Dimitar, Lucas, Ivan

---

## Executive Summary

The Resource Library section of Fourth's AI Portal will be split into two distinct but complementary sections:

1. **Azure Cloud Asset Inventory** - Live view of deployed Azure resources via API integration
2. **Educational Resource Library** - Curated knowledge base with preview functionality

Both sections serve the AI Architect Team's need for centralized visibility into Fourth's AI platform resources—both technical infrastructure and educational materials.

---

## Section 1: Azure Cloud Asset Inventory

### Overview

**Mark's Original Concept:**
> "Resource Library could be a place to pull information directly from Azure, such as a cloud assets inventory, using API calls to display resources from the subscription."

This section provides real-time visibility into Fourth's Azure AI Landing Zone infrastructure, complementing the Budget & Licensing page's cost tracking with detailed resource-level information.

### Key Features

#### 1.1 Resource Discovery & Display

**API Integration:**
- **Azure Resource Graph API** - Query all resources across subscriptions
- **Azure Resource Manager (ARM) API** - Detailed resource properties
- **Azure Cost Management API** - Per-resource cost attribution

**Resource Types to Display:**
- **AI Services:**
  - Azure AI Foundry (hub/project instances)
  - Azure OpenAI Service (deployments, models)
  - Azure Cognitive Services (endpoints)
  - Azure AI Search (indexes, skillsets)

- **Data & Storage:**
  - Cosmos DB (databases, collections)
  - Azure Blob Storage (containers, capacity)
  - Azure SQL Database (if used)

- **Compute & Networking:**
  - App Services (agent UIs, custom apps)
  - Container Apps (if deployed)
  - Virtual Networks (VNets, subnets)
  - Private Endpoints (security architecture)

- **Governance & Security:**
  - Key Vaults (credential management)
  - Log Analytics Workspaces (monitoring)
  - Application Insights (observability)
  - Managed Identities (service principals)

#### 1.2 Information Architecture

**Resource Card Design:**

Each resource displays:
- **Resource Name** (e.g., "fourth-ai-foundry-prod")
- **Type** (e.g., "Azure AI Foundry Hub")
- **Status** (Running, Stopped, Provisioning, Failed)
- **Location/Region** (North Europe, North America)
- **Resource Group** (logical grouping)
- **Tags** (Environment: Production, Department: AI-Architects, Owner: Mark)
- **Current Month Cost** (from Cost Management API)
- **Last Modified** (deployment/update timestamp)
- **Quick Actions** (View in Portal, View Metrics, View Logs)

**Example Card:**

```
┌─────────────────────────────────────────────────┐
│ 🏭 fourth-ai-foundry-prod                       │
│ Azure AI Foundry Hub                            │
│                                                 │
│ Status: ● Running    Region: North Europe      │
│ Resource Group: rg-ai-landing-zone-prod        │
│ Cost (Nov): $1,245.32                          │
│                                                 │
│ Tags: env:prod | dept:ai-architects            │
│ Last Updated: Nov 22, 2025 14:23 UTC          │
│                                                 │
│ [View in Portal] [Metrics] [Logs]             │
└─────────────────────────────────────────────────┘
```

#### 1.3 Filtering & Search

**Filter Options:**
- **By Type:** AI Services | Data & Storage | Compute | Networking | Security
- **By Region:** North Europe | North America | Other
- **By Environment:** Production | Non-Production | Sandbox
- **By Status:** Running | Stopped | Provisioning | Failed
- **By Cost:** High (>$1000/mo) | Medium ($100-$1000) | Low (<$100)

**Search:**
- Search by resource name
- Search by tags (e.g., "owner:mark" or "project:landing-zone")
- Search by resource group

#### 1.4 Aggregation Views

**Summary Statistics (Top of Page):**

```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Total Resources  │ │ Running Services │ │ Current Month    │ │ Regions          │
│      42          │ │      38          │ │   $8,234.50      │ │       2          │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

**Resource Breakdown by Type (Chart):**
- AI Services: 12 resources, $4,200/mo
- Data & Storage: 8 resources, $1,450/mo
- Compute: 10 resources, $1,800/mo
- Networking: 7 resources, $450/mo
- Security & Governance: 5 resources, $334.50/mo

#### 1.5 Drilldown Capabilities

**Click on Resource Card → Detail View Shows:**
- Full ARM resource JSON (collapsible, for technical users)
- Configuration details (SKU, pricing tier, capacity)
- Historical cost trend (last 30 days)
- Related resources (e.g., Foundry → connected AI Search, Key Vault)
- Recent activity logs (deployments, configuration changes)
- Metrics (if applicable): requests/sec, storage used, CPU/memory
- Alert history (if monitoring enabled)

**Integration with Azure Portal:**
- "View in Azure Portal" button opens resource in Azure Portal
- "View Metrics" opens Azure Monitor for that resource
- "View Logs" opens Log Analytics queries for that resource

#### 1.6 Cost Attribution

**Per-Resource Cost Tracking:**
- Pull from Azure Cost Management API
- Show current month spend
- Compare to budget (if budgets configured in Azure)
- Display cost trends (increasing/decreasing)

**Integration with Budget Page:**
- Budget page shows service-level aggregations (Azure OpenAI total spend)
- Asset Inventory shows resource-level detail (specific OpenAI deployment spend)
- Clicking on service in Budget page filters Asset Inventory to that service type

### Technical Implementation

#### Backend Architecture

**FastAPI Endpoints:**

```python
# Resource inventory endpoints
GET  /api/azure/resources              # List all resources
GET  /api/azure/resources/{id}         # Get resource details
GET  /api/azure/resources/summary      # Get aggregation stats
GET  /api/azure/resources/cost/{id}    # Get resource cost history
GET  /api/azure/resources/metrics/{id} # Get resource metrics

# Cache refresh
POST /api/azure/resources/refresh      # Force cache refresh
```

**Azure SDK Integration:**

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.monitor import MonitorManagementClient

# Initialize clients
credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, subscription_id)
cost_client = CostManagementClient(credential)
monitor_client = MonitorManagementClient(credential, subscription_id)

# Query resources
resources = resource_client.resources.list()

# Query cost for resource
scope = f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}/providers/{resource_id}"
cost_data = cost_client.query.usage(scope, parameters)
```

**Caching Strategy:**
- Cache resource list for 5 minutes (resources don't change frequently)
- Cache cost data for 1 hour (cost data updated hourly by Azure)
- Cache metrics for 1 minute (near real-time for monitoring)
- Provide manual refresh button for immediate updates

**Authentication:**
- Use **Managed Identity** when deployed in Azure
- Use **Service Principal** for local development
- Requires **Reader** role on subscription or resource groups
- Requires **Cost Management Reader** role for cost data

#### Frontend Components

**React Components:**

```typescript
// Main inventory page
/resources/inventory/page.tsx

// Components
components/azure/
  ├── ResourceCard.tsx           // Individual resource card
  ├── ResourceGrid.tsx           // Grid layout for cards
  ├── ResourceFilters.tsx        // Filter sidebar
  ├── ResourceSummary.tsx        // Stat cards at top
  ├── ResourceDetail.tsx         // Detail dialog/page
  └── ResourceCostChart.tsx      // Cost trend chart
```

**State Management:**

```typescript
interface AzureResource {
  id: string;
  name: string;
  type: string;
  location: string;
  resourceGroup: string;
  tags: Record<string, string>;
  status: 'Running' | 'Stopped' | 'Provisioning' | 'Failed';
  currentMonthCost: number;
  lastModified: string;
  properties: Record<string, any>;
}

// Fetch and filter logic
const [resources, setResources] = useState<AzureResource[]>([]);
const [filters, setFilters] = useState({ type: 'all', region: 'all', status: 'all' });
const [searchTerm, setSearchTerm] = useState('');

// Apply filters
const filteredResources = resources.filter(r =>
  matchesTypeFilter(r, filters.type) &&
  matchesRegionFilter(r, filters.region) &&
  matchesStatusFilter(r, filters.status) &&
  matchesSearch(r, searchTerm)
);
```

### User Workflows

**Scenario 1: Mark Checks Landing Zone Resources**
1. Navigate to Resources → Azure Inventory
2. See summary: 42 total resources, 38 running, $8,234 spent
3. Filter by "AI Services" type
4. View Azure AI Foundry hub, see it's running in North Europe, $1,245 cost
5. Click "View Metrics" to check usage patterns
6. Identify underutilized resources for cost optimization

**Scenario 2: David Prepares Executive Dashboard**
1. Navigate to Resources → Azure Inventory
2. Export resource summary statistics
3. Pull into AI Portal dashboard for Carly
4. Show executive-friendly view: "We have 42 Azure resources deployed across 2 regions"

**Scenario 3: Boyan Debugs Agent Deployment**
1. Agent fails to connect to Azure AI Search
2. Navigate to Resources → Azure Inventory
3. Search for "search" to find AI Search resource
4. Click on resource card, view status (Running) and location (North Europe)
5. Click "View Logs" to check for errors
6. Identify private endpoint configuration issue

**Scenario 4: Team Validates Microsoft Architecture Proposal**
1. During Microsoft working session, question about deployed resources
2. Pull up Azure Inventory on screen
3. Show: "We currently have 1 Foundry hub, 3 AI Search indexes, 2 Cosmos DBs"
4. Validate architecture aligns with Microsoft's recommended landing zone pattern

---

## Section 2: Educational Resource Library with Preview

### Overview

This section serves as a curated knowledge repository for the AI Architect Team, housing Microsoft documentation, research papers, architecture diagrams, and web links—with rich preview functionality to enable quick understanding without navigation.

### Key Features

#### 2.1 Resource Types

**Document Resources:**
- **PDFs:** Architecture diagrams, Microsoft guides, research papers
- **Markdown Files:** Internal documentation, ADRs, meeting notes
- **Word/PowerPoint:** Meeting briefs, presentations (David's executive PDFs)
- **Excel/CSV:** Data exports, cost analyses, planning spreadsheets

**Web Link Resources:**
- **Microsoft Learn Articles** (e.g., Azure AI Foundry docs)
- **Blog Posts** (Microsoft Tech Community, Fourth internal blogs)
- **GitHub Repositories** (Microsoft Agent Framework, sample code)
- **Video Tutorials** (Microsoft Ignite sessions, training videos)
- **External Research** (ArXiv papers, industry reports)

**Resource Metadata:**
- Title
- Description (auto-generated or manual)
- Category (Azure AI Foundry, Agent Framework, Governance, Licensing, Architecture, Security, etc.)
- Tags (multiple: "landing-zone", "fabric", "identity", "cost-management")
- Uploaded By / Added By
- Upload/Add Date
- Last Accessed (track usage)
- File Size (for documents)
- File Type / Link Type

#### 2.2 Preview Functionality (No-Navigation Design)

**For Document Resources:**

**PDF Preview:**
- Display first page as thumbnail (300x400px)
- On hover or click: Expand to show first 3 pages in modal
- Extract text preview (first 500 characters)
- Show file size, page count, upload date
- Download button + "Open Full Document" button

**Example PDF Card:**

```
┌─────────────────────────────────────────────────┐
│ 📄 Enterprise Landing Zone Architecture        │
│ Microsoft Learn                                 │
│                                                 │
│ [PDF Thumbnail - First Page Preview]          │
│                                                 │
│ "This document provides guidance on Azure     │
│  landing zones for enterprise AI workloads..." │
│                                                 │
│ 📊 12 pages | 2.4 MB | Added Nov 18, 2025     │
│ Tags: landing-zone, architecture, security     │
│                                                 │
│ [Preview] [Download] [Open Full Doc]          │
└─────────────────────────────────────────────────┘
```

**Markdown/Text Preview:**
- Extract first 500 characters with formatting preserved
- Show headings, bullet points in preview
- Click to expand full document in modal (with markdown rendering)

**Office Document Preview:**
- Use Microsoft Graph API or Office Online Viewer embed
- Generate thumbnail from first page/slide
- Show preview in iframe (if permissions allow)
- Fallback: Download option if preview unavailable

**For Web Link Resources:**

**OpenGraph Metadata Extraction:**
- Fetch `og:title`, `og:description`, `og:image` from target URL
- Display as rich preview card
- Cache metadata to avoid repeated fetches

**Screenshot Preview (Optional Enhancement):**
- Use service like Puppeteer or Cloudflare Workers
- Generate screenshot of first viewport
- Display as preview image
- Note: May require backend processing, consider for Phase 2

**Example Web Link Card:**

```
┌─────────────────────────────────────────────────┐
│ 🔗 Azure AI Foundry Documentation               │
│ Microsoft Learn (learn.microsoft.com)          │
│                                                 │
│ [OpenGraph Image - Azure AI Foundry logo]     │
│                                                 │
│ "Azure AI Foundry provides a unified platform  │
│  for building and deploying enterprise AI      │
│  agents with built-in security and governance."│
│                                                 │
│ Added Nov 20, 2025 | Last accessed: 12 times   │
│ Tags: foundry, agents, microsoft, platform     │
│                                                 │
│ [Preview in Modal] [Open in New Tab]          │
└─────────────────────────────────────────────────┘
```

**Video Link Preview:**
- If YouTube/Vimeo: Embed video player directly in card (lazy load)
- Show video thumbnail from platform API
- Display video duration, view count
- Play inline or expand to full modal

#### 2.3 Modal Preview System

**Design Philosophy:**
User should be able to understand 80% of a resource's content without leaving the Resource Library page.

**Modal Preview Features:**

**For Documents:**
- Left panel: Document content (scrollable, paginated for PDFs)
- Right panel: Metadata, tags, related resources
- Full-screen toggle
- Download button
- "Open in New Tab" button (for native browser viewing)
- Keyboard navigation (arrow keys for pages, ESC to close)

**For Web Links:**
- Iframe embed of target URL (if allowed by CORS)
- Fallback: Display OpenGraph metadata + screenshot + "Open in New Tab" button
- Option to "Save Snapshot" (download HTML/PDF copy for archival)

**Modal Preview UX:**

```
┌─────────────────────────────────────────────────────────────────┐
│ [X] Close                                      [↗] Open Externally │
├─────────────────────────────────────────────────────────────────┤
│                                                   │               │
│                                                   │ 📄 Details    │
│    [Document Content / Web Page Embed]           │               │
│                                                   │ Title:        │
│    (80% width, scrollable)                       │ Azure Landing │
│                                                   │ Zones         │
│                                                   │               │
│                                                   │ Category:     │
│                                                   │ Architecture  │
│                                                   │               │
│                                                   │ Tags:         │
│    [Page navigation if PDF]                      │ landing-zone  │
│                                                   │ security      │
│                                                   │               │
│                                                   │ Added By:     │
│                                                   │ Mark Beynon   │
│                                                   │               │
│                                                   │ [Download]    │
│                                                   │ [Share Link]  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.4 Organization & Discovery

**Category System:**

Primary categories (aligned with AI Portal sections):
- **Azure AI Foundry** (platform docs, tutorials, best practices)
- **Microsoft Agent Framework** (SDK docs, code samples, architecture)
- **Governance & Compliance** (policies, frameworks, security standards)
- **Licensing & Budget** (pricing guides, cost optimization, contract docs)
- **Architecture & Infrastructure** (landing zones, networking, identity)
- **Meeting Materials** (transcripts, briefs, decision records)
- **Research & Analysis** (industry reports, competitive analysis, papers)
- **Training & Enablement** (tutorials, certification materials, videos)

**Tag System:**

Multi-tag support for cross-cutting topics:
- Technical: `foundry`, `agent-framework`, `fabric`, `model-router`, `identity`
- Process: `decision`, `proposal`, `meeting-notes`, `action-items`
- Team: `ai-architects`, `microsoft-partnership`, `governance-team`
- Priority: `high-priority`, `executive-review`, `quick-reference`

**Search Functionality:**

```typescript
interface ResourceLibrarySearch {
  // Full-text search
  searchTerm: string;  // Searches title, description, tags, extracted text

  // Filters
  category: string;    // Single category
  tags: string[];      // Multiple tags (AND logic)
  type: 'document' | 'link' | 'video' | 'all';
  dateRange: { start: Date; end: Date };
  addedBy: string;     // Filter by uploader

  // Sort
  sortBy: 'date-added' | 'last-accessed' | 'relevance' | 'alphabetical';
  sortOrder: 'asc' | 'desc';
}
```

**Smart Suggestions:**

- "Related Resources" section on each resource card
- Auto-suggest based on tags (e.g., viewing "landing-zone" doc suggests other landing-zone resources)
- "Frequently Accessed Together" (track co-access patterns)
- "Recommended for You" (based on user's role: architect, developer, governance)

#### 2.5 Collaboration Features

**Annotations & Notes:**
- Users can add personal notes to resources
- Notes visible only to note creator (private)
- Option to share notes with team (future enhancement)

**Usage Analytics:**
- Track view count per resource
- Track last accessed date
- Display "Most Popular" and "Recently Added" sections
- Help identify underutilized resources for archival

**Version Control (for Documents):**
- Upload new version of existing document
- Keep version history (v1, v2, v3)
- Display "Updated" badge on resource cards
- Compare versions (future enhancement)

### Technical Implementation

#### Backend Architecture

**FastAPI Endpoints:**

```python
# Resource library endpoints
GET    /api/resources                       # List all resources
POST   /api/resources                       # Add new resource (upload or link)
GET    /api/resources/{id}                  # Get resource details
PATCH  /api/resources/{id}                  # Update metadata
DELETE /api/resources/{id}                  # Delete resource
GET    /api/resources/{id}/preview          # Get preview data
POST   /api/resources/{id}/view             # Increment view count
GET    /api/resources/search                # Search with filters

# Document processing
POST   /api/resources/extract-text/{id}     # Extract text from PDF
POST   /api/resources/generate-thumbnail/{id} # Generate PDF thumbnail
POST   /api/resources/fetch-og-metadata     # Fetch OpenGraph for URL

# Categories & tags
GET    /api/resources/categories            # List all categories
GET    /api/resources/tags                  # List all tags with usage count
```

**Document Storage (Azure Blob Storage):**

```python
from azure.storage.blob import BlobServiceClient

# Upload document to Blob Storage
blob_service = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service.get_container_client("resources")

# Upload with metadata
blob_client = container_client.upload_blob(
    name=f"{resource_id}/{filename}",
    data=file_stream,
    metadata={
        "uploaded_by": user_id,
        "category": category,
        "tags": ",".join(tags)
    }
)

# Generate SAS URL for secure download
sas_url = generate_blob_sas_url(blob_client, expiry_hours=1)
```

**Metadata Storage (Cosmos DB):**

```json
{
  "id": "resource-001",
  "type": "document",
  "title": "Enterprise Landing Zone Architecture",
  "description": "Microsoft's reference architecture for Azure landing zones",
  "category": "Architecture & Infrastructure",
  "tags": ["landing-zone", "architecture", "security", "networking"],
  "file_type": "pdf",
  "file_size_bytes": 2457600,
  "blob_url": "https://fourthstorage.blob.core.windows.net/resources/resource-001/landing-zone.pdf",
  "thumbnail_url": "https://fourthstorage.blob.core.windows.net/resources/resource-001/thumbnail.png",
  "preview_text": "This document provides guidance on Azure landing zones...",
  "page_count": 12,
  "uploaded_by": "mark.beynon@fourth.com",
  "uploaded_at": "2025-11-18T14:23:00Z",
  "last_accessed": "2025-11-24T09:15:00Z",
  "view_count": 12,
  "related_resources": ["resource-003", "resource-007"]
}
```

**OpenGraph Metadata Fetching:**

```python
import requests
from bs4 import BeautifulSoup

def fetch_og_metadata(url: str):
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.content, 'html.parser')

    metadata = {
        'title': soup.find('meta', property='og:title')['content'],
        'description': soup.find('meta', property='og:description')['content'],
        'image': soup.find('meta', property='og:image')['content'],
        'url': url
    }

    # Cache in Cosmos DB to avoid repeated fetches
    return metadata
```

**PDF Preview Generation:**

```python
from pdf2image import convert_from_path
from PIL import Image

def generate_pdf_thumbnail(pdf_path: str, resource_id: str):
    # Convert first page to image
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    thumbnail = images[0].resize((300, 400))

    # Upload thumbnail to Blob Storage
    thumbnail_path = f"{resource_id}/thumbnail.png"
    thumbnail.save(thumbnail_path)
    upload_to_blob(thumbnail_path)

    return thumbnail_url
```

#### Frontend Components

**React Components:**

```typescript
// Main resource library page
/resources/library/page.tsx

// Components
components/resources/
  ├── ResourceCard.tsx              // Card with preview
  ├── ResourceGrid.tsx              // Grid layout
  ├── ResourceFilters.tsx           // Category/tag filters
  ├── ResourceSearch.tsx            // Search bar with suggestions
  ├── ResourceUpload.tsx            // Upload dialog
  ├── AddLinkDialog.tsx             // Add web link dialog
  ├── ResourcePreviewModal.tsx      // Modal for full preview
  ├── DocumentPreview.tsx           // PDF/doc preview component
  ├── LinkPreview.tsx               // Web link preview component
  └── ResourceMetadata.tsx          // Metadata display panel
```

**State Management:**

```typescript
interface Resource {
  id: string;
  type: 'document' | 'link' | 'video';
  title: string;
  description: string;
  category: string;
  tags: string[];
  thumbnail_url?: string;
  preview_text?: string;
  uploaded_by: string;
  uploaded_at: string;
  view_count: number;
  file_type?: string;
  file_size_bytes?: number;
  url?: string;  // For links
  blob_url?: string;  // For documents
}

const [resources, setResources] = useState<Resource[]>([]);
const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
const [previewModalOpen, setPreviewModalOpen] = useState(false);
const [filters, setFilters] = useState({ category: 'all', tags: [], type: 'all' });
const [searchTerm, setSearchTerm] = useState('');

// Open preview modal
const handlePreview = (resource: Resource) => {
  setSelectedResource(resource);
  setPreviewModalOpen(true);

  // Increment view count
  fetch(`/api/resources/${resource.id}/view`, { method: 'POST' });
};
```

**Upload Workflow:**

```typescript
const handleUpload = async (file: File, metadata: ResourceMetadata) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', metadata.title);
  formData.append('category', metadata.category);
  formData.append('tags', JSON.stringify(metadata.tags));
  formData.append('description', metadata.description);

  const response = await fetch('/api/resources', {
    method: 'POST',
    body: formData
  });

  if (response.ok) {
    const newResource = await response.json();
    setResources([newResource, ...resources]);
    toast.success('Resource uploaded successfully');
  }
};
```

### User Workflows

**Scenario 1: Mark Adds Microsoft Landing Zone Guide**
1. Navigate to Resources → Educational Library
2. Click "Upload Document"
3. Select PDF file, fill in metadata:
   - Title: "Enterprise Landing Zone Architecture"
   - Category: Architecture & Infrastructure
   - Tags: landing-zone, architecture, security
   - Description: Auto-extracted from PDF or manually entered
4. Upload completes, thumbnail generated automatically
5. Resource appears in library with preview

**Scenario 2: Boyan Searches for Foundry Documentation**
1. Navigate to Resources → Educational Library
2. Type "foundry deployment" in search bar
3. See filtered results: 5 documents, 3 web links
4. Hover over "Azure AI Foundry Quickstart" card, see preview text
5. Click "Preview" to open modal
6. Read first 3 pages without leaving Resource Library
7. Click "Open Full Document" to view complete guide

**Scenario 3: David Prepares for Executive Meeting**
1. Navigate to Resources → Educational Library
2. Filter by Category: "Licensing & Budget"
3. Find "Enterprise Licensing Strategy Brief" PDF (previously created)
4. Click Preview to review key points
5. Click Download to save for offline viewing during meeting
6. Add personal note: "Present budget slide first, then licensing options"

**Scenario 4: Team Onboarding New Member (Ivan)**
1. Navigate to Resources → Educational Library
2. Filter by Tag: "quick-reference"
3. Send Ivan links to:
   - "Fourth AI Platform Overview" (PDF)
   - "Agent Framework Decision Diagram" (markdown)
   - "Microsoft Partnership Overview" (PDF)
4. Ivan can preview all documents in browser without downloads
5. Ivan saves frequently accessed resources to personal dashboard (future feature)

**Scenario 5: Research Mode - Mark Compares Architecture Patterns**
1. Search for "multi-agent orchestration"
2. Find 3 Microsoft Learn articles, 2 GitHub repos, 1 research paper
3. Open each in preview modal, compare side-by-side (future: split-screen)
4. Add notes to each resource: "Best for Tier 2 agents" vs "Overkill for Tier 1"
5. Tag all with "comparison-nov-2025" for later reference

---

## Integration Between Both Sections

### Unified Navigation

**Resource Library Page Structure:**

```
Resource Library
├── [Tab 1] Azure Cloud Inventory
│   ├── Summary Stats
│   ├── Filters (Type, Region, Status)
│   └── Resource Cards (live Azure data)
│
└── [Tab 2] Educational Library
    ├── Search & Filters (Category, Tags)
    ├── Upload/Add Buttons
    └── Resource Cards (documents & links)
```

**User can toggle between tabs without losing context**

### Cross-Section Features

**Resource Linking:**
- Document in Educational Library can reference Azure resource
  - Example: "Landing Zone Architecture Guide" document links to actual Azure VNet in Inventory
  - Click link in document preview → Jump to Azure Inventory tab, filtered to that resource

**Cost Attribution in Documents:**
- Upload financial planning spreadsheet in Educational Library
- Link to specific Azure resources in Cloud Inventory
- Display cost data inline in document preview

**Automated Documentation:**
- Generate "Current Infrastructure Summary" document from Azure Inventory
- Auto-update monthly with latest resource list and costs
- Store in Educational Library under "Architecture & Infrastructure" category

### Shared Search

**Global Search Across Both Sections:**
- Search term: "foundry"
- Results:
  - Azure Inventory: "fourth-ai-foundry-prod" resource (live Azure)
  - Educational Library: "Azure AI Foundry Documentation" (PDF)
  - Educational Library: "Foundry Deployment Guide" (web link)

**Intelligent Result Ordering:**
- Prioritize by relevance and recency
- Show section indicator: [Azure Resource] vs [Document] vs [Link]

---

## Implementation Roadmap

### Phase 1: Core Functionality (Week 1)

**Azure Cloud Inventory:**
- ✅ Azure Resource Graph API integration
- ✅ Resource card display (name, type, status, cost)
- ✅ Basic filtering (type, region)
- ✅ Summary statistics

**Educational Library:**
- ✅ Document upload to Blob Storage
- ✅ Metadata storage in Cosmos DB
- ✅ Resource cards with thumbnails
- ✅ Basic search and category filtering

### Phase 2: Preview & Enhanced Features (Week 2)

**Azure Cloud Inventory:**
- ✅ Resource detail modal (full ARM JSON, metrics)
- ✅ Cost Management API integration
- ✅ Quick actions (View in Portal, Logs, Metrics)
- ✅ Cost trend charts

**Educational Library:**
- ✅ PDF preview generation (first page thumbnail)
- ✅ OpenGraph metadata fetching for links
- ✅ Preview modal (documents and links)
- ✅ Tag system with multi-select filtering
- ✅ Upload wizard with auto-metadata extraction

### Phase 3: Advanced Features (Week 3)

**Azure Cloud Inventory:**
- Resource dependency mapping (visualize relationships)
- Alert configuration (high cost, resource failures)
- Export to Excel/CSV
- Bulk operations (stop/start multiple resources)

**Educational Library:**
- Full-text search (search within PDF contents)
- Version control for documents
- Collaboration features (annotations, shared notes)
- Video embed for YouTube/Vimeo links
- Screenshot preview for web links (Puppeteer)

### Phase 4: Intelligence & Automation (Week 4)

**Both Sections:**
- Fourth AI Guide integration (chat with resources)
  - "Show me all Foundry resources" → Searches both Azure and Library
  - "What's our current Azure spend on AI services?" → Queries Inventory
  - "Find the landing zone architecture document" → Opens Educational Library resource

**Azure Cloud Inventory:**
- Anomaly detection (cost spikes, resource failures)
- Predictive cost forecasting
- Automated resource tagging recommendations

**Educational Library:**
- Auto-categorization of uploaded documents (AI-powered)
- Smart recommendations ("People who viewed this also viewed...")
- Duplicate detection (prevent uploading same document twice)

---

## Success Metrics

### For Azure Cloud Inventory

**Visibility & Awareness:**
- 100% of deployed Azure resources visible in inventory within 5 minutes of deployment
- All 6 AI Architect Team members access inventory at least weekly
- Executive stakeholders (Carly) view summary stats monthly

**Cost Management:**
- Identify at least 3 cost optimization opportunities per quarter
- Reduce "unknown" or "untagged" resources to <5%
- Track cost trends per resource (detect spikes within 24 hours)

**Operational Efficiency:**
- Reduce time to find resource information from 5 minutes (Azure Portal navigation) to 30 seconds (inventory search)
- 80% of resource troubleshooting starts with inventory review

### For Educational Resource Library

**Content Growth:**
- 50+ resources uploaded in first month (Microsoft docs, internal guides)
- 10+ web links added (high-value Microsoft Learn articles)
- 5+ meeting materials archived per bi-weekly session

**User Engagement:**
- 70% of team accesses library at least once per week
- Average 3 previews per user per session (preview functionality actively used)
- Search used in 60% of visits (discovery via search, not just browsing)

**Knowledge Sharing:**
- New team member onboarding uses library as primary resource (reduce onboarding time by 30%)
- 90% of meeting action items include link to relevant library resource
- "Resource not found" incidents drop to <1 per month

---

## Security & Governance Considerations

### Azure Cloud Inventory

**Data Sensitivity:**
- Resource metadata is **low sensitivity** (names, types, regions)
- Cost data is **medium sensitivity** (financial information)
- ARM JSON and configurations may contain **high sensitivity** data (private endpoints, connection strings)

**Access Control:**
- Require EntraID authentication for all users
- Implement RBAC:
  - **AI Architect Team:** Full read access to all resources
  - **Governance Team:** Read access to summary stats and cost data
  - **Executives:** Read access to summary stats only (no detailed resource data)
  - **Microsoft Partnership Team:** No access (Fourth internal only)

**API Permissions:**
- Backend uses **Managed Identity** with **Reader** role on subscription
- Backend uses **Cost Management Reader** role for cost data
- No write access from AI Portal (read-only to prevent accidental changes)

### Educational Resource Library

**Data Sensitivity:**
- Public Microsoft documentation: **Low sensitivity** (ok to share externally)
- Internal meeting transcripts: **High sensitivity** (Fourth confidential)
- Financial planning documents: **High sensitivity** (restricted access)

**Access Control:**
- Implement **document-level permissions**:
  - Public documents: All authenticated Fourth users
  - Team documents: AI Architect Team only
  - Executive documents: AI Architects + Governance Team + Executives
  - Meeting transcripts: Mark as sensitive, restrict to attendees

**Data Retention:**
- Meeting materials: Retain indefinitely (historical record)
- External links: Check accessibility quarterly (remove broken links)
- Uploaded documents: Version control, archive old versions after 1 year

**Compliance:**
- No customer data in Resource Library (Fourth internal use only)
- Microsoft partnership materials: Check NDA terms before uploading
- Cost data: Treat as financial information (restricted access)

---

## Open Questions for Team Discussion

### Azure Cloud Inventory

1. **Subscription Scope:** Should inventory cover only AI Landing Zone subscription, or all Fourth Azure subscriptions?
2. **Cost Alerts:** What thresholds should trigger alerts? (e.g., resource >$500/month, 50% over budget)
3. **Resource Tagging:** Should we enforce tagging standards via policy, or just recommend?
4. **Access Control:** Should Microsoft Partnership Team have read access to inventory?

### Educational Resource Library

1. **Content Moderation:** Who approves new uploads? (Free-for-all vs review process)
2. **Storage Quota:** What's the budget for Blob Storage? (Unlimited vs set per-user limit)
3. **External Links:** Should we allow linking to non-Microsoft sites? (e.g., competitor docs, research papers)
4. **Video Hosting:** Should we upload videos to Blob Storage, or just link to YouTube/Microsoft Stream?

### Both Sections

1. **Fourth AI Guide Integration:** Priority level? (Should chat interface query both sections simultaneously?)
2. **Mobile Access:** Is mobile-responsive design required for field access?
3. **Notifications:** Should users receive alerts when new resources are added or costs spike?
4. **Export Capabilities:** Should users be able to export data (inventory list, library catalog) to Excel?

---

## Conclusion

The dual-section Resource Library transforms Fourth's AI Portal from a project tracker into a comprehensive **command center** for the AI Architect Team:

- **Azure Cloud Inventory** provides real-time visibility into Fourth's AI infrastructure, complementing cost tracking with operational intelligence.
- **Educational Resource Library** centralizes knowledge management, enabling the team to preview and discover resources without context-switching.

Together, these sections address Mark's vision of a "single source of truth" for Fourth's Microsoft Agent Ecosystem adoption—combining live infrastructure data with curated educational content.

**Next Steps:**
1. Review proposal with Mark, David, and AI Architect Team
2. Prioritize open questions for team discussion
3. Finalize Phase 1 scope and implementation timeline
4. Begin backend development (Azure SDK integration, Blob Storage setup)
5. Design frontend mockups for both sections (UI/UX review)

---

**Document Owner:** David Hayes (AI Enablement Lead)
**Contributors:** Mark Beynon (Cloud Architecture concept), AI Architect Team
**Last Updated:** November 24, 2025
**Status:** Proposal - Awaiting Team Review
