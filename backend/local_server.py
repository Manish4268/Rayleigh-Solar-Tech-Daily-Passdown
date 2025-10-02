from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, TodayModel, YesterdayModel

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database connection
db_manager = DatabaseManager()

def init_db():
    """Initialize database connection"""
    if not db_manager.connect():
        print("Failed to connect to database")
        return False
    return True

# Today endpoints
@app.route('/api/today', methods=['GET'])
def get_today():
    try:
        today_model = TodayModel(db_manager)
        entries = today_model.get_all()
        # Convert datetime objects to strings for JSON serialization
        for entry in entries:
            if 'timestamp' in entry:
                entry['timestamp'] = entry['timestamp'].isoformat()
        return jsonify(entries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/today', methods=['POST'])
def create_today():
    try:
        data = request.get_json()
        today_model = TodayModel(db_manager)
        result = today_model.create(
            description=data['description'],
            resolved=data['resolved'],
            who=data['who'],
            whom=data['whom']
        )
        # Convert datetime to string for JSON serialization
        if 'timestamp' in result:
            result['timestamp'] = result['timestamp'].isoformat()
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/today/<int:sr_no>', methods=['PUT'])
def update_today(sr_no):
    try:
        data = request.get_json()
        today_model = TodayModel(db_manager)
        result = today_model.update(
            sr_no=sr_no,
            description=data.get('description'),
            resolved=data.get('resolved'),
            who=data.get('who'),
            whom=data.get('whom')
        )
        if result:
            return jsonify({"message": "Entry updated successfully"}), 200
        else:
            return jsonify({"error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/today/<int:sr_no>', methods=['DELETE'])
def delete_today(sr_no):
    try:
        today_model = TodayModel(db_manager)
        result = today_model.delete(sr_no)
        if result:
            return jsonify({"message": "Entry deleted successfully"}), 200
        else:
            return jsonify({"error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Yesterday endpoints
@app.route('/api/yesterday', methods=['GET'])
def get_yesterday():
    try:
        yesterday_model = YesterdayModel(db_manager)
        entries = yesterday_model.get_all()
        # Convert datetime objects to strings for JSON serialization
        for entry in entries:
            if 'timestamp' in entry:
                entry['timestamp'] = entry['timestamp'].isoformat()
        return jsonify(entries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/yesterday', methods=['POST'])
def create_yesterday():
    try:
        data = request.get_json()
        yesterday_model = YesterdayModel(db_manager)
        result = yesterday_model.create(
            description=data['description'],
            resolved=data['resolved'],
            who=data['who'],
            whom=data['whom'],
            resolved_status=data['resolved_status']
        )
        # Convert datetime to string for JSON serialization
        if 'timestamp' in result:
            result['timestamp'] = result['timestamp'].isoformat()
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/yesterday/<int:sr_no>', methods=['PUT'])
def update_yesterday(sr_no):
    try:
        data = request.get_json()
        yesterday_model = YesterdayModel(db_manager)
        result = yesterday_model.update(
            sr_no=sr_no,
            description=data.get('description'),
            resolved=data.get('resolved'),
            who=data.get('who'),
            whom=data.get('whom'),
            resolved_status=data.get('resolved_status')
        )
        if result:
            return jsonify({"message": "Entry updated successfully"}), 200
        else:
            return jsonify({"error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/yesterday/<int:sr_no>', methods=['DELETE'])
def delete_yesterday(sr_no):
    try:
        yesterday_model = YesterdayModel(db_manager)
        result = yesterday_model.delete(sr_no)
        if result:
            return jsonify({"message": "Entry deleted successfully"}), 200
        else:
            return jsonify({"error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Local Flask server running"}), 200

if __name__ == '__main__':
    if init_db():
        print("✅ Database connected successfully")
        print("🚀 Starting local Flask server...")
        print("📡 API endpoints available at: http://localhost:7071/api")
        app.run(host='0.0.0.0', port=7071, debug=True)
    else:
        print("❌ Failed to start server - database connection failed")