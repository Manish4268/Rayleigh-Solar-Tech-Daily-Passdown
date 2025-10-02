#!/usr/bin/env python3
"""
Demo data for the consolidated backend
Creates sample data for all four features
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passdown_app import DatabaseManager, COLLECTIONS

def create_consolidated_demo_data():
    """Create demo data for all four features"""
    print("🎭 Creating Demo Data for Consolidated Passdown System")
    print("=" * 60)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if not db_manager.connect():
            print("❌ Failed to connect to database")
            return False
        
        print("✅ Connected to database successfully")
        
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        for collection_name in COLLECTIONS.values():
            db_manager.db[collection_name].delete_many({})
        print("✅ Existing data cleared")
        
        # Create Safety Issues
        print("\n🚨 Creating Safety Issues...")
        safety_collection = db_manager.db[COLLECTIONS['safety_issues']]
        safety_issues = [
            {
                "id": 1,
                "issue": "Chemical spill in clean room",
                "person": "Sarah Chen",
                "action": "Containment protocol initiated",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 2,
                "issue": "Equipment overheating alert",
                "person": "Mike Rodriguez", 
                "action": "Maintenance scheduled",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 3,
                "issue": "PPE compliance check",
                "person": "Lisa Wang",
                "action": "Training session planned",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            }
        ]
        
        for issue in safety_issues:
            safety_collection.insert_one(issue)
            print(f"  ✅ Created safety issue: {issue['issue'][:40]}...")
        
        # Create Kudos
        print("\n🏆 Creating Kudos...")
        kudos_collection = db_manager.db[COLLECTIONS['kudos']]
        kudos_entries = [
            {
                "id": 1,
                "name": "Alex Thompson",
                "action": "Improved yield by 2% through process optimization",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 2,
                "name": "Maria Garcia",
                "action": "Prevented downtime with proactive maintenance",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 3,
                "name": "David Kim",
                "action": "Mentored new team members effectively",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 4,
                "name": "Jennifer Liu",
                "action": "Streamlined quality control procedures",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            }
        ]
        
        for kudos in kudos_entries:
            kudos_collection.insert_one(kudos)
            print(f"  ✅ Created kudos for: {kudos['name']} - {kudos['action'][:30]}...")
        
        # Create Today's Issues
        print("\n📋 Creating Today's Issues...")
        today_collection = db_manager.db[COLLECTIONS['today_issues']]
        today_issues = [
            {
                "id": 1,
                "description": "Temperature sensor calibration drift in Cell A-1",
                "who": "Tech Team Alpha",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 2,
                "description": "Software update required for quality control system",
                "who": "IT Department",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 3,
                "description": "Routine maintenance check for wafer prep equipment",
                "who": "Tech Team Beta",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 4,
                "description": "Performance monitoring alert on lithography tool",
                "who": "Process Engineering",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 5,
                "description": "Chemical inventory check for etching process",
                "who": "Chemical Team",
                "date": "10/1",
                "timestamp": datetime.utcnow()
            }
        ]
        
        for issue in today_issues:
            today_collection.insert_one(issue)
            print(f"  ✅ Created today's issue #{issue['id']}: {issue['description'][:40]}...")
        
        # Create Yesterday's Issues
        print("\n📋 Creating Yesterday's Issues...")
        yesterday_collection = db_manager.db[COLLECTIONS['yesterday_issues']]
        yesterday_issues = [
            {
                "id": 1,
                "description": "Ion implant tool pressure variance detected",
                "who": "Tech Team Charlie",
                "done": "Yes",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 2,
                "description": "CMP tool requires pad replacement",
                "who": "Maintenance Team",
                "done": "No",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 3,
                "description": "Metrology station calibration overdue",
                "who": "Metrology Team",
                "done": "Yes",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 4,
                "description": "Annealing furnace temperature uniformity check",
                "who": "Process Team Delta",
                "done": "No",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 5,
                "description": "Packaging line efficiency optimization",
                "who": "Production Team",
                "done": "Yes",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 6,
                "description": "Final test equipment software glitch",
                "who": "Test Engineering",
                "done": "No",
                "date": "9/30",
                "timestamp": datetime.utcnow()
            }
        ]
        
        for issue in yesterday_issues:
            yesterday_collection.insert_one(issue)
            print(f"  ✅ Created yesterday's issue #{issue['id']}: {issue['description'][:40]}...")
        
        print(f"\n🎉 Demo data creation completed successfully!")
        print(f"📊 Created {len(safety_issues)} safety issues")
        print(f"📊 Created {len(kudos_entries)} kudos entries")
        print(f"📊 Created {len(today_issues)} today's issues")
        print(f"📊 Created {len(yesterday_issues)} yesterday's issues")
        print("\n🚀 You can now test the consolidated API!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create demo data: {str(e)}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()

if __name__ == "__main__":
    print("🎭 Consolidated Demo Data Creator")
    print("=" * 40)
    
    response = input("This will clear existing data and create new demo data. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = create_consolidated_demo_data()
        
        if success:
            print("\n🎯 Next steps:")
            print("1. Start the consolidated server: python consolidated_api.py")
            print("2. Start the frontend server: npm run dev (in frontend directory)")
            print("3. Open http://localhost:5173 to view the application")
            print("4. The dashboard will now show all demo data!")
        else:
            print("\n❌ Demo data creation failed. Please check your database connection.")
            sys.exit(1)
    else:
        print("Demo data creation cancelled.")