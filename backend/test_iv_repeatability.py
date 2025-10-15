#!/usr/bin/env python3
"""
Test the IV repeatability API endpoint
"""

import requests
import json

def test_iv_repeatability_endpoint():
    """Test the IV repeatability API endpoint"""
    url = "http://localhost:7071/api/charts/iv-repeatability"
    
    try:
        print(f"🔍 Testing IV repeatability endpoint: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print(f"📊 Success: {data.get('success')}")
            
            if data.get('success') and 'data' in data:
                iv_data = data['data']
                print(f"📋 Parameters: {iv_data.get('parameters', [])}")
                print(f"📅 Dates: {iv_data.get('dates', [])}")
                print(f"📊 Data points: {len(iv_data.get('repeatability_data', []))}")
                
                if iv_data.get('repeatability_data'):
                    sample_data = iv_data['repeatability_data'][0]
                    print(f"📈 Sample data point: {sample_data}")
            else:
                print(f"❌ API returned error: {data}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_iv_repeatability_endpoint()