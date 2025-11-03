# Azure Static Web Apps Deployment Guide

## Overview
This guide will help you deploy the Rayleigh Solar Tech Daily Passdown System to Azure Static Web Apps with built-in authentication.

## What You Get (FREE Tier)
- ✅ **FREE** for first 100GB bandwidth/month
- ✅ Built-in authentication (GitHub, Azure AD, Twitter, etc.)
- ✅ Custom domains
- ✅ SSL certificates (automatic)
- ✅ Global CDN
- ✅ Staging environments

## Deployment Options

### Option 1: Simple Login (Already Implemented)
**Test Credentials:**
- Username: `admin` / Password: `admin123`
- Username: `user` / Password: `user123`

This works locally and can be deployed as-is. No Azure configuration needed!

### Option 2: Azure Built-in Authentication (Recommended for Production)

#### Step 1: Create Azure Static Web App

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Static Web App"
4. Click "Create"

**Configuration:**
- **Subscription**: Your Azure subscription
- **Resource Group**: Create new or use existing
- **Name**: `rayleigh-solar-passdown` (or your choice)
- **Plan Type**: **Free** (no cost!)
- **Region**: Choose closest to you
- **Source**: GitHub
- **Organization**: Your GitHub username
- **Repository**: `Rayleigh-Solar-Tech-Daily-Passdown`
- **Branch**: `pce` or `main`
- **Build Presets**: Custom
- **App location**: `/frontend`
- **Api location**: `/backend`
- **Output location**: `dist`

5. Click "Review + create"
6. Click "Create"

#### Step 2: Get Deployment Token

After creation:
1. Go to your Static Web App in Azure Portal
2. Click "Manage deployment token"
3. Copy the token
4. Go to your GitHub repository
5. Settings → Secrets and variables → Actions
6. Add new secret:
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: Paste the token

#### Step 3: Enable Authentication (Optional)

**For Azure AD (Microsoft Accounts):**
1. In Azure Portal, go to your Static Web App
2. Click "Authentication" in the left menu
3. Click "Add identity provider"
4. Choose "Azure Active Directory"
5. Click "Add"

**For GitHub:**
1. Same steps, but choose "GitHub"
2. You'll need to create a GitHub OAuth app

**For Custom Providers:**
Users can login with:
- `/.auth/login/aad` - Azure AD
- `/.auth/login/github` - GitHub
- `/.auth/login/twitter` - Twitter

#### Step 4: Deploy

The GitHub Actions workflow is already configured. Just push your code:

```bash
git add .
git commit -m "Add authentication and Azure deployment"
git push origin pce
```

Azure will automatically build and deploy!

## Backend API Deployment

### Option A: Keep Backend Separate (Current Setup)
Your Flask backend can run on:
- Your current server
- Azure App Service
- Azure Container Apps
- Any cloud provider

Update `frontend/src/lib/api.js` with your backend URL.

### Option B: Azure Functions (Serverless)
Convert Flask routes to Azure Functions for serverless deployment.

## Environment Variables

Add these in Azure Portal → Static Web App → Configuration:

```
MONGODB_CONNECTION_STRING=your_mongodb_connection_string
VITE_API_URL=https://your-backend-url.com
```

## Testing Authentication

### Local Testing:
1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open: `http://localhost:5173`
4. Login with: `admin` / `admin123`

### Production Testing:
1. Your app will be available at: `https://<your-app-name>.azurestaticapps.net`
2. Login options:
   - Simple login (admin/admin123)
   - Azure AD (if enabled)
   - GitHub (if enabled)

## Cost Breakdown

### FREE Tier Includes:
- ✅ 100 GB bandwidth/month
- ✅ 0.5 GB storage
- ✅ Unlimited API requests
- ✅ 2 custom domains
- ✅ Built-in authentication

### Paid Features (if needed later):
- Standard tier: $9/month
  - 100 GB bandwidth included
  - Additional bandwidth: $0.20/GB

## Security Features

1. **Built-in Authentication**: No coding required
2. **HTTPS by default**: Free SSL certificates
3. **Custom authentication**: Already implemented (login page)
4. **Role-based access**: Configure in `staticwebapp.config.json`

## Monitoring

View in Azure Portal:
- Request logs
- Error rates
- Bandwidth usage
- Authentication events

## Troubleshooting

### Build Fails:
- Check GitHub Actions logs
- Verify paths in workflow file
- Check Node.js version compatibility

### Authentication Issues:
- Clear browser cache
- Check `staticwebapp.config.json`
- Verify authentication provider settings

### Backend Connection:
- Check CORS settings in Flask
- Verify API URL in frontend
- Check environment variables

## Next Steps

1. ✅ Login page is already added
2. ✅ GitHub Actions workflow is configured
3. ⏳ Create Azure Static Web App (5 minutes)
4. ⏳ Push code to deploy
5. ⏳ (Optional) Enable Azure AD/GitHub auth

## Support

- Azure Static Web Apps: https://docs.microsoft.com/azure/static-web-apps/
- Authentication: https://docs.microsoft.com/azure/static-web-apps/authentication-authorization
- GitHub Actions: https://docs.github.com/actions

## Alternative: Deploy Without Azure

If you want to avoid Azure, you can deploy to:

### Vercel (FREE):
```bash
npm install -g vercel
cd frontend
vercel
```

### Netlify (FREE):
```bash
npm install -g netlify-cli
cd frontend
npm run build
netlify deploy
```

Both support authentication and are completely free for small apps!
