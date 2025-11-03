# Authentication Flow Documentation

## User Journey

```
┌─────────────────────────────────────────────────────────────┐
│                    User Opens App                            │
│                http://localhost:5173                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Is User Authenticated? │
              └──────────┬────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
           NO                        YES
            │                         │
            ▼                         ▼
    ┌───────────────┐        ┌──────────────────┐
    │  Login Page   │        │   Main Dashboard │
    └───────┬───────┘        │  (Full Access)   │
            │                └──────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌──────────┐
│  Login  │    │  Signup  │
└────┬────┘    └─────┬────┘
     │               │
     │               ▼
     │    ┌──────────────────────┐
     │    │ Enter:               │
     │    │ - Full Name          │
     │    │ - Email*             │
     │    │ - Password (min 6)   │
     │    │ - Confirm Password   │
     │    └──────────┬───────────┘
     │               │
     │               ▼
     │    ┌──────────────────────┐
     │    │ Validate Email:      │
     │    │ Must end with:       │
     │    │ @rayleighsolartech   │
     │    │         .com         │
     │    └──────────┬───────────┘
     │               │
     │          ┌────┴─────┐
     │          │          │
     │        PASS       FAIL
     │          │          │
     │          ▼          ▼
     │    ┌─────────┐  ┌────────┐
     │    │ Create  │  │ Error  │
     │    │ Account │  │Message │
     │    └────┬────┘  └────────┘
     │         │
     │         ▼
     └────►┌─────────────────┐
           │ Login with      │
           │ Email+Password  │
           └────────┬────────┘
                    │
           ┌────────┴────────┐
           │                 │
        SUCCESS           FAIL
           │                 │
           ▼                 ▼
    ┌─────────────┐    ┌──────────┐
    │  Dashboard  │    │  Error   │
    │  (Logged)   │    │ Message  │
    └─────────────┘    └──────────┘
```

## Email Validation Rules

### Accepted Format:
✅ `yourname@rayleighsolartech.com`
✅ `first.last@rayleighsolartech.com`
✅ `department@rayleighsolartech.com`

### Rejected Formats:
❌ `user@gmail.com` (wrong domain)
❌ `user@rayleigh.com` (wrong domain)
❌ `user@rayleighsolar.com` (wrong domain)
❌ `user@company.com` (wrong domain)
❌ `plaintext` (not an email)

## Security Layers

```
┌─────────────────────────────────────────┐
│         Layer 1: Frontend              │
│  - Email domain validation              │
│  - Password length check (min 6)        │
│  - Password confirmation match          │
│  - Duplicate email prevention           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Layer 2: Local Storage         │
│  - User credentials stored locally      │
│  - Session persistence                  │
│  - Auto-logout on clear storage         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Layer 3: Optional (Production)      │
│  - Backend API validation               │
│  - Database storage                     │
│  - Password hashing (bcrypt)            │
│  - JWT tokens                           │
│  - Azure AD integration                 │
└─────────────────────────────────────────┘
```

## Data Storage

### localStorage Structure:

```javascript
// User Registry (all registered users)
localStorage.setItem('registeredUsers', JSON.stringify({
  "john@rayleighsolartech.com": {
    name: "John Doe",
    password: "password123",
    email: "john@rayleighsolartech.com",
    createdAt: "2025-10-23T10:30:00.000Z"
  },
  "jane@rayleighsolartech.com": {
    name: "Jane Smith",
    password: "secure456",
    email: "jane@rayleighsolartech.com",
    createdAt: "2025-10-23T11:45:00.000Z"
  }
}));

// Current Session
localStorage.setItem('isAuthenticated', 'true');
localStorage.setItem('userEmail', 'john@rayleighsolartech.com');
localStorage.setItem('userName', 'John Doe');
```

## Component Architecture

```
App.jsx (Main Container)
│
├── Authentication Check
│   ├── isCheckingAuth → Loading Spinner
│   ├── isAuthenticated = false → Login/Signup
│   └── isAuthenticated = true → Dashboard
│
├── Login Component
│   ├── Email Input (validated)
│   ├── Password Input
│   ├── Login Button
│   ├── Azure AD Button (optional)
│   ├── GitHub Button (optional)
│   └── "Create Account" Link → Signup
│
├── Signup Component
│   ├── Name Input
│   ├── Email Input (validated)
│   ├── Password Input (min 6 chars)
│   ├── Confirm Password Input
│   ├── Create Account Button
│   ├── Success Dialog
│   └── "Back to Login" Link
│
└── Main Dashboard
    ├── Navbar (with logout)
    ├── All existing features
    └── Protected routes
```

## State Management

```javascript
// App.jsx states
const [isAuthenticated, setIsAuthenticated] = useState(false)
const [isCheckingAuth, setIsCheckingAuth] = useState(true)
const [showSignup, setShowSignup] = useState(false)

// Login.jsx states
const [credentials, setCredentials] = useState({
  email: '',
  password: ''
})
const [error, setError] = useState('')

// Signup.jsx states
const [formData, setFormData] = useState({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const [error, setError] = useState('')
const [showSuccess, setShowSuccess] = useState(false)
```

## Migration Path to Production

### Phase 1: Current (Local Storage) ✅
- User data in browser
- Email validation
- Password protection
- Works offline

### Phase 2: Backend API (Recommended Next)
```python
# backend/auth_api.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Validate email domain
    if not data['email'].endswith('@rayleighsolartech.com'):
        return jsonify({'error': 'Invalid email domain'}), 403
    
    # Hash password
    hashed = generate_password_hash(data['password'])
    
    # Store in MongoDB
    user = {
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'created_at': datetime.utcnow()
    }
    users_collection.insert_one(user)
    
    return jsonify({'success': True}), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = users_collection.find_one({'email': data['email']})
    
    if user and check_password_hash(user['password'], data['password']):
        token = jwt.encode({'email': user['email']}, SECRET_KEY)
        return jsonify({'token': token, 'name': user['name']})
    
    return jsonify({'error': 'Invalid credentials'}), 401
```

### Phase 3: Azure AD Integration
- Single Sign-On (SSO)
- Microsoft 365 integration
- Enterprise security
- No password management needed

## Testing Script

```bash
# Test 1: Invalid email domain
Email: test@gmail.com
Expected: Error "Only @rayleighsolartech.com emails allowed"

# Test 2: Valid signup
Email: john@rayleighsolartech.com
Password: secure123
Expected: Success, redirect to login

# Test 3: Duplicate email
Email: john@rayleighsolartech.com (same as test 2)
Expected: Error "Account already exists"

# Test 4: Short password
Password: 12345
Expected: Error "Password must be at least 6 characters"

# Test 5: Password mismatch
Password: password123
Confirm: password456
Expected: Error "Passwords do not match"

# Test 6: Successful login
Email: john@rayleighsolartech.com
Password: secure123
Expected: Redirect to dashboard, show user name in navbar

# Test 7: Wrong password
Email: john@rayleighsolartech.com
Password: wrongpass
Expected: Error "Invalid email or password"

# Test 8: Logout
Click logout button
Expected: Redirect to login page, session cleared
```

## Troubleshooting

### Issue: Can't login after signup
**Solution**: Check browser console, verify localStorage has registeredUsers

### Issue: Email validation not working
**Solution**: Check exact spelling of domain: `@rayleighsolartech.com`

### Issue: Session lost on refresh
**Solution**: Check if localStorage is disabled in browser settings

### Issue: Multiple accounts with same email
**Solution**: Clear localStorage and re-register: `localStorage.clear()`

### Issue: Forgot password
**Solution**: Currently no recovery (future feature). Clear localStorage to reset.
