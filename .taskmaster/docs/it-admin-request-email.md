# IT/Admin Request Email - Agent Architecture Guide Platform

**Subject:** Request: Azure Entra ID App Registration + Custom Domain + Resource Monitoring Permissions for AI Agent Architecture Platform

---

**To:** Fourth IT/Azure Administrators

**From:** David Hayes

**Priority:** High

**Project:** Fourth AI Agent Architecture Guide Platform

---

## Overview

I'm developing an internal AI-powered platform to manage our agent architecture, governance decisions, task tracking, and team coordination. The platform is deployed on Azure and requires IT/Admin assistance for:

1. **Microsoft Entra ID App Registration** (for SSO authentication)
2. **Custom Domain Configuration** (for professional URL)
3. **Production Redirect URIs** (for OAuth flow)
4. **Azure Resource Monitoring Permissions** (for Cloud Asset Inventory dashboard)

---

## Request 1: Microsoft Entra ID Application Registration

### What's Needed
Register a new application in Microsoft Entra ID to enable Single Sign-On (SSO) for Fourth employees.

### Detailed Steps
*(Reference: `.taskmaster/docs/task-13.1-azure-setup-guide.md`)*

1. **Create App Registration**
   - Navigate to: Azure Portal → Microsoft Entra ID → App registrations → New registration
   - **Name:** `Fourth AI Portal - Agent Architecture Guide`
   - **Supported account types:** `Accounts in this organizational directory only (Fourth Limited only - Single tenant)`
   - **Redirect URI (Platform: Web):** `http://localhost:8080/auth/callback`

2. **Values I Need Returned**
   - Application (client) ID: `_______________`
   - Directory (tenant) ID: `_______________`

3. **Generate Client Secret**
   - Go to: Certificates & secrets → New client secret
   - **Description:** `Fourth AI Portal Backend Authentication`
   - **Expires:** 24 months
   - **Client Secret Value:** `_______________` (CRITICAL: only shown once!)

4. **Configure API Permissions**
   - Add Microsoft Graph permissions:
     - `User.Read` (should already be present)
     - `User.ReadBasic.All` (for reading directory users)
   - **Grant admin consent** for Fourth Limited

5. **Enable Token Options**
   - Go to: Authentication
   - Under "Implicit grant and hybrid flows":
     - Check: Access tokens
     - Check: ID tokens

6. **Add Optional Claims**
   - Go to: Token configuration → Add optional claim → ID
   - Add: `email`, `family_name`, `given_name`

### Role Required
- **Application Administrator** or **Cloud Application Administrator** in Entra ID

---

## Request 2: Custom Domain for Azure Static Web App

### What's Needed
Configure a custom domain to replace the auto-generated Azure URL.

### Current State
- **Current URL:** `https://witty-coast-0e5f72203.3.azurestaticapps.net`
- **Desired URL:** `https://agent-arch.fourth.com` (or similar)

### DNS Configuration Required
| Type | Name | Value |
|------|------|-------|
| CNAME | `agent-arch` | `witty-coast-0e5f72203.3.azurestaticapps.net` |

### After DNS Propagation
I will run:
```bash
az staticwebapp hostname set --name agent-arch-web-prod --hostname agent-arch.fourth.com
```

Azure will automatically provision a free SSL certificate.

---

## Request 3: Production Redirect URIs (After Requests 1 & 2)

### What's Needed
Once the app registration exists, add production redirect URIs for OAuth authentication.

### URIs to Add
In the app registration → Authentication → Web platform:

```
https://witty-coast-0e5f72203.3.azurestaticapps.net/auth/callback
https://witty-coast-0e5f72203.3.azurestaticapps.net/api/auth/callback
```

If custom domain is approved:
```
https://agent-arch.fourth.com/auth/callback
https://agent-arch.fourth.com/api/auth/callback
```

---

## Request 4: Azure Resource Monitoring Permissions (Cloud Asset Inventory)

### What's Needed
Grant the platform's Managed Identity permissions to query Azure resources, costs, and metrics for a Cloud Asset Inventory dashboard.

### Purpose
The platform will display:
- Real-time Azure resource inventory (VMs, storage, databases, etc.)
- Cost tracking and budget monitoring
- Resource health and metrics
- Subscription-wide resource overview

### Backend Managed Identity
The Azure Container App (`agent-arch-api`) uses a **System-assigned Managed Identity** that needs the following permissions.

### Required Role Assignments

| Role | Scope | Purpose |
|------|-------|---------|
| **Reader** | Subscription or Resource Group | Read resource metadata |
| **Cost Management Reader** | Subscription | Access cost and budget data |
| **Monitoring Reader** | Subscription or Resource Group | Access metrics and health data |

### How to Assign (Azure Portal)

1. **Get the Managed Identity Object ID:**
   ```bash
   az containerapp show --name agent-arch-api --resource-group rg-agent-architecture --query "identity.principalId" -o tsv
   ```

2. **Assign Reader Role:**
   - Navigate to: Subscription → Access Control (IAM) → Add role assignment
   - **Role:** Reader
   - **Assign access to:** Managed Identity
   - **Select:** `agent-arch-api` (Container App)

3. **Assign Cost Management Reader:**
   - Same process, **Role:** Cost Management Reader

4. **Assign Monitoring Reader:**
   - Same process, **Role:** Monitoring Reader

### Alternative: Resource Group Scope (More Restricted)
If subscription-wide access isn't approved, these roles can be assigned at the resource group level for `rg-agent-architecture` only. This limits visibility to resources within that group.

### APIs the Platform Will Use
- **Azure Resource Graph API** - Query resources across subscriptions
- **Cost Management API** - Retrieve cost and budget data
- **Azure Monitor API** - Get resource metrics and health

### Subscription ID Needed
Please provide the subscription ID where resources should be monitored:
- **Subscription ID:** `_______________`

---

## Summary Checklist

| # | Request | Status | Admin Action |
|---|---------|--------|--------------|
| 1 | Entra ID App Registration | Blocked | Create app, return client ID/secret/tenant ID |
| 2 | Custom Domain (DNS) | Blocked | Create CNAME record |
| 3 | Production Redirect URIs | Blocked | Add URIs to app registration |
| 4 | Resource Monitoring Permissions | Blocked | Assign Reader, Cost Mgmt Reader, Monitoring Reader roles to Managed Identity |

---

## Azure Resources (For Reference)

| Resource | Name | Resource Group |
|----------|------|----------------|
| Static Web App (Frontend) | `agent-arch-web-prod` | `rg-agent-architecture` |
| Container App (Backend API) | `agent-arch-api` | `rg-agent-architecture` |
| Backend URL | `agent-arch-api.icyplant-75ca2495.westeurope.azurecontainerapps.io` | - |

---

## Questions?

Please contact me at **david.hayes@fourth.com** or Teams if you have any questions.

Once completed, please reply with:
1. Application (client) ID
2. Directory (tenant) ID
3. Client Secret Value
4. Subscription ID (for resource monitoring)
5. Confirmation of role assignments to Managed Identity

I will securely store credentials in Azure Key Vault / environment variables.

---

**Thank you for your assistance!**

*David Hayes*
*AI Agent Architecture Project Lead*
