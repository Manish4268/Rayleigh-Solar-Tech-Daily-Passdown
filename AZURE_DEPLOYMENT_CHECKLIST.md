# Azure Deployment Pre-Flight Checklist

## ✅ Before Deploying to Azure

### 1. **Test Locally First**

Run these commands to ensure everything works:

```bash
cd frontend
npm install
npm run build
npm run preview
```

Open browser and check:
- [ ] Login page loads correctly
- [ ] Can create account (signup)
- [ ] Can login with created account
- [ ] Dashboard loads after login
- [ ] Logout works
- [ ] Logo displays on all pages

### 2. **Check Browser Console for Errors**

Open Developer Tools (F12) → Console tab:
- [ ] No red error messages
- [ ] Authentication logs show: `[Auth] Local environment, isAuthenticated: true`

### 3. **Verify Files are Ready**

Make sure these files exist and are correct:

```bash
# Check files exist
frontend/src/lib/azureAuth.js          ✅
frontend/src/components/Login.jsx      ✅
frontend/src/components/Signup.jsx     ✅
frontend/staticwebapp.config.json      ✅
frontend/public/logo.png               ✅
```

Run this in PowerShell to verify:
```powershell
Test-Path "frontend\src\lib\azureAuth.js"
Test-Path "frontend\staticwebapp.config.json"
Test-Path "frontend\public\logo.png"
```

### 4. **Commit and Push to GitHub**

```bash
git add .
git commit -m "Add Azure SWA authentication support"
git push origin pce
```

---

## 🚀 Deployment Steps

### Step 1: Create Azure Static Web App

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"**
3. Search for **"Static Web App"** → Click **"Create"**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new: `rg-rayleigh-solar`
   - **Name**: `rayleigh-solar-passdown`
   - **Plan type**: Free
   - **Region**: Choose closest to you (e.g., East US 2)
   - **Deployment details**:
     - **Source**: GitHub
     - Click **"Sign in with GitHub"** (if needed)
     - **Organization**: Kamani007
     - **Repository**: Rayleigh-Solar-Tech-Daily-Passdown
     - **Branch**: pce
   - **Build Details**:
     - **Build Presets**: Custom
     - **App location**: `/frontend`
     - **Api location**: (leave empty)
     - **Output location**: `dist`
5. Click **"Review + create"**
6. Click **"Create"**
7. Wait 2-3 minutes for deployment

**Expected Result**: Your app URL will be like: `https://rayleigh-solar-passdown-xxxxx.azurestaticapps.net`

### Step 2: Register Azure AD Application

1. In Azure Portal, search for **"Azure Active Directory"**
2. Click **"App registrations"** → **"+ New registration"**
3. Fill in:
   - **Name**: `Rayleigh Solar Passdown Auth`
   - **Supported account types**: 
     - Select: **"Accounts in this organizational directory only (Single tenant)"**
   - **Redirect URI**:
     - Platform: **Web**
     - URL: `https://rayleigh-solar-passdown-xxxxx.azurestaticapps.net/.auth/login/aad/callback`
     - (Replace `xxxxx` with your actual SWA URL)
4. Click **"Register"**

5. On the app page, note down:
   - **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - **Directory (tenant) ID**: `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy`

6. Click **"Certificates & secrets"** (left menu)
7. Click **"+ New client secret"**
   - **Description**: `SWA Auth Secret`
   - **Expires**: 6 months (or 24 months for less frequent rotation)
8. Click **"Add"**
9. **IMMEDIATELY COPY** the secret **Value** (not the Secret ID!)
   - Save it securely - you can't see it again!

### Step 3: Configure Authentication in Azure AD App

1. In your App Registration, click **"Authentication"** (left menu)
2. Under **"Implicit grant and hybrid flows"**:
   - ✅ Check **"ID tokens (used for implicit and hybrid flows)"**
3. Under **"Supported account types"**:
   - Make sure it's set to your organization only
4. Click **"Save"**

### Step 4: Add Environment Variables to Static Web App

1. Go back to your Static Web App in Azure Portal
2. Click **"Configuration"** in the left menu
3. Click **"+ Add"** under "Application settings"
4. Add these two settings:

   **Setting 1:**
   - **Name**: `AZURE_CLIENT_ID`
   - **Value**: `<paste your Application (client) ID>`
   
   **Setting 2:**
   - **Name**: `AZURE_CLIENT_SECRET`
   - **Value**: `<paste your secret value>`

5. Click **"Save"** at the top

### Step 5: Wait for Deployment to Complete

1. Go to your Static Web App
2. Click **"GitHub Action runs"** in left menu
3. Wait for the workflow to complete (green checkmark)
4. Or check: `https://github.com/Kamani007/Rayleigh-Solar-Tech-Daily-Passdown/actions`

---

## 🧪 Testing on Azure

### Test 1: Basic Access
1. Open your SWA URL in **incognito/private window**: 
   ```
   https://rayleigh-solar-passdown-xxxxx.azurestaticapps.net
   ```
2. You should see the **login page** with logo
3. Open Developer Tools (F12) → **Console** tab
4. You should see:
   ```
   [Auth] Environment check: { hostname: "rayleigh-solar-passdown-xxxxx.azurestaticapps.net", isAzure: true }
   [Auth] Checking authentication...
   [Auth] Azure environment detected, checking /.auth/me
   ```

### Test 2: Microsoft Login
1. Click **"Sign in with Microsoft"** button
2. You should be redirected to Microsoft login page
3. Enter your @rayleighsolartech.com credentials
4. After login, you should be redirected back to the dashboard
5. Check browser console for:
   ```
   [Auth] User authenticated: { email: "yourname@rayleighsolartech.com", ... }
   ```

### Test 3: Check Authentication Endpoint
1. While logged in, open new tab and go to:
   ```
   https://rayleigh-solar-passdown-xxxxx.azurestaticapps.net/.auth/me
   ```
2. You should see JSON like:
   ```json
   {
     "clientPrincipal": {
       "userId": "...",
       "userRoles": ["authenticated"],
       "identityProvider": "aad",
       "userDetails": "yourname@rayleighsolartech.com"
     }
   }
   ```

### Test 4: Email Domain Restriction
1. Try logging in with a non-@rayleighsolartech.com email
2. You should see an alert: "Access denied: Only @rayleighsolartech.com emails are allowed"
3. You should be redirected back to login

### Test 5: Logout
1. Click the **"Logout"** button in the navbar
2. You should be logged out and redirected to login page
3. Going to `/.auth/me` should show empty `clientPrincipal`

---

## 🔍 Troubleshooting

### Problem: "Sign in with Microsoft" does nothing locally

**Expected Behavior**: On localhost, the button won't work because `/.auth/login/aad` doesn't exist locally.

**Solution**: Use email/password login for local testing. Microsoft login only works on Azure.

### Problem: After deployment, clicking Microsoft button shows 404

**Check:**
1. Are `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` set in Azure SWA Configuration?
2. Is the redirect URI correct in Azure AD App Registration?
3. Did you save the settings and wait for redeployment?

**Fix:**
1. Go to Azure Portal → Your Static Web App → Configuration
2. Verify both environment variables are there
3. Click "Save" and wait 2-3 minutes

### Problem: Login works but then shows "Access denied"

**Reason**: Email domain is not @rayleighsolartech.com

**Check:**
1. Open browser console and look for:
   ```
   [Auth] Invalid email domain: user@otherdomain.com
   ```

**Fix:**
- Only users with @rayleighsolartech.com can access
- If you need to test with different domain, temporarily comment out the email check in `azureAuth.js`:
  ```javascript
  // if (!email.endsWith('@rayleighsolartech.com')) {
  //   console.error('[Auth] Invalid email domain:', email);
  //   alert('Access denied: Only @rayleighsolartech.com emails are allowed');
  //   return null;
  // }
  ```

### Problem: "Cannot read properties of undefined (reading 'clientPrincipal')"

**Reason**: Authentication is not set up correctly in Azure

**Check:**
1. Go to `https://your-swa-url.azurestaticapps.net/.auth/me`
2. If you see `{}` (empty), auth is not working

**Fix:**
1. Verify Azure AD app registration
2. Check redirect URI matches exactly
3. Ensure Client ID and Secret are correct
4. Try logging out and in again

### Problem: Build fails on Azure

**Check GitHub Actions:**
1. Go to: `https://github.com/Kamani007/Rayleigh-Solar-Tech-Daily-Passdown/actions`
2. Click on the failed run
3. Look for errors

**Common Issues:**
- Missing dependencies: Run `npm install` locally first
- Build errors: Run `npm run build` locally to check
- Wrong paths: Verify "App location" is `/frontend` and "Output location" is `dist`

---

## 📋 Quick Verification Commands

Run these in PowerShell to verify your setup:

```powershell
# 1. Check all files exist
$files = @(
  "frontend\src\lib\azureAuth.js",
  "frontend\src\components\Login.jsx",
  "frontend\src\components\Signup.jsx",
  "frontend\staticwebapp.config.json",
  "frontend\public\logo.png"
)

foreach ($file in $files) {
  if (Test-Path $file) {
    Write-Host "✅ $file" -ForegroundColor Green
  } else {
    Write-Host "❌ $file MISSING" -ForegroundColor Red
  }
}

# 2. Check if code is committed
Write-Host "`nGit Status:" -ForegroundColor Yellow
git status

# 3. Test build locally
Write-Host "`nBuilding..." -ForegroundColor Yellow
cd frontend
npm run build
```

---

## ✅ Final Checklist Before Going Live

- [ ] Local testing passed (signup, login, logout all work)
- [ ] No console errors in browser
- [ ] Logo displays correctly on all pages
- [ ] Code committed and pushed to GitHub
- [ ] Azure Static Web App created
- [ ] Azure AD App registered
- [ ] Client ID and Secret added to Azure SWA Configuration
- [ ] Redirect URI matches exactly
- [ ] GitHub Actions deployment completed successfully
- [ ] Tested login on Azure URL
- [ ] Tested logout on Azure URL
- [ ] Email restriction working (@rayleighsolartech.com only)
- [ ] Console logs show correct authentication flow

---

## 🎉 Success Indicators

When everything works correctly, you'll see:

**Browser Console (Azure deployment):**
```
[Auth] Environment check: { hostname: "rayleigh-solar-passdown-xxxxx.azurestaticapps.net", isAzure: true }
[Auth] Checking authentication...
[Auth] Azure environment detected, checking /.auth/me
[Auth] Fetching user from /.auth/me...
[Auth] /.auth/me response: { clientPrincipal: {...} }
[Auth] User authenticated: { email: "user@rayleighsolartech.com", name: "user", ... }
[Auth] User authenticated on Azure
```

**User Experience:**
1. User visits site → sees login page with logo
2. Clicks "Sign in with Microsoft" → redirects to Microsoft login
3. Enters @rayleighsolartech.com credentials
4. Redirected back to app → sees dashboard
5. Name/email shown in top-right corner
6. Clicks logout → redirected to login page

You're ready for Azure! 🚀
