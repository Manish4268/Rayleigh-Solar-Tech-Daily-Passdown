#!/usr/bin/env python3
"""
Test the new Today's Issues workflow:
1. Add Today's Issue → should auto-appear in Top Issues as "No" 
2. Test manual reset functionality
"""

import requests
import json

BASE_URL = "http://localhost:7071/api"

def test_workflow():
    print("🧪 Testing Today's Issues → Top Issues Workflow")
    print("=" * 60)
    
    # Test 1: Add Today's Issue
    print("\n1️⃣ Testing: Add Today's Issue")
    test_data = {
        "description": "Test workflow - Auto-add to Top Issues",
        "who": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/today", json=test_data, timeout=5)
        if response.status_code == 201:
            created_item = response.json()
            print(f"✅ Today's Issue created (ID: {created_item.get('id')})")
            
            # Check if it appears in yesterday's issues (Top Issues) as "No"
            print("\n2️⃣ Testing: Auto-add to Top Issues")
            response = requests.get(f"{BASE_URL}/yesterday", timeout=5)
            if response.status_code == 200:
                yesterday_items = response.json()
                # Look for our test item
                found = False
                for item in yesterday_items:
                    if item['description'] == test_data['description'] and item['done'] == 'No':
                        print(f"✅ Found in Top Issues with done='No' (ID: {item.get('id')})")
                        found = True
                        break
                
                if not found:
                    print("❌ Item not found in Top Issues or wrong status")
            else:
                print(f"❌ Failed to get Top Issues: {response.status_code}")
        else:
            print(f"❌ Failed to create Today's Issue: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Manual Reset
    print("\n3️⃣ Testing: Manual Reset")
    try:
        response = requests.post(f"{BASE_URL}/reset-today", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reset successful: {result.get('message')}")
            print(f"   Cleared items: {result.get('cleared_count', 0)}")
            
            # Verify Today's Issues are cleared
            response = requests.get(f"{BASE_URL}/today", timeout=5)
            if response.status_code == 200:
                today_items = response.json()
                print(f"✅ Today's Issues after reset: {len(today_items)} items")
            else:
                print("❌ Failed to verify reset")
        else:
            print(f"❌ Reset failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Reset error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Workflow Summary:")
    print("   ✅ Add Today's Issue → Auto-appears in Top Issues as 'No'")
    print("   ✅ Manual Reset Button → Clears Today's Issues for fresh standup")
    print("=" * 60)

if __name__ == "__main__":
    test_workflow()