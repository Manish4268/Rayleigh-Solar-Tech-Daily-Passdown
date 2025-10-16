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
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse date and time strings into a datetime object with seconds precision"""
        try:
            # Try to parse with seconds first, then without
            datetime_str = f"{date_str} {time_str}"
            try:
                # First try with seconds format
                return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Fallback to minutes only format
                return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        except ValueError as e:
            raise Exception(f"Invalid date/time format. Expected YYYY-MM-DD for date and HH:MM or HH:MM:SS for time: {str(e)}")
    
    def check_expired_devices(self) -> List[Dict]:
        """Check for devices that have exceeded their time_hours and should be auto-removed"""
        try:
            current_time = datetime.now()  # Use local time
            expired_devices = list(self.collection.find({
                "status": "active",
                "out_datetime": {"$lte": current_time}
            }))
            
            for device in expired_devices:
                device["_id"] = str(device["_id"])
            
            return expired_devices
        except Exception as e:
            raise Exception(f"Failed to check expired devices: {str(e)}")
    
    def auto_remove_expired_devices(self) -> int:
        """Automatically remove expired devices and return count of removed devices"""
        try:
            expired_devices = self.check_expired_devices()
            removed_count = 0
            
            for device in expired_devices:
                # Soft delete the device with 'system' as remover
                success = self.soft_delete(
                    section_key=device['section_key'],
                    subsection_key=device['subsection_key'],
                    row=device['row'],
                    col=device['col'],
                    removed_by='system'
                )
                if success:
                    removed_count += 1
            
            return removed_count
        except Exception as e:
            raise Exception(f"Failed to auto-remove expired devices: {str(e)}")
    
    def create(self, section_key: str, subsection_key: str, row: int, col: int,
               device_id: str, in_date: str, in_time: str, time_hours: float, 
               created_by: str, time_hours_component: int = 0, 
               time_minutes_component: int = 0, time_seconds_component: int = 0) -> Dict:
        """Create a new stability device entry with precise time components"""
        try:
            # Check if slot is already occupied
            existing = self.get_by_position(section_key, subsection_key, row, col)
            if existing:
                raise Exception(f"Slot {row}-{col} in {section_key}/{subsection_key} is already occupied")
            
            # Parse in_date and in_time to create full datetime
            in_datetime = self._parse_datetime(in_date, in_time)
            
            # Calculate out_date and out_time based on in_datetime + precise time components
            from datetime import timedelta
            total_seconds = (time_hours_component * 3600 + 
                           time_minutes_component * 60 + 
                           time_seconds_component)
            out_datetime = in_datetime + timedelta(seconds=total_seconds)
            
            entry = {
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col,
                "device_id": device_id,
                "in_date": in_datetime.strftime('%Y-%m-%d'),
                "in_time": in_datetime.strftime('%H:%M'),
                "in_datetime": in_datetime,
                "out_date": out_datetime.strftime('%Y-%m-%d'),
                "out_time": out_datetime.strftime('%H:%M:%S'),  # Include seconds for precision
                "out_datetime": out_datetime,
                "time_hours": time_hours,  # Keep for backward compatibility
                "duration_hours": time_hours_component,
                "duration_minutes": time_minutes_component,
                "duration_seconds": time_seconds_component,
                "total_duration_seconds": total_seconds,
                "status": "active",
                "created_by": created_by,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
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
                # Convert datetime objects to strings for JSON serialization
                if "in_datetime" in entry and hasattr(entry["in_datetime"], 'isoformat'):
                    entry["in_datetime"] = entry["in_datetime"].isoformat()
                if "out_datetime" in entry and hasattr(entry["out_datetime"], 'isoformat'):
                    entry["out_datetime"] = entry["out_datetime"].isoformat()
                # Legacy support for old date fields
                if "in_date" in entry and hasattr(entry["in_date"], 'isoformat'):
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry and hasattr(entry["out_date"], 'isoformat'):
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
                # Convert datetime objects to strings for JSON serialization
                if "in_datetime" in entry and hasattr(entry["in_datetime"], 'isoformat'):
                    entry["in_datetime"] = entry["in_datetime"].isoformat()
                if "out_datetime" in entry and hasattr(entry["out_datetime"], 'isoformat'):
                    entry["out_datetime"] = entry["out_datetime"].isoformat()
                # Legacy support for old date fields
                if "in_date" in entry and hasattr(entry["in_date"], 'isoformat'):
                    entry["in_date"] = entry["in_date"].isoformat() if hasattr(entry["in_date"], 'isoformat') else entry["in_date"]
                if "out_date" in entry and hasattr(entry["out_date"], 'isoformat'):
                    entry["out_date"] = entry["out_date"].isoformat() if hasattr(entry["out_date"], 'isoformat') else entry["out_date"]
            return entry
        except Exception as e:
            raise Exception(f"Failed to get device by position: {str(e)}")
    
    def update(self, device_id: str, section_key: str, subsection_key: str, row: int, col: int,
               new_device_id: str = None, in_date: str = None, in_time: str = None,
               time_hours: int = None, updated_by: str = None) -> bool:
        """Update device entry"""
        try:
            update_fields = {}
            if new_device_id is not None:
                update_fields["device_id"] = new_device_id
            
            # If in_date or in_time or time_hours are updated, recalculate everything
            if in_date is not None or in_time is not None or time_hours is not None:
                # Get current entry to use existing values if not provided
                current_entry = self.get_by_position(section_key, subsection_key, row, col)
                if not current_entry:
                    return False
                
                # Use provided values or existing ones
                final_in_date = in_date if in_date is not None else current_entry.get('in_date')
                final_in_time = in_time if in_time is not None else current_entry.get('in_time')
                final_time_hours = time_hours if time_hours is not None else current_entry.get('time_hours')
                
                # Parse and calculate new datetime values
                in_datetime = self._parse_datetime(final_in_date, final_in_time)
                from datetime import timedelta
                out_datetime = in_datetime + timedelta(hours=final_time_hours)
                
                update_fields.update({
                    "in_date": in_datetime.strftime('%Y-%m-%d'),
                    "in_time": in_datetime.strftime('%H:%M'),
                    "in_datetime": in_datetime,
                    "out_date": out_datetime.strftime('%Y-%m-%d'),
                    "out_time": out_datetime.strftime('%H:%M'),
                    "out_datetime": out_datetime,
                    "time_hours": final_time_hours
                })
            
            if updated_by is not None:
                update_fields["updated_by"] = updated_by
            
            if update_fields:
                update_fields["updated_at"] = datetime.now()
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
        """Remove device from active collection and move to history with enhanced tracking"""
        try:
            # First get the device to move to history
            device = self.get_by_position(section_key, subsection_key, row, col)
            if not device:
                return False
            
            # Calculate actual time stayed and removal details
            removal_time = datetime.now()  # Use local time instead of UTC
            placement_time = device.get('in_datetime')
            planned_out_time = device.get('out_datetime')
            
            # Handle datetime parsing if stored as strings
            if isinstance(placement_time, str):
                placement_time = datetime.fromisoformat(placement_time.replace('Z', '+00:00'))
            if isinstance(planned_out_time, str):
                planned_out_time = datetime.fromisoformat(planned_out_time.replace('Z', '+00:00'))
            
            # Calculate actual hours stayed
            actual_hours_stayed = 0
            actual_days_stayed = 0
            if placement_time:
                time_diff = removal_time - placement_time
                actual_hours_stayed = time_diff.total_seconds() / 3600
                actual_days_stayed = actual_hours_stayed / 24
            
            # Determine if this is early removal or automatic removal
            planned_hours = device.get('time_hours', 0)
            planned_days = planned_hours / 24
            is_early_removal = actual_hours_stayed < planned_hours
            removal_type = 'manual' if removed_by != 'system' else 'automatic'
            
            # Create enhanced history entry
            history_model = StabilityHistoryModel(self.db_manager)
            enhanced_device_data = device.copy()
            enhanced_device_data.update({
                'actual_removal_time': removal_time,
                'actual_hours_stayed': round(actual_hours_stayed, 2),
                'actual_days_stayed': round(actual_days_stayed, 2),
                'planned_hours': planned_hours,
                'planned_days': round(planned_days, 2),
                'is_early_removal': is_early_removal,
                'removal_type': removal_type,
                'hours_difference': round(actual_hours_stayed - planned_hours, 2)
            })
            
            history_model.create_from_device(enhanced_device_data, removed_by)
            
            # Actually DELETE the device from the active collection (not just mark as removed)
            result = self.collection.delete_one({
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col,
                "status": "active"
            })
            
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to remove device: {str(e)}")


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
        """Create history entry from device data with enhanced tracking"""
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
                "in_date": device_data.get("in_date"),
                "in_time": device_data.get("in_time"),
                "in_datetime": device_data.get("in_datetime"),
                "out_date": device_data.get("out_date"),
                "out_time": device_data.get("out_time"),
                "out_datetime": device_data.get("out_datetime"),
                "planned_time_hours": device_data["time_hours"],
                "duration_hours": device_data.get("duration_hours", 0),
                "duration_minutes": device_data.get("duration_minutes", 0),
                "duration_seconds": device_data.get("duration_seconds", 0),
                "total_duration_seconds": device_data.get("total_duration_seconds", 0),
                "actual_removal_time": device_data.get("actual_removal_time"),
                "actual_hours_stayed": device_data.get("actual_hours_stayed"),
                "actual_days_stayed": device_data.get("actual_days_stayed"),
                "planned_hours": device_data.get("planned_hours"),
                "planned_days": device_data.get("planned_days"),
                "is_early_removal": device_data.get("is_early_removal", False),
                "removal_type": device_data.get("removal_type", "manual"),
                "hours_difference": device_data.get("hours_difference", 0),
                "status": "completed",
                "created_by": device_data.get("created_by", "unknown"),
                "removed_by": removed_by,
                "original_created_at": device_data["created_at"],
                "moved_to_history_at": datetime.now()
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