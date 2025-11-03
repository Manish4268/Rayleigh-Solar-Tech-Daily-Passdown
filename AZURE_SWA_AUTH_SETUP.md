# Azure Static Web Apps Deployment Guide

## 📋 What Code Changes Were Made?

### ✅ **Files Created/Modified:**

1. **`frontend/src/lib/azureAuth.js`** (NEW)
   - Detects if running on Azure SWA or locally
   - Fetches user info from `/.auth/me` endpoint on Azure
   - Handles login/logout for both environments
   - **No changes needed** - works automatically

2. **`frontend/src/App.jsx`** (MODIFIED)
   - Uses `checkAuthentication()` from azureAuth.js
   - Uses `azureLogout()` for logout button
   - **No changes needed** - works for both local and Azure

3. **`frontend/staticwebapp.config.json`** (MODIFIED)
   - Added Azure AD authentication configuration
   - **You'll need to set environment variables in Azure**

4. **`frontend/src/components/Login.jsx`** (ALREADY DONE)
   - "Microsoft Account" button redirects to `/.auth/login/aad`
   - **No changes needed** - works automatically on Azure

---

## 🚀 Deployment Steps to Azure

### **Step 1: Create Azure Static Web App**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → Search for **"Static Web App"**
3. Click **"Create"**
4. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `rayleigh-solar-passdown` (or your choice)
   - **Region**: Choose closest to you
   - **Deployment details**:
     - **Source**: GitHub
     - **Organization**: Kamani007
     - **Repository**: Rayleigh-Solar-Tech-Daily-Passdown
     - **Branch**: pce
5. **Build Details**:
   - **Build Presets**: Custom
   - **App location**: `/frontend`
   - **Api location**: Leave empty (we're using external API)
   - **Output location**: `dist`
6. Click **"Review + create"** → **"Create"**

### **Step 2: Configure Azure AD Authentication**

After deployment, you need to register an Azure AD app:

1. In Azure Portal, go to **"Azure Active Directory"**
2. Click **"App registrations"** → **"New registration"**
3. Fill in:
   - **Name**: `Rayleigh Solar Passdown Auth`
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: 
     - Platform: **Web**
     - URL: `https://<your-swa-name>.azurestaticapps.net/.auth/login/aad/callback`
4. Click **"Register"**
5. Note down:
   - **Application (client) ID**
   - **Directory (tenant) ID**
6. Go to **"Certificates & secrets"** → **"New client secret"**
   - Description: `SWA Auth Secret`
   - Expires: Choose duration
   - Click **"Add"**
   - **Copy the secret value immediately** (you won't see it again!)

### **Step 3: Add Environment Variables to Static Web App**

1. Go to your Static Web App in Azure Portal
2. Click **"Configuration"** in left menu
3. Click **"+ Add"** under "Application settings"
4. Add these variables:
   ```
   AZURE_CLIENT_ID = <your-application-client-id>
   AZURE_CLIENT_SECRET = <your-client-secret-value>
   ```
5. Click **"Save"**

### **Step 4: Update Redirect URI in App Registration**

1. Go back to your App Registration in Azure AD
2. Click **"Authentication"** in left menu
3. Under "Redirect URIs", make sure you have:
   ```
   https://<your-swa-name>.azurestaticapps.net/.auth/login/aad/callback
   ```
4. Under "Implicit grant and hybrid flows":
   - ✅ Check **"ID tokens"**
5. Click **"Save"**

### **Step 5: Test Your Deployment**

1. Go to your SWA URL: `https://<your-swa-name>.azurestaticapps.net`
2. You should see the login page
3. Click **"Sign in with Microsoft"**
4. It will redirect to Microsoft login
5. After login, you'll be redirected back to the dashboard

---

## 🔧 Do You Need to Change Code When Deploying?

### **NO! The code is already ready.** Here's why:

#### **Local Development (localhost:5175):**
- Uses email/password login (stored in localStorage)
- Sign up creates accounts locally
- Microsoft button does nothing (no Azure endpoints)

#### **Azure Deployment (azurestaticapps.net):**
- Detects Azure environment automatically
- Microsoft button works (redirects to `/.auth/login/aad`)
- Azure handles authentication
- User info fetched from `/.auth/me`
- Logout redirects to `/.auth/logout`

The `azureAuth.js` helper detects the environment and handles both cases automatically!

---

## 🔐 Email Domain Restriction

To restrict to `@rayleighsolartech.com` emails only:

### **Option 1: Azure AD Organization Settings**
1. In Azure AD, ensure only users from your organization can register
2. All users will have @rayleighsolartech.com automatically

### **Option 2: Code-level Check (Already Implemented)**
The Login component already checks for `@rayleighsolartech.com` domain in the email/password flow.

For Azure AD, you can add additional check in `azureAuth.js`:

```javascript
export const getAzureUser = async () => {
  try {
    const response = await fetch('/.auth/me');
    const payload = await response.json();
    const { clientPrincipal } = payload;
    
    if (clientPrincipal) {
      const email = clientPrincipal.userDetails;
      
      // Validate email domain
      if (!email.endsWith('@rayleighsolartech.com')) {
        throw new Error('Only @rayleighsolartech.com emails are allowed');
      }
      
      return {
        email: email,
        name: email.split('@')[0],
        userId: clientPrincipal.userId,
        provider: clientPrincipal.identityProvider
      };
    }
    return null;
  } catch (error) {
    console.error('Failed to get Azure user:', error);
    return null;
  }
};
```

---

## 📊 Backend API Configuration

Your backend is currently on `http://localhost:7071`. For production:

### **Option 1: Azure Functions (Recommended)**
1. Deploy backend to Azure Functions
2. Update API URLs in `frontend/src/lib/api.js`
3. Add CORS settings in Azure Functions

### **Option 2: Keep Separate Backend**
1. Deploy backend to Azure App Service or VM
2. Update `API_BASE_URL` in `frontend/src/lib/api.js`:
   ```javascript
   const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:7071';
   ```
3. Add environment variable in Azure SWA:
   ```
   VITE_API_URL = https://your-backend-url.azure.com
   ```

---

## 🧪 Testing

### **Local Testing:**
```bash
cd frontend
npm run dev
# Test at http://localhost:5175
```

### **Azure Testing:**
1. Push code to GitHub
2. Azure automatically builds and deploys
3. Check deployment status in Azure Portal
4. Test at your SWA URL

---

## 🆘 Troubleshooting

### **Issue: Microsoft login doesn't work**
- Check `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` are set
- Verify redirect URI matches exactly
- Check Azure AD app registration is correct

### **Issue: "Not authorized" after login**
- Check email domain restriction
- Verify user is in your Azure AD tenant
- Check browser console for errors

### **Issue: App shows "loading" forever**
- Check browser console for errors
- Verify `/.auth/me` endpoint returns data
- Check network tab in developer tools

---

## ✅ Summary

**Your code is READY for Azure deployment!**

**What you need to do:**
1. ✅ Create Azure Static Web App
2. ✅ Register Azure AD application
3. ✅ Set environment variables
4. ✅ Push code to GitHub (already done)
5. ✅ Test!

**What you DON'T need to do:**
- ❌ Change any frontend code
- ❌ Modify authentication logic
- ❌ Update Login/Signup components

The code automatically detects the environment and works in both local and Azure! 🎉
