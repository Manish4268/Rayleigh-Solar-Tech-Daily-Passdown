# Modular Backend Architecture

## Overview
Restructured backend into a single-server deployment with modular code organization for easy future Azure Functions migration.

## Architecture Changes

### Before (Azure Functions Approach - Abandoned)
- ❌ Two separate Azure Function apps (charts + data)
- ❌ Separate local servers on ports 7071 and 7072
- ❌ Port conflicts and server instability
- ❌ Complex local development setup

### After (Modular Single Backend - Current)
- ✅ Single Flask server on port 7071
- ✅ Modular code in separate files
- ✅ Easy to test and develop locally
- ✅ Ready for future Azure Functions conversion

## File Structure

```
backend/
├── passdown_app.py              # Main Flask server with route definitions
├── charts_api.py                # Chart data processing (modular)
├── data_management_api.py       # CRUD operations for all data (modular)
├── data_processor.py            # Excel data processing utilities
└── .env                         # Environment variables
```

## Module Breakdown

### 1. charts_api.py
**Purpose:** All chart-related functionality separated for future Azure Functions deployment

**Endpoints Handled:**
- `GET /api/charts/parameters` - List available chart parameters
- `GET /api/charts/data/<parameter>` - Get chart data for specific parameter
- `GET /api/charts/device-yield` - Device yield with quantiles and batch averages
- `GET /api/charts/iv-repeatability` - IV repeatability daily averages

**Key Functions:**
```python
charts_api.get_parameters()
charts_api.get_chart_data(parameter)
charts_api.get_device_yield_data()
charts_api.get_iv_repeatability_data()
```

### 2. data_management_api.py
**Purpose:** All CRUD operations for safety issues, kudos, and top issues

**Endpoints Handled:**
- `GET/POST/DELETE /api/safety` - Safety issues management
- `GET/POST/DELETE /api/kudos` - Kudos management
- `GET/POST/DELETE /api/today` - Today's top issues
- `GET/PUT/DELETE /api/yesterday` - Yesterday's top issues
- `POST /api/reset-today` - Reset today's issues

**Key Class:**
```python
class DataManagementAPI:
    - get_all_safety_issues()
    - create_safety_issue(data)
    - delete_safety_issue(issue_id)
    - get_all_kudos()
    - create_kudos(data)
    - delete_kudos(kudos_id)
    - get_all_today_issues()
    - create_today_issue(data)
    - delete_today_issue(issue_id)
    - get_all_yesterday_issues()
    - update_yesterday_issue(issue_id, data)
    - delete_yesterday_issue(issue_id)
    - reset_today_issues()
```

### 3. passdown_app.py
**Purpose:** Main Flask server that imports and uses the modular APIs

**Structure:**
```python
from charts_api import charts_api
from data_management_api import data_api

# Route definitions that delegate to modules
@app.route('/api/charts/parameters')
def get_chart_parameters():
    return charts_api.get_parameters()

@app.route('/api/safety', methods=['GET'])
def get_safety_issues():
    return data_api.get_all_safety_issues()
```

## Frontend Configuration

### Updated API Configuration (frontend/src/lib/api.js)
```javascript
// Before (Dual Azure Functions)
const CHARTS_API_URL = 'http://localhost:7071/api';
const DATA_API_URL = 'http://localhost:7072/api';

// After (Single Backend)
const API_BASE_URL = 'http://localhost:7071/api';
```

All API calls now point to single backend with proper endpoint paths.

## Running the Application

### Start Backend Server
```powershell
cd backend
python passdown_app.py
```
Server runs on: `http://localhost:7071`

### Start Frontend
```powershell
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

## API Endpoints

### Data Management (data_management_api.py)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/safety | Get all safety issues |
| POST | /api/safety | Create safety issue |
| DELETE | /api/safety/{id} | Delete safety issue |
| GET | /api/kudos | Get all kudos |
| POST | /api/kudos | Create kudos |
| DELETE | /api/kudos/{id} | Delete kudos |
| GET | /api/today | Get today's issues |
| POST | /api/today | Create today's issue |
| DELETE | /api/today/{id} | Delete today's issue |
| GET | /api/yesterday | Get yesterday's issues |
| PUT | /api/yesterday/{id} | Update yesterday's issue |
| DELETE | /api/yesterday/{id} | Delete yesterday's issue |
| POST | /api/reset-today | Reset today's issues |

### Chart Data (charts_api.py)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/charts/parameters | Get available parameters |
| GET | /api/charts/data/{param} | Get chart data for parameter |
| GET | /api/charts/device-yield | Get device yield data |
| GET | /api/charts/iv-repeatability | Get IV repeatability data |

## Benefits of This Architecture

### 1. **Simplicity**
- Single server process to run
- No port conflicts
- Easier debugging

### 2. **Modularity**
- Clear separation of concerns
- Charts and data logic in separate files
- Easy to maintain and update

### 3. **Future-Ready**
- Each module (charts_api.py, data_management_api.py) can easily become an Azure Function
- Minimal code changes needed for migration
- Functions are already organized by responsibility

### 4. **Development Experience**
- Fast local development
- Single command to start backend
- No complex multi-process setup

## Future Azure Functions Migration

When ready to deploy to Azure Functions:

### Step 1: Create Azure Function Apps
1. Create `charts-function-app` in Azure
2. Create `data-function-app` in Azure

### Step 2: Adapt Modules
Each module is already organized with proper separation:
- Copy `charts_api.py` logic to charts function
- Copy `data_management_api.py` logic to data function
- Add Azure Functions decorators and HTTP triggers

### Step 3: Update Frontend
Update `API_BASE_URL` to point to Azure Function URLs:
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-app.azurewebsites.net/api'
  : 'http://localhost:7071/api';
```

## Removed/Archived

The following Azure Functions code was created but abandoned:
- `azure-functions/charts-function-app/` - Complete charts Azure Function
- `azure-functions/data-management-function-app/` - Complete data Azure Function
- `azure-functions/charts_local_server.py` - Local Flask wrapper for charts
- `azure-functions/data_local_server.py` - Local Flask wrapper for data

These can be deleted or kept as reference for future migration.

## Summary

✅ **Single backend server** with modular code organization
✅ **Simplified development** - one command to start backend
✅ **Future-proof** - ready for Azure Functions when needed
✅ **Working frontend** - properly configured to connect to backend
✅ **Clear separation** - charts vs data management in separate files
