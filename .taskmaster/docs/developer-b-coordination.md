# Developer B Coordination Plan
## Task #13: Microsoft SSO Authentication Integration

**Last Updated:** 2025-01-24
**Developer:** B (Authentication Track)
**Status:** Task 13.1 In Progress

---

## Overview

This document outlines coordination and integration points between Developer B (Authentication) and the other parallel development tracks.

---

## Integration Points with Developer A (Transcript Processing)

### Developer A's Work (Tasks 1-4)
- Task 1: Implement Transcript File Upload Backend
- Task 2: Azure AI Search Integration
- Task 3: Transcript Detail Modal
- Task 4: Transcript Search & Filter UI

### Integration Timeline

#### Phase 1: Independent Development (Current)
**Status:** ✅ Both teams work independently

**Developer A's Approach:**
- Uses `created_by: "system"` for all transcript uploads
- No user authentication required initially
- Endpoints accessible with shared API key

**Developer B's Approach:**
- Build authentication infrastructure independently
- Don't modify Developer A's code during initial implementation
- Keep shared API key working alongside new SSO

#### Phase 2: Integration (After Task 13.5 Complete)
**Status:** ⏳ Pending Task 13.5 completion

**Changes Required:**

1. **Backend Transcript Endpoints** (`backend/src/routers/transcripts.py`):
   ```python
   # BEFORE (Developer A's version)
   @router.post("/api/transcripts/upload")
   async def upload_transcript(file: UploadFile):
       transcript = {
           "created_by": "system",
           ...
       }

   # AFTER (with Developer B's auth)
   @router.post("/api/transcripts/upload")
   async def upload_transcript(
       file: UploadFile,
       current_user: User = Depends(get_current_user)  # Add this
   ):
       transcript = {
           "created_by": current_user["id"],  # Change this
           "created_by_name": current_user["name"],  # Add this
           "created_by_email": current_user["email"],  # Add this
           ...
       }
   ```

2. **Data Model Migration**:
   ```python
   # Script: backend/src/scripts/migrate_transcript_auth.py

   async def migrate_existing_transcripts():
       """Update existing transcripts with proper user attribution"""

       # Get all transcripts with created_by = "system"
       transcripts = cosmos_container.query_items(
           query="SELECT * FROM c WHERE c.created_by = 'system'",
           enable_cross_partition_query=True
       )

       # Option 1: Assign to admin user
       admin_user = await get_user_by_email("david.hayes@fourth.com")

       # Option 2: Keep as "system" for historical records
       for transcript in transcripts:
           transcript["created_by"] = admin_user["id"]
           transcript["created_by_name"] = admin_user["name"]
           transcript["migrated_at"] = datetime.utcnow().isoformat()
           cosmos_container.upsert_item(transcript)
   ```

3. **Frontend Changes** (`frontend/components/transcripts/`):
   - Add user avatar/name to transcript cards
   - Show "Uploaded by [User Name]" in transcript details
   - Filter transcripts by current user (optional)

### Coordination Actions

**For Developer B:**
- [ ] After Task 13.5 complete, notify Developer A via task-master
- [ ] Provide migration script template
- [ ] Test transcript upload with authenticated user
- [ ] Create PR with `get_current_user` dependency examples

**For Developer A:**
- [ ] Monitor Task 13.5 completion status
- [ ] Review migration script before running
- [ ] Update frontend to display user information
- [ ] Test transcript features with SSO enabled

### Communication Protocol

**Slack/Teams Channel:** `#agent-architecture-dev`

**Key Messages:**
```
[Developer B → Developer A]
"🔐 Task 13.5 complete! SSO now active. Ready to integrate?"

[Developer A → Developer B]
"✅ Reviewed migration script. Running on dev environment."

[Developer B → Developer A]
"✅ Migration successful. All transcripts now have proper user attribution."
```

---

## Integration Points with Developer C (Resource Library)

### Developer C's Work (Tasks 8-9)
- Task 8: Resource Library Dual-Section UI
- Task 9: Resource Upload & Management Backend

### Integration Timeline

#### Phase 1: Independent Development (Current)
**Status:** ✅ Both teams work independently

**Developer C's Approach:**
- Uses `uploaded_by: "system"` for all resource uploads
- No user authentication required initially
- Endpoints accessible with shared API key

**Developer B's Approach:**
- Build authentication infrastructure independently
- Don't modify Developer C's code during initial implementation

#### Phase 2: Integration (After Task 13.5 Complete)
**Status:** ⏳ Pending Task 13.5 completion

**Changes Required:**

1. **Backend Resource Endpoints** (`backend/src/routers/resources.py`):
   ```python
   # BEFORE (Developer C's version)
   @router.post("/api/resources/upload")
   async def upload_resource(
       file: UploadFile,
       title: str,
       category: str,
       tags: List[str]
   ):
       resource = {
           "uploaded_by": "system",
           ...
       }

   # AFTER (with Developer B's auth)
   @router.post("/api/resources/upload")
   async def upload_resource(
       file: UploadFile,
       title: str,
       category: str,
       tags: List[str],
       current_user: User = Depends(get_current_user)  # Add this
   ):
       resource = {
           "uploaded_by": current_user["id"],  # Change this
           "uploaded_by_name": current_user["name"],  # Add this
           "uploaded_by_email": current_user["email"],  # Add this
           ...
       }
   ```

2. **Resource Access Control** (New Feature):
   ```python
   class ResourceVisibility(str, Enum):
       PUBLIC = "public"           # All authenticated users
       INTERNAL = "internal"       # Fourth Limited only
       RESTRICTED = "restricted"   # Specific users/roles only

   @router.get("/api/resources/{id}")
   async def get_resource(
       id: str,
       current_user: User = Depends(get_current_user)
   ):
       resource = await get_resource_by_id(id)

       # Access control check
       if resource["visibility"] == "restricted":
           if current_user["id"] not in resource["allowed_users"]:
               raise HTTPException(403, "Access denied")

       return resource
   ```

3. **Data Model Migration**:
   ```python
   # Script: backend/src/scripts/migrate_resource_auth.py

   async def migrate_existing_resources():
       """Update existing resources with proper user attribution"""

       resources = cosmos_container.query_items(
           query="SELECT * FROM c WHERE c.uploaded_by = 'system'",
           enable_cross_partition_query=True
       )

       admin_user = await get_user_by_email("david.hayes@fourth.com")

       for resource in resources:
           resource["uploaded_by"] = admin_user["id"]
           resource["uploaded_by_name"] = admin_user["name"]
           resource["visibility"] = "public"  # Default
           resource["migrated_at"] = datetime.utcnow().isoformat()
           cosmos_container.upsert_item(resource)
   ```

4. **Frontend Changes** (`frontend/components/resources/`):
   - Add "Uploaded by [User Name]" to resource cards
   - Show visibility indicator (public/internal/restricted)
   - Add "My Resources" filter option
   - Show edit/delete options only for uploaded_by === current_user

### Coordination Actions

**For Developer B:**
- [ ] After Task 13.5 complete, notify Developer C
- [ ] Provide migration script template
- [ ] Document access control patterns
- [ ] Test resource upload with authenticated user

**For Developer C:**
- [ ] Monitor Task 13.5 completion status
- [ ] Review and run migration script
- [ ] Implement access control UI elements
- [ ] Test resource features with SSO enabled

### Communication Protocol

**Key Messages:**
```
[Developer B → Developer C]
"🔐 Task 13.5 complete! Adding user context to resources. Ready to integrate?"

[Developer C → Developer B]
"✅ Reviewed access control patterns. Implementing visibility options."

[Developer B → Developer C]
"✅ Migration complete. All resources now have user attribution & access control."
```

---

## Coordination Strategy

### Development Phases

#### Phase 1: Independent Development (Weeks 1-2)
- All developers work independently on their tracks
- No integration required
- Shared API key remains active

#### Phase 2: Authentication Foundation (Week 2-3)
- Developer B completes Tasks 13.1-13.4
- Authentication infrastructure ready
- Backend endpoints can use `Depends(get_current_user)`

#### Phase 3: Integration Planning (Week 3)
- Developer B notifies Developers A & C
- Review integration requirements
- Schedule integration window

#### Phase 4: Integration Execution (Week 3-4)
- Run data migration scripts
- Update endpoints with authentication
- Test all features with SSO
- Remove shared API key (Task 13.5)

### Communication Channels

**Primary:** Task Master updates
```bash
# Developer B announces readiness
task-master update-task --id=13 --prompt="Task 13.5 complete. SSO ready for integration with Tasks 1-4 and 8-9."

# Developers A & C can check status
task-master show 13
```

**Secondary:** Git/GitHub
- Developer B creates integration branch: `feature/sso-integration`
- Developers A & C review PRs
- Merge after successful testing

**Tertiary:** Project documentation
- Update `.taskmaster/docs/integration-status.md`
- Document breaking changes
- Update API documentation

### Testing Strategy

**Parallel Testing (During Development):**
- Developer B: Test authentication flows independently
- Developers A & C: Test features with shared API key

**Integration Testing (After Task 13.5):**
- All developers test together
- Verify user attribution works correctly
- Test access control scenarios
- End-to-end workflow testing

**Test Scenarios:**
1. Upload transcript as authenticated user → Verify created_by
2. Upload resource as authenticated user → Verify uploaded_by
3. Filter my transcripts → Shows only current user's uploads
4. Access restricted resource → Verify access control
5. Logout → Re-login → Session persists

---

## Integration Checklist

### Developer B Responsibilities

**Pre-Integration:**
- [ ] Complete Task 13.1: Azure App Registration
- [ ] Complete Task 13.2: Backend MSAL Integration
- [ ] Complete Task 13.3: Frontend MSAL Integration
- [ ] Complete Task 13.4: User Model & Cosmos DB
- [ ] Create migration script templates
- [ ] Document authentication patterns

**Integration:**
- [ ] Notify Developers A & C via task-master
- [ ] Provide code examples for `get_current_user`
- [ ] Support migration script execution
- [ ] Test integrated features
- [ ] Complete Task 13.5: Remove Shared API Key
- [ ] Complete Task 13.6: End-to-End Testing

**Post-Integration:**
- [ ] Verify all endpoints use Bearer tokens
- [ ] Confirm shared API key removed
- [ ] Update API documentation
- [ ] Document integration patterns for future features

### Developer A Responsibilities

**Pre-Integration:**
- [ ] Complete transcript processing features
- [ ] Monitor Task 13 progress
- [ ] Review migration requirements

**Integration:**
- [ ] Add `current_user` dependency to endpoints
- [ ] Run transcript migration script
- [ ] Update frontend to show user info
- [ ] Test transcript features with SSO

**Post-Integration:**
- [ ] Verify user attribution works
- [ ] Update component documentation

### Developer C Responsibilities

**Pre-Integration:**
- [ ] Complete resource library features
- [ ] Monitor Task 13 progress
- [ ] Review access control requirements

**Integration:**
- [ ] Add `current_user` dependency to endpoints
- [ ] Implement resource visibility model
- [ ] Run resource migration script
- [ ] Update frontend with access control UI
- [ ] Test resource features with SSO

**Post-Integration:**
- [ ] Verify access control works correctly
- [ ] Update component documentation

---

## Risk Mitigation

### Risk: Breaking Changes During Integration

**Mitigation:**
- Keep shared API key working during development
- Remove API key only in Task 13.5 (final step)
- Create feature branch for integration testing
- Rollback plan: Re-enable API key if issues arise

### Risk: Data Migration Failures

**Mitigation:**
- Test migration scripts on dev environment first
- Backup Cosmos DB containers before migration
- Use Azure Point-in-Time Restore if needed
- Migrate in phases (transcripts → resources → other)

### Risk: Authentication Blocking Features

**Mitigation:**
- SSO is non-blocking until Task 13.5
- Developers A & C can continue independently
- Integration happens only when all parties ready

### Risk: User Session Issues

**Mitigation:**
- Implement proper token refresh logic
- Test session persistence thoroughly
- Add clear error messages for auth failures
- Provide logout/re-login instructions

---

## Success Criteria

Integration is considered successful when:

✅ **Authentication:**
- [ ] Users can login with Microsoft SSO
- [ ] JWT tokens validated on all endpoints
- [ ] Session management works correctly

✅ **Transcript Integration:**
- [ ] Transcripts show correct user attribution
- [ ] Upload requires authentication
- [ ] Migration completed successfully

✅ **Resource Integration:**
- [ ] Resources show correct user attribution
- [ ] Access control enforced correctly
- [ ] Upload requires authentication
- [ ] Migration completed successfully

✅ **Security:**
- [ ] Shared API key fully removed
- [ ] No unauthenticated access to endpoints
- [ ] Proper error handling for auth failures

✅ **Testing:**
- [ ] All end-to-end scenarios pass
- [ ] No regressions in existing features
- [ ] Performance acceptable

---

## Timeline

```
Week 1-2: Independent Development
├─ Developer B: Tasks 13.1-13.4
├─ Developer A: Tasks 1-4
└─ Developer C: Tasks 8-9

Week 3: Integration Planning
├─ Developer B: Notify A & C
├─ All: Review integration requirements
└─ All: Schedule integration window

Week 3-4: Integration Execution
├─ Developer B: Complete Tasks 13.5-13.6
├─ Developer A: Update transcript endpoints
├─ Developer C: Update resource endpoints
└─ All: End-to-end testing

Week 4: Validation & Documentation
├─ All: Final testing
├─ All: Update documentation
└─ All: Mark tasks complete
```

---

**Developer B: Ready to proceed with Azure App Registration (Task 13.1)** 🔐
