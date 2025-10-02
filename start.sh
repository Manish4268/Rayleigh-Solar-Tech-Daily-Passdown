#!/bin/bash
# Enhanced Development Startup Script for Rayleigh Solar Tech Daily Passdown

echo "🚀 Starting Rayleigh Solar Tech Daily Passdown - Enhanced Version"
echo "=================================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start backend server
echo "🐍 Starting Backend Server..."
cd backend
python passdown_app.py &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# Start frontend development server
echo "⚛️  Starting Frontend Development Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"

echo ""
echo "🎉 Both servers are starting up!"
echo "=================================================================="
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:7071"
echo "🩺 Health:   http://localhost:7071/api/health"
echo "=================================================================="
echo ""
echo "📋 New Features Available:"
echo "  ✅ Today → Yesterday workflow automation"
echo "  ✅ Enhanced Kudos with 'By Whom' field"
echo "  ✅ Scrollable tables with sticky headers"
echo "  ✅ Smart filtering for Top Issues"
echo "  ✅ Individual table refresh"
echo "  ✅ Performance optimizations"
echo ""
echo "⚡ Press Ctrl+C to stop both servers"

# Function to clean up background processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait