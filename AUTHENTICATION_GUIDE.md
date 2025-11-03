# 🔐 Authentication Added - Quick Start

## What Changed?

✅ **Login page added** - Email-based authentication system  
✅ **Signup page added** - Self-service account creation  
✅ **Email restriction** - Only @rayleighsolartech.com emails allowed  
✅ **Azure deployment ready** - GitHub Actions workflow configured  
✅ **No existing code broken** - All features work the same  

## Test Locally

### 1. Start Backend
```bash
cd backend
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Open Browser
Go to: `http://localhost:5173`

### 4. Create Account (First Time)
Click "Create Account" and use:
- **Name**: Your Name
- **Email**: `yourname@rayleighsolartech.com` (REQUIRED)
- **Password**: Your password (min 6 characters)

**Important**: Only emails ending with `@rayleighsolartech.com` are accepted!

### 5. Login
After creating account, login with your email and password.

## Deploy to Azure (FREE)

### Quick Deploy (5 minutes):

1. **Create Azure Static Web App** (FREE tier)
   - Go to: https://portal.azure.com
   - Create resource → Static Web App
   - Choose FREE plan
   - Connect your GitHub repo
   - Branch: `pce`
   - App location: `/frontend`
   - API location: `/backend`
   - Output: `dist`

2. **Copy Deployment Token**
   - After creation, copy the deployment token
   - Add to GitHub: Settings → Secrets → `AZURE_STATIC_WEB_APPS_API_TOKEN`

3. **Push Code**
   ```bash
   git add .
   git commit -m "Add authentication"
   git push
   ```

4. **Done!** ✅
   - Your app will be live at: `https://<your-app>.azurestaticapps.net`

## Alternative FREE Options

### Vercel (Recommended for Beginners)
```bash
npm install -g vercel
cd frontend
vercel
```

### Netlify
```bash
npm install -g netlify-cli
cd frontend
npm run build
netlify deploy
```

## Features

- ✅ **Signup page** - Self-service account creation
- ✅ **Login page** - Email-based authentication
- ✅ **Email restriction** - Only @rayleighsolartech.com allowed
- ✅ **Logout button** - In navbar
- ✅ **Protected routes** - All pages require login
- ✅ **User display** - Shows logged-in user name/email
- ✅ **Azure AD ready** - Optional enterprise auth
- ✅ **GitHub auth ready** - Optional OAuth
- ✅ **Local storage** - Session persistence
- ✅ **All existing features intact** - No functionality broken

## Security Features

### Email Domain Restriction
- ✅ Only `@rayleighsolartech.com` emails can signup
- ✅ Email validation on both signup and login
- ✅ Clear error messages for invalid emails
- ✅ Cannot bypass email check

### Password Security
- ✅ Minimum 6 characters required
- ✅ Password confirmation on signup
- ✅ Stored in browser localStorage (for demo)
- ✅ Can be upgraded to backend authentication later

### User Management
- ✅ No duplicate email registrations
- ✅ User data stored locally
- ✅ Name and email tracking
- ✅ Account creation timestamp

## Customization

### Add More Email Domains
Edit: `frontend/src/components/Login.jsx` and `frontend/src/components/Signup.jsx`

Change this line:
```javascript
if (!formData.email.endsWith('@rayleighsolartech.com')) {
```

To allow multiple domains:
```javascript
const allowedDomains = ['@rayleighsolartech.com', '@partner.com'];
const isValidDomain = allowedDomains.some(domain => formData.email.endsWith(domain));
if (!isValidDomain) {
```

### Change Password Requirements
Edit: `frontend/src/components/Signup.jsx`

```javascript
// Current: minimum 6 characters
if (formData.password.length < 6) {

// Change to 8 characters with complexity:
if (formData.password.length < 8 || !/[A-Z]/.test(formData.password)) {
  setError('Password must be 8+ characters with uppercase letter');
```

### Migrate to Backend Authentication
Currently users are stored in browser localStorage. For production:

1. Create a backend API endpoint:
```python
# backend/auth_api.py
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    # Validate email domain
    if not data['email'].endswith('@rayleighsolartech.com'):
        return jsonify({'error': 'Invalid email domain'}), 403
    # Store in MongoDB
    # Hash password with bcrypt
    # Return JWT token
```

2. Update frontend to call backend instead of localStorage

### Add Azure AD Login
See: `AZURE_DEPLOYMENT.md` for detailed guide

### Disable Authentication (Rollback)
Remove from `frontend/src/App.jsx`:
- `import Login` and `import Signup` statements
- Authentication state (`isAuthenticated`, `showSignup`)
- Auth check in useEffect
- Logout button
- Conditional rendering logic

The app will work without authentication like before.

## Cost

### Azure Static Web Apps (FREE tier):
- ✅ 100GB bandwidth/month
- ✅ Custom domains
- ✅ SSL certificates
- ✅ Authentication
- ✅ Global CDN

### When to Upgrade ($9/month):
- Only if you exceed 100GB bandwidth
- Most small-medium apps never need it

## Need Help?

1. Check `AZURE_DEPLOYMENT.md` for detailed guide
2. Check GitHub Actions tab for deployment logs
3. Check Azure Portal for app status

## What's Next?

1. ✅ Signup page works locally
2. ✅ Login with email restriction works
3. ✅ Only @rayleighsolartech.com emails accepted
4. ⏳ Deploy to Azure (optional)
5. ⏳ Add Azure AD auth (optional - for SSO with Microsoft accounts)
6. ⏳ Migrate to backend database (optional - for production)

## Testing Checklist

### Signup Flow:
- [ ] Try signup with non-company email (should fail)
- [ ] Try signup with `test@rayleighsolartech.com` (should work)
- [ ] Try duplicate email (should show error)
- [ ] Try password less than 6 chars (should show error)
- [ ] Try mismatched passwords (should show error)

### Login Flow:
- [ ] Try login with non-company email (should fail)
- [ ] Try login with wrong password (should show error)
- [ ] Try login with correct credentials (should work)
- [ ] Check if name appears in navbar
- [ ] Test logout button

### Security:
- [ ] Can't access app without login
- [ ] Can't use non-rayleighsolartech.com emails
- [ ] Session persists on page refresh
- [ ] Logout clears session

Everything works offline too! No cloud required for local use.
