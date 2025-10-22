import requests
import json
import time

def test_delete():
    # URL encode the path: "LS w/Temp/25C/0/0"
    url = "http://127.0.0.1:7071/api/stability/devices/LS%20w%2FTemp%2F25C%2F0%2F0"
    data = {"removedBy": "test_user"}
    
    print(f"🧪 Testing DELETE request to: {url}")
    print(f"📤 Request data: {json.dumps(data, indent=2)}")
    
    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            # First test if server is alive
            health_response = requests.get("http://127.0.0.1:7071/api/health", timeout=2)
            if health_response.status_code == 200:
                print(f"✅ Server is ready")
                break
        except:
            print(f"⏳ Waiting for server... (attempt {i+1}/{max_retries})")
            time.sleep(1)
    else:
        print(f"❌ Server not ready after {max_retries} attempts")
        return
    
    try:
        response = requests.delete(url, json=data, timeout=5)
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        print(f"📥 Response body: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_delete()