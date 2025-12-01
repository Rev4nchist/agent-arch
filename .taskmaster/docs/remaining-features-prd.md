# Product Requirements Document - Remaining Features

## Project: Agent Architecture Guide - Phase 2 Implementation

### Executive Summary
Complete the remaining 4 major pages and critical AI features for the Agent Architecture Guide web application. This PRD covers the implementation of high-priority features including transcript processing, AI chat interface, and content management pages.

---

## 1. Transcript Processing System (HIGH PRIORITY)

### Overview
Enable automated processing of meeting transcripts to extract action items, decisions, topics, and summaries using Azure AI Foundry Model Router.

### Requirements

#### 1.1 Backend - File Upload Endpoint
- Create POST `/api/transcripts/upload` endpoint
- Accept file upload (.txt, .md, .docx formats)
- Store transcript file in Azure Blob Storage
- Return blob URL and file metadata
- Maximum file size: 10MB
- Validate file type before processing

#### 1.2 Backend - AI Processing Pipeline
- Create POST `/api/transcripts/process` endpoint
- Accept meeting ID and transcript blob URL
- Read transcript from Blob Storage
- Implement chunking for transcripts >15k tokens (split into 10k chunks)
- Send chunks to Azure AI Foundry Model Router
- Extract:
  - Meeting summary (2-3 sentences)
  - Action items (list of tasks)
  - Key decisions made (list)
  - Topics discussed (tags/keywords)
- Deduplicate and merge results from multiple chunks
- Update meeting record in Cosmos DB with extracted data

#### 1.3 Backend - Auto-Task Creation
- For each extracted action item, create a task in Cosmos DB
- Set task status to "Pending"
- Link task to originating meeting (created_from_meeting field)
- Assign to mentioned person if name detected in action item
- Set priority based on keywords (urgent, critical, ASAP = High)

#### 1.4 Backend - Meeting Status Update
- Automatically change meeting status from "Scheduled" to "Completed"
- Update meeting.updated_at timestamp
- Store original transcript text in meeting record

#### 1.5 Frontend - Connect Upload Dialog
- Connect existing upload dialog in meetings/page.tsx to backend
- Implement file upload with progress indicator
- Show processing status (Uploading → Processing → Complete)
- Display success message with count of extracted items
- Refresh meeting list after successful processing
- Handle errors gracefully with user-friendly messages

### Success Criteria
- User can upload transcript file for any meeting
- System extracts at least 3 types of data (summary, action items, decisions)
- Tasks are auto-created with proper linking
- Meeting status updates automatically
- Processing completes within 60 seconds for typical transcript

---

## 2. Fourth AI Guide - Chat Interface (HIGH PRIORITY)

### Overview
Build an AI-powered chat interface that allows users to query meeting transcripts, tasks, agents, governance policies, and budget information using RAG (Retrieval Augmented Generation).

### Requirements

#### 2.1 Backend - Azure AI Search Setup
- Create Azure AI Search index for:
  - Meeting transcripts (with chunks)
  - Task descriptions
  - Agent information
  - Governance policies (static content)
- Implement vector embeddings using Azure OpenAI text-embedding-ada-002
- Index all existing data on startup
- Create incremental indexing for new data

#### 2.2 Backend - RAG Implementation
- Create POST `/api/agent/query` endpoint
- Accept: user query string, conversation history (optional)
- Search Azure AI Search for relevant context (top 5 results)
- Construct prompt with:
  - User query
  - Retrieved context
  - Conversation history (last 5 messages)
  - System instructions
- Call Azure AI Foundry Model Router with constructed prompt
- Return response with source citations

#### 2.3 Backend - Query Processing
- Handle query types:
  - "What was discussed in the last governance meeting?"
  - "Show me all high-priority tasks assigned to David"
  - "What agents are in production status?"
  - "What's our current Azure spend?"
  - "What are the Semantic Kernel requirements?"
- Extract entities from queries (dates, names, statuses)
- Route to appropriate data sources
- Combine structured query results with AI-generated explanations

#### 2.4 Frontend - Chat Interface (`/guide` page)
- Create new page at `/app/guide/page.tsx`
- Design chat UI with:
  - Message list (scrollable)
  - User messages (right-aligned, blue)
  - AI messages (left-aligned, gray)
  - Input box at bottom with send button
  - Loading indicator while processing
- Display source citations as expandable badges
- Store conversation in component state (no persistence needed for MVP)
- Auto-scroll to latest message
- Clear conversation button

#### 2.5 Frontend - Query Suggestions
- Show example queries when chat is empty:
  - "What meetings are scheduled this week?"
  - "Show me blocked tasks"
  - "Which agents are still in development?"
  - "What's our governance framework timeline?"
- Make suggestions clickable to auto-populate input

### Success Criteria
- User can ask natural language questions
- System returns accurate answers with source citations
- Response time < 5 seconds for typical query
- Sources link back to original data
- Handles at least 5 different query types correctly

---

## 3. Resources Library Page (MEDIUM PRIORITY)

### Overview
Create a document management system for uploading and organizing PDFs, Word docs, links, and other resources with tagging and search capabilities.

### Requirements

#### 3.1 Backend - Upload System
- Create POST `/api/resources/upload` endpoint
- Accept file uploads (PDF, DOCX, XLSX, TXT)
- Store files in Azure Blob Storage (container: "resources")
- Generate unique blob URLs
- Maximum file size: 50MB

#### 3.2 Backend - Resource CRUD
- Create endpoints:
  - GET `/api/resources` - List all resources with filtering
  - POST `/api/resources` - Create resource metadata
  - PUT `/api/resources/{id}` - Update resource
  - DELETE `/api/resources/{id}` - Delete resource and blob
- Store in Cosmos DB collection: `resources`
- Fields: id, title, description, type (PDF|Document|Link|Other), blob_url, tags[], created_by, created_at, updated_at

#### 3.3 Backend - Search & Filter
- Implement filtering by:
  - Resource type
  - Tags (multiple)
  - Date range
  - Created by
- Implement text search across title and description
- Return results sorted by created_at (newest first)

#### 3.4 Frontend - Resources Page (`/resources`)
- Create page at `/app/resources/page.tsx`
- Grid view of resource cards showing:
  - File icon based on type
  - Title and description
  - Tags as badges
  - Upload date
  - Uploaded by
- Upload dialog with fields:
  - File picker or URL input
  - Title (required)
  - Description (optional)
  - Tags (comma-separated)
  - Type auto-detected or manual select

#### 3.5 Frontend - Resource Actions
- View/Download button (opens blob URL)
- Edit button (opens edit dialog)
- Delete button (with confirmation)
- Search bar with live filtering
- Filter dropdowns (Type, Tags)
- Create Resource button (opens upload dialog)

### Success Criteria
- User can upload files up to 50MB
- Files are stored securely in Blob Storage
- User can tag and categorize resources
- Search returns relevant results within 1 second
- Download links work correctly

---

## 4. Tech Radar Page (MEDIUM PRIORITY)

### Overview
Create a technology tracking system to monitor adoption status of tools and frameworks across the organization.

### Requirements

#### 4.1 Backend - Tech Radar CRUD
- Create endpoints:
  - GET `/api/tech-radar` - List all items
  - POST `/api/tech-radar` - Create item
  - PUT `/api/tech-radar/{id}` - Update item
  - DELETE `/api/tech-radar/{id}` - Delete item
- Store in Cosmos DB collection: `tech_radar_items`
- Fields: id, tool_name, category (Adopt|Trial|Assess|Hold), description, team_using, date_added, last_reviewed, link, created_at, updated_at

#### 4.2 Backend - Filtering
- Filter by category
- Search by tool name or description
- Sort by date_added or last_reviewed

#### 4.3 Frontend - Tech Radar Page (`/tech-radar`)
- Create page at `/app/tech-radar/page.tsx`
- 4-column grid layout (one column per category)
- Each card shows:
  - Tool name
  - Description
  - Team using it
  - Last reviewed date
  - External link (if available)

#### 4.4 Frontend - Category Management
- Drag and drop to move items between categories (optional for MVP)
- Create dialog with fields:
  - Tool name (required)
  - Category (dropdown: Adopt, Trial, Assess, Hold)
  - Description
  - Team using
  - Link (optional URL)
- Edit and delete functionality

#### 4.5 Frontend - Category Descriptions
- Display category meanings:
  - **Adopt:** Proven and ready for use
  - **Trial:** Worth pursuing in select projects
  - **Assess:** Worth exploring to understand potential
  - **Hold:** Proceed with caution or avoid

### Success Criteria
- User can add technologies to any category
- Items are visually grouped by category
- Moving items between categories is intuitive
- Category meanings are clear to users

---

## 5. Architecture Lab Page (MEDIUM PRIORITY)

### Overview
Create a knowledge base for code patterns and deployment guides to standardize development practices.

### Requirements

#### 5.1 Backend - Code Patterns CRUD
- Create endpoints:
  - GET `/api/code-patterns` - List patterns
  - POST `/api/code-patterns` - Create pattern
  - PUT `/api/code-patterns/{id}` - Update pattern
  - DELETE `/api/code-patterns/{id}` - Delete pattern
- Store in Cosmos DB collection: `code_patterns`
- Fields: id, title, pattern_type (Code-First|Low-Code|Hybrid), description, code_snippet, language, use_case, created_at, updated_at

#### 5.2 Backend - Deployment Guides CRUD
- Create endpoints:
  - GET `/api/deployment-guides` - List guides
  - POST `/api/deployment-guides` - Create guide
  - PUT `/api/deployment-guides/{id}` - Update guide
  - DELETE `/api/deployment-guides/{id}` - Delete guide
- Store in Cosmos DB collection: `deployment_guides`
- Fields: id, title, platform (Azure Container Apps|Static Web Apps|Function Apps|Other), guide_content (markdown), prerequisites[], steps[], created_at, updated_at

#### 5.3 Frontend - Architecture Lab Page (`/architecture`)
- Create page at `/app/architecture/page.tsx`
- Two-tab interface: Code Patterns | Deployment Guides

#### 5.4 Frontend - Code Patterns Tab
- Grid of pattern cards showing:
  - Pattern title
  - Pattern type badge
  - Description preview
  - Language tag
- Click to expand showing:
  - Full description
  - Code snippet with syntax highlighting
  - Use case
  - Copy code button
- Create pattern dialog with:
  - Title, type, description
  - Code editor with syntax highlighting
  - Language selector
  - Use case field

#### 5.5 Frontend - Deployment Guides Tab
- List of guide cards showing:
  - Guide title
  - Platform badge
  - Prerequisites count
  - Steps count
- Click to expand showing:
  - Full markdown-rendered guide
  - Prerequisites checklist
  - Step-by-step instructions
  - Copy-pasteable commands
- Create guide dialog with:
  - Title, platform
  - Markdown editor for guide content
  - Prerequisites array input
  - Steps array input

### Success Criteria
- Code patterns display with proper syntax highlighting
- Deployment guides render markdown correctly
- Users can easily copy code snippets
- Guides include all necessary deployment steps

---

## 6. Edit/Delete Operations (ENHANCEMENT)

### Overview
Add full CRUD functionality to pages that currently only support Create and Read operations.

### Requirements

#### 6.1 Backend - Update Endpoints
- Add PUT endpoints for:
  - `/api/meetings/{id}`
  - `/api/tasks/{id}`
  - `/api/agents/{id}`
  - `/api/decisions/{id}`
- Accept partial updates (only changed fields)
- Validate data before updating
- Return updated entity

#### 6.2 Backend - Delete Endpoints
- Add DELETE endpoints for:
  - `/api/meetings/{id}`
  - `/api/tasks/{id}`
  - `/api/agents/{id}`
  - `/api/proposals/{id}`
  - `/api/decisions/{id}`
- Soft delete or hard delete based on entity type
- Check for dependencies before deletion
- Return success/error status

#### 6.3 Frontend - Edit Dialogs
- Add edit dialog components for:
  - Meetings (reuse create dialog with pre-filled data)
  - Tasks (reuse create dialog)
  - Agents (reuse create dialog)
- Populate dialog with existing data
- Call PUT endpoint on save
- Update UI optimistically

#### 6.4 Frontend - Delete Confirmations
- Add delete buttons to entity cards
- Show confirmation dialog:
  - "Are you sure you want to delete [entity name]?"
  - Warning about consequences (if any)
  - Cancel and Confirm buttons
- Call DELETE endpoint on confirm
- Remove from UI immediately
- Show success toast

#### 6.5 Frontend - Detail Views
- Make "View Details" buttons functional
- Either:
  - Open expanded dialog with all entity fields
  - OR navigate to dedicated detail page
- Show related entities (e.g., tasks created from meeting)
- Display full metadata (created_at, updated_at)

### Success Criteria
- Users can edit any entity after creation
- Delete operations require confirmation
- UI updates immediately after changes
- Related data is preserved or handled correctly

---

## 7. Real Azure Budget Integration (ENHANCEMENT)

### Overview
Replace mock budget data with real-time Azure cost data from Azure Cost Management API.

### Requirements

#### 7.1 Backend - Azure Cost Management Integration
- Install Azure Cost Management SDK
- Create `/api/budget/azure-costs` endpoint
- Fetch actual costs for:
  - Azure OpenAI
  - Cosmos DB
  - AI Search
  - Blob Storage
  - App Service
  - AI Foundry
- Support time period filtering (week, month, quarter, year)
- Cache results for 1 hour to avoid excessive API calls

#### 7.2 Backend - Budget Configuration
- Allow setting budget amounts per service
- Store budgets in Cosmos DB collection: `budget_config`
- Calculate spent vs. budget percentages
- Determine status (On Track, Warning, Critical)

#### 7.3 Frontend - Replace Mock Data
- Update `/app/budget/page.tsx` to fetch real data
- Remove mockBudgetData constant
- Add loading state during data fetch
- Handle API errors gracefully
- Show "Last updated" timestamp

#### 7.4 Frontend - Historical Charts
- Add trend chart showing spend over time
- Use chart library (recharts or chart.js)
- Display 30-day trend by default
- Toggle between daily/weekly/monthly views

### Success Criteria
- Budget page displays real Azure costs
- Data refreshes automatically (with caching)
- Historical trends are visualized
- Users can set budget limits per service

---

## Implementation Priority

### Phase 1: Critical AI Features (Days 1-2)
1. Transcript Processing System (6-8 hours)
2. Fourth AI Guide Chat Interface (6-8 hours)

### Phase 2: Content Management (Day 3)
3. Resources Library (3-4 hours)
4. Tech Radar (3-4 hours)
5. Architecture Lab (4-5 hours)

### Phase 3: Enhancements (Day 4)
6. Edit/Delete Operations (4-5 hours)
7. Real Azure Budget Integration (3-4 hours)

---

## Technical Constraints

- **Backend:** Python 3.11, FastAPI
- **Database:** Azure Cosmos DB (2MB document limit)
- **Storage:** Azure Blob Storage
- **AI:** Azure AI Foundry Model Router
- **Search:** Azure AI Search
- **Frontend:** Next.js 16, TypeScript, Shadcn UI
- **Auth:** Shared Access Key (MVP level)

---

## Success Metrics

- All 11 pages functional
- Transcript processing works end-to-end
- AI Guide answers queries accurately
- File uploads work reliably
- Edit/Delete available for all entities
- Real budget data displayed

---

## Risks & Mitigations

**Risk:** Azure AI Search quota limits
**Mitigation:** Implement request throttling, use caching

**Risk:** Large transcript processing timeout
**Mitigation:** Implement async processing with status polling

**Risk:** Blob Storage costs
**Mitigation:** Set file size limits, implement file compression

**Risk:** Model Router API costs
**Mitigation:** Cache common queries, implement rate limiting
