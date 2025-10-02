# 🏭 Rayleigh Solar Tech Daily Passdown System

A streamlined full-stack application for managing daily passdown operations in a solar technology manufacturing environment.

## 📁 Project Structure (Cleaned)

```
Rayleigh-Solar-Tech-Daily-Passdown/
├── backend/
│   ├── passdown_app.py           # Main backend application (renamed from consolidated_api.py)
│   ├── create_demo_data_new.py   # Demo data creator
│   ├── test_connection.py        # Database connection test
│   ├── requirements.txt          # Python dependencies (minimal)
│   ├── .env                      # Database configuration
│   ├── .env.example             # Environment template
│   ├── function.json            # Azure Functions config
│   └── host.json                # Azure Functions host config
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main dashboard (cleaned)
│   │   ├── main.jsx            
│   │   ├── index.css           
│   │   ├── lib/
│   │   │   ├── api.js           # API integration
│   │   │   └── utils.js         # Utilities
│   │   └── components/ui/       # UI components
│   ├── package.json            
│   ├── .env.local              # Frontend config
│   └── vite.config.js          
│
├── README.md                    # Updated documentation
├── start-dev.bat               # Windows startup script
└── start-dev.sh                # Unix startup script
```

## 🚀 Quick Start

### **1. Backend Setup**
```powershell
cd backend

# Test connection
python test_connection.py

# Create demo data
python create_demo_data_new.py

# Start server
python passdown_app.py
```

### **2. Frontend Setup**
```powershell
cd frontend
npm install  # (if needed)
npm run dev
```

## 🎯 Features

### **Dashboard Sections:**
1. **🚨 Near Misses / Safety** - Track safety issues and actions
2. **🏆 Kudos** - Recognize team achievements  
3. **📋 Today's Issues** - Manage current day tasks
4. **📋 Yesterday's Issues** - Review and update previous day items

### **API Endpoints:**
```
GET/POST/DELETE /api/safety      # Safety management
GET/POST/DELETE /api/kudos       # Kudos management  
GET/POST/DELETE /api/today       # Today's issues
GET/POST/PUT/DELETE /api/yesterday  # Yesterday's issues
GET /api/health                  # Health check
```

## 🔧 Configuration

### **Backend (.env):**
```env
MONGODB_CONNECTION_STRING=mongodb+srv://your_credentials@cluster.mongodb.net/
DATABASE_NAME=passdown_db
```

### **Frontend (.env.local):**
```env
VITE_API_BASE_URL=http://localhost:7071/api
```

## 🌐 Deployment Ready

- **Backend:** Ready for Azure Functions deployment
- **Frontend:** Ready for Azure Static Web Apps
- **Database:** MongoDB Atlas (cloud-ready)

## 📊 Key Improvements

✅ **Cleaned codebase** - Removed unnecessary files  
✅ **Single backend file** - `passdown_app.py` handles everything  
✅ **Simplified structure** - Only essential files remain  
✅ **Better naming** - More descriptive file names  
✅ **Production ready** - Optimized for deployment  

## 🛠️ Development

**Start both servers:**
```powershell
# Use the startup script
.\start-dev.bat
```

**Or manually:**
```powershell
# Terminal 1: Backend
cd backend && python passdown_app.py

# Terminal 2: Frontend  
cd frontend && npm run dev
```

The application will be available at:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:7071/api