# Task 13.1 Quick Checklist

**Status:** ⏳ In Progress
**Time Required:** 2-3 hours
**Azure Portal:** https://portal.azure.com

---

## Prerequisites
- [ ] Azure subscription access
- [ ] Application Administrator role (or higher)
- [ ] Access to Fourth Limited tenant

---

## Azure Portal Steps

### 1. Create App Registration (10 min)
- [ ] Navigate to Azure Portal → Entra ID → App registrations
- [ ] Click "New registration"
- [ ] Name: `Fourth AI Portal - Agent Architecture Guide`
- [ ] Account type: Single tenant (Fourth Limited only)
- [ ] Redirect URI (Web): `http://localhost:8080/auth/callback`
- [ ] Click Register
- [ ] **SAVE:** Application (client) ID
- [ ] **SAVE:** Directory (tenant) ID

### 2. Generate Client Secret (10 min)
- [ ] Go to Certificates & secrets
- [ ] Click "New client secret"
- [ ] Description: `Fourth AI Portal Backend Authentication`
- [ ] Expires: 24 months
- [ ] Click Add
- [ ] ⚠️ **SAVE IMMEDIATELY:** Client secret value (shown only once!)

### 3. Configure Redirect URIs (10 min)
- [ ] Go to Authentication
- [ ] Add URIs:
  - `http://localhost:8080/auth/callback`
  - `http://localhost:8080/api/auth/callback`
  - `http://localhost:3000/auth/callback`
- [ ] Enable "Access tokens" ✅
- [ ] Enable "ID tokens" ✅
- [ ] Click Save

### 4. Set API Permissions (15 min)
- [ ] Go to API permissions
- [ ] Verify `User.Read` present
- [ ] Add permission → Microsoft Graph → Delegated
- [ ] Search and add: `User.ReadBasic.All`
- [ ] Click "Grant admin consent for Fourth Limited"
- [ ] Verify green checkmarks appear

### 5. Add Optional Claims (10 min)
- [ ] Go to Token configuration
- [ ] Add optional claim → ID
- [ ] Select:
  - `email` ✅
  - `family_name` ✅
  - `given_name` ✅
- [ ] Accept Microsoft Graph permissions if prompted

---

## Configuration Update

### Update backend/.env

Replace placeholders with your Azure values:

```bash
# Microsoft Entra ID Authentication
ENTRA_CLIENT_ID=<paste-your-client-id>
ENTRA_CLIENT_SECRET=<paste-your-secret-value>
ENTRA_TENANT_ID=<paste-your-tenant-id>
ENTRA_AUTHORITY=https://login.microsoftonline.com/<paste-your-tenant-id>

# JWT Configuration
JWT_SECRET_KEY=<generate-random-secret>
JWT_ALGORITHM=HS256
SESSION_EXPIRY_HOURS=8
```

### Generate JWT Secret

**PowerShell:**
```powershell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

**Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Mark Complete

After finishing:

```bash
task-master set-status --id=13.1 --status=done
task-master update-subtask --id=13.1 --prompt="Created app registration, configured redirect URIs, obtained client ID, tenant ID, and secret"
```

---

## Troubleshooting

**Can't find App registrations?**
→ Make sure you're in Microsoft Entra ID, not Entra ID Admin Center

**Client secret not showing?**
→ It only shows once after creation. Delete and create new if missed.

**Admin consent failed?**
→ You need Global Administrator role. Contact Azure admin.

---

## Next Steps

After completing 13.1:
1. ✅ Update .env file with credentials
2. ➡️ Start Task 13.2: Backend Python MSAL Integration

---

**Full guide:** `.taskmaster/docs/task-13.1-azure-setup-guide.md`
