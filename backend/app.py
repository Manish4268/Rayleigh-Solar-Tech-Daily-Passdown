"""
Rayleigh Solar Tech Daily Passdown System - Main Application
Single backend server with modular architecture

This is the main entry point that imports modular APIs:
- charts_api: Handles all chart-related functionality
- data_management_api: Handles all CRUD operations for safety, kudos, and issues
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import modular API modules
from charts_api import charts_api
from data_management_api import data_api
from upload_data_api import upload_api

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    from flask import jsonify
    from datetime import datetime
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "Passdown API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": "connected" if data_api.db is not None else "disconnected",
        "features": [
            "Safety Issues Management",
            "Kudos Management",
            "Today's Top Issues",
            "Yesterday's Top Issues",
            "Chart Data API"
        ]
    }), 200

# ==================== DATA MANAGEMENT ENDPOINTS ====================

# Safety Issues
@app.route('/api/safety', methods=['GET'])
def get_safety_issues():
    return data_api.get_all_safety_issues()

@app.route('/api/safety', methods=['POST'])
def create_safety_issue():
    from flask import request
    return data_api.create_safety_issue(request.get_json())

@app.route('/api/safety/<issue_id>', methods=['DELETE'])
def delete_safety_issue(issue_id):
    return data_api.delete_safety_issue(issue_id)

# Kudos
@app.route('/api/kudos', methods=['GET'])
def get_kudos():
    return data_api.get_all_kudos()

@app.route('/api/kudos', methods=['POST'])
def create_kudos():
    from flask import request
    return data_api.create_kudos(request.get_json())

@app.route('/api/kudos/<kudos_id>', methods=['DELETE'])
def delete_kudos(kudos_id):
    return data_api.delete_kudos(kudos_id)

# Today's Issues
@app.route('/api/today', methods=['GET'])
def get_today_issues():
    return data_api.get_all_today_issues()

@app.route('/api/today', methods=['POST'])
def create_today_issue():
    from flask import request
    return data_api.create_today_issue(request.get_json())

@app.route('/api/today/<issue_id>', methods=['PUT'])
def update_today_issue(issue_id):
    from flask import request
    return data_api.update_today_issue(issue_id, request.get_json())

@app.route('/api/today/<issue_id>', methods=['DELETE'])
def delete_today_issue(issue_id):
    return data_api.delete_today_issue(issue_id)

# Yesterday's Issues
@app.route('/api/yesterday', methods=['GET'])
def get_yesterday_issues():
    return data_api.get_all_yesterday_issues()

@app.route('/api/yesterday', methods=['POST'])
def create_yesterday_issue():
    from flask import request
    return data_api.create_yesterday_issue(request.get_json())

@app.route('/api/yesterday/<issue_id>', methods=['PUT'])
def update_yesterday_issue(issue_id):
    from flask import request
    return data_api.update_yesterday_issue(issue_id, request.get_json())

@app.route('/api/yesterday/<issue_id>', methods=['DELETE'])
def delete_yesterday_issue(issue_id):
    return data_api.delete_yesterday_issue(issue_id)

# Manual reset endpoint
@app.route('/api/reset-today', methods=['POST'])
def manual_reset_today():
    return data_api.reset_today_issues()

# ==================== CHART ENDPOINTS ====================

@app.route('/api/charts/parameters', methods=['GET'])
def get_chart_parameters():
    """Get list of available chart parameters."""
    return charts_api.get_parameters()

@app.route('/api/charts/data/<parameter>', methods=['GET'])
def get_chart_data(parameter):
    """Get chart data for a specific parameter."""
    return charts_api.get_chart_data(parameter)

@app.route('/api/charts/device-yield', methods=['GET'])
def get_device_yield_data():
    """Get device yield data with 2.5% quantiles and batch averages."""
    return charts_api.get_device_yield_data()

@app.route('/api/charts/iv-repeatability', methods=['GET'])
def get_iv_repeatability_data():
    """Get IV repeatability data with daily averages for last 10 days."""
    return charts_api.get_iv_repeatability_data()

@app.route('/api/storage/check-connection', methods=['GET'])
def make_connection_check():
    """Get IV repeatability data with daily averages for last 10 days."""
    return charts_api.get_iv_repeatability_data()

# ==================== UPLOAD DATA ENDPOINTS ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file to Azure Blob Storage"""
    return upload_api.upload_file()

# ==================== START SERVER ====================

if __name__ == '__main__':
    print("🚀 Starting Modular Passdown API Server")
    print("=" * 60)
    print("📊 Features Available:")
    print("  ✅ Safety Issues Management (data_management_api.py)")
    print("  ✅ Kudos Management (data_management_api.py)")
    print("  ✅ Today's Top Issues (data_management_api.py)")
    print("  ✅ Yesterday's Top Issues (data_management_api.py)")
    print("  ✅ Chart Data API (charts_api.py)")
    print("\n🔧 Manual Reset: POST /api/reset-today")
    print("🏥 Health Check: GET /api/health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=7071, debug=False)
