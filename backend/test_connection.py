#!/usr/bin/env python3
"""
Simple test script for the Passdown App
Tests database connection and basic functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passdown_app import DatabaseManager

def test_connection():
    """Test basic database connection"""
    print("🧪 Testing Passdown App Database Connection")
    print("=" * 50)
    
    try:
        db_manager = DatabaseManager()
        
        if db_manager.connect():
            print("✅ Database connection successful!")
            
            # List collections
            collections = db_manager.db.list_collection_names()
            print(f"📊 Available collections: {collections}")
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()

if __name__ == "__main__":
    print("🚀 Passdown App - Connection Test")
    print("=" * 40)
    
    success = test_connection()
    
    if success:
        print("\n🎯 Ready to start:")
        print("1. Start server: python passdown_app.py")
        print("2. Create demo data: python create_demo_data_new.py")
        print("3. Open frontend: http://localhost:5173")
    else:
        print("\n❌ Please check your .env configuration")
        sys.exit(1)