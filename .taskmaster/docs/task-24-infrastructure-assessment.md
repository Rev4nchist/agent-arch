# Task 24.1: Infrastructure Assessment and Resource Planning

**Status:** In Progress
**Date:** 2025-11-30

---

## 1. Existing Azure Resources (Verified from .env)

### Cosmos DB
| Property | Value |
|----------|-------|
| Endpoint | `agent-architecture-cosmos.documents.azure.com` |
| Database | `agent-architecture-db` |
| Status | Active, in use |

### Azure OpenAI
| Property | Value |
|----------|-------|
| Endpoint | `swedencentral.api.cognitive.microsoft.com` |
| Deployment | `gpt-4o` |
| Embeddings | `text-embedding-ada-002` |
| API Version | `2024-02-15-preview` |
| Region | Sweden Central |

### Azure AI Foundry
| Property | Value |
|----------|-------|
| Endpoint | `mb-ai-foundry.openai.azure.com` |
| Deployment | `gpt-4o` |

### Azure AI Search
| Property | Value |
|----------|-------|
| Endpoint | `agent-demo-search.search.windows.net` |
| Index | `transcripts` |

### Azure Blob Storage
| Property | Value |
|----------|-------|
| Account | `agentarchstorage` |
| Container | `resources` |
| Endpoints | Blob, File, Queue, Table |

### Azure Subscription
| Property | Value |
|----------|-------|
| ID | `c9bed202-c4a1-43e9-922d-9a38d966f83e` |

### Microsoft Entra ID (Pending - Task 13)
| Property | Value |
|----------|-------|
| Client ID | Not configured |
| Tenant ID | Not configured |
| Status | BLOCKED - awaiting IT admin |

---

## 2. Current Application Stack

### Backend (FastAPI)
- **Runtime:** Python 3.11+
- **Framework:** FastAPI 0.115.5
- **Key Dependencies:**
  - `azure-cosmos` 4.9.0
  - `azure-identity` 1.19.0
  - `azure-search-documents` 11.6.0
  - `azure-storage-blob` 12.23.1
  - `openai` 1.55.3
  - `python-jose` (JWT handling)
- **Auth:** API key + JWT (Entra ID ready but not configured)

### Frontend (Next.js)
- **Runtime:** Node.js (Next.js 16.0.3)
- **Framework:** React 19.2.0
- **UI:** Radix UI + Tailwind CSS 4.x
- **Build:** TypeScript 5.x

---

## 3. New Azure Resources Required

### For Backend API
| Resource | SKU/Tier | Est. Monthly Cost | Notes |
|----------|----------|-------------------|-------|
| App Service Plan | B2 (Basic) or P1v2 | $55-$75 | Python 3.11, Always On |
| App Service (Backend) | - | Included in plan | FastAPI, gunicorn |

### For Frontend
| Resource | SKU/Tier | Est. Monthly Cost | Notes |
|----------|----------|-------------------|-------|
| Static Web Apps | Free/Standard | $0-$9 | Next.js static export |
| **OR** App Service | B1 | $55 | If SSR required |

### For Operations
| Resource | SKU/Tier | Est. Monthly Cost | Notes |
|----------|----------|-------------------|-------|
| Key Vault | Standard | $0.03/10k ops | Secrets management |
| Application Insights | Pay-as-you-go | ~$2-10 | Depends on volume |
| Log Analytics | Pay-as-you-go | Included | 5GB free/month |

### Estimated Total New Costs
| Scenario | Monthly Estimate |
|----------|------------------|
| Minimum (Static Web App + B2) | $55-65 |
| Standard (Both App Services) | $110-130 |

---

## 4. Resource Naming Convention

```
Pattern: {app}-{component}-{environment}

Examples:
- agent-arch-api-prod        (Backend App Service)
- agent-arch-web-prod        (Frontend Static Web App)
- agent-arch-kv-prod         (Key Vault)
- agent-arch-insights-prod   (Application Insights)
- agent-arch-logs-prod       (Log Analytics)
```

---

## 5. Secrets Inventory for Key Vault

### From Backend .env (17 secrets)
| Secret Name | Category | Has Value |
|-------------|----------|-----------|
| COSMOS-ENDPOINT | Database | Yes |
| COSMOS-KEY | Database | Yes |
| COSMOS-DATABASE-NAME | Database | Yes |
| AZURE-STORAGE-CONNECTION-STRING | Storage | Yes |
| AZURE-STORAGE-CONTAINER-NAME | Storage | Yes |
| AZURE-OPENAI-ENDPOINT | AI | Yes |
| AZURE-OPENAI-API-KEY | AI | Yes |
| AZURE-OPENAI-DEPLOYMENT | AI | Yes |
| AZURE-OPENAI-EMBEDDINGS-DEPLOYMENT | AI | Yes |
| AZURE-SEARCH-ENDPOINT | Search | Yes |
| AZURE-SEARCH-API-KEY | Search | Yes |
| AZURE-SEARCH-INDEX-NAME | Search | Yes |
| AZURE-AI-FOUNDRY-ENDPOINT | AI | Yes |
| AZURE-AI-FOUNDRY-API-KEY | AI | Yes |
| ENTRA-CLIENT-ID | Auth | PENDING (Task 13) |
| ENTRA-CLIENT-SECRET | Auth | PENDING (Task 13) |
| ENTRA-TENANT-ID | Auth | PENDING (Task 13) |
| JWT-SECRET-KEY | Auth | Generate for prod |
| API-ACCESS-KEY | Auth | Generate for prod |

---

## 6. Network/Region Considerations

| Resource | Current Region | Notes |
|----------|---------------|-------|
| OpenAI | Sweden Central | Keep for GDPR |
| AI Foundry | Unknown | Check region |
| Cosmos DB | Unknown | Check region |
| AI Search | Unknown | Check region |
| **New Resources** | UK South (recommended) | Fourth Limited HQ |

**Recommendation:** Deploy new compute resources (App Service) to **UK South** for latency to London office, unless existing data resources require co-location.

---

## 7. Pre-requisites Checklist

- [x] Azure subscription access verified
- [x] Existing resource inventory complete
- [x] Secrets inventory complete
- [ ] Resource naming approved by team
- [ ] Cost estimate approved
- [ ] Region selection confirmed
- [ ] Resource Group created for new resources

---

## 8. Recommended Resource Group Structure

```
Existing (keep as-is):
└── [existing-rg]
    ├── agent-architecture-cosmos (Cosmos DB)
    ├── agentarchstorage (Storage Account)
    ├── swedencentral OpenAI (Cognitive Services)
    └── agent-demo-search (AI Search)

New (create):
└── agent-arch-prod-rg
    ├── agent-arch-plan-prod (App Service Plan)
    ├── agent-arch-api-prod (Backend App Service)
    ├── agent-arch-web-prod (Static Web App)
    ├── agent-arch-kv-prod (Key Vault)
    ├── agent-arch-insights-prod (App Insights)
    └── agent-arch-logs-prod (Log Analytics)
```

---

## 9. Next Steps

1. **Confirm region selection** with team (UK South recommended)
2. **Create resource group** `agent-arch-prod-rg`
3. **Proceed to Task 24.2** - Key Vault setup and secrets migration

---

## 10. Questions for Team

1. Do we need SSR for frontend, or is static export sufficient?
2. Preferred App Service tier: B2 (cheaper) or P1v2 (more performant)?
3. Should we use existing resource group or create new one?
4. Any custom domain requirements?

