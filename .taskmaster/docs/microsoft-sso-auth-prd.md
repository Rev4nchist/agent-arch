# Microsoft SSO Authentication - Product Requirements Document

## Overview
Implement Microsoft Single Sign-On (SSO) using Entra ID (Azure AD) to replace the current shared API key authentication. Enable proper user identification, task assignment, and access control.

---

## Business Requirements

### User Stories
- As a team member, I want to login with my Microsoft work account so that my actions are attributed to me
- As a team member, I want to see only my assigned tasks and meetings I'm involved in
- As a manager, I want to assign tasks to specific team members by their actual identity
- As an administrator, I want to control access based on user roles and permissions

### Team Members to Support
- David Hayes (AI Enablement Lead)
- Mark Beynon (Cloud Architecture)
- Boyan Asenov (Agent Development)
- Lucas (Agent Development)
- Dimitar Stoynev (Data Engineering)
- Ivan Georgiev (Development)
- Julia Hilfrich (Microsoft - AI Business Process Specialist)
- Josh Rogers (Microsoft - Solution Engineer)
- Helen Foy (Microsoft - Purview Specialist)

---

## Technical Requirements

### 1. Backend - Entra ID Integration

#### 1.1 Azure App Registration
- Create App Registration in Azure Portal
- Configure redirect URIs:
  - Development: `http://localhost:8080/auth/callback`
  - Production: `https://your-domain.com/auth/callback`
- Set up API permissions:
  - Microsoft Graph: `User.Read` (Delegated)
  - Microsoft Graph: `User.ReadBasic.All` (Delegated) - for user lookup
- Generate client secret and store in Key Vault
- Note Application (client) ID
- Note Directory (tenant) ID

#### 1.2 Backend Authentication Middleware
- Install required packages:
  ```bash
  pip install msal fastapi-azure-auth python-jose[cryptography]
  ```
- Create `src/auth/entra_auth.py`:
  - Implement MSAL (Microsoft Authentication Library) integration
  - Validate JWT tokens from Entra ID
  - Extract user information (email, name, object_id)
  - Create user session management
- Update `src/config.py`:
  - Add ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET, ENTRA_TENANT_ID
  - Add JWT_SECRET_KEY for session tokens
  - Add SESSION_EXPIRY (default: 8 hours)

#### 1.3 User Management Endpoints
- Create `src/models/user.py`:
  - User model: id, email, name, object_id (Entra ID), role, created_at, last_login
  - Roles: admin, member, readonly
- Create Cosmos DB collection: `users`
- Create endpoints:
  - POST `/api/auth/login` - Initiate OAuth flow
  - POST `/api/auth/callback` - Handle OAuth callback
  - POST `/api/auth/logout` - Invalidate session
  - GET `/api/auth/me` - Get current user info
  - GET `/api/users` - List all users (admin only)
  - PUT `/api/users/{id}/role` - Update user role (admin only)

#### 1.4 Protected Route Middleware
- Create `src/auth/dependencies.py`:
  - `get_current_user` dependency
  - `require_admin` dependency
  - `require_auth` decorator for protected routes
- Update all existing endpoints to require authentication:
  - Use `current_user: User = Depends(get_current_user)`
  - Filter data based on user permissions

#### 1.5 User Context in Data Models
- Add `created_by` field to all entities:
  - Meetings: created_by (user_id)
  - Tasks: created_by, assigned_to (user_id or list)
  - Agents: created_by, owner (user_id)
  - Proposals: proposer (user_id)
  - Decisions: decision_maker (user_id)
- Automatically populate `created_by` from authenticated user
- Add migration script to set created_by for existing data (default to system/unknown)

---

### 2. Frontend - MSAL Integration

#### 2.1 Install Dependencies
```bash
cd frontend
npm install @azure/msal-browser @azure/msal-react
```

#### 2.2 MSAL Configuration
- Create `lib/authConfig.ts`:
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

#### 2.3 Authentication Provider
- Update `app/layout.tsx`:
  - Wrap app with `<MsalProvider instance={msalInstance}>`
  - Add authentication status check
  - Redirect to login if not authenticated
- Create `components/AuthGuard.tsx`:
  - Check authentication status
  - Show loading spinner during auth check
  - Redirect to Microsoft login if unauthenticated

#### 2.4 Login Page
- Create `app/login/page.tsx`:
  - Microsoft Sign In button
  - Redirects to Entra ID login flow
  - Handles callback and token storage
  - Navigates to dashboard on success
- Style with Fourth branding
- Show error messages for failed login attempts

#### 2.5 User Profile Component
- Create `components/UserProfile.tsx`:
  - Display user avatar (from Microsoft Graph)
  - Show user name and email
  - Logout button
- Add to Sidebar:
  - Show at top or bottom of sidebar
  - Replace current static branding area

#### 2.6 Update API Client
- Update `lib/api.ts`:
  - Add `getAccessToken()` function using MSAL
  - Include Bearer token in all API requests:
    ```typescript
    headers: {
      'Authorization': `Bearer ${await getAccessToken()}`,
      'Content-Type': 'application/json'
    }
    ```
  - Handle 401 responses (redirect to login)
  - Handle 403 responses (show permission error)

---

### 3. User Assignment Features

#### 3.1 User Selector Component
- Create `components/UserSelector.tsx`:
  - Dropdown/combobox for selecting users
  - Search users by name or email
  - Support single and multi-select modes
  - Display user avatar + name
  - Fetch users from `/api/users` endpoint

#### 3.2 Update Task Assignment
- Update `app/tasks/page.tsx`:
  - Replace text input with UserSelector component
  - Support assigning multiple users to a task
  - Show assigned user avatars in task cards
  - Filter tasks by "My Tasks" (assigned to current user)

#### 3.3 Update Meeting Facilitator
- Update `app/meetings/page.tsx`:
  - Replace text input with UserSelector for facilitator
  - Replace text input with UserSelector for attendees (multi-select)
  - Show attendee avatars in meeting cards

#### 3.4 Update Proposal Owner
- Update `app/decisions/page.tsx`:
  - Replace text input with UserSelector for proposer
  - Replace text input with UserSelector for decision_maker
  - Show user info instead of plain text

#### 3.5 Update Agent Owner
- Update `app/agents/page.tsx`:
  - Replace text input with UserSelector for owner
  - Filter agents by owner
  - Show "My Agents" view

---

### 4. Role-Based Access Control (RBAC)

#### 4.1 Define Roles
- **Admin**: Full access to all features
  - Can manage all entities
  - Can assign roles to users
  - Can view all data
  - Default: David Hayes
- **Member**: Standard access
  - Can create/edit own entities
  - Can view all entities
  - Can be assigned tasks
  - Cannot delete others' entities
- **Readonly**: View-only access
  - Can view all entities
  - Cannot create/edit/delete
  - Good for executives or external partners

#### 4.2 Backend Permission Checks
- Implement permission decorators:
  - `@require_role("admin")` - Admin only
  - `@require_owner_or_admin` - Creator or admin can modify
  - `@require_assigned_or_admin` - Assignee or admin can modify
- Add permission checks to endpoints:
  - DELETE operations: require owner or admin
  - PUT operations: require owner or admin (except assignments)
  - GET operations: generally allowed (but filter by user context)

#### 4.3 Frontend Permission Handling
- Create `hooks/usePermissions.ts`:
  - Check if user can edit entity
  - Check if user can delete entity
  - Check if user is admin
- Update UI components:
  - Hide Edit/Delete buttons if user lacks permission
  - Show read-only badges on entities user can't modify
  - Display permission errors gracefully

---

### 5. Data Migration

#### 5.1 Create Migration Script
- Create `backend/scripts/migrate_user_data.py`:
  - Read all existing entities from Cosmos DB
  - Add `created_by: "system"` to entities without owner
  - Convert text-based assignments to user IDs:
    - Look up users by name/email
    - Replace with user object_id
    - Leave as text if user not found (with warning)
  - Update all documents in place

#### 5.2 User Initialization
- Create `backend/scripts/init_users.py`:
  - Create user records for all team members
  - Set roles:
    - David Hayes: admin
    - All others: member
  - Generate from a config file:
    ```json
    [
      {"email": "david.hayes@fourth.com", "name": "David Hayes", "role": "admin"},
      {"email": "mark.beynon@fourth.com", "name": "Mark Beynon", "role": "member"},
      ...
    ]
    ```

---

### 6. Session Management

#### 6.1 Backend Session Storage
- Store sessions in Cosmos DB collection: `sessions`
- Session model: user_id, token, expires_at, created_at, last_activity
- Implement session cleanup (delete expired sessions daily)

#### 6.2 Token Refresh
- Implement automatic token refresh in frontend:
  - Check token expiry before API calls
  - Refresh if < 5 minutes remaining
  - Use MSAL `acquireTokenSilent`
- Handle refresh failures (redirect to login)

#### 6.3 Activity Tracking
- Update `last_login` on user login
- Track `last_activity` on each API request (every 5 minutes)
- Show "Last seen" in user profile

---

### 7. Security Considerations

#### 7.1 Token Storage
- Store access tokens in sessionStorage (not localStorage)
- Store refresh tokens in httpOnly cookies (backend-managed)
- Never expose tokens in frontend logs or errors

#### 7.2 CORS Configuration
- Update backend CORS settings:
  - Allow only specific origins (no wildcards in production)
  - Include credentials: `allow_credentials=True`
  - Whitelist specific headers

#### 7.3 API Key Deprecation
- Keep shared API key as fallback for system operations
- Add `X-API-Key` header support for internal services
- Remove API key from frontend environment variables

#### 7.4 Audit Logging
- Log all authentication events:
  - Successful logins (user, timestamp, IP)
  - Failed login attempts
  - Token refreshes
  - Logouts
- Log permission denials
- Store in Cosmos DB collection: `audit_logs`

---

### 8. Testing Requirements

#### 8.1 Backend Tests
- Unit tests for authentication middleware
- Test token validation (valid, expired, malformed)
- Test permission decorators
- Test user CRUD operations
- Test role-based access control

#### 8.2 Frontend Tests
- Test login flow (manual initially)
- Test token refresh logic
- Test permission-based UI rendering
- Test logout functionality

#### 8.3 Integration Tests
- Test end-to-end authentication flow
- Test API requests with valid tokens
- Test 401/403 handling
- Test multi-user scenarios (different permissions)

---

## Implementation Phases

### Phase 1: Backend Authentication (4-6 hours)
1. Azure App Registration setup
2. Backend MSAL integration
3. User model and database collection
4. Auth endpoints (login, callback, logout, me)
5. Protected route middleware

### Phase 2: Frontend Authentication (3-4 hours)
1. Install MSAL packages
2. MSAL configuration and provider
3. Login page
4. Auth guard component
5. Update API client with token handling

### Phase 3: User Management (3-4 hours)
1. User selector component
2. Update all entity forms with user selectors
3. User profile component in sidebar
4. Display user info in entity cards

### Phase 4: RBAC & Permissions (3-4 hours)
1. Backend permission checks
2. Frontend permission hooks
3. UI updates based on permissions
4. Admin role features

### Phase 5: Migration & Cleanup (2-3 hours)
1. Data migration script
2. User initialization script
3. Remove API key from frontend
4. Update documentation

**Total Estimated Time:** 15-21 hours

---

## Success Criteria

- ✅ Users can login with Microsoft work accounts
- ✅ Users see their name and avatar in the UI
- ✅ Task assignment uses real user accounts
- ✅ Meeting facilitators and attendees are actual users
- ✅ Permissions prevent unauthorized actions
- ✅ Admins can manage user roles
- ✅ Sessions persist across page refreshes
- ✅ Tokens refresh automatically
- ✅ Logout works correctly
- ✅ All existing data migrated successfully

---

## Environment Variables

### Backend (.env)
```bash
# Entra ID Configuration
ENTRA_CLIENT_ID=your-client-id
ENTRA_CLIENT_SECRET=your-client-secret
ENTRA_TENANT_ID=your-tenant-id

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-generate-random
JWT_ALGORITHM=HS256
SESSION_EXPIRY_HOURS=8

# Keep for backward compatibility
API_ACCESS_KEY=your-shared-key  # For system operations only
```

### Frontend (.env.local)
```bash
# Entra ID Configuration (Public)
NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id
NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id
NEXT_PUBLIC_REDIRECT_URI=http://localhost:8080

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8080
```

---

## Risks & Mitigations

**Risk:** Users locked out if Entra ID is down
**Mitigation:** Implement emergency admin bypass (secure fallback)

**Risk:** Token refresh fails during active session
**Mitigation:** Graceful degradation with re-login prompt

**Risk:** Migration assigns wrong users
**Mitigation:** Manual review step before final migration, backup data

**Risk:** Performance impact of permission checks
**Mitigation:** Cache user roles, optimize database queries

---

## Dependencies

This task should be completed **BEFORE** or **IN PARALLEL** with other tasks that involve user assignment:
- Task #3: Auto-Task Creation (needs user assignment)
- Task #4: Frontend Upload Dialog (needs user context)
- Task #7: AI Chat Interface (needs user context)
- Task #12: Edit/Delete Operations (needs permission checks)

---

## Post-Implementation

After Microsoft SSO is implemented:
1. Update all task assignment flows to use real users
2. Add "My Dashboard" view showing only user's assigned items
3. Implement email notifications for task assignments
4. Add user activity feed
5. Implement team analytics (tasks per user, completion rates)
