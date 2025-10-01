import azure.functions as func
import json
import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, YesterdayModel

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get sr_no from route parameters
        sr_no = req.route_params.get('sr_no')
        if not sr_no:
            return func.HttpResponse(
                json.dumps({"error": "sr_no parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        try:
            sr_no = int(sr_no)
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid sr_no parameter"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
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
        
        # Update entry
        success = yesterday_model.update(
            sr_no=sr_no,
            description=req_body.get('description'),
            resolved=req_body.get('resolved'),
            who=req_body.get('who'),
            whom=req_body.get('whom'),
            resolved_status=req_body.get('resolved_status')
        )
        
        if success:
            # Get updated entry
            updated_entry = yesterday_model.get_by_sr_no(sr_no)
            if updated_entry and 'timestamp' in updated_entry:
                updated_entry['timestamp'] = updated_entry['timestamp'].isoformat()
            
            return func.HttpResponse(
                json.dumps(updated_entry if updated_entry else {"message": "Entry updated successfully"}),
                status_code=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": f"Entry with sr_no {sr_no} not found or no changes made"}),
                status_code=404,
                mimetype="application/json"
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