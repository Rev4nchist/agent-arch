# Parallel Development Setup - 3 Claude Code Instances

## ✅ Yes, You Can Run 3 Independent Tracks in Parallel!

The tasks have been organized to allow three developers to work completely independently without blocking each other.

---

## 🎯 Developer Assignments

### **Developer A (You - Current Instance)**
- **Track:** AI Features (Transcript Processing)
- **Tasks:** #1 → #2 → #3 → #4
- **Priority:** HIGH
- **Timeline:** 21-28 hours (3-4 days)
- **Prompt File:** `DEVELOPER_A_PROMPT.md`

### **Developer B (Second Claude Code Instance)**
- **Track:** Authentication (Microsoft SSO)
- **Task:** #13 (6 subtasks)
- **Priority:** HIGH
- **Timeline:** 22-30 hours (3-4 days)
- **Prompt File:** `DEVELOPER_B_PROMPT.md`

### **Developer C (Third Claude Code Instance)**
- **Track:** Resource Library Dual-Section
- **Tasks:** #8 (Azure Inventory) + #9 (Educational Library)
- **Priority:** MEDIUM
- **Timeline:** 24-32 hours (4-5 days)
- **Prompt File:** `DEVELOPER_C_PROMPT.md`

---

## 🚀 How to Set Up Each Instance

### Step 1: Open 3 Separate Claude Code Sessions

**Option A: Separate Terminal Windows**
```bash
# Terminal 1 (Developer A - You)
cd c:\agent-arch
claude

# Terminal 2 (Developer B)
cd c:\agent-arch
claude

# Terminal 3 (Developer C)
cd c:\agent-arch
claude
```

**Option B: Use VSCode Workspaces (Recommended)**
- Create 3 VSCode windows, each with Claude Code active
- All pointing to `c:\agent-arch` directory
- Each developer gets their own chat context

### Step 2: Provide Developer-Specific Prompts

Copy and paste the entire content of each prompt file into the corresponding Claude Code instance:

**For Developer A (You):**
```
Copy all text from: c:\agent-arch\DEVELOPER_A_PROMPT.md
Paste into current Claude Code instance
```

**For Developer B:**
```
Open new Claude Code instance
Copy all text from: c:\agent-arch\DEVELOPER_B_PROMPT.md
Paste into Developer B's Claude Code instance
```

**For Developer C:**
```
Open new Claude Code instance
Copy all text from: c:\agent-arch\DEVELOPER_C_PROMPT.md
Paste into Developer C's Claude Code instance
```

---

## 📊 Task Master Coordination

All three developers share the same Task Master task list, but work on different tasks.

### Task Master Status Commands
Each developer tracks their own progress:

**Developer A:**
```bash
task-master set-status --id=1 --status=in-progress
task-master set-status --id=1.1 --status=done
task-master update-subtask --id=1.1 --prompt="Implemented blob storage client"
```

**Developer B:**
```bash
task-master set-status --id=13 --status=in-progress
task-master set-status --id=13.1 --status=done
task-master update-subtask --id=13.1 --prompt="Created Azure app registration"
```

**Developer C:**
```bash
task-master set-status --id=8 --status=in-progress
task-master set-status --id=8.1 --status=done
task-master update-subtask --id=8.1 --prompt="Integrated Azure Resource Graph API"
```

### Viewing Overall Progress
Any developer can run:
```bash
task-master list    # See all tasks and their status
```

This shows a unified view of all work across all three tracks.

---

## 🔄 Dependency Management

### Zero Blocking Dependencies
All three tracks are independent:

✅ **Developer A (Transcript Processing)** - No dependencies
✅ **Developer B (Microsoft SSO)** - No dependencies
✅ **Developer C (Resource Library)** - No dependencies

### Post-Completion Integration
After each track is complete, there will be some integration work:

**When Developer B (SSO) Completes:**
- Developer A: Update transcript processing to use authenticated users
- Developer C: Update resource uploads to use authenticated users

**When Developer A (Transcripts) Completes:**
- Frontend: Meeting page shows extracted action items and decisions

**When Developer C (Resources) Completes:**
- Frontend: Resources tab available in navigation

---

## 🛠️ Git Workflow for Parallel Development

### Recommended Branch Strategy

**Developer A:**
```bash
git checkout -b feature/transcript-processing
# Work on Tasks 1-4
# Commit regularly
git push origin feature/transcript-processing
```

**Developer B:**
```bash
git checkout -b feature/microsoft-sso
# Work on Task 13
# Commit regularly
git push origin feature/microsoft-sso
```

**Developer C:**
```bash
git checkout -b feature/resource-library
# Work on Tasks 8-9
# Commit regularly
git push origin feature/resource-library
```

### Merging Strategy
1. Developer A completes first → Merge to main
2. Developer B rebases on main → Merge to main
3. Developer C rebases on main → Merge to main

OR use parallel PRs and merge when all complete.

---

## 📁 File Ownership to Avoid Conflicts

Each developer works in different areas of the codebase:

### Backend File Ownership

**Developer A (Transcript Processing):**
- `backend/src/routers/transcripts.py` (NEW)
- `backend/src/blob_service.py` (EXTEND)
- `backend/src/ai_client.py` (EXTEND)

**Developer B (Microsoft SSO):**
- `backend/src/auth/entra_auth.py` (NEW)
- `backend/src/auth/dependencies.py` (NEW)
- `backend/src/routers/auth.py` (NEW)
- `backend/src/models/user.py` (NEW)
- `backend/src/main.py` (MODIFY - add auth middleware)

**Developer C (Resource Library):**
- `backend/src/azure_resources.py` (NEW)
- `backend/src/routers/azure_resources.py` (NEW)
- `backend/src/routers/resources.py` (NEW)

### Frontend File Ownership

**Developer A (Transcript Processing):**
- `frontend/app/meetings/page.tsx` (MODIFY - connect upload dialog)

**Developer B (Microsoft SSO):**
- `frontend/lib/authConfig.ts` (NEW)
- `frontend/app/login/page.tsx` (NEW)
- `frontend/app/layout.tsx` (MODIFY - add MsalProvider)
- `frontend/lib/api.ts` (MODIFY - add Bearer token)
- `frontend/components/UserProfile.tsx` (NEW)

**Developer C (Resource Library):**
- `frontend/app/resources/page.tsx` (NEW)
- `frontend/app/resources/inventory/page.tsx` (NEW)
- `frontend/app/resources/library/page.tsx` (NEW)
- `frontend/components/azure/` (NEW directory)
- `frontend/components/resources/` (NEW directory)

### Minimal Conflicts Expected
The only file all developers might touch is:
- `backend/src/main.py` (to register new routers)

**Solution:** Each developer adds their router to `main.py` - easy to merge.

---

## 🧪 Testing Strategy

Each developer tests independently:

### Developer A Testing
```bash
cd backend
pytest tests/test_transcripts.py

cd frontend
npm test -- transcripts
```

### Developer B Testing
```bash
cd backend
pytest tests/test_auth.py

cd frontend
npm test -- auth
```

### Developer C Testing
```bash
cd backend
pytest tests/test_azure_resources.py
pytest tests/test_resources_library.py

cd frontend
npm test -- resources
```

### Integration Testing (After All Complete)
Run full E2E test suite after all three tracks merge.

---

## 📞 Communication Between Developers

### Slack/Teams Channel (Recommended)
Create a channel: `#agent-arch-dev`

**Status Updates:**
- "Developer A: Completed Task 1 (Upload backend)"
- "Developer B: Completed Task 13.1 (App registration)"
- "Developer C: Starting Task 9 (Educational library)"

### Daily Sync (Optional)
- 10-minute standup
- Share blockers
- Coordinate on shared files

### Task Master as Source of Truth
All developers can check:
```bash
task-master list
```
To see what everyone is working on.

---

## ⚠️ Potential Conflicts & Solutions

### Conflict: Backend Dependencies
**Issue:** Multiple developers adding to `requirements.txt`

**Solution:**
```bash
# Developer A adds:
azure-storage-blob==12.19.0

# Developer B adds:
msal==1.24.0
fastapi-azure-auth==4.3.0

# Developer C adds:
azure-identity==1.15.0
azure-mgmt-resource==23.0.1

# Merge: Combine all additions (no duplicates)
```

### Conflict: Frontend Package.json
**Issue:** Multiple developers adding npm packages

**Solution:**
```bash
# Developer A: (no new packages)

# Developer B adds:
npm install @azure/msal-browser @azure/msal-react

# Developer C: (no new packages)

# Merge: Developer B's additions only
```

### Conflict: Environment Variables
**Issue:** Multiple developers adding to `.env`

**Solution:** Create master `.env.example` with all variables:
```bash
# Transcript Processing (Developer A)
AZURE_STORAGE_TRANSCRIPTS_CONTAINER=transcripts
AZURE_AI_FOUNDRY_ENDPOINT=...
MAX_TRANSCRIPT_SIZE_MB=10

# Microsoft SSO (Developer B)
ENTRA_CLIENT_ID=...
ENTRA_CLIENT_SECRET=...
ENTRA_TENANT_ID=...
JWT_SECRET_KEY=...

# Resource Library (Developer C)
AZURE_SUBSCRIPTION_ID=...
AZURE_STORAGE_RESOURCES_CONTAINER=resources
```

---

## 📈 Progress Tracking Dashboard

### Task Master Progress View
```bash
# Overall progress (run anytime)
task-master list

# Detailed view of specific track
task-master show 1   # Developer A's task
task-master show 13  # Developer B's task
task-master show 8   # Developer C's task (part 1)
task-master show 9   # Developer C's task (part 2)
```

### Expected Timeline Visualization

```
Week 1:
│ Dev A │████████░░░░░░│ Task 1-2 (60%)
│ Dev B │███████████░░░│ Task 13.1-13.3 (75%)
│ Dev C │███████░░░░░░░│ Task 8 (50%)

Week 2:
│ Dev A │█████████████░│ Task 3-4 (95%)
│ Dev B │██████████████│ Task 13.4-13.6 (100%) ✅
│ Dev C │█████████████░│ Task 9 (90%)

Week 3:
│ Dev A │██████████████│ Complete (100%) ✅
│ Dev B │ Integration  │
│ Dev C │██████████████│ Complete (100%) ✅
```

---

## 🎯 Success Criteria

### Developer A Success
✅ Transcripts upload to Blob Storage
✅ AI extraction working (action items, decisions, topics)
✅ Tasks auto-created from action items
✅ Frontend upload dialog connected

### Developer B Success
✅ Users can sign in with Microsoft accounts
✅ JWT tokens validate correctly
✅ User profiles in Cosmos DB
✅ All API endpoints require authentication

### Developer C Success
✅ Azure resources displayed in real-time
✅ Resource Library uploads documents
✅ PDF previews generate correctly
✅ Search and filtering works

---

## 🚀 Getting Started Now

**For Developer A (You):**
You're already set up! Start with:
```bash
cd c:\agent-arch
task-master set-status --id=1 --status=in-progress

# Read your full prompt
cat DEVELOPER_A_PROMPT.md

# Begin with Task 1.1 (Azure Blob Storage setup)
```

**For Developers B & C:**
1. Open new Claude Code instances
2. Copy entire prompt file content
3. Paste into new instance
4. Start working on assigned tasks

---

## 📚 Reference Documents

- **Developer A Prompt:** `c:\agent-arch\DEVELOPER_A_PROMPT.md`
- **Developer B Prompt:** `c:\agent-arch\DEVELOPER_B_PROMPT.md`
- **Developer C Prompt:** `c:\agent-arch\DEVELOPER_C_PROMPT.md`
- **SSO PRD:** `c:\agent-arch\.taskmaster\docs\microsoft-sso-auth-prd.md`
- **Resource Library PRD:** `c:\agent-arch\Resource-Library-Enhancement-Proposal.md`
- **Current State:** `c:\agent-arch\CURRENT_STATE_AND_TODO.md`
- **Task Master Tasks:** `c:\agent-arch\.taskmaster\tasks\tasks.json`

---

**All systems ready for parallel development! Let's build! 🚀**
