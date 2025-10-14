#!/usr/bin/env python3
"""
Test Chart Endpoints
"""

import requests
import json

BASE_URL = "http://localhost:7071/api"

def test_chart_endpoints():
    print("🧪 Testing Chart Endpoints")
    print("=" * 40)
    
    # Test 1: Get chart parameters
    print("\n1️⃣ Testing: GET /api/charts/parameters")
    try:
        response = requests.get(f"{BASE_URL}/charts/parameters", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('parameters', []))} parameters")
            parameters = data.get('parameters', [])
            print(f"Parameters: {parameters[:5]}...")  # Show first 5
            
            # Test 2: Get data for a specific parameter
            if parameters:
                test_param = parameters[0]
                print(f"\n2️⃣ Testing: GET /api/charts/data/{test_param}")
                response = requests.get(f"{BASE_URL}/charts/data/{test_param}", timeout=5)
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success: Got data for {test_param}")
                    chart_data = data.get('data', [])
                    print(f"Batches: {len(chart_data)} batches")
                    if chart_data:
                        print(f"Sample data: {chart_data[0]}")
                else:
                    print(f"❌ Failed: {response.text}")
            else:
                print("❌ No parameters to test")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_chart_endpoints()