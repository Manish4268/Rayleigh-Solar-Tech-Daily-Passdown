import requests
import json

def quick_delete_test():
    url = "http://127.0.0.1:7071/api/stability/devices/LS%20w%2FTemp%2F25C%2F0%2F0"
    data = {"removedBy": "test_user"}
    
    print(f"🧪 Quick DELETE test: {url}")
    
    try:
        response = requests.delete(url, json=data, timeout=10)
        print(f"📥 Response: {response.status_code} - {response.text}")
        return response.status_code == 200 and "success" in response.text
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_delete_test()