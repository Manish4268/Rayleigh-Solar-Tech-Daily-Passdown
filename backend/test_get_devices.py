import requests
import json

def test_get_devices():
    url = "http://127.0.0.1:7071/api/stability/devices"
    
    print(f"🧪 Testing GET devices request to: {url}")
    
    try:
        response = requests.get(url)
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('devices'):
                print(f"📊 Found {len(data['devices'])} devices:")
                for i, device in enumerate(data['devices'][:3]):  # Show first 3
                    print(f"  {i+1}. Device: {device.get('deviceId', device.get('device_id', 'unknown'))}")
                    print(f"     Section: {device.get('sectionKey', device.get('section_key', 'unknown'))}")
                    print(f"     Subsection: {device.get('subsectionKey', device.get('subsection_key', 'unknown'))}")
                    print(f"     Position: row={device.get('row')}, col={device.get('col')}")
                    print(f"     Status: {device.get('status')}")
                    print()
            else:
                print("📭 No devices found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_get_devices()