import azure.functions as func
import json
import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, YesterdayModel

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
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
        
        # Get query parameters
        sr_no = req.params.get('sr_no')
        
        if sr_no:
            # Get specific entry by sr_no
            try:
                sr_no = int(sr_no)
                entry = yesterday_model.get_by_sr_no(sr_no)
                if entry:
                    # Convert datetime to string for JSON serialization
                    if 'timestamp' in entry:
                        entry['timestamp'] = entry['timestamp'].isoformat()
                    
                    return func.HttpResponse(
                        json.dumps(entry),
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
                        json.dumps({"error": f"Entry with sr_no {sr_no} not found"}),
                        status_code=404,
                        mimetype="application/json"
                    )
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid sr_no parameter"}),
                    status_code=400,
                    mimetype="application/json"
                )
        else:
            # Get all entries
            entries = yesterday_model.get_all()
            
            # Convert datetime objects to strings for JSON serialization
            for entry in entries:
                if 'timestamp' in entry:
                    entry['timestamp'] = entry['timestamp'].isoformat()
            
            return func.HttpResponse(
                json.dumps(entries),
                status_code=200,
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