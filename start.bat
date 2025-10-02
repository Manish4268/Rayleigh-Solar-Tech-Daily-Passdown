@echo off
REM Enhanced Development Startup Script for Rayleigh Solar Tech Daily Passdown

echo 🚀 Starting Rayleigh Solar Tech Daily Passdown - Enhanced Version
echo ==================================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js/npm is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Start backend server
echo 🐍 Starting Backend Server...
cd backend
start "Backend Server" python passdown_app.py
echo ✅ Backend server started

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend development server
echo ⚛️  Starting Frontend Development Server...
cd ../frontend
start "Frontend Server" npm run dev
echo ✅ Frontend server started

echo.
echo 🎉 Both servers are starting up!
echo ==================================================================
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend:  http://localhost:7071
echo 🩺 Health:   http://localhost:7071/api/health
echo ==================================================================
echo.
echo 📋 New Features Available:
echo   ✅ Today → Yesterday workflow automation
echo   ✅ Enhanced Kudos with 'By Whom' field
echo   ✅ Scrollable tables with sticky headers
echo   ✅ Smart filtering for Top Issues
echo   ✅ Individual table refresh
echo   ✅ Performance optimizations
echo.
echo ⚡ Close this window or press Ctrl+C to stop
echo 🌐 Opening application in browser...

REM Wait a moment then open browser
timeout /t 5 /nobreak >nul
start http://localhost:5173

pause