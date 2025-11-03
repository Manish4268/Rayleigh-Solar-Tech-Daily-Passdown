"""
Data Management API Module
Handles all CRUD operations for safety issues, kudos, and top issues
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from flask import jsonify
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataManagementAPI:
    """Data Management API class handling all data CRUD operations"""
    
    def __init__(self):
        # MongoDB connection
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self.database_name = os.getenv('DATABASE_NAME', 'passdown_db')
        self.client = None
        self.db = None
        self._connect_to_mongodb()
        
        # Collection names
        self.COLLECTION_SAFETY = 'safety_issues'
        self.COLLECTION_KUDOS = 'kudos_entries'
        self.COLLECTION_TODAY = os.getenv('COLLECTION_TODAY', 'today_updates')
        self.COLLECTION_YESTERDAY = os.getenv('COLLECTION_YESTERDAY', 'yesterday_updates')
    
    def _connect_to_mongodb(self):
        """Establish MongoDB connection"""
        try:
            if not self.connection_string:
                logging.warning("MongoDB connection string not found. Using local fallback.")
                return
            
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
            logging.info("✅ MongoDB connection established")
        except Exception as e:
            logging.error(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
    
    def _serialize_doc(self, doc):
        """Convert MongoDB document to JSON-serializable format"""
        if doc and '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc
    
    # ==================== SAFETY ISSUES ====================
    
    def get_all_safety_issues(self):
        """Get all safety issues"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            issues = list(self.db[self.COLLECTION_SAFETY].find().sort('date', -1))
            serialized = [self._serialize_doc(issue) for issue in issues]
            
            return jsonify({"success": True, "data": serialized}), 200
        except Exception as e:
            logging.error(f"Error getting safety issues: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def create_safety_issue(self, data):
        """Create a new safety issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            # Get the next ID (max + 1)
            existing_issues = list(self.db[self.COLLECTION_SAFETY].find())
            next_id = max([item.get('id', 0) for item in existing_issues], default=0) + 1
            
            issue = {
                'id': next_id,
                'issue': data.get('issue'),
                'person': data.get('person'),
                'action': data.get('action'),
                'done': data.get('done', 'No'),  # Default to "No" for new issues
                'date': datetime.now().strftime('%m/%d'),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.db[self.COLLECTION_SAFETY].insert_one(issue)
            issue['_id'] = str(result.inserted_id)
            
            return jsonify({"success": True, "data": self._serialize_doc(issue)}), 201
        except Exception as e:
            logging.error(f"Error creating safety issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def update_safety_issue(self, issue_id, data):
        """Update a safety issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            logging.info(f"🔄 Updating safety issue {issue_id} with data: {data}")
            
            update_data = {}
            if 'done' in data:
                update_data['done'] = data['done']
                logging.info(f"📝 Setting done status to: {data['done']}")
            if 'issue' in data:
                update_data['issue'] = data['issue']
            if 'person' in data:
                update_data['person'] = data['person']
            if 'action' in data:
                update_data['action'] = data['action']
            
            result = self.db[self.COLLECTION_SAFETY].update_one(
                {'_id': ObjectId(issue_id)},
                {'$set': update_data}
            )
            
            logging.info(f"✅ Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue updated"}), 200
        except Exception as e:
            logging.error(f"Error updating safety issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    def delete_safety_issue(self, issue_id):
        """Delete a safety issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            result = self.db[self.COLLECTION_SAFETY].delete_one({'_id': ObjectId(issue_id)})
            
            if result.deleted_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue deleted"}), 200
        except Exception as e:
            logging.error(f"Error deleting safety issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ==================== KUDOS ====================
    
    def get_all_kudos(self):
        """Get all kudos entries"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            kudos = list(self.db[self.COLLECTION_KUDOS].find().sort('date', -1))
            serialized = [self._serialize_doc(entry) for entry in kudos]
            
            return jsonify({"success": True, "data": serialized}), 200
        except Exception as e:
            logging.error(f"Error getting kudos: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def create_kudos(self, data):
        """Create a new kudos entry"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            # Get the next ID (max + 1)
            existing_kudos = list(self.db[self.COLLECTION_KUDOS].find())
            next_id = max([item.get('id', 0) for item in existing_kudos], default=0) + 1
            
            kudos = {
                'id': next_id,
                'name': data.get('name'),
                'action': data.get('action'),
                'by_whom': data.get('by_whom', ''),
                'date': datetime.now().strftime('%m/%d'),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.db[self.COLLECTION_KUDOS].insert_one(kudos)
            kudos['_id'] = str(result.inserted_id)
            
            return jsonify({"success": True, "data": self._serialize_doc(kudos)}), 201
        except Exception as e:
            logging.error(f"Error creating kudos: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def delete_kudos(self, kudos_id):
        """Delete a kudos entry"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            result = self.db[self.COLLECTION_KUDOS].delete_one({'_id': ObjectId(kudos_id)})
            
            if result.deleted_count == 0:
                return jsonify({"success": False, "error": "Kudos not found"}), 404
            
            return jsonify({"success": True, "message": "Kudos deleted"}), 200
        except Exception as e:
            logging.error(f"Error deleting kudos: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ==================== TODAY'S TOP ISSUES ====================
    
    def get_all_today_issues(self):
        """Get all today's issues"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            issues = list(self.db[self.COLLECTION_TODAY].find().sort('id', 1))
            serialized = [self._serialize_doc(issue) for issue in issues]
            
            return jsonify({"success": True, "data": serialized}), 200
        except Exception as e:
            logging.error(f"Error getting today's issues: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def create_today_issue(self, data):
        """Create a new today's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            # Get next ID
            last_issue = self.db[self.COLLECTION_TODAY].find_one(sort=[('id', -1)])
            next_id = (last_issue['id'] + 1) if last_issue else 1
            
            # Create today's issue
            today_issue = {
                'id': next_id,
                'description': data.get('description'),
                'who': data.get('who'),
                'date': datetime.now().strftime('%m/%d')
            }
            
            result = self.db[self.COLLECTION_TODAY].insert_one(today_issue)
            today_issue['_id'] = str(result.inserted_id)
            
            # Also add to yesterday's issues as incomplete
            yesterday_issue = {
                'id': next_id,
                'description': data.get('description'),
                'who': data.get('who'),
                'done': 'No',
                'date': datetime.now().strftime('%m/%d')
            }
            self.db[self.COLLECTION_YESTERDAY].insert_one(yesterday_issue)
            
            return jsonify({"success": True, "data": today_issue}), 201
        except Exception as e:
            logging.error(f"Error creating today's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def update_today_issue(self, issue_id, data):
        """Update a today's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            update_data = {}
            if 'description' in data:
                update_data['description'] = data['description']
            if 'who' in data:
                update_data['who'] = data['who']
            if 'date' in data:
                update_data['date'] = data['date']
            
            result = self.db[self.COLLECTION_TODAY].update_one(
                {'id': int(issue_id)},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue updated"}), 200
        except Exception as e:
            logging.error(f"Error updating today's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def delete_today_issue(self, issue_id):
        """Delete a today's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            result = self.db[self.COLLECTION_TODAY].delete_one({'id': int(issue_id)})
            
            if result.deleted_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue deleted"}), 200
        except Exception as e:
            logging.error(f"Error deleting today's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ==================== YESTERDAY'S TOP ISSUES ====================
    
    def get_all_yesterday_issues(self):
        """Get all yesterday's issues"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            issues = list(self.db[self.COLLECTION_YESTERDAY].find().sort('id', 1))
            serialized = [self._serialize_doc(issue) for issue in issues]
            
            return jsonify({"success": True, "data": serialized}), 200
        except Exception as e:
            logging.error(f"Error getting yesterday's issues: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def create_yesterday_issue(self, data):
        """Create a new yesterday's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            # Get the next ID (max + 1)
            existing_issues = list(self.db[self.COLLECTION_YESTERDAY].find())
            next_id = max([item.get('id', 0) for item in existing_issues], default=0) + 1
            
            issue = {
                'id': next_id,
                'description': data.get('description'),
                'who': data.get('who'),
                'done': data.get('done', 'No'),
                'date': datetime.now().strftime('%m/%d'),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.db[self.COLLECTION_YESTERDAY].insert_one(issue)
            issue['_id'] = str(result.inserted_id)
            
            return jsonify({"success": True, "data": self._serialize_doc(issue)}), 201
        except Exception as e:
            logging.error(f"Error creating yesterday's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def update_yesterday_issue(self, issue_id, data):
        """Update a yesterday's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            update_data = {}
            if 'done' in data:
                update_data['done'] = data['done']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'who' in data:
                update_data['who'] = data['who']
            
            result = self.db[self.COLLECTION_YESTERDAY].update_one(
                {'id': int(issue_id)},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue updated"}), 200
        except Exception as e:
            logging.error(f"Error updating yesterday's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def delete_yesterday_issue(self, issue_id):
        """Delete a yesterday's issue"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            result = self.db[self.COLLECTION_YESTERDAY].delete_one({'id': int(issue_id)})
            
            if result.deleted_count == 0:
                return jsonify({"success": False, "error": "Issue not found"}), 404
            
            return jsonify({"success": True, "message": "Issue deleted"}), 200
        except Exception as e:
            logging.error(f"Error deleting yesterday's issue: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ==================== RESET ====================
    
    def reset_today_issues(self):
        """Reset today's issues"""
        try:
            if self.db is None:
                return jsonify({"success": False, "error": "Database error"}), 500
            
            result = self.db[self.COLLECTION_TODAY].delete_many({})
            
            return jsonify({
                "success": True,
                "message": f"Reset complete. Deleted {result.deleted_count} issues."
            }), 200
        except Exception as e:
            logging.error(f"Error resetting today's issues: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

# Lazy singleton instance - will be created on first access
_data_api_instance = None

def get_data_api():
    """Get or create the singleton data API instance"""
    global _data_api_instance
    if _data_api_instance is None:
        _data_api_instance = DataManagementAPI()
    return _data_api_instance

# For backward compatibility
class DataAPIProxy:
    """Proxy class that delegates to the lazy-loaded singleton"""
    def __getattr__(self, name):
        return getattr(get_data_api(), name)

data_api = DataAPIProxy()
