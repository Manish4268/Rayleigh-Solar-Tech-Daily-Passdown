import os
import pymongo
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self.db_name = os.getenv('DATABASE_NAME', 'passdown_db')
        self.collection_today = os.getenv('COLLECTION_TODAY', 'today_updates')
        self.collection_yesterday = os.getenv('COLLECTION_YESTERDAY', 'yesterday_updates')
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB and create database/collections if they don't exist"""
        try:
            self.client = pymongo.MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            # Create collections if they don't exist
            self._ensure_collections_exist()
            
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def _ensure_collections_exist(self):
        """Create collections and indexes if they don't exist"""
        collections = self.db.list_collection_names()
        
        # Create Today collection
        if self.collection_today not in collections:
            self.db.create_collection(self.collection_today)
            # Create index on sr_no for better performance
            self.db[self.collection_today].create_index("sr_no", unique=True)
            print(f"Created collection: {self.collection_today}")
        
        # Create Yesterday collection  
        if self.collection_yesterday not in collections:
            self.db.create_collection(self.collection_yesterday)
            # Create index on sr_no for better performance
            self.db[self.collection_yesterday].create_index("sr_no", unique=True)
            print(f"Created collection: {self.collection_yesterday}")
    
    def get_next_sr_no(self, collection_name: str) -> int:
        """Get the next serial number for a collection"""
        collection = self.db[collection_name]
        last_doc = collection.find_one(sort=[("sr_no", -1)])
        return (last_doc["sr_no"] + 1) if last_doc else 1
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()

class TodayModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection = db_manager.db[db_manager.collection_today]
    
    def create(self, description: str, resolved: str, who: str, whom: str) -> Dict:
        """Create a new today entry"""
        try:
            sr_no = self.db_manager.get_next_sr_no(self.db_manager.collection_today)
            
            entry = {
                "sr_no": sr_no,
                "description": description,
                "resolved": resolved,
                "who": who,
                "whom": whom,
                "timestamp": datetime.utcnow()
            }
            
            result = self.collection.insert_one(entry)
            entry["_id"] = str(result.inserted_id)
            return entry
        except Exception as e:
            raise Exception(f"Failed to create entry: {str(e)}")
    
    def get_all(self) -> List[Dict]:
        """Get all today entries"""
        try:
            entries = list(self.collection.find().sort("sr_no", 1))
            for entry in entries:
                entry["_id"] = str(entry["_id"])
            return entries
        except Exception as e:
            raise Exception(f"Failed to get entries: {str(e)}")
    
    def get_by_sr_no(self, sr_no: int) -> Optional[Dict]:
        """Get entry by serial number"""
        try:
            entry = self.collection.find_one({"sr_no": sr_no})
            if entry:
                entry["_id"] = str(entry["_id"])
            return entry
        except Exception as e:
            raise Exception(f"Failed to get entry: {str(e)}")
    
    def update(self, sr_no: int, description: str = None, resolved: str = None, 
               who: str = None, whom: str = None) -> bool:
        """Update an existing entry"""
        try:
            update_fields = {}
            if description is not None:
                update_fields["description"] = description
            if resolved is not None:
                update_fields["resolved"] = resolved
            if who is not None:
                update_fields["who"] = who
            if whom is not None:
                update_fields["whom"] = whom
            
            if update_fields:
                update_fields["timestamp"] = datetime.utcnow()
                result = self.collection.update_one(
                    {"sr_no": sr_no}, 
                    {"$set": update_fields}
                )
                return result.modified_count > 0
            return False
        except Exception as e:
            raise Exception(f"Failed to update entry: {str(e)}")
    
    def delete(self, sr_no: int) -> bool:
        """Delete an entry"""
        try:
            result = self.collection.delete_one({"sr_no": sr_no})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete entry: {str(e)}")

class YesterdayModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection = db_manager.db[db_manager.collection_yesterday]
    
    def create(self, description: str, resolved: str, who: str, whom: str, resolved_status: str) -> Dict:
        """Create a new yesterday entry"""
        try:
            sr_no = self.db_manager.get_next_sr_no(self.db_manager.collection_yesterday)
            
            entry = {
                "sr_no": sr_no,
                "description": description,
                "resolved": resolved,
                "who": who,
                "whom": whom,
                "resolved_status": resolved_status,
                "timestamp": datetime.utcnow()
            }
            
            result = self.collection.insert_one(entry)
            entry["_id"] = str(result.inserted_id)
            return entry
        except Exception as e:
            raise Exception(f"Failed to create entry: {str(e)}")
    
    def get_all(self) -> List[Dict]:
        """Get all yesterday entries"""
        try:
            entries = list(self.collection.find().sort("sr_no", 1))
            for entry in entries:
                entry["_id"] = str(entry["_id"])
            return entries
        except Exception as e:
            raise Exception(f"Failed to get entries: {str(e)}")
    
    def get_by_sr_no(self, sr_no: int) -> Optional[Dict]:
        """Get entry by serial number"""
        try:
            entry = self.collection.find_one({"sr_no": sr_no})
            if entry:
                entry["_id"] = str(entry["_id"])
            return entry
        except Exception as e:
            raise Exception(f"Failed to get entry: {str(e)}")
    
    def update(self, sr_no: int, description: str = None, resolved: str = None, 
               who: str = None, whom: str = None, resolved_status: str = None) -> bool:
        """Update an existing entry"""
        try:
            update_fields = {}
            if description is not None:
                update_fields["description"] = description
            if resolved is not None:
                update_fields["resolved"] = resolved
            if who is not None:
                update_fields["who"] = who
            if whom is not None:
                update_fields["whom"] = whom
            if resolved_status is not None:
                update_fields["resolved_status"] = resolved_status
            
            if update_fields:
                update_fields["timestamp"] = datetime.utcnow()
                result = self.collection.update_one(
                    {"sr_no": sr_no}, 
                    {"$set": update_fields}
                )
                return result.modified_count > 0
            return False
        except Exception as e:
            raise Exception(f"Failed to update entry: {str(e)}")
    
    def delete(self, sr_no: int) -> bool:
        """Delete an entry"""
        try:
            result = self.collection.delete_one({"sr_no": sr_no})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete entry: {str(e)}")