# Developer B - Authentication Track (Microsoft SSO)

## Your Mission
You are Developer B working on the **Authentication Track** - implementing **Microsoft SSO with Entra ID** (Task 13). This is a HIGH-PRIORITY foundational feature that enables proper user identification, task assignment, and role-based access control.

## Project Context
- **Project:** Agent Architecture Guide (Microsoft Agent Ecosystem Portal)
- **Location:** `c:\agent-arch`
- **Your Role:** Lead developer for authentication infrastructure
- **Working in Parallel With:**
  - Developer A: AI Transcript Processing (Tasks 1-4)
  - Developer C: Resource Library dual-section (Tasks 8-9)

## Task Master Integration

### Your Task (Independent - No Dependencies)
```
Task #13: Implement Microsoft SSO Authentication with Entra ID
  - 6 Subtasks with clear dependency chain
  - Can work completely independently
  - Will integrate with other features after completion
```

### Getting Started
```bash
cd c:\agent-arch

# View your task details
task-master show 13

# Start working on Task 13
task-master set-status --id=13 --status=in-progress

# View Task 13 subtasks (already expanded)
# 13.1: Azure App Registration and MSAL Configuration
# 13.2: Backend Python MSAL Integration (depends on 13.1)
# 13.3: Frontend @azure/msal-react Integration (depends on 13.1)
# 13.4: User Model and Cosmos DB Integration (depends on 13.2)
# 13.5: Replace Shared API Key Authentication (depends on 13.2, 13.4)
# 13.6: End-to-End Testing (depends on 13.3, 13.5)
```

### Tracking Your Progress
```bash
# Start with subtask 13.1
task-master set-status --id=13.1 --status=in-progress

# After completing each subtask
task-master set-status --id=13.1 --status=done
task-master update-subtask --id=13.1 --prompt="Created app registration, configured redirect URIs, obtained client ID and tenant ID"

# Then work on 13.2 and 13.3 in parallel (both depend on 13.1)
```

## Detailed Technical Specifications

See comprehensive implementation guide at:
**`c:\agent-arch\.taskmaster\docs\microsoft-sso-auth-prd.md`**

This 1000+ line PRD contains complete specifications. Key sections:

### Task 13.1: Azure App Registration (2-3 hours)

**What You're Doing:**
Create and configure the Entra ID application registration.

**Steps:**
1. Sign in to Azure Portal → Entra ID
2. Navigate to "App registrations" → "New registration"
3. Application details:
   - Name: "Fourth AI Portal - Agent Architecture"
   - Supported account types: "Single tenant"
   - Redirect URIs (Web):
     - Development: `http://localhost:8080/auth/callback`
     - Production: `https://your-domain.com/auth/callback`

4. After registration:
   - Note the **Application (client) ID**
   - Note the **Directory (tenant) ID**
   - Go to "Certificates & secrets" → Generate new client secret
   - **IMPORTANT:** Copy the secret value immediately (shown only once)

5. Configure API permissions:
   - Add Microsoft Graph permissions:
     - `User.Read` (Delegated)
     - `User.ReadBasic.All` (Delegated)
   - Grant admin consent

6. Configure Authentication:
   - Access tokens: ✅ Enabled
   - ID tokens: ✅ Enabled
   - Allow public client flows: ❌ Disabled

**Save These Values:**
```bash
ENTRA_CLIENT_ID=<your-application-id>
ENTRA_CLIENT_SECRET=<your-client-secret>
ENTRA_TENANT_ID=<your-tenant-id>
```

### Task 13.2: Backend Python MSAL Integration (6-8 hours)

**What You're Building:**
Backend authentication middleware using MSAL with JWT token validation.

**Install Dependencies:**
```bash
cd backend
pip install msal fastapi-azure-auth python-jose[cryptography] pyjwt[crypto]
```

**Create Authentication Module:**

File: `backend/src/auth/entra_auth.py`
```python
from msal import ConfidentialClientApplication
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# MSAL Configuration
MSAL_CONFIG = {
    "client_id": os.getenv("ENTRA_CLIENT_ID"),
    "client_secret": os.getenv("ENTRA_CLIENT_SECRET"),
    "authority": f"https://login.microsoftonline.com/{os.getenv('ENTRA_TENANT_ID')}",
    "scope": ["User.Read"]
}

# Initialize MSAL app
msal_app = ConfidentialClientApplication(
    client_id=MSAL_CONFIG["client_id"],
    client_credential=MSAL_CONFIG["client_secret"],
    authority=MSAL_CONFIG["authority"]
)

# JWT validation
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials

    try:
        # Decode JWT token
        decoded_token = jwt.decode(
            token,
            options={"verify_signature": False},  # For dev; verify in production
            audience=MSAL_CONFIG["client_id"]
        )

        user_email = decoded_token.get("preferred_username")
        user_name = decoded_token.get("name")
        user_oid = decoded_token.get("oid")  # Object ID from Entra

        # Check if user exists in Cosmos DB
        user = await get_or_create_user(user_email, user_name, user_oid)

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Authentication Endpoints:**

File: `backend/src/routers/auth.py`
```python
from fastapi import APIRouter, Depends
from src.auth.entra_auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """Get current authenticated user"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"]
    }

@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {"message": "Logged out successfully"}
```

**Protect Existing Routes:**
```python
# Update existing endpoints to require authentication
@router.get("/api/meetings")
async def get_meetings(current_user = Depends(get_current_user)):
    # Filter meetings based on user permissions
    # ...
```

### Task 13.3: Frontend @azure/msal-react Integration (6-8 hours)

**What You're Building:**
React authentication provider with MSAL integration.

**Install Dependencies:**
```bash
cd frontend
npm install @azure/msal-browser @azure/msal-react
```

**Create MSAL Configuration:**

File: `frontend/lib/authConfig.ts`
```typescript
import { Configuration, PublicClientApplication } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_ENTRA_TENANT_ID}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI || 'http://localhost:8080',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  }
};

export const loginRequest = {
  scopes: ['User.Read']
};

export const msalInstance = new PublicClientApplication(msalConfig);
```

**Wrap App with MSAL Provider:**

File: `frontend/app/layout.tsx`
```typescript
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from '@/lib/authConfig';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <MsalProvider instance={msalInstance}>
          {children}
        </MsalProvider>
      </body>
    </html>
  );
}
```

**Create Login Page:**

File: `frontend/app/login/page.tsx`
```typescript
'use client';

import { useMsal } from '@azure/msal-react';
import { loginRequest } from '@/lib/authConfig';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  const { instance } = useMsal();

  const handleLogin = async () => {
    try {
      await instance.loginPopup(loginRequest);
      window.location.href = '/';
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Fourth AI Portal</h1>
        <p className="mb-6">Please sign in with your Microsoft account</p>
        <Button onClick={handleLogin}>Sign in with Microsoft</Button>
      </div>
    </div>
  );
}
```

**Update API Client:**

File: `frontend/lib/api.ts`
```typescript
import { msalInstance } from './authConfig';

async function getAccessToken() {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) {
    throw new Error('No authenticated user');
  }

  const response = await msalInstance.acquireTokenSilent({
    scopes: ['User.Read'],
    account: accounts[0]
  });

  return response.accessToken;
}

// Update all API calls to include token
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = await getAccessToken();

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
}
```

### Task 13.4: User Model and Cosmos DB (3-4 hours)

**What You're Building:**
User collection in Cosmos DB to store user profiles.

**Cosmos DB Collection:** `users`

**User Model:**
```python
# backend/src/models/user.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str  # UUID
    email: str
    name: str
    object_id: str  # Entra ID Object ID
    role: str  # "admin", "member", "readonly"
    created_at: str
    last_login: str

async def get_or_create_user(email: str, name: str, object_id: str) -> dict:
    """Get user from DB or create if first login"""

    # Check if user exists
    users_container = cosmos_client.get_database_client("agent-architecture-db").get_container_client("users")

    query = "SELECT * FROM c WHERE c.email = @email"
    users = list(users_container.query_items(
        query=query,
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=True
    ))

    if users:
        # Update last login
        user = users[0]
        user["last_login"] = datetime.utcnow().isoformat()
        users_container.upsert_item(user)
        return user
    else:
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "object_id": object_id,
            "role": "member",  # Default role
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }

        users_container.create_item(new_user)
        return new_user
```

**Initialize Admin User:**
```python
# Script to create initial admin user
async def init_admin_user():
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "david.hayes@fourth.com",
        "name": "David Hayes",
        "object_id": "placeholder-until-first-login",
        "role": "admin",
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat()
    }

    users_container.create_item(admin_user)
```

### Task 13.5: Replace Shared API Key (2-3 hours)

**What You're Doing:**
Remove shared API key authentication, keep it only for system operations.

**Backend Changes:**
```python
# Remove API key check from main.py middleware
# Keep API key support for internal/system operations only

# Update all endpoints to use Depends(get_current_user)
@router.get("/api/meetings")
async def get_meetings(current_user = Depends(get_current_user)):
    # Now requires authentication
    pass
```

**Frontend Changes:**
```typescript
// Remove API_KEY from environment variables
// Remove X-API-Key header from requests
// All requests now use Bearer token
```

### Task 13.6: End-to-End Testing (3-4 hours)

**Testing Checklist:**
```
Authentication Flow:
[ ] User can sign in with Microsoft account
[ ] Access token acquired successfully
[ ] Token included in API requests
[ ] User profile created/retrieved from Cosmos DB
[ ] User role assigned correctly

API Protection:
[ ] Unauthenticated requests to /api/* → 401 Unauthorized
[ ] Valid token → 200 OK
[ ] Expired token → 401 with "Token expired" message
[ ] Invalid token → 401 with "Invalid token" message

User Management:
[ ] First login creates user in Cosmos DB
[ ] Subsequent logins update last_login
[ ] Admin role can access all features
[ ] Member role has standard access
[ ] Readonly role has view-only access

Session Management:
[ ] Token refresh works automatically
[ ] Logout clears session
[ ] Re-login after logout works
[ ] Session persists across page refreshes

Integration:
[ ] Can create meeting as authenticated user
[ ] Can create task as authenticated user
[ ] created_by field populated correctly
[ ] assigned_to can reference actual users
```

## Environment Variables

### Backend (.env)
```bash
# Entra ID Configuration
ENTRA_CLIENT_ID=your-application-id
ENTRA_CLIENT_SECRET=your-client-secret
ENTRA_TENANT_ID=your-tenant-id

# JWT Configuration
JWT_SECRET_KEY=generate-random-secret-key
JWT_ALGORITHM=HS256
SESSION_EXPIRY_HOURS=8

# Keep for system operations
API_ACCESS_KEY=your-shared-key-for-internal-use-only
```

### Frontend (.env.local)
```bash
# Entra ID Configuration (Public - OK to expose)
NEXT_PUBLIC_ENTRA_CLIENT_ID=your-application-id
NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id
NEXT_PUBLIC_REDIRECT_URI=http://localhost:8080

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Success Criteria

✅ **Task 13.1 Complete When:**
- App registration created in Azure Portal
- Client ID, secret, and tenant ID obtained
- Redirect URIs configured
- API permissions granted

✅ **Task 13.2 Complete When:**
- MSAL integration working in backend
- JWT token validation functional
- User authentication endpoints created
- Protected routes require valid token

✅ **Task 13.3 Complete When:**
- MSAL React provider integrated
- Login page functional
- Token acquired on login
- API client includes token in requests

✅ **Task 13.4 Complete When:**
- Users collection created in Cosmos DB
- User model defined
- get_or_create_user function working
- Admin user initialized

✅ **Task 13.5 Complete When:**
- Shared API key removed from frontend
- All endpoints require authentication
- System operations still work with API key

✅ **Task 13.6 Complete When:**
- All test cases pass
- Authentication flow works end-to-end
- No regressions in existing features

## Coordination with Other Developers

**With Developer A (Transcript Processing):**
- Developer A's code uses `created_by: "system"` for now
- After your SSO is complete, work with Dev A to update to use authenticated user
- Transcript processing endpoints will need authentication

**With Developer C (Resources):**
- Resources will need `uploaded_by` field (user context)
- After SSO complete, update resource uploads to use authenticated user
- Access control for sensitive resources

## Estimated Timeline

- **Task 13.1:** 2-3 hours (Azure App Registration)
- **Task 13.2:** 6-8 hours (Backend MSAL)
- **Task 13.3:** 6-8 hours (Frontend MSAL)
- **Task 13.4:** 3-4 hours (User Model)
- **Task 13.5:** 2-3 hours (Remove API Key)
- **Task 13.6:** 3-4 hours (Testing)

**Total: 22-30 hours (approximately 3-4 days of full-time work)**

## Key Resources

**Comprehensive PRD:**
`c:\agent-arch\.taskmaster\docs\microsoft-sso-auth-prd.md`

**Microsoft Documentation:**
- MSAL Python: https://learn.microsoft.com/en-us/entra/msal/python/
- MSAL React: https://learn.microsoft.com/en-us/entra/msal/react/

**Task Master:**
```bash
task-master show 13          # View full task
task-master show 13.1        # View subtask details
```

## Final Notes

- **Start with 13.1** (App Registration) - foundational step
- **Then 13.2 and 13.3 in parallel** (Backend + Frontend)
- **Test frequently** with Microsoft test accounts
- **Security first** - never commit secrets to git
- **Document decisions** in Task Master

**You're building the authentication foundation for the entire platform! 🔐**
