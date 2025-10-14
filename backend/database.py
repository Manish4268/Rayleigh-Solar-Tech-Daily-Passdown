import os
import pymongo
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self.db_name = os.getenv('DATABASE_NAME', 'passdown_db')
        self.collection_today = os.getenv('COLLECTION_TODAY', 'today_updates')
        self.collection_yesterday = os.getenv('COLLECTION_YESTERDAY', 'yesterday_updates')
        # Stability Dashboard Collections
        self.collection_stability_devices = os.getenv('COLLECTION_STABILITY_DEVICES', 'stability_devices')
        self.collection_stability_history = os.getenv('COLLECTION_STABILITY_HISTORY', 'stability_history')
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB and create database/collections if they don't exist"""
        try:
            # First, try connecting to MongoDB Atlas with different SSL configurations
            connection_attempts = [
                # Try 1: Standard SSL with certificate validation disabled
                {
                    'tls': True,
                    'tlsAllowInvalidCertificates': True,
                    'serverSelectionTimeoutMS': 10000,
                    'connectTimeoutMS': 10000
                },
                # Try 2: Disable SSL entirely (for development)
                {
                    'ssl': False,
                    'serverSelectionTimeoutMS': 5000
                },
                # Try 3: Use local MongoDB if available
                None
            ]
            
            for attempt_config in connection_attempts:
                try:
                    if attempt_config is None:
                        # Try local MongoDB
                        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
                        local_db_name = 'passdown_local'
                    else:
                        self.client = pymongo.MongoClient(self.connection_string, **attempt_config)
                        local_db_name = self.db_name
                    
                    self.db = self.client[local_db_name]
                    
                    # Test connection
                    self.client.admin.command('ping')
                    print(f"Successfully connected to MongoDB! (Database: {local_db_name})")
                    
                    # Create collections if they don't exist
                    self._ensure_collections_exist()
                    
                    return True
                except Exception as connection_error:
                    print(f"Connection attempt failed: {str(connection_error)}")
                    continue
            
            print("All MongoDB connection attempts failed")
            return False
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
    
    def create(self, description: str, resolved: str, who: str, whom: str, resolved_status: bool = False) -> Dict:
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
    
    def update(self, sr_no: int, description: str = None, resolved: str = None, 
               who: str = None, whom: str = None, resolved_status: bool = None) -> bool:
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


class StabilityDeviceModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = db_manager.collection_stability_devices
        self.collection = db_manager.db[self.collection_name]
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection and indexes if they don't exist"""
        collections = self.db_manager.db.list_collection_names()
        if self.collection_name not in collections:
            self.db_manager.db.create_collection(self.collection_name)
            # Create compound index for position-based queries
            self.collection.create_index([
                ("section_key", 1),
                ("subsection_key", 1), 
                ("row", 1),
                ("col", 1)
            ])
            print(f"Created collection: {self.collection_name}")
    
    def create(self, section_key: str, subsection_key: str, row: int, col: int,
               device_id: str, in_date: str, out_date: str, time_hours: int, 
               created_by: str) -> Dict:
        """Create a new stability device entry"""
        try:
            # Check if slot is already occupied
            existing = self.get_by_position(section_key, subsection_key, row, col)
            if existing:
                raise Exception(f"Slot {row}-{col} in {section_key}/{subsection_key} is already occupied")
            
            entry = {
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col,
                "device_id": device_id,
                "in_date": datetime.fromisoformat(in_date.replace('Z', '+00:00')) if isinstance(in_date, str) else in_date,
                "out_date": datetime.fromisoformat(out_date.replace('Z', '+00:00')) if isinstance(out_date, str) else out_date,
                "time_hours": time_hours,
                "status": "active",
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(entry)
            entry["_id"] = str(result.inserted_id)
            return entry
        except Exception as e:
            raise Exception(f"Failed to create device entry: {str(e)}")
    
    def get_all(self) -> List[Dict]:
        """Get all active stability device entries"""
        try:
            entries = list(self.collection.find({"status": "active"}))
            for entry in entries:
                entry["_id"] = str(entry["_id"])
                # Convert dates to ISO string format for JSON serialization
                if "in_date" in entry:
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry:
                    entry["out_date"] = entry["out_date"].isoformat() if hasattr(entry["out_date"], 'isoformat') else entry["out_date"]
            return entries
        except Exception as e:
            raise Exception(f"Failed to get device entries: {str(e)}")
    
    def get_by_position(self, section_key: str, subsection_key: str, row: int, col: int) -> Optional[Dict]:
        """Get device at specific position"""
        try:
            entry = self.collection.find_one({
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col,
                "status": "active"
            })
            if entry:
                entry["_id"] = str(entry["_id"])
                if "in_date" in entry:
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry:
                    entry["out_date"] = entry["out_date"].isoformat() if hasattr(entry["out_date"], 'isoformat') else entry["out_date"]
            return entry
        except Exception as e:
            raise Exception(f"Failed to get device by position: {str(e)}")
    
    def update(self, device_id: str, section_key: str, subsection_key: str, row: int, col: int,
               new_device_id: str = None, in_date: str = None, out_date: str = None,
               time_hours: int = None, updated_by: str = None) -> bool:
        """Update device entry"""
        try:
            update_fields = {}
            if new_device_id is not None:
                update_fields["device_id"] = new_device_id
            if in_date is not None:
                update_fields["in_date"] = datetime.fromisoformat(in_date.replace('Z', '+00:00')) if isinstance(in_date, str) else in_date
            if out_date is not None:
                update_fields["out_date"] = datetime.fromisoformat(out_date.replace('Z', '+00:00')) if isinstance(out_date, str) else out_date
            if time_hours is not None:
                update_fields["time_hours"] = time_hours
            if updated_by is not None:
                update_fields["updated_by"] = updated_by
            
            if update_fields:
                update_fields["updated_at"] = datetime.utcnow()
                result = self.collection.update_one(
                    {
                        "section_key": section_key,
                        "subsection_key": subsection_key,
                        "row": row,
                        "col": col,
                        "status": "active"
                    },
                    {"$set": update_fields}
                )
                return result.modified_count > 0
            return False
        except Exception as e:
            raise Exception(f"Failed to update device entry: {str(e)}")
    
    def soft_delete(self, section_key: str, subsection_key: str, row: int, col: int, removed_by: str) -> bool:
        """Soft delete device (mark as removed and move to history)"""
        try:
            # First get the device to move to history
            device = self.get_by_position(section_key, subsection_key, row, col)
            if not device:
                return False
            
            # Move to history
            history_model = StabilityHistoryModel(self.db_manager)
            history_model.create_from_device(device, removed_by)
            
            # Mark as removed
            result = self.collection.update_one(
                {
                    "section_key": section_key,
                    "subsection_key": subsection_key,
                    "row": row,
                    "col": col,
                    "status": "active"
                },
                {
                    "$set": {
                        "status": "removed",
                        "removed_by": removed_by,
                        "removed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Failed to soft delete device: {str(e)}")


class StabilityHistoryModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = db_manager.collection_stability_history
        self.collection = db_manager.db[self.collection_name]
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection and indexes if they don't exist"""
        collections = self.db_manager.db.list_collection_names()
        if self.collection_name not in collections:
            self.db_manager.db.create_collection(self.collection_name)
            # Create indexes for history queries
            self.collection.create_index("id", unique=True)  # Unique id index
            # Create compound index for position-based queries
            self.collection.create_index([
                ("section_key", 1),
                ("subsection_key", 1),
                ("row", 1),
                ("col", 1),
                ("moved_to_history_at", -1)  # Most recent first
            ])
            print(f"Created collection: {self.collection_name}")
    
    def create_from_device(self, device_data: Dict, removed_by: str) -> Dict:
        """Create history entry from device data"""
        try:
            # Generate a unique ID for the history entry
            import time
            history_id = int(time.time() * 1000)  # Timestamp in milliseconds
            
            entry = {
                "id": history_id,  # Add unique id field for index compatibility
                "section_key": device_data["section_key"],
                "subsection_key": device_data["subsection_key"],
                "row": device_data["row"],
                "col": device_data["col"],
                "device_id": device_data["device_id"],
                "in_date": device_data["in_date"],
                "out_date": device_data["out_date"],
                "time_hours": device_data["time_hours"],
                "status": "completed",
                "created_by": device_data.get("created_by", "unknown"),
                "removed_by": removed_by,
                "original_created_at": device_data["created_at"],
                "moved_to_history_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(entry)
            entry["_id"] = str(result.inserted_id)
            return entry
        except Exception as e:
            raise Exception(f"Failed to create history entry: {str(e)}")
    
    def get_by_position(self, section_key: str, subsection_key: str, row: int, col: int) -> List[Dict]:
        """Get history for specific position"""
        try:
            entries = list(self.collection.find({
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col
            }).sort("moved_to_history_at", -1))  # Most recent first
            
            for entry in entries:
                entry["_id"] = str(entry["_id"])
                # Convert dates to ISO string format for JSON serialization
                if "in_date" in entry:
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry:
                    entry["out_date"] = entry["out_date"].isoformat() if hasattr(entry["out_date"], 'isoformat') else entry["out_date"]
            return entries
        except Exception as e:
            raise Exception(f"Failed to get history entries: {str(e)}")
    
    def get_all(self) -> List[Dict]:
        """Get all history entries"""
        try:
            entries = list(self.collection.find().sort("moved_to_history_at", -1))
            for entry in entries:
                entry["_id"] = str(entry["_id"])
                if "in_date" in entry:
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry:
                    entry["out_date"] = entry["out_date"].isoformat() if hasattr(entry["out_date"], 'isoformat') else entry["out_date"]
            return entries
        except Exception as e:
            raise Exception(f"Failed to get all history entries: {str(e)}")