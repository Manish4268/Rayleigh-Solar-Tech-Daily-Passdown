"""
Consolidated Backend for Rayleigh Solar Tech Daily Passdown System
Single file containing all API endpoints for Azure Functions deployment

Features:
1. Near Misses / Safety Issues
2. Kudos Management  
3. Yesterday's Top Issues
4. Today's Top Issues
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import threading
import time

# Scheduler imports (legacy - keeping for potential future use)
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    # Note: APScheduler not needed for current startup-only device checking

# Azure Functions imports
try:
    import azure.functions as func
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False

# Detect runtime environment  
# Set to True only when actually running in Azure Functions context
AZURE_FUNCTIONS = AZURE_FUNCTIONS_AVAILABLE and hasattr(func, 'HttpRequest') and '__name__' != '__main__'
AZURE_FUNCTIONS = AZURE_FUNCTIONS_AVAILABLE and hasattr(func, 'HttpRequest') and '__name__' != '__main__'

# Database imports
try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Flask imports for local development
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database models for stability dashboard
try:
    from database import DatabaseManager as StabilityDatabaseManager, StabilityDeviceModel, StabilityHistoryModel
    STABILITY_MODELS_AVAILABLE = True
except ImportError:
    STABILITY_MODELS_AVAILABLE = False
    print("⚠️  Stability models not available - some endpoints may not work")

# Configuration
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'passdown_db')

# Collections for each feature
COLLECTIONS = {
    'safety_issues': 'safety_issues',
    'kudos': 'kudos_entries', 
    'today_issues': 'today_top_issues',
    'yesterday_issues': 'yesterday_top_issues',
    # Stability Dashboard Collections
    'stability_devices': os.getenv('COLLECTION_STABILITY_DEVICES', 'stability_devices'),
    'stability_history': os.getenv('COLLECTION_STABILITY_HISTORY', 'stability_history')
}

class DatabaseManager:
    """Unified database manager for all collections with connection pooling"""
    
    _shared_client = None
    _shared_db = None
    _initialized = False
    
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB Atlas with connection reuse"""
        try:
            # Use shared connection if available and healthy
            if DatabaseManager._shared_client is not None:
                try:
                    # Quick health check on existing connection
                    DatabaseManager._shared_client.admin.command('ping')
                    self.client = DatabaseManager._shared_client
                    self.db = DatabaseManager._shared_db
                    return True
                except:
                    # Connection is stale, will create new one
                    DatabaseManager._shared_client = None
                    DatabaseManager._shared_db = None
            
            if not MONGODB_CONNECTION_STRING:
                raise Exception("MongoDB connection string not found")
                
            self.client = MongoClient(MONGODB_CONNECTION_STRING)
            self.db = self.client[DATABASE_NAME]
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas successfully")
            
            # Store for reuse
            DatabaseManager._shared_client = self.client
            DatabaseManager._shared_db = self.db
            
            # Ensure collections exist only once
            if not DatabaseManager._initialized:
                self._ensure_collections_exist()
                DatabaseManager._initialized = True
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    def _ensure_collections_exist(self):
        """Create collections and indexes if they don't exist"""
        try:
            if self.db is None:
                print("❌ Database not connected")
                return
                
            existing_collections = self.db.list_collection_names()
            for collection_name in COLLECTIONS.values():
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)
                    # Create index on id field for better performance
                    self.db[collection_name].create_index("id", unique=True)
                    print(f"✅ Created collection: {collection_name}")
        except Exception as e:
            print(f"❌ Failed to ensure collections: {str(e)}")
    
    def get_next_id(self, collection_name: str) -> int:
        """Get the next ID for a collection"""
        collection = self.db[collection_name]
        last_doc = collection.find_one(sort=[("id", -1)])
        return (last_doc["id"] + 1) if last_doc else 1
    
    def close(self):
        """Close database connection - but preserve shared connections for performance"""
        # Don't close shared connections to avoid "Cannot use MongoClient after close" errors
        # The shared connection will be managed by the class-level variables
        pass

class PassdownAPI:
    """Main API class handling all four features"""
    
    def __init__(self):
        # Initialize a shared database manager
        self._db_manager_instance = None
    
    def _get_db_connection(self):
        """Get database connection with connection reuse for better performance"""
        if self._db_manager_instance is None:
            self._db_manager_instance = DatabaseManager()
        
        if self._db_manager_instance.connect():
            return self._db_manager_instance
        return None
        
    def _serialize_datetime(self, obj):
        """Convert datetime objects to ISO format strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        return obj
    
    def _create_response(self, data, status_code=200):
        """Create standardized API response"""
        serialized_data = self._serialize_datetime(data)
        
        # Check if we're running in Flask local development mode
        # Import here to avoid circular imports
        try:
            from flask import jsonify
            # If we're in Flask context, return Flask response
            return jsonify(serialized_data), status_code
        except (ImportError, RuntimeError):
            # If Flask is not available or not in Flask context, use Azure Functions response
            if AZURE_FUNCTIONS_AVAILABLE:
                return func.HttpResponse(
                    json.dumps(serialized_data),
                    status_code=status_code,
                    mimetype="application/json",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type"
                    }
                )
            else:
                # Fallback to basic dict response
                return serialized_data
    
    def _get_request_data(self, req):
        """Extract JSON data from request (Azure Functions or Flask)"""
        if AZURE_FUNCTIONS and hasattr(req, 'get_json'):
            return req.get_json()
        elif hasattr(req, 'get_json'):
            return req.get_json()
        else:
            return json.loads(req) if isinstance(req, str) else req
    
    # ============================================================================
    # SAFETY ISSUES ENDPOINTS
    # ============================================================================
    
    def get_safety_issues(self, req=None):
        """GET /api/safety - Get all safety issues"""
        db_manager = None
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['safety_issues']]
            issues = list(collection.find().sort("id", 1))
            
            for issue in issues:
                issue["_id"] = str(issue["_id"])
            
            return self._create_response(issues)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def create_safety_issue(self, req):
        """POST /api/safety - Create new safety issue"""
        db_manager = None
        try:
            data = self._get_request_data(req)
            
            # Validate required fields
            required_fields = ['issue', 'person', 'action']
            if not all(field in data for field in required_fields):
                return self._create_response({"error": "Missing required fields: issue, person, action"}, 400)
            
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['safety_issues']]
            issue_id = db_manager.get_next_id(COLLECTIONS['safety_issues'])
            
            safety_issue = {
                "id": issue_id,
                "issue": data['issue'],
                "person": data['person'],
                "action": data['action'],
                "date": datetime.now().strftime("%m/%d"),
                "timestamp": datetime.now()
            }
            
            result = collection.insert_one(safety_issue)
            safety_issue["_id"] = str(result.inserted_id)
            
            return self._create_response(safety_issue, 201)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def delete_safety_issue(self, req, issue_id):
        """DELETE /api/safety/{id} - Delete safety issue"""
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['safety_issues']]
            result = collection.delete_one({"id": int(issue_id)})
            
            if result.deleted_count > 0:
                return self._create_response({"message": f"Safety issue {issue_id} deleted successfully"})
            else:
                return self._create_response({"error": "Safety issue not found"}, 404)
                
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if 'db_manager' in locals() and db_manager:
                db_manager.close()
    
    # ============================================================================
    # KUDOS ENDPOINTS
    # ============================================================================
    
    def get_kudos(self, req=None):
        """GET /api/kudos - Get all kudos entries"""
        db_manager = None
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['kudos']]
            kudos = list(collection.find().sort("id", 1))
            
            for entry in kudos:
                entry["_id"] = str(entry["_id"])
            
            return self._create_response(kudos)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def create_kudos(self, req):
        """POST /api/kudos - Create new kudos entry"""
        db_manager = None
        try:
            data = self._get_request_data(req)
            
            # Validate required fields
            required_fields = ['name', 'action', 'by_whom']
            if not all(field in data for field in required_fields):
                return self._create_response({"error": "Missing required fields: name, action, by_whom"}, 400)
            
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['kudos']]
            kudos_id = db_manager.get_next_id(COLLECTIONS['kudos'])
            
            kudos_entry = {
                "id": kudos_id,
                "name": data['name'],
                "action": data['action'],
                "by_whom": data['by_whom'],
                "date": datetime.now().strftime("%m/%d"),
                "timestamp": datetime.now()
            }
            
            result = collection.insert_one(kudos_entry)
            kudos_entry["_id"] = str(result.inserted_id)
            
            return self._create_response(kudos_entry, 201)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def delete_kudos(self, req, kudos_id):
        """DELETE /api/kudos/{id} - Delete kudos entry"""
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['kudos']]
            result = collection.delete_one({"id": int(kudos_id)})
            
            if result.deleted_count > 0:
                return self._create_response({"message": f"Kudos entry {kudos_id} deleted successfully"})
            else:
                return self._create_response({"error": "Kudos entry not found"}, 404)
                
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if 'db_manager' in locals() and db_manager:
                db_manager.close()
    
    # ============================================================================
    # TODAY'S ISSUES ENDPOINTS
    # ============================================================================
    
    def get_today_issues(self, req=None):
        """GET /api/today - Get all today's top issues"""
        db_manager = None
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['today_issues']]
            issues = list(collection.find().sort("id", 1))
            
            for issue in issues:
                issue["_id"] = str(issue["_id"])
            
            return self._create_response(issues)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def create_today_issue(self, req):
        """POST /api/today - Create new today's issue (also adds to yesterday for Top Issues)"""
        db_manager = None
        try:
            data = self._get_request_data(req)
            
            # Validate required fields
            required_fields = ['description', 'who']
            if not all(field in data for field in required_fields):
                return self._create_response({"error": "Missing required fields: description, who"}, 400)
            
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            # Add to today's issues
            today_collection = db_manager.db[COLLECTIONS['today_issues']]
            today_issue_id = db_manager.get_next_id(COLLECTIONS['today_issues'])
            
            today_issue = {
                "id": today_issue_id,
                "description": data['description'],
                "who": data['who'],
                "date": datetime.now().strftime("%m/%d"),
                "timestamp": datetime.now()
            }
            
            result = today_collection.insert_one(today_issue)
            today_issue["_id"] = str(result.inserted_id)
            
            # Also add to yesterday's issues (Top Issues) with "done": "No"
            yesterday_collection = db_manager.db[COLLECTIONS['yesterday_issues']]
            yesterday_issue_id = db_manager.get_next_id(COLLECTIONS['yesterday_issues'])
            
            yesterday_issue = {
                "id": yesterday_issue_id,
                "description": data['description'],
                "who": data['who'],
                "done": "No",  # Initially incomplete
                "date": datetime.now().strftime("%m/%d"),
                "timestamp": datetime.now()
            }
            
            yesterday_collection.insert_one(yesterday_issue)
            
            return self._create_response(today_issue, 201)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def delete_today_issue(self, req, issue_id):
        """DELETE /api/today/{id} - Delete today's issue"""
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['today_issues']]
            result = collection.delete_one({"id": int(issue_id)})
            
            if result.deleted_count > 0:
                return self._create_response({"message": f"Today's issue {issue_id} deleted successfully"})
            else:
                return self._create_response({"error": "Today's issue not found"}, 404)
                
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
    
    # ============================================================================
    # YESTERDAY'S ISSUES ENDPOINTS
    # ============================================================================
    
    def get_yesterday_issues(self, req=None):
        """GET /api/yesterday - Get all yesterday's top issues"""
        db_manager = None
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['yesterday_issues']]
            issues = list(collection.find().sort("id", 1))
            
            for issue in issues:
                issue["_id"] = str(issue["_id"])
            
            return self._create_response(issues)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
        finally:
            if db_manager:
                db_manager.close()
    
    def create_yesterday_issue(self, req):
        """POST /api/yesterday - Create new yesterday's issue"""
        try:
            data = self._get_request_data(req)
            
            # Validate required fields
            required_fields = ['description', 'who', 'done']
            if not all(field in data for field in required_fields):
                return self._create_response({"error": "Missing required fields: description, who, done"}, 400)
            
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['yesterday_issues']]
            issue_id = db_manager.get_next_id(COLLECTIONS['yesterday_issues'])
            
            yesterday_issue = {
                "id": issue_id,
                "description": data['description'],
                "who": data['who'],
                "done": data['done'],
                "date": datetime.now().strftime("%m/%d"),
                "timestamp": datetime.now()
            }
            
            result = collection.insert_one(yesterday_issue)
            yesterday_issue["_id"] = str(result.inserted_id)
            
            return self._create_response(yesterday_issue, 201)
            
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
    
    def update_yesterday_issue(self, req, issue_id):
        """PUT /api/yesterday/{id} - Update yesterday's issue (toggle done status)"""
        try:
            data = self._get_request_data(req)
            
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['yesterday_issues']]
            
            update_fields = {}
            if 'done' in data:
                update_fields['done'] = data['done']
            if 'description' in data:
                update_fields['description'] = data['description']
            if 'who' in data:
                update_fields['who'] = data['who']
            
            if update_fields:
                update_fields['timestamp'] = datetime.now()
                result = collection.update_one(
                    {"id": int(issue_id)}, 
                    {"$set": update_fields}
                )
                
                if result.modified_count > 0:
                    return self._create_response({"message": f"Yesterday's issue {issue_id} updated successfully"})
                else:
                    return self._create_response({"error": "Yesterday's issue not found"}, 404)
            else:
                return self._create_response({"error": "No fields to update"}, 400)
                
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
    
    def delete_yesterday_issue(self, req, issue_id):
        """DELETE /api/yesterday/{id} - Delete yesterday's issue"""
        try:
            db_manager = self._get_db_connection()
            if not db_manager:
                return self._create_response({"error": "Database connection failed"}, 500)
            
            collection = db_manager.db[COLLECTIONS['yesterday_issues']]
            result = collection.delete_one({"id": int(issue_id)})
            
            if result.deleted_count > 0:
                return self._create_response({"message": f"Yesterday's issue {issue_id} deleted successfully"})
            else:
                return self._create_response({"error": "Yesterday's issue not found"}, 404)
                
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    def health_check(self, req=None):
        """GET /api/health - Health check endpoint"""
        try:
            db_manager = self._get_db_connection()
            db_status = "connected" if db_manager else "disconnected"
            if db_manager:
                db_manager.close()
            return self._create_response({
                "status": "healthy",
                "message": "Passdown API is running",
                "database": db_status,
                "timestamp": datetime.now().isoformat(),
                "features": [
                    "Safety Issues Management",
                    "Kudos Management", 
                    "Today's Top Issues",
                    "Yesterday's Top Issues"
                ]
            })
        except Exception as e:
            return self._create_response({"error": str(e)}, 500)

# ============================================================================
# AZURE FUNCTIONS ENTRY POINTS
# ============================================================================

# Initialize API instance
api = PassdownAPI()

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main Azure Function entry point"""
    try:
        # Get route and method
        route = req.route_params.get('route', '')
        method = req.method.upper()
        
        # Route to appropriate handler
        if route == 'health':
            return api.health_check(req)
        
        elif route == 'safety':
            if method == 'GET':
                return api.get_safety_issues(req)
            elif method == 'POST':
                return api.create_safety_issue(req)
        
        elif route.startswith('safety/'):
            issue_id = route.split('/')[-1]
            if method == 'DELETE':
                return api.delete_safety_issue(req, issue_id)
        
        elif route == 'kudos':
            if method == 'GET':
                return api.get_kudos(req)
            elif method == 'POST':
                return api.create_kudos(req)
        
        elif route.startswith('kudos/'):
            kudos_id = route.split('/')[-1]
            if method == 'DELETE':
                return api.delete_kudos(req, kudos_id)
        
        elif route == 'today':
            if method == 'GET':
                return api.get_today_issues(req)
            elif method == 'POST':
                return api.create_today_issue(req)
        
        elif route.startswith('today/'):
            issue_id = route.split('/')[-1]
            if method == 'DELETE':
                return api.delete_today_issue(req, issue_id)
        
        elif route == 'yesterday':
            if method == 'GET':
                return api.get_yesterday_issues(req)
            elif method == 'POST':
                return api.create_yesterday_issue(req)
        
        elif route.startswith('yesterday/'):
            issue_id = route.split('/')[-1]
            if method == 'PUT':
                return api.update_yesterday_issue(req, issue_id)
            elif method == 'DELETE':
                return api.delete_yesterday_issue(req, issue_id)
        
        else:
            return func.HttpResponse(
                json.dumps({"error": "Route not found"}),
                status_code=404,
                mimetype="application/json"
            )
            
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

# ============================================================================
# AUTOMATIC DEVICE REMOVAL (STARTUP CHECK)
# ============================================================================

def automatic_device_checker():
    """Check and remove expired devices (called once at startup)"""
    try:
        if not STABILITY_MODELS_AVAILABLE:
            return
            
        print(f"🤖 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running automatic device expiry check...")
        
        # Create API instance and check for expired devices
        api = PassdownAPI()
        db_manager = api._get_db_connection()
        if not db_manager:
            print("❌ Database connection failed during automatic check")
            return
            
        # Create a stability database manager using the working connection
        stability_db = StabilityDatabaseManager()
        stability_db.client = db_manager.client
        stability_db.db = db_manager.db
        
        device_model = StabilityDeviceModel(stability_db)
        
        # Check for expired devices
        expired_devices = device_model.check_expired_devices()
        
        if expired_devices:
            print(f"⚠️  Found {len(expired_devices)} expired devices - processing removal...")
            removed_count = 0
            
            for device in expired_devices:
                success = device_model.soft_delete(
                    section_key=device['section_key'],
                    subsection_key=device['subsection_key'],
                    row=device['row'],
                    col=device['col'],
                    removed_by='system'
                )
                if success:
                    removed_count += 1
                    print(f"✅ Auto-removed device {device['device_id']} from {device['section_key']}/{device['subsection_key']} ({device['row']},{device['col']})")
            
            print(f"🎯 Automatic removal complete: {removed_count}/{len(expired_devices)} devices processed")
        else:
            print("✓ No expired devices found")
            
        # Close connections if needed
        if hasattr(db_manager, 'close_connection'):
            db_manager.close_connection()
        elif hasattr(db_manager, 'close'):
            db_manager.close()
            
    except Exception as e:
        print(f"❌ Error in automatic device checker: {str(e)}")

def setup_startup_device_check():
    """Run device expiry check once at startup only"""
    try:
        # Run the automatic checker once after a short delay to ensure database is ready
        def delayed_startup_check():
            time.sleep(5)  # Wait 5 seconds after startup for database connection
            print("🔍 Running startup device expiry check...")
            removed_count = automatic_device_checker()
            if removed_count and removed_count > 0:
                print(f"✅ Startup check completed: Removed {removed_count} expired device(s)")
            else:
                print("✅ Startup check completed: No expired devices found")
        
        # Run the check in a separate thread to avoid blocking startup
        startup_check_thread = threading.Thread(target=delayed_startup_check, daemon=True)
        startup_check_thread.start()
        
        print("📋 Startup device expiry check scheduled")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup startup device check: {str(e)}")
        return False

# ============================================================================
# FLASK LOCAL DEVELOPMENT SERVER
# ============================================================================

def create_flask_app():
    """Create Flask app for local development"""
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is not available. Install with: pip install flask flask-cors")
    
    app = Flask(__name__)
    CORS(app)
    
    # Initialize API instance
    api = PassdownAPI()
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return api.health_check()
    
    # Safety Issues
    @app.route('/api/safety', methods=['GET', 'POST'])
    def safety_issues():
        if request.method == 'GET':
            return api.get_safety_issues()
        elif request.method == 'POST':
            return api.create_safety_issue(request)
    
    @app.route('/api/safety/<int:safety_id>', methods=['DELETE'])
    def safety_issue_by_id(safety_id):
        return api.delete_safety_issue(request, safety_id)
    
    # Kudos
    @app.route('/api/kudos', methods=['GET', 'POST'])
    def kudos():
        if request.method == 'GET':
            return api.get_kudos()
        elif request.method == 'POST':
            return api.create_kudos(request)
    
    @app.route('/api/kudos/<int:kudos_id>', methods=['DELETE'])
    def kudos_by_id(kudos_id):
        return api.delete_kudos(request, kudos_id)
    
    # Today's Issues
    @app.route('/api/today', methods=['GET', 'POST'])
    def today_issues():
        if request.method == 'GET':
            return api.get_today_issues()
        elif request.method == 'POST':
            return api.create_today_issue(request)
    
    @app.route('/api/today/<int:issue_id>', methods=['DELETE'])
    def today_issue_by_id(issue_id):
        return api.delete_today_issue(request, issue_id)
    
    # Yesterday's Issues
    @app.route('/api/yesterday', methods=['GET', 'POST'])
    def yesterday_issues():
        if request.method == 'GET':
            return api.get_yesterday_issues()
        elif request.method == 'POST':
            return api.create_yesterday_issue(request)
    
    @app.route('/api/yesterday/<int:issue_id>', methods=['PUT', 'DELETE'])
    def yesterday_issue_by_id(issue_id):
        if request.method == 'PUT':
            return api.update_yesterday_issue(request, issue_id)
        elif request.method == 'DELETE':
            return api.delete_yesterday_issue(request, issue_id)
    
    # Stability Dashboard Endpoints
    @app.route('/api/stability/grid-data', methods=['GET'])
    def get_stability_grid_data():
        """Get all stability grid data including devices and history."""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            devices = device_model.get_all()
            
            # Organize devices by grid structure
            grid_data = {
                "LS w/Temp": {
                    "25C": {"rows": 6, "cols": 4, "devices": {}},
                    "45C": {"rows": 6, "cols": 4, "devices": {}},
                    "85C": {"rows": 6, "cols": 4, "devices": {}}
                },
                "Damp Heat": {
                    "": {"rows": 6, "cols": 6, "devices": {}}
                },
                "Outdoor Testing": {
                    "": {"rows": 3, "cols": 4, "devices": {}}
                }
            }
            
            # Populate grid with active devices
            for device in devices:
                section_key = device["section_key"]
                subsection_key = device["subsection_key"]
                row = device["row"]
                col = device["col"]
                slot_key = f"{row}-{col}"
                
                if section_key in grid_data and subsection_key in grid_data[section_key]:
                    grid_data[section_key][subsection_key]["devices"][slot_key] = {
                        "id": device["device_id"],
                        "inDate": device["in_date"][:10] if isinstance(device["in_date"], str) else device["in_date"].strftime("%Y-%m-%d"),
                        "inTime": device.get("in_time", "00:00"),
                        "outDate": device["out_date"][:10] if isinstance(device["out_date"], str) else device["out_date"].strftime("%Y-%m-%d"),
                        "time": device["time_hours"],
                        "duration_hours": device.get("duration_hours", 0),
                        "duration_minutes": device.get("duration_minutes", 0),
                        "duration_seconds": device.get("duration_seconds", 0)
                    }
            
            # Close connections if needed
            if hasattr(db_manager, 'close_connection'):
                db_manager.close_connection()
            elif hasattr(db_manager, 'close'):
                db_manager.close()
                
            return jsonify({
                'success': True,
                'gridData': grid_data
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/devices', methods=['GET', 'POST'])
    def stability_devices():
        """Handle stability device CRUD operations."""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
                
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            history_model = StabilityHistoryModel(stability_db)
            
            if request.method == 'GET':
                devices = device_model.get_all()
                # Close connections if needed
                if hasattr(db_manager, 'close_connection'):
                    db_manager.close_connection()
                elif hasattr(db_manager, 'close'):
                    db_manager.close()
                return jsonify({
                    'success': True,
                    'devices': devices
                })
            
            elif request.method == 'POST':
                data = request.get_json()
                required_fields = ['sectionKey', 'subsectionKey', 'row', 'col', 'deviceId', 'inDate', 'inTime', 'createdBy']
                
                if not all(field in data for field in required_fields):
                    return jsonify({'success': False, 'error': 'Missing required fields'}), 400
                
                # Handle time duration - accept either legacy timeHours or new hours/minutes/seconds format
                time_hours = 0
                if 'timeHours' in data:
                    time_hours = float(data['timeHours'])
                else:
                    # Calculate time_hours from hours, minutes, seconds - ensure all are integers
                    hours = int(data.get('hours', 0)) if data.get('hours', 0) != '' else 0
                    minutes = int(data.get('minutes', 0)) if data.get('minutes', 0) != '' else 0
                    seconds = int(data.get('seconds', 0)) if data.get('seconds', 0) != '' else 0
                    
                    # Validate that at least one component is greater than 0
                    if hours == 0 and minutes == 0 and seconds == 0:
                        return jsonify({'success': False, 'error': 'Duration must be greater than 0. Please enter hours, minutes, or seconds.'}), 400
                    
                    time_hours = hours + (minutes / 60) + (seconds / 3600)
                
                # Ensure minimum duration
                if time_hours <= 0:
                    return jsonify({'success': False, 'error': 'Duration must be greater than 0'}), 400
                
                device = device_model.create(
                    section_key=data['sectionKey'],
                    subsection_key=data['subsectionKey'],
                    row=data['row'],
                    col=data['col'],
                    device_id=data['deviceId'],
                    in_date=data['inDate'],
                    in_time=data['inTime'],
                    time_hours=time_hours,
                    created_by=data['createdBy'],
                    # Store original time components for display - ensure integers
                    time_hours_component=int(data.get('hours', 0)) if data.get('hours', 0) != '' else 0,
                    time_minutes_component=int(data.get('minutes', 0)) if data.get('minutes', 0) != '' else 0,
                    time_seconds_component=int(data.get('seconds', 0)) if data.get('seconds', 0) != '' else 0
                )
                
                # Close connections if needed
                if hasattr(db_manager, 'close_connection'):
                    db_manager.close_connection()
                elif hasattr(db_manager, 'close'):
                    db_manager.close()
                return jsonify({
                    'success': True,
                    'device': device
                }), 201
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/devices/<path:device_path>', methods=['PUT', 'DELETE'])
    def stability_device_by_position(device_path):
        """Update or delete stability device by position."""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Parse the device_path manually to handle forward slashes correctly
            # Expected format: section_key/subsection_key/row/col
            # where section_key might contain forward slashes (like "LS w/Temp")
            
            from urllib.parse import unquote
            # URL decode the entire path first
            decoded_path = unquote(device_path)
            print(f"DEBUG: Received device_path: {device_path}")
            print(f"DEBUG: Decoded device_path: {decoded_path}")
            
            # Split from the right to get row and col first
            path_parts = decoded_path.split('/')
            print(f"DEBUG: Path parts: {path_parts}")
            
            if len(path_parts) < 4:
                return jsonify({'success': False, 'error': 'Invalid device path format'}), 400
            
            # Extract row and col from the end
            try:
                col = int(path_parts[-1])
                row = int(path_parts[-2])
                subsection_key = path_parts[-3]
                # Everything before subsection_key is part of section_key
                section_key = '/'.join(path_parts[:-3])
            except (ValueError, IndexError):
                return jsonify({'success': False, 'error': 'Invalid row/col values'}), 400
            
            print(f"DEBUG: Parsed - section_key='{section_key}', subsection_key='{subsection_key}', row={row}, col={col}")
            
            # Handle empty subsection_key placeholder
            if subsection_key == '_empty_':
                subsection_key = ''
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
                
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            history_model = StabilityHistoryModel(stability_db)
            
            if request.method == 'PUT':
                data = request.get_json()
                
                success = device_model.update(
                    device_id=data.get('deviceId', ''),
                    section_key=section_key,
                    subsection_key=subsection_key,
                    row=row,
                    col=col,
                    new_device_id=data.get('deviceId'),
                    in_date=data.get('inDate'),
                    in_time=data.get('inTime'),
                    time_hours=data.get('timeHours'),
                    updated_by=data.get('updatedBy', 'unknown')
                )
                
                # Close connections if needed
                if hasattr(db_manager, 'close_connection'):
                    db_manager.close_connection()
                elif hasattr(db_manager, 'close'):
                    db_manager.close()
                return jsonify({
                    'success': success,
                    'message': 'Device updated successfully' if success else 'Device not found or no changes made'
                })
            
            elif request.method == 'DELETE':
                data = request.get_json()
                removed_by = data.get('removedBy', 'unknown')
                
                success = device_model.soft_delete(
                    section_key=section_key,
                    subsection_key=subsection_key,
                    row=row,
                    col=col,
                    removed_by=removed_by
                )
                
                # Close connections if needed
                if hasattr(db_manager, 'close_connection'):
                    db_manager.close_connection()
                elif hasattr(db_manager, 'close'):
                    db_manager.close()
                return jsonify({
                    'success': success,
                    'message': 'Device removed successfully' if success else 'Device not found'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/history/<path:device_path>', methods=['GET'])
    def get_stability_history(device_path):
        """Get history for specific stability slot."""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Parse the device_path manually to handle forward slashes correctly
            from urllib.parse import unquote
            decoded_path = unquote(device_path)
            path_parts = decoded_path.split('/')
            
            if len(path_parts) < 4:
                return jsonify({'success': False, 'error': 'Invalid device path format'}), 400
            
            try:
                col = int(path_parts[-1])
                row = int(path_parts[-2])
                subsection_key = path_parts[-3]
                section_key = '/'.join(path_parts[:-3])
            except (ValueError, IndexError):
                return jsonify({'success': False, 'error': 'Invalid row/col values'}), 400
            
            # Handle empty subsection_key placeholder
            if subsection_key == '_empty_':
                subsection_key = ''
                
            db_manager = StabilityDatabaseManager()
            if not db_manager.connect():
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            history_model = StabilityHistoryModel(db_manager)
            history = history_model.get_by_position(section_key, subsection_key, row, col)
            
            # Format history for frontend
            formatted_history = []
            for item in history:
                # Handle date formatting - support both string and datetime objects
                in_date = item.get("in_date", "")
                if hasattr(in_date, 'strftime'):
                    in_date = in_date.strftime("%Y-%m-%d")
                elif isinstance(in_date, str) and len(in_date) >= 10:
                    in_date = in_date[:10]
                
                # Format actual removal time for outDate and outTime display
                actual_removal_time = item.get("actual_removal_time", "")
                actual_out_date = ""
                actual_out_time = ""
                
                if hasattr(actual_removal_time, 'strftime'):
                    actual_out_date = actual_removal_time.strftime("%Y-%m-%d")
                    actual_out_time = actual_removal_time.strftime("%H:%M")
                elif isinstance(actual_removal_time, str) and len(actual_removal_time) >= 16:
                    actual_out_date = actual_removal_time[:10]
                    actual_out_time = actual_removal_time[11:16]
                
                # If no actual removal time, fall back to planned times
                if not actual_out_date:
                    out_date = item.get("out_date", "")
                    if hasattr(out_date, 'strftime'):
                        actual_out_date = out_date.strftime("%Y-%m-%d")
                    elif isinstance(out_date, str) and len(out_date) >= 10:
                        actual_out_date = out_date[:10]
                    actual_out_time = item.get("out_time", "")
                
                # Fix for system removals: actual time should equal planned time
                removal_type = item.get("removal_type", "manual")
                removed_by = item.get("removed_by", "")
                is_system_removal = removal_type == "automatic" or removed_by == "system"
                
                # Calculate planned time in hours from components
                duration_hours = item.get("duration_hours", 0)
                duration_minutes = item.get("duration_minutes", 0) 
                duration_seconds = item.get("duration_seconds", 0)
                total_duration_seconds = item.get("total_duration_seconds", 0)
                
                if total_duration_seconds > 0:
                    planned_time_hours = total_duration_seconds / 3600
                else:
                    planned_time_hours = duration_hours + (duration_minutes / 60) + (duration_seconds / 3600)
                
                # For system removals, set actual time to match planned time
                if is_system_removal:
                    actual_hours_stayed = planned_time_hours
                    actual_days_stayed = planned_time_hours / 24
                    hours_difference = 0  # No difference for system removals
                else:
                    actual_hours_stayed = item.get("actual_hours_stayed", 0)
                    actual_days_stayed = item.get("actual_days_stayed", 0)
                    hours_difference = item.get("hours_difference", 0)
                
                formatted_history.append({
                    "deviceId": item["device_id"],
                    "inDate": in_date,
                    "inTime": item.get("in_time", ""),
                    "outDate": actual_out_date,  # Show actual removal date
                    "outTime": actual_out_time,  # Show actual removal time
                    "plannedTimeHours": item.get("planned_time_hours", item.get("time_hours", planned_time_hours)),
                    "duration_hours": duration_hours,
                    "duration_minutes": duration_minutes,
                    "duration_seconds": duration_seconds,
                    "actualHoursStayed": actual_hours_stayed,
                    "actualDaysStayed": actual_days_stayed,
                    "plannedDays": item.get("planned_days", planned_time_hours / 24),
                    "isEarlyRemoval": item.get("is_early_removal", False),
                    "removalType": removal_type,
                    "hoursDifference": hours_difference,
                    "wasDelayedRemoval": item.get("was_delayed_removal", False),
                    "placedBy": item.get("created_by", "unknown"),
                    "removedBy": item.get("removed_by", "unknown"),
                    "placedAt": item.get("original_created_at", "").isoformat() if hasattr(item.get("original_created_at", ""), 'isoformat') else item.get("original_created_at", ""),
                    "removedAt": item.get("moved_to_history_at", "").isoformat() if hasattr(item.get("moved_to_history_at", ""), 'isoformat') else item.get("moved_to_history_at", ""),
                    "actualRemovalTime": actual_removal_time.strftime("%Y-%m-%d %H:%M:%S") if hasattr(actual_removal_time, 'strftime') else str(actual_removal_time),
                    "systemRemovalTime": item.get("system_removal_time", "").isoformat() if hasattr(item.get("system_removal_time", ""), 'isoformat') else item.get("system_removal_time", ""),
                    "plannedRemovalTime": item.get("planned_removal_time", "").isoformat() if hasattr(item.get("planned_removal_time", ""), 'isoformat') else item.get("planned_removal_time", "")
                })
            
            # Close connections if needed
            if hasattr(db_manager, 'close_connection'):
                db_manager.close_connection()
            elif hasattr(db_manager, 'close'):
                db_manager.close()
            return jsonify({
                'success': True,
                'history': formatted_history
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/auto-remove', methods=['POST'])
    def auto_remove_expired_devices():
        """Automatically remove expired devices based on time_hours"""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
                
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            removed_count = device_model.auto_remove_expired_devices()
            
            # Close connections if needed
            if hasattr(db_manager, 'close_connection'):
                db_manager.close_connection()
            elif hasattr(db_manager, 'close'):
                db_manager.close()
            return jsonify({
                'success': True,
                'message': f'Automatically removed {removed_count} expired devices',
                'removed_count': removed_count
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/process-expired', methods=['POST'])
    def process_expired_devices():
        """Process expired devices automatically and return details of processed devices"""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
                
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            
            # First get list of expired devices before processing
            expired_devices = device_model.check_expired_devices()
            processed_devices = []
            
            for device in expired_devices:
                # Process each expired device
                success = device_model.soft_delete(
                    section_key=device['section_key'],
                    subsection_key=device['subsection_key'],
                    row=device['row'],
                    col=device['col'],
                    removed_by='system'
                )
                if success:
                    processed_devices.append({
                        'deviceId': device['device_id'],
                        'sectionKey': device['section_key'],
                        'subsectionKey': device['subsection_key'],
                        'row': device['row'],
                        'col': device['col'],
                        'processedAt': datetime.utcnow().isoformat()
                    })
            
            # Close connections if needed
            if hasattr(db_manager, 'close_connection'):
                db_manager.close_connection()
            elif hasattr(db_manager, 'close'):
                db_manager.close()
            
            return jsonify({
                'success': True,
                'message': f'Processed {len(processed_devices)} expired devices',
                'processed_count': len(processed_devices),
                'processed_devices': processed_devices
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/stability/check-expired', methods=['GET'])
    def check_expired_devices():
        """Check for devices that have exceeded their time_hours"""
        try:
            if not STABILITY_MODELS_AVAILABLE:
                return jsonify({'success': False, 'error': 'Stability models not available'}), 500
            
            # Use the working database connection from homepage
            api = PassdownAPI()
            db_manager = api._get_db_connection()
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
                
            # Create a stability database manager using the working connection
            stability_db = StabilityDatabaseManager()
            stability_db.client = db_manager.client
            stability_db.db = db_manager.db
            
            device_model = StabilityDeviceModel(stability_db)
            expired_devices = device_model.check_expired_devices()
            
            # Close connections if needed
            if hasattr(db_manager, 'close_connection'):
                db_manager.close_connection()
            elif hasattr(db_manager, 'close'):
                db_manager.close()
            return jsonify({
                'success': True,
                'expired_devices': expired_devices,
                'count': len(expired_devices)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Chart Data Endpoints
    @app.route('/api/charts/parameters', methods=['GET'])
    def get_chart_parameters():
        """Get list of available chart parameters."""
        try:
            from data_processor import get_all_parameters
            parameters = get_all_parameters()
            return jsonify({
                'success': True,
                'parameters': parameters
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/charts/data/<parameter>', methods=['GET'])
    def get_chart_data(parameter):
        """Get chart data for a specific parameter."""
        try:
            from data_processor import get_parameter_data
            data = get_parameter_data(parameter)
            return jsonify({
                'success': True,
                'parameter': parameter,
                'data': data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Parquet Data Endpoints
    @app.route('/api/process-information', methods=['GET'])
    def get_process_info():
        """Get process information data from parquet files using REAL data only."""
        try:
            from real_data_processor import get_process_information
            result = get_process_information()
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f"Real data processor failed: {str(e)}",
                'data': [],
                'source': 'error'
            }), 500
            # COMMENTED OUT: Fallback to simulated data - we only want real data
            # try:
            #     from parquet_processor import get_process_information
            #     result = get_process_information()
            #     return jsonify(result)
            # except Exception as e2:
            #     return jsonify({
            #         'success': False,
            #         'error': f"Both real and simulated processors failed: {str(e)}, {str(e2)}",
            #         'data': [],
            #         'source': 'error'
            #     }), 500
    
    @app.route('/api/equipment', methods=['GET'])
    def get_equipment():
        """Get equipment list from parquet files using REAL data only."""
        try:
            from real_data_processor import get_equipment_list
            result = get_equipment_list()
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f"Real data processor failed: {str(e)}"
            }), 500
            # COMMENTED OUT: Fallback to simulated data - we only want real data
            # try:
            #     from parquet_processor import get_equipment_list
            #     result = get_equipment_list()
            #     return jsonify(result)
            # except Exception as e2:
            #     return jsonify({
            #         'success': False,
            #         'error': f"Both real and simulated processors failed: {str(e)}, {str(e2)}"
            #     }), 500
    
    @app.route('/api/data-summary', methods=['GET'])
    def get_data_summary():
        """Get a summary of the real data being used."""
        try:
            from real_data_processor import get_data_summary
            result = get_data_summary()
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Setup startup device expiry check (runs once at startup)
    setup_startup_device_check()
    
    return app

# Local development server
if __name__ == '__main__':
    print("🚀 Starting Consolidated Passdown API Server")
    print("=" * 50)
    print("📊 Features Available:")
    print("  ✅ Safety Issues Management")
    print("  ✅ Kudos Management")
    print("  ✅ Today's Top Issues")
    print("  ✅ Yesterday's Top Issues")
    print("  🤖 Automatic Device Removal (On Startup)")
    print("=" * 50)
    print("📍 Server URL: http://localhost:7071")
    print("📍 Health Check: http://localhost:7071/api/health")
    print("=" * 50)
    
    # Create and run Flask app for local development
    app = create_flask_app()
    
    try:
        app.run(host='0.0.0.0', port=7071, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested...")
        # Clean up scheduler if it exists
        if hasattr(app, 'scheduler') and app.scheduler:
            print("🤖 Shutting down automatic scheduler...")
            app.scheduler.shutdown()
        print("👋 Server stopped gracefully")
