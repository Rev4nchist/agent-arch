# Agent Architecture Platform - Deployment Runbook

**Created:** 2025-12-01
**Status:** Ready for Deployment

---

## Azure Resources Summary

| Resource | Name | Location | Status |
|----------|------|----------|--------|
| Resource Group | `rg-agent-architecture` | North Europe | Active |
| Key Vault | `agent-arch-kv-prod` | North Europe | Active |
| App Service Plan | `agent-arch-plan-prod` | North Europe | P1v2 |
| Backend App Service | `agent-arch-api-prod` | North Europe | Active |
| Static Web App | `agent-arch-web-prod` | West Europe | Active |
| Log Analytics | `agent-arch-logs-prod` | North Europe | Active |
| App Insights | `agent-arch-insights-prod` | North Europe | Active |
| Cosmos DB | `agent-architecture-cosmos` | (existing) | Active |
| Azure OpenAI | Sweden Central | (existing) | Active |
| AI Search | `agent-demo-search` | (existing) | Active |
| Blob Storage | `agentarchstorage` | (existing) | Active |

---

## URLs

| Component | URL |
|-----------|-----|
| **Frontend** | https://witty-coast-0e5f72203.3.azurestaticapps.net |
| **Backend API** | https://agent-arch-api-prod.azurewebsites.net |
| **Key Vault** | https://agent-arch-kv-prod.vault.azure.net |

---

## GitHub Secrets Required

Before the CI/CD pipelines will work, add these secrets to your GitHub repository:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Backend deployment profile | Azure Portal > App Service > Deployment Center > Manage Publish Profile |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Frontend deployment token | Already in Key Vault as `SWA-DEPLOYMENT-TOKEN` |

---

## Pre-Deployment Checklist

### 1. GitHub Repository Setup
- [ ] Create GitHub repository for `agent-arch`
- [ ] Push code to repository
- [ ] Add `AZURE_WEBAPP_PUBLISH_PROFILE` secret
- [ ] Add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret

### 2. Backend Verification
- [ ] Verify Key Vault secrets are accessible
- [ ] Check App Service startup logs
- [ ] Test health endpoint: `https://agent-arch-api-prod.azurewebsites.net/api/health`

### 3. Frontend Verification
- [ ] Verify Next.js build succeeds locally
- [ ] Test API proxy configuration
- [ ] Check static export output

### 4. Integration Testing
- [ ] Test frontend-to-backend connectivity
- [ ] Verify CORS is working
- [ ] Test authentication (API key for now)

---

## Deployment Steps

### Option A: Manual First Deployment

**Backend:**
```bash
cd backend
zip -r ../backend.zip . -x "venv/*" -x "__pycache__/*" -x ".pytest_cache/*" -x "tests/*"
az webapp deployment source config-zip --resource-group rg-agent-architecture --name agent-arch-api-prod --src ../backend.zip
```

**Frontend:**
```bash
cd frontend
npm ci
npm run build
cp staticwebapp.config.json out/
npx @azure/static-web-apps-cli deploy ./out --deployment-token <token>
```

### Option B: CI/CD Deployment (Recommended)

1. Push code to `main` branch
2. GitHub Actions will automatically:
   - Run tests
   - Build and deploy backend
   - Build and deploy frontend

---

## Monitoring

| Dashboard | URL |
|-----------|-----|
| App Insights | Azure Portal > agent-arch-insights-prod |
| Log Analytics | Azure Portal > agent-arch-logs-prod |
| App Service Logs | Azure Portal > agent-arch-api-prod > Logs |

---

## Rollback Procedure

### Backend
```bash
# View deployment history
az webapp deployment list --resource-group rg-agent-architecture --name agent-arch-api-prod

# Rollback to previous deployment
az webapp deployment slot swap --resource-group rg-agent-architecture --name agent-arch-api-prod --slot staging
```

### Frontend
- Static Web Apps maintains deployment history
- Rollback via Azure Portal or redeploy previous commit

---

## Blocked Items (Pending Task 13)

The following features require Entra ID configuration from IT Admin:

- [ ] User authentication with Microsoft accounts
- [ ] SSO integration
- [ ] Role-based access control

**Current Workaround:** Using API key authentication (`API_ACCESS_KEY`)

---

## Estimated Monthly Cost

| Resource | Tier | Est. Cost |
|----------|------|-----------|
| App Service Plan | P1v2 | ~$75 |
| Static Web App | Free | $0 |
| Key Vault | Standard | ~$0.03/10k ops |
| App Insights | Pay-as-you-go | ~$5 |
| Log Analytics | Free tier | $0 |
| **Total** | | **~$80/month** |

(Existing resources like Cosmos DB, OpenAI not included - already provisioned)

---

## Support Contacts

| Role | Contact |
|------|---------|
| Platform Owner | David Hayes |
| Azure Admin | IT Admin Team |

---

## Change Log

| Date | Change | By |
|------|--------|-----|
| 2025-12-01 | Initial deployment setup | Claude + David |
