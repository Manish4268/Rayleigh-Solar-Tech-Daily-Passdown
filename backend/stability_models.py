"""
Stability Models - Database models for stability device tracking
Uses the same MongoDB connection as the main data management system
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StabilityDatabaseManager:
    """Database connection manager for stability system"""
    
    def __init__(self):
        # MongoDB connection - following exact same pattern as DataManagementAPI
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self.database_name = os.getenv('DATABASE_NAME', 'passdown_db')
        self.client = None
        self.db = None
        self.connected = False
        self._connect_to_mongodb()
    
    def _connect_to_mongodb(self):
        """Establish MongoDB connection - exact same pattern as DataManagementAPI"""
        try:
            if not self.connection_string:
                logging.warning("MongoDB connection string not found. Using local fallback.")
                return
            
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
            logging.info("✅ Stability MongoDB connection established")
            self.connected = True
        except Exception as e:
            logging.error(f"❌ Stability MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.connected = False
    
    def connect(self):
        """Legacy connect method for backward compatibility"""
        return self.connected
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.connected = False

class StabilityDeviceModel:
    """Model for stability device management"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.collection = db_manager.db.stability_devices
    
    def get_all(self):
        """Get all active devices"""
        try:
            devices = list(self.collection.find({"status": {"$ne": "removed"}}))
            # Convert ObjectId to string
            for device in devices:
                device['_id'] = str(device['_id'])
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
    
    def get_by_id(self, device_id):
        """Get device by ID"""
        try:
            from bson import ObjectId
            device = self.collection.find_one({"_id": ObjectId(device_id)})
            if device:
                device['_id'] = str(device['_id'])
            return device
        except Exception as e:
            print(f"Error getting device by ID: {e}")
            return None
    
    def get_by_position(self, section_key, subsection_key, row, col):
        """Get device at specific position"""
        try:
            # Primary query using camelCase (which is what the database actually uses)
            query = {
                "sectionKey": section_key,
                "subsectionKey": subsection_key,
                "row": row,
                "col": col,
                "status": {"$ne": "removed"}
            }
            
            debug_msg = f"🔍 get_by_position query: section='{section_key}', subsection='{subsection_key}', row={row}, col={col}"
            print(debug_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{debug_msg}\n")
            
            device = self.collection.find_one(query)
            
            # If not found with camelCase, try snake_case as fallback
            if not device:
                query_fallback = {
                    "section_key": section_key,
                    "subsection_key": subsection_key,
                    "row": row,
                    "col": col,
                    "status": {"$ne": "removed"}
                }
                device = self.collection.find_one(query_fallback)
                if device:
                    fallback_msg = f"� Found device using snake_case fallback"
                    print(fallback_msg)
                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"{fallback_msg}\n")
            
            if device:
                device['_id'] = str(device['_id'])
                result_msg = f"✅ Found device: {device.get('deviceId', device.get('device_id', 'unknown'))}"
                print(result_msg)
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{result_msg}\n")
            else:
                result_msg = f"❌ No device found at position"
                print(result_msg)
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{result_msg}\n")
            return device
        except Exception as e:
            error_msg = f"Error getting device by position: {e}"
            print(error_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
            return None
    
    def create(self, data):
        """Create new device"""
        try:
            # Add metadata
            data['created_at'] = datetime.utcnow()
            data['status'] = 'active'
            
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating device: {e}")
            return None
    
    def update(self, device_id, data):
        """Update device by ID"""
        try:
            from bson import ObjectId
            update_data = data.copy()
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(device_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating device: {e}")
            return False
    
    def delete(self, device_id):
        """Soft delete device by ID (mark as removed)"""
        try:
            from bson import ObjectId
            
            # Get the device first
            device = self.get_by_id(device_id)
            if not device:
                return False
            
            # Move to history
            history_model = StabilityHistoryModel(self.db_manager)
            history_model.archive_device(device, "System")
            
            # Mark as removed
            result = self.collection.update_one(
                {"_id": ObjectId(device_id)},
                {
                    "$set": {
                        "status": "removed",
                        "removed_at": datetime.utcnow(),
                        "removed_by": "System"
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting device: {e}")
            return False
    
    def update_by_position(self, section_key, subsection_key, row, col, data):
        """Update or create device at position"""
        try:
            # Check if device exists
            existing = self.get_by_position(section_key, subsection_key, row, col)
            
            if existing:
                # Update existing device
                update_data = data.copy()
                update_data['updated_at'] = datetime.utcnow()
                
                result = self.collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            else:
                # Create new device
                data['section_key'] = section_key
                data['subsection_key'] = subsection_key
                data['row'] = row
                data['col'] = col
                return self.create(data) is not None
                
        except Exception as e:
            print(f"Error updating device: {e}")
            return False
    
    def soft_delete(self, section_key, subsection_key, row, col, removed_by):
        """Soft delete device (mark as removed)"""
        try:
            debug_msg = f"🗑️ soft_delete called: section='{section_key}', subsection='{subsection_key}', row={row}, col={col}"
            print(debug_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{debug_msg}\n")
            
            device = self.get_by_position(section_key, subsection_key, row, col)
            if not device:
                error_msg = f"❌ soft_delete: Device not found at position"
                print(error_msg)
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{error_msg}\n")
                return False
            
            success_msg = f"📦 Device found for deletion: {device.get('deviceId', device.get('device_id', 'unknown'))}"
            print(success_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{success_msg}\n")
            
            # Move to history
            try:
                history_model = StabilityHistoryModel(self.db_manager)
                history_model.archive_device(device, removed_by)
                print(f"📝 Device archived to history")
            except Exception as history_error:
                print(f"⚠️ Warning: Could not archive to history: {history_error}")
            
            # Mark as removed using the same field names as the database (camelCase)
            update_query = {
                "sectionKey": section_key,
                "subsectionKey": subsection_key,
                "row": row,
                "col": col,
                "status": {"$ne": "removed"}
            }
            
            update_msg = f"🔄 Updating device with query: {update_query}"
            print(update_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{update_msg}\n")
            
            result = self.collection.update_one(
                update_query,
                {
                    "$set": {
                        "status": "removed",
                        "removed_at": datetime.utcnow(),
                        "removed_by": removed_by
                    }
                }
            )
            print(f"📊 Update result: modified_count={result.modified_count}, matched_count={result.matched_count}")
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error soft deleting device: {e}")
            return False
    
    def check_expired_devices(self):
        """Check for devices that have exceeded their time limit"""
        try:
            expired_devices = []
            active_devices = self.get_all()
            
            for device in active_devices:
                # Check if device has time_hours field and in_date/in_time
                if not device.get('time_hours') or not device.get('in_date') or not device.get('in_time'):
                    continue
                
                try:
                    # Parse in_date and in_time
                    in_datetime_str = f"{device['in_date']} {device['in_time']}"
                    in_datetime = datetime.strptime(in_datetime_str, "%Y-%m-%d %H:%M")
                    
                    # Calculate expiry time
                    time_hours = float(device['time_hours'])
                    expiry_time = in_datetime + timedelta(hours=time_hours)
                    
                    # Check if expired
                    if datetime.now() > expiry_time:
                        expired_devices.append({
                            'device_id': device.get('id', device.get('device_id', 'Unknown')),
                            'section_key': device['section_key'],
                            'subsection_key': device['subsection_key'],
                            'row': device['row'],
                            'col': device['col'],
                            'expired_time': expiry_time.isoformat(),
                            'hours_over': (datetime.now() - expiry_time).total_seconds() / 3600
                        })
                        
                except (ValueError, KeyError) as e:
                    print(f"Error parsing device time data: {e}")
                    continue
            
            return expired_devices
            
        except Exception as e:
            print(f"Error checking expired devices: {e}")
            return []

class StabilityHistoryModel:
    """Model for stability device history"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.collection = db_manager.db.stability_history
    
    def get_by_device_id(self, device_id):
        """Get history for a specific device ID"""
        try:
            history = list(self.collection.find({
                "device_id": device_id
            }).sort("created_at", -1))  # Most recent first
            
            # Convert ObjectId to string
            for item in history:
                item['_id'] = str(item['_id'])
            
            return history
        except Exception as e:
            print(f"Error getting device history: {e}")
            return []
    
    def get_by_position(self, section_key, subsection_key, row, col):
        """Get history for specific position"""
        try:
            history = list(self.collection.find({
                "section_key": section_key,
                "subsection_key": subsection_key,
                "row": row,
                "col": col
            }).sort("created_at", -1))  # Most recent first
            
            # Convert ObjectId to string
            for item in history:
                item['_id'] = str(item['_id'])
            
            return history
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def add_entry(self, data):
        """Add history entry"""
        try:
            data['created_at'] = datetime.utcnow()
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding history entry: {e}")
            return None
    
    def archive_device(self, device, removed_by):
        """Archive device to history"""
        try:
            history_entry = device.copy()
            history_entry['removed_by'] = removed_by
            history_entry['removed_at'] = datetime.utcnow()
            
            # Remove the original _id to create new history entry
            if '_id' in history_entry:
                del history_entry['_id']
            
            # Calculate duration if possible
            if device.get('in_date') and device.get('in_time'):
                try:
                    in_datetime_str = f"{device['in_date']} {device['in_time']}"
                    in_datetime = datetime.strptime(in_datetime_str, "%Y-%m-%d %H:%M")
                    duration = datetime.utcnow() - in_datetime
                    
                    total_seconds = int(duration.total_seconds())
                    history_entry['duration_hours'] = total_seconds // 3600
                    history_entry['duration_minutes'] = (total_seconds % 3600) // 60
                    history_entry['duration_seconds'] = total_seconds % 60
                    
                    # Set out_date and out_time
                    now = datetime.utcnow()
                    history_entry['out_date'] = now.strftime("%Y-%m-%d")
                    history_entry['out_time'] = now.strftime("%H:%M")
                    
                except (ValueError, KeyError):
                    pass
            
            result = self.collection.insert_one(history_entry)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error archiving device: {e}")
            return None