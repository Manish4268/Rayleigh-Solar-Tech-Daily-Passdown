"""
Rayleigh Solar Tech Daily Passdown System - Main Application
Single backend server with modular architecture

This is the main entry point that imports modular APIs:
- charts_api: Handles all chart-related functionality
- data_management_api: Handles all CRUD operations for safety, kudos, and issues
"""

import os
import sys

# Ensure we're working from the correct directory for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
os.chdir(current_dir)

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import modular API modules
from charts_api import charts_api
from data_management_api import data_api
from upload_data_api import upload_api
from analysis_api import process_excel_analysis
from stability_api import stability_api

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
            "Chart Data API",
            "Excel/CSV Analysis API"
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

@app.route('/api/safety/<issue_id>', methods=['PUT'])
def update_safety_issue(issue_id):
    from flask import request
    return data_api.update_safety_issue(issue_id, request.get_json())

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

# ==================== STABILITY ENDPOINTS ====================

@app.route('/api/stability/grid-data', methods=['GET'])
def get_stability_grid_data():
    """Get all stability grid data including devices and history"""
    return stability_api.get_grid_data()

@app.route('/api/stability/devices', methods=['GET'])
def get_stability_devices():
    """Get all active stability devices"""
    return stability_api.get_devices()

@app.route('/api/stability/devices', methods=['POST'])
def create_stability_device():
    """Create a new stability device"""
    return stability_api.create_device()

@app.route('/api/stability/devices/<path:device_path>', methods=['PUT'])
def update_stability_device(device_path):
    """Update stability device by position"""
    return stability_api.device_by_position(device_path)

@app.route('/api/stability/devices/<path:device_path>', methods=['DELETE'])
def delete_stability_device(device_path):
    """Delete stability device by position (soft delete)"""
    return stability_api.device_by_position(device_path)

@app.route('/api/stability/history/<path:device_path>', methods=['GET'])
def get_stability_history(device_path):
    """Get history for specific stability slot"""
    return stability_api.get_history(device_path)

@app.route('/api/stability/check-expired', methods=['GET'])
def check_expired_devices():
    """Check for devices that have exceeded their time_hours"""
    return stability_api.check_expired_devices()

@app.route('/api/stability/process-expired', methods=['POST'])
def process_expired_devices():
    """Process expired devices automatically and return details"""
    return stability_api.process_expired_devices()

# ==================== ANALYSIS ENDPOINTS ====================

@app.route('/api/analysis/process', methods=['POST'])
def process_analysis():
    """Process Excel/CSV file for analysis"""
    from flask import request, jsonify
    import tempfile
    import os
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        
        # Get processing options from form data
        options = {}
        try:
            options['sheetsMode'] = request.form.get('sheetsMode', 'top-k')
            options['sheetsTopK'] = int(request.form.get('sheetsTopK', 6))
            options['devicesMode'] = request.form.get('devicesMode', 'top-k')
            options['devicesTopK'] = int(request.form.get('devicesTopK', 6))
            options['pixelsPerDevice'] = int(request.form.get('pixelsPerDevice', 3))
            options['method'] = request.form.get('method', 'minimize-sd')
            options['basis'] = request.form.get('basis', 'forward')
            options['useAllSheets'] = request.form.get('useAllSheets', 'true').lower() == 'true'
            options['sheetIds'] = request.form.get('sheetIds', '')
        except (ValueError, TypeError) as e:
            return jsonify({"status": "error", "message": f"Invalid options format: {str(e)}"}), 400
        
        # Save uploaded file temporarily
        tmp_file = None
        try:
            # Determine file extension
            if file.filename.lower().endswith(('.xlsx', '.xls')):
                suffix = '.xlsx'
            elif file.filename.lower().endswith('.csv'):
                suffix = '.csv'
            else:
                suffix = '.xlsx'  # Default fallback
            
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            file.save(tmp_file.name)
            tmp_file.close()  # Close file handle before processing
            
            # Process the file
            result = process_excel_analysis(tmp_file.name, options)
            
            # Add filename to result
            result['fileName'] = file.filename
            
            return jsonify(result)
            
        finally:
            # Safe cleanup - try to delete temp file if it exists
            if tmp_file and os.path.exists(tmp_file.name):
                try:
                    os.unlink(tmp_file.name)
                except Exception:
                    # If deletion fails, just log it - don't crash the request
                    print(f"⚠️ Could not delete temporary file: {tmp_file.name}")
                    pass
            
    except Exception as e:
        import traceback
        error_msg = f"Unexpected error: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"❌ ANALYSIS ERROR: {error_msg}")
        print(f"📋 TRACEBACK:\n{traceback_str}")
        
        return jsonify({
            "status": "error", 
            "message": error_msg,
            "logs": [error_msg, f"Traceback: {traceback_str}"]
        }), 500

@app.route('/api/analysis/download', methods=['POST'])
def download_analysis_results():
    """Generate and download analysis results as separate Excel files"""
    from flask import request, jsonify, send_file
    import tempfile
    import os
    import pandas as pd
    from datetime import datetime
    from analysis_api import stored_results
    
    try:
        # Get the file type from request
        data = request.get_json() or {}
        file_type = data.get('fileType', 'quick')  # 'quick' or 'entire'
        
        print(f"🔍 Download request received - fileType: {file_type}")
        print(f"📝 Request data: {data}")
        
        # Check if we have stored results
        if stored_results is None:
            print("❌ No stored results available")
            return jsonify({"status": "error", "message": "No analysis results available. Please run analysis first."}), 400
        
        quick_df = stored_results.get('quick_data')
        entire_df = stored_results.get('entire_data')
        
        if quick_df is None or quick_df.empty:
            return jsonify({"status": "error", "message": "No Quick Data available"}), 400
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create temporary file
        if file_type == 'entire':
            if entire_df is None or entire_df.empty:
                return jsonify({"status": "error", "message": "No Entire Data available"}), 400
            
            filename = f"Entire_Data_{timestamp}.xlsx"
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                    entire_df.to_excel(writer, sheet_name='Entire_Data', index=False)
                    
                    # Auto-adjust column widths
                    workbook = writer.book
                    worksheet = writer.sheets['Entire_Data']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                return send_file(
                    tmp_file.name,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        else:
            # Default to quick data
            filename = f"Quick_Data_{timestamp}.xlsx"
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                    quick_df.to_excel(writer, sheet_name='Quick_Data', index=False)
                    
                    # Auto-adjust column widths
                    workbook = writer.book
                    worksheet = writer.sheets['Quick_Data']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                return send_file(
                    tmp_file.name,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            
    except Exception as e:
        import traceback
        error_msg = f"Download error: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"❌ DOWNLOAD ERROR: {error_msg}")
        print(f"📋 TRACEBACK:\n{traceback_str}")
        
        return jsonify({
            "status": "error", 
            "message": error_msg
        }), 500

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
    print("  ✅ Excel/CSV Analysis API (analysis_api.py)")
    print("  ✅ Stability Dashboard API (stability_api.py)")
    print("\n🔧 Manual Reset: POST /api/reset-today")
    print("🏥 Health Check: GET /api/health")
    print("📊 Analysis Processing: POST /api/analysis/process")
    print("📥 Download Results: POST /api/analysis/download")
    print("🔬 Stability Grid: GET /api/stability/grid-data")
    print("⚗️ Device Management: /api/stability/devices")
    print("=" * 60)
    app.run(host='0.0.0.0', port=7071, debug=False)
