# Rayleigh Solar Tech Daily Passdown System - Enhanced Version

A full-stack production dashboard application for managing daily issues and updates in a solar technology manufacturing environment.

## ✨ New Features & Enhancements

### 🔄 Workflow Automation
- **Today → Yesterday Flow**: Items added to "Today" automatically appear in "Top Issues" as incomplete tasks
- **Smart Status Management**: Users can mark items as complete directly in the Top Issues section
- **Intelligent Filtering**: "Show only incomplete" checkbox to focus on active tasks

### � Enhanced Kudos System
- **Attribution Tracking**: New "By Whom" field to track who gave the kudos
- **Complete Information**: Name, Action, and Attribution all captured
- **Enhanced UI**: Improved form with three input fields for comprehensive kudos tracking

### 📊 Improved User Interface
- **Scrollable Tables**: All tables now scroll with max-height of 320px for better data management
- **Sticky Headers**: Table headers remain visible while scrolling through data
- **Enhanced Styling**: Improved borders, rounded corners, and responsive design
- **Individual Refresh**: Tables refresh individually instead of full page reload for better UX

### 🔧 Backend Improvements
- **Robust Validation**: Enhanced data validation across all endpoints
- **Workflow Integration**: Automatic cross-collection updates for Today→Yesterday flow
- **Improved Error Handling**: Consistent error responses and database connection management
- **Performance Optimization**: Individual database connections for reliability

### 🧪 Testing & Quality
- **Comprehensive Test Suite**: Complete API endpoint testing with automated validation
- **Edge Case Testing**: Unicode, special characters, and data validation testing
- **Performance Testing**: Multi-request performance validation
- **Workflow Testing**: Automated testing of the Today→Yesterday workflow

## �🏗️ Architecture

### Backend
- **Python Flask** local development server
- **Azure Functions** for cloud deployment
- **MongoDB Atlas** for data storage
- **CORS** enabled for frontend integration
- **Individual DB connections** for improved reliability

### Frontend
- **React 19** with Vite
- **Tailwind CSS** for styling
- **Radix UI** components
- **Recharts** for data visualization
- **Individual table refresh** for better performance

## 📁 Project Structure

```
├── backend/
│   ├── passdown_app.py          # Main consolidated backend (Flask + Azure Functions)
│   ├── create_demo_data_new.py  # Demo data generator
│   ├── test_connection.py       # Database connection test
│   ├── test_all_endpoints.py    # Comprehensive test suite
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── function.json           # Azure Functions configuration
│   └── host.json               # Azure Functions host config
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main dashboard component
│   │   ├── lib/
│   │   │   ├── api.js          # API integration utilities
│   │   │   └── utils.js        # UI utilities
│   │   └── components/ui/      # Reusable UI components
│   ├── package.json            # Node.js dependencies
│   ├── .env.example           # Environment variables template
│   └── vite.config.js         # Vite configuration
│
├── start.bat                   # Windows startup script
├── start.sh                    # Linux/macOS startup script
└── README.md                   # This file
```

## 🚀 Quick Start

### 🏃‍♂️ Express Setup (Recommended)

Use the startup scripts for the fastest setup:

**Windows:**
```cmd
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

These scripts will automatically:
- ✅ Check prerequisites (Python, Node.js)
- 🐍 Start the backend server on port 7071
- ⚛️ Start the frontend dev server on port 5173
- 🌐 Open the application in your browser

### 📋 Manual Setup

### Prerequisites
- **Node.js 18+** for frontend
- **Python 3.8+** for backend
- **MongoDB Atlas** account and cluster

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and configure
copy .env.example .env
# Edit .env with your MongoDB connection string

# Test database connection
python test_connection.py

# Create demo data (optional)
python create_demo_data_new.py

# Run comprehensive tests
python test_all_endpoints.py

# Start local development server
python passdown_app.py
```

The backend will be available at `http://localhost:7071`

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Copy environment template
copy .env.example .env.local
# .env.local is pre-configured for local development

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables (.env)
```env
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=passdown_db
COLLECTION_TODAY=today_updates
COLLECTION_YESTERDAY=yesterday_updates
```

### Frontend Environment Variables (.env.local)
```env
VITE_API_BASE_URL=http://localhost:7071/api
VITE_DEVELOPMENT_MODE=true
VITE_BACKEND_TYPE=local
```

## 📊 API Endpoints

### Safety Issues
- `GET /api/safety` - Get all safety issues
- `POST /api/safety` - Create a new safety issue
- `DELETE /api/safety/{safety_id}` - Delete a safety issue

### Kudos
- `GET /api/kudos` - Get all kudos entries
- `POST /api/kudos` - Create a new kudos entry
- `DELETE /api/kudos/{kudos_id}` - Delete a kudos entry

### Today's Issues
- `GET /api/today` - Get all today's issues
- `POST /api/today` - Create a new today's issue
- `DELETE /api/today/{issue_id}` - Delete a today's issue

### Yesterday's Issues
- `GET /api/yesterday` - Get all yesterday's issues
- `POST /api/yesterday` - Create a new yesterday's issue
- `PUT /api/yesterday/{issue_id}` - Update a yesterday's issue
- `DELETE /api/yesterday/{issue_id}` - Delete a yesterday's issue

### Health Check
- `GET /api/health` - Check API status

## 🎯 Features

### Dashboard
- **Real-time data** from MongoDB
- **API status indicator** in the navbar
- **Error handling** with user feedback
- **Loading states** for better UX

### Today's Issues Management
- ✅ Create new issues
- ✅ View all issues
- ✅ Delete issues
- 🔄 Auto-refresh data

### Yesterday's Issues Management
- ✅ View yesterday's issues
- ✅ Toggle completion status
- ✅ Delete issues
- 🔍 Filter incomplete items

### Process Information
- Static process data display
- Performance metrics visualization

### Safety & Kudos
- Safety issues tracking
- Team kudos management
- Date-stamped entries

## 🛠️ Development

### Adding New Features

1. **Backend**: Add new endpoints in `local_server.py`
2. **Database**: Update models in `database.py`
3. **Frontend**: Update `src/lib/api.js` for new API calls
4. **UI**: Modify `src/App.jsx` for new interface elements

### Running Tests

```powershell
# Backend database test
cd backend
python test_db.py

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```powershell
# Frontend build
cd frontend
npm run build

# The built files will be in the dist/ directory
```

## 🌐 Deployment

### Current Architecture (MongoDB Atlas + Local Flask)
- **Database:** MongoDB Atlas (cloud-ready)
- **Local Development:** Flask server in `passdown_app.py`
- **Production Ready:** Single file design for easy Azure migration

### Future Azure Migration
The application is designed for seamless Azure migration:

#### Azure Functions (Backend)
```powershell
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Initialize Azure Functions (already configured)
# Deploy to Azure
func azure functionapp publish <your-function-app-name>
```

#### Azure Static Web Apps (Frontend)
1. Build the frontend: `npm run build`
2. Deploy the `dist/` folder to Azure Static Web Apps
3. Configure API routes to point to your Azure Functions

### Environment Variables for Production
```env
# Backend (.env)
MONGODB_CONNECTION_STRING=mongodb+srv://your-cluster@azure.mongodb.net/
DATABASE_NAME=passdown_db

# Frontend (.env.local)
VITE_API_BASE_URL=https://your-function-app.azurewebsites.net/api
```

## 🐛 Troubleshooting

### Common Issues

1. **"API Disconnected"** - Check if backend server is running
2. **CORS errors** - Ensure CORS is properly configured in backend
3. **Database connection fails** - Verify MongoDB connection string
4. **Frontend build fails** - Check Node.js version compatibility

### Debugging Tips

1. Check browser developer console for frontend errors
2. Check backend logs for API errors
3. Test API endpoints directly with curl or Postman
4. Verify environment variables are loaded correctly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation
- Check MongoDB Atlas connectivity
- Verify environment variables