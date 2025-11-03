"""
Simple API Test - Quick verification of all endpoints
Just checks if endpoints respond with 200/201 status codes
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:7071/api"

def test_get(name, endpoint):
    """Test GET endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_post(name, endpoint, data):
    """Test POST endpoint"""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ {name}: {response.status_code}")
            return response.json() if response.text else None
        else:
            print(f"❌ {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return None

def test_put(name, endpoint, data):
    """Test PUT endpoint"""
    try:
        response = requests.put(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_delete(name, endpoint):
    """Test DELETE endpoint"""
    try:
        response = requests.delete(f"{BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

print("=" * 60)
print("SIMPLE API TEST - Backend Verification")
print("=" * 60)

# Health Check
print("\n1. Health Check")
test_get("GET /api/health", "/health")

# Safety Issues
print("\n2. Safety Issues")
test_get("GET /api/safety", "/safety")
result = test_post("POST /api/safety", "/safety", {
    "issue": "Test issue",
    "person": "Test person",
    "action": "Test action"
})
if result and result.get("data", {}).get("id"):
    test_id = result["data"]["id"]
    test_delete(f"DELETE /api/safety/{test_id}", f"/safety/{test_id}")

# Kudos
print("\n3. Kudos")
test_get("GET /api/kudos", "/kudos")
result = test_post("POST /api/kudos", "/kudos", {
    "name": "Test User",
    "action": "Test action",
    "by_whom": "Manager"
})
if result and result.get("data", {}).get("id"):
    test_id = result["data"]["id"]
    test_delete(f"DELETE /api/kudos/{test_id}", f"/kudos/{test_id}")

# Today's Issues
print("\n4. Today's Issues")
test_get("GET /api/today", "/today")
result = test_post("POST /api/today", "/today", {
    "description": "Test today issue",
    "who": "Test User"
})
if result and result.get("data", {}).get("id"):
    test_id = result["data"]["id"]
    test_put(f"PUT /api/today/{test_id}", f"/today/{test_id}", {
        "description": "Updated issue",
        "who": "Updated User"
    })
    test_delete(f"DELETE /api/today/{test_id}", f"/today/{test_id}")

# Yesterday's Issues
print("\n5. Yesterday's Issues")
test_get("GET /api/yesterday", "/yesterday")
result = test_post("POST /api/yesterday", "/yesterday", {
    "description": "Test yesterday issue",
    "who": "Test User",
    "done": "No"
})
if result and result.get("data", {}).get("id"):
    test_id = result["data"]["id"]
    test_put(f"PUT /api/yesterday/{test_id}", f"/yesterday/{test_id}", {
        "description": "Updated issue",
        "done": "Yes"
    })
    test_delete(f"DELETE /api/yesterday/{test_id}", f"/yesterday/{test_id}")

# Chart Data
print("\n6. Chart Data")
test_get("GET /api/charts/parameters", "/charts/parameters")
test_get("GET /api/charts/data/PCE", "/charts/data/PCE")
test_get("GET /api/charts/data/FF", "/charts/data/FF")
test_get("GET /api/charts/device-yield", "/charts/device-yield")
test_get("GET /api/charts/iv-repeatability", "/charts/iv-repeatability")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
