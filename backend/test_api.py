import requests

# Test if the API endpoints are working
def test_api():
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:7071/api/health")
        print(f"Health check: {response.status_code} - {response.text}")
        
        # Test stability grid data
        response = requests.get("http://127.0.0.1:7071/api/stability/grid-data")
        print(f"Grid data: {response.status_code}")
        
        # Test devices endpoint
        response = requests.get("http://127.0.0.1:7071/api/stability/devices")
        print(f"Devices: {response.status_code}")
        
        print("\n🧪 Now testing DELETE with debug...")
        response = requests.delete("http://127.0.0.1:7071/api/stability/devices/LS%20w%2FTemp%2F25C%2F0%2F0", 
                                 json={"removedBy": "test"})
        print(f"Delete: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()