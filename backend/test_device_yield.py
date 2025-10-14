#!/usr/bin/env python3
"""
Test the device yield API endpoint
"""

import requests
import json

def test_device_yield_endpoint():
    """Test the device yield API endpoint"""
    url = "http://localhost:7071/api/charts/device-yield"
    
    try:
        print(f"🔍 Testing device yield endpoint: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print(f"📊 Success: {data.get('success')}")
            
            if data.get('success') and 'data' in data:
                yield_data = data['data']
                print(f"📋 Parameters: {yield_data.get('parameters', [])}")
                print(f"📋 Batches: {yield_data.get('batches', [])}")
                print(f"📊 Quantiles sample: {dict(list(yield_data.get('quantiles', {}).items())[:3])}")
                print(f"📈 Batch averages sample: {dict(list(yield_data.get('batch_averages', {}).items())[:2])}")
            else:
                print(f"❌ API returned error: {data}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_device_yield_endpoint()