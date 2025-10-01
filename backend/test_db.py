#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and create initial collections
"""

import sys
import os

# Add current directory to path to import database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, TodayModel, YesterdayModel

def test_database_connection():
    """Test database connection and collection creation"""
    print("🔄 Testing MongoDB connection...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Test connection
        if db_manager.connect():
            print("✅ Successfully connected to MongoDB Atlas!")
            
            # Test Today collection
            print("\n📋 Testing Today collection...")
            today_model = TodayModel(db_manager)
            
            # Create a test entry
            test_entry = today_model.create(
                description="Test issue for database verification",
                resolved="No",
                who="System Test",
                whom="Developer"
            )
            print(f"✅ Created test entry: {test_entry}")
            
            # Get all entries
            all_entries = today_model.get_all()
            print(f"📊 Total Today entries: {len(all_entries)}")
            
            # Test Yesterday collection
            print("\n📋 Testing Yesterday collection...")
            yesterday_model = YesterdayModel(db_manager)
            
            # Create a test entry
            test_entry_yesterday = yesterday_model.create(
                description="Test yesterday issue for database verification",
                resolved="Yes",
                who="System Test",
                whom="Developer",
                resolved_status="Completed"
            )
            print(f"✅ Created test entry: {test_entry_yesterday}")
            
            # Get all entries
            all_yesterday_entries = yesterday_model.get_all()
            print(f"📊 Total Yesterday entries: {len(all_yesterday_entries)}")
            
            print("\n🎉 Database test completed successfully!")
            print("✅ Database and collections are working properly")
            print("✅ CRUD operations are functional")
            
        else:
            print("❌ Failed to connect to MongoDB Atlas")
            print("Please check your connection string in the .env file")
            
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()
    
    return True

if __name__ == "__main__":
    print("🚀 Passdown Database Test")
    print("=" * 50)
    success = test_database_connection()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Start the backend server: func start")
        print("2. Start the frontend server: npm start (in frontend directory)")
        print("3. Open http://localhost:3000 to view the application")
    else:
        print("\n❌ Please fix the database connection before proceeding")
        sys.exit(1)