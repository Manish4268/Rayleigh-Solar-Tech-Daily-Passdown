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

# Configuration
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'passdown_db')

# Collections for each feature
COLLECTIONS = {
    'safety_issues': 'safety_issues',
    'kudos': 'kudos_entries', 
    'today_issues': 'today_top_issues',
    'yesterday_issues': 'yesterday_top_issues'
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
    print("=" * 50)
    print("📍 Server URL: http://localhost:7071")
    print("📍 Health Check: http://localhost:7071/api/health")
    print("=" * 50)
    
    # Create and run Flask app for local development
    app = create_flask_app()
    app.run(host='0.0.0.0', port=7071, debug=True)
