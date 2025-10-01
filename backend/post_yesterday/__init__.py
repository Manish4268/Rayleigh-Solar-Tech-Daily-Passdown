import azure.functions as func
import json
import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, YesterdayModel

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        required_fields = ['description', 'resolved', 'who', 'whom', 'resolved_status']
        missing_fields = [field for field in required_fields if field not in req_body]
        
        if missing_fields:
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Initialize database connection
        db_manager = DatabaseManager()
        if not db_manager.connect():
            return func.HttpResponse(
                json.dumps({"error": "Database connection failed"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Initialize Yesterday model
        yesterday_model = YesterdayModel(db_manager)
        
        # Create new entry
        new_entry = yesterday_model.create(
            description=req_body['description'],
            resolved=req_body['resolved'],
            who=req_body['who'],
            whom=req_body['whom'],
            resolved_status=req_body['resolved_status']
        )
        
        # Convert datetime to string for JSON serialization
        if 'timestamp' in new_entry:
            new_entry['timestamp'] = new_entry['timestamp'].isoformat()
        
        return func.HttpResponse(
            json.dumps(new_entry),
            status_code=201,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
    
    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()