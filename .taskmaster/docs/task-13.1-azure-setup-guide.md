# Task 13.1: Azure App Registration Setup Guide

**Status:** In Progress
**Estimated Time:** 2-3 hours
**Prerequisites:** Azure subscription with admin access to Entra ID

---

## Objective
Create and configure Microsoft Entra ID (Azure AD) application registration for SSO authentication using MSAL with OAuth 2.0/OIDC.

---

## Step-by-Step Instructions

### Step 1: Access Azure Portal (5 minutes)

1. Open browser and navigate to: https://portal.azure.com
2. Sign in with your Fourth Limited Microsoft account
3. Navigate to **Microsoft Entra ID** (search in top search bar)
4. Select **App registrations** from the left sidebar

### Step 2: Create New App Registration (10 minutes)

1. Click **+ New registration** button

2. **Application Registration Details:**
   ```
   Name: Fourth AI Portal - Agent Architecture Guide
   Supported account types: Accounts in this organizational directory only (Fourth Limited only - Single tenant)
   Redirect URI:
     - Platform: Web
     - URI: http://localhost:8080/auth/callback
   ```

3. Click **Register**

4. **IMPORTANT: Save these values immediately:**
   - Application (client) ID: `_________________________`
   - Directory (tenant) ID: `_________________________`

   ⚠️ Copy these to a secure location - you'll need them for .env configuration

### Step 3: Generate Client Secret (10 minutes)

1. In your new app registration, go to **Certificates & secrets** (left sidebar)

2. Click **+ New client secret**

3. Configure:
   ```
   Description: Fourth AI Portal Backend Authentication
   Expires: 24 months (recommended for development)
   ```

4. Click **Add**

5. **⚠️ CRITICAL: Copy the secret VALUE immediately!**
   ```
   Client Secret Value: _________________________
   ```

   ⚠️ This value is shown ONLY ONCE! If you miss it, you'll need to generate a new secret.

### Step 4: Configure Redirect URIs (10 minutes)

1. Go to **Authentication** (left sidebar)

2. Under **Platform configurations → Web**:
   - Click **Add URI**
   - Add development URIs:
     ```
     http://localhost:8080/auth/callback
     http://localhost:8080/api/auth/callback
     http://localhost:3000/auth/callback
     ```

3. Under **Implicit grant and hybrid flows**:
   - ✅ Check **Access tokens** (used for implicit flows)
   - ✅ Check **ID tokens** (used for user authentication)

4. Under **Advanced settings**:
   - Allow public client flows: ❌ No (keep disabled for security)

5. Click **Save**

### Step 5: Configure API Permissions (15 minutes)

1. Go to **API permissions** (left sidebar)

2. You should see **User.Read** already listed (default)

3. Click **+ Add a permission**

4. Select **Microsoft Graph**

5. Select **Delegated permissions**

6. Add these permissions:
   ```
   User.Read (already present - allows user to sign in and read their profile)
   User.ReadBasic.All (allows app to read basic profile of all users in the directory)
   ```

7. Search for and check:
   - `User.ReadBasic.All`

8. Click **Add permissions**

9. **Grant Admin Consent:**
   - Click **✓ Grant admin consent for Fourth Limited**
   - Confirm the action
   - Verify all permissions show green checkmarks under "Status"

### Step 6: Configure Token Configuration (Optional - 10 minutes)

1. Go to **Token configuration** (left sidebar)

2. Click **+ Add optional claim**

3. Select **ID**

4. Add these claims:
   ```
   ✅ email
   ✅ family_name
   ✅ given_name
   ```

5. If prompted about Microsoft Graph permissions, check the box and click **Add**

### Step 7: Configure Expose an API (Optional for future - 15 minutes)

*Skip this for now - will be needed when implementing API-to-API authentication*

1. Go to **Expose an API** (left sidebar)
2. Click **Set** next to Application ID URI
3. Accept default: `api://<your-client-id>`
4. Click **Save**

---

## Verification Checklist

Before proceeding to Task 13.2, verify you have:

- [ ] Application (client) ID saved
- [ ] Directory (tenant) ID saved
- [ ] Client secret value saved (shown only once!)
- [ ] Redirect URIs configured (development URLs)
- [ ] Access tokens and ID tokens enabled
- [ ] API permissions configured:
  - [ ] User.Read
  - [ ] User.ReadBasic.All
- [ ] Admin consent granted (green checkmarks)
- [ ] Optional claims added (email, family_name, given_name)

---

## Configuration Values to Save

**Copy these values to update your .env file:**

```bash
# Microsoft Entra ID Configuration
ENTRA_CLIENT_ID=<your-application-client-id>
ENTRA_CLIENT_SECRET=<your-client-secret-value>
ENTRA_TENANT_ID=<your-directory-tenant-id>
ENTRA_AUTHORITY=https://login.microsoftonline.com/<your-tenant-id>

# JWT Configuration (generate a random secret)
JWT_SECRET_KEY=<generate-random-secret-see-below>
JWT_ALGORITHM=HS256
SESSION_EXPIRY_HOURS=8
```

### Generate JWT_SECRET_KEY

Run this command to generate a secure random key:

```bash
# Windows PowerShell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use online generator (secure sites only):
# https://generate-random.org/api-key-generator
```

---

## Troubleshooting

### Can't find App registrations?
- Make sure you're in **Microsoft Entra ID** (not Entra ID Admin Center)
- You need **Application Administrator** or **Cloud Application Administrator** role

### Client secret not showing?
- Secret value is shown ONLY immediately after creation
- If you missed it, delete the secret and create a new one
- Store it securely in Azure Key Vault or .env file

### Admin consent failed?
- You need **Global Administrator** or **Privileged Role Administrator** role
- Contact your Azure admin if you don't have permissions

### Redirect URI not working?
- Make sure you're using exact URLs (case-sensitive)
- Include both `/auth/callback` and `/api/auth/callback` variants
- Add http://localhost:3000 for frontend development

---

## Next Steps

After completing this task:

1. ✅ Update backend/.env with Entra ID credentials
2. ✅ Mark Task 13.1 as complete
3. ➡️ Start Task 13.2: Backend Python MSAL Integration

---

## Security Notes

⚠️ **CRITICAL SECURITY REMINDERS:**

1. **Never commit secrets to git:**
   - .env files should be in .gitignore
   - Use Azure Key Vault for production
   - Rotate secrets if accidentally exposed

2. **Production deployment:**
   - Use managed identities when possible
   - Store secrets in Azure Key Vault
   - Update redirect URIs to production domains
   - Set client secret expiration to 6-12 months (shorter is more secure)

3. **Access control:**
   - Only grant minimum required permissions
   - Review app permissions regularly
   - Monitor sign-in logs for suspicious activity

---

**Estimated completion time: 2-3 hours (including documentation and verification)**
