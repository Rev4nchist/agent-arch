# Deployment Workflow

## Dev → Staging → Production

### Local Development

```bash
# Start Docker Compose (recommended)
docker-compose up -d --build

# Access at: http://localhost:8080
# Frontend: nginx reverse proxy → Next.js (port 3000)
# Backend: nginx reverse proxy → FastAPI (port 8000)
```

Alternatively, run services directly:
```bash
# Backend
cd backend && python -m uvicorn src.main:app --reload

# Frontend (in another terminal)
cd frontend && npm run dev
```

### Staging Deployment

**Option A: Manual Workflow (Recommended for Feature Branches)**
1. Push your feature branch
2. Go to GitHub Actions → "Staging Deploy"
3. Click "Run workflow"
4. Select your branch and choose what to deploy
5. Check the workflow summary for staging URLs

**Option B: Pull Request Preview**
- Create a PR to main
- SWA automatically creates a preview environment
- Preview URL appears in PR comments

### Production Deployment

Automatic on merge to `main`:
- **Frontend**: Deploys to Azure Static Web Apps
- **Backend**: Builds Docker image, pushes to ACR, updates Container App

### Deployment Checklist

Before deploying to production:

- [ ] Code reviewed and approved
- [ ] Tested locally with `docker-compose up`
- [ ] Deployed to staging and verified
- [ ] No breaking API changes (or coordinated frontend/backend deploy)
- [ ] Environment variables updated if needed
- [ ] Azure RBAC permissions confirmed (Cost Management Reader for budget feature)

### Environment Configuration

| Environment | Frontend URL | Backend URL |
|-------------|-------------|-------------|
| Local | http://localhost:8080 | http://localhost:8080/api |
| Production | witty-coast-0e5f72203.3.azurestaticapps.net | agent-arch-api.icyplant-75ca2495.westeurope.azurecontainerapps.io |

### Secrets Required

| Secret | Description | Where to Set |
|--------|-------------|--------------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | SWA deployment token | GitHub Secrets |
| `AZURE_CREDENTIALS` | Service principal JSON | GitHub Secrets |
| `COSMOS_KEY` | Cosmos DB key | Container App env vars |
| `AZURE_SUBSCRIPTION_ID` | For Cost Management API | Container App env vars |

### Rollback

**Frontend**:
```bash
# List recent deployments
az staticwebapp show --name agent-arch-web-prod --query deploymentId

# SWA doesn't support direct rollback - redeploy previous commit
```

**Backend**:
```bash
# List revisions
az containerapp revision list --name agent-arch-api --resource-group rg-agent-architecture -o table

# Activate previous revision
az containerapp revision activate --name agent-arch-api --resource-group rg-agent-architecture --revision <previous-revision>
```

### Budget Feature RBAC

The budget feature requires Cost Management Reader role on the subscription:

```bash
# Get the Container App's managed identity
PRINCIPAL_ID=$(az containerapp show --name agent-arch-api --resource-group rg-agent-architecture --query identity.principalId -o tsv)

# Assign Cost Management Reader role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cost Management Reader" \
  --scope /subscriptions/c9bed202-c4a1-43e9-922d-9a38d966f83e
```
