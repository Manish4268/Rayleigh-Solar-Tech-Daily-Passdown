#!/usr/bin/env python3
"""
HTTP API Test for Analysis endpoint
Tests the Flask API endpoint with BaseLine.xlsx
"""

import requests
import json
import os
import time

def test_flask_api():
    """Test the Flask API endpoint with BaseLine.xlsx"""
    
    api_url = "http://localhost:7071/api/analysis/process"
    file_path = "../Data/BaseLine.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("🌐 TESTING FLASK API ENDPOINT")
    print("=" * 60)
    print(f"📍 API URL: {api_url}")
    print(f"📁 File: {file_path}")
    
    # Test options
    form_data = {
        'sheetsMode': 'top-k',
        'sheetsTopK': '3',  # String format as it comes from forms
        'devicesMode': 'top-k',
        'devicesTopK': '4',
        'pixelsPerDevice': '3',
        'method': 'minimize-sd',
        'basis': 'forward',
        'useAllSheets': 'true',
        'sheetIds': ''
    }
    
    print(f"⚙️ Form data: {form_data}")
    
    try:
        # Prepare file for upload
        with open(file_path, 'rb') as f:
            files = {'file': ('BaseLine.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("\n📤 Sending request...")
            start_time = time.time()
            
            response = requests.post(
                api_url,
                data=form_data,
                files=files,
                timeout=60  # 60 second timeout
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ SUCCESS!")
                print(f"Status: {result.get('status', 'unknown')}")
                print(f"Message: {result.get('message', 'no message')}")
                print(f"Filename: {result.get('fileName', 'no filename')}")
                
                summary = result.get('summary', {})
                print(f"\n📈 SUMMARY:")
                print(f"  Sheets processed: {summary.get('sheetsProcessed', 'N/A')}")
                print(f"  Devices analyzed: {summary.get('devicesAnalyzed', 'N/A')}")
                print(f"  Total pixels: {summary.get('totalPixels', 'N/A')}")
                
                results_data = result.get('results', [])
                print(f"\n📋 ANALYSIS RESULTS: ({len(results_data)} entries)")
                
                if results_data:
                    print("Top 3 results:")
                    for i, row in enumerate(results_data[:3]):
                        rank = row.get('Rank', i+1)
                        batch_id = row.get('Batch ID', 'N/A')
                        sheet_id = row.get('Sheet ID', 'N/A')
                        mean_pce = row.get('Combined mean PCE', 0)
                        sd_pce = row.get('Combined SD PCE', 0)
                        total_pixels = row.get('Total pixels used', 0)
                        
                        print(f"  {rank}. Batch: {batch_id}, Sheet: {sheet_id}")
                        print(f"     Mean PCE: {mean_pce:.4f}, SD PCE: {sd_pce:.4f}")
                        print(f"     Total Pixels: {total_pixels}")
                
                logs = result.get('logs', [])
                if logs:
                    print(f"\n📝 PROCESSING LOGS:")
                    for log in logs:
                        print(f"  {log}")
                
                return True
                
            else:
                print(f"\n❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error message: {error_data.get('message', 'No message')}")
                    logs = error_data.get('logs', [])
                    if logs:
                        print("Error logs:")
                        for log in logs:
                            print(f"  {log}")
                except:
                    print(f"Response text: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the Flask server running?")
        print("💡 Start server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the health endpoint to verify server is running"""
    health_url = "http://localhost:7071/api/health"
    
    print("🏥 TESTING HEALTH ENDPOINT")
    print("=" * 30)
    
    try:
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy!")
            print(f"Status: {health_data.get('status', 'unknown')}")
            print(f"MongoDB: {health_data.get('mongodb', 'unknown')}")
            
            features = health_data.get('features', [])
            print(f"Features: {len(features)}")
            for feature in features:
                print(f"  - {feature}")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 FLASK API ANALYSIS TEST")
    print("=" * 60)
    
    # Step 1: Check if server is running
    if not test_health_endpoint():
        print("\n💡 Please start the Flask server first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    print("\n")
    
    # Step 2: Test the analysis endpoint
    success = test_flask_api()
    
    if success:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n❌ Tests failed")

if __name__ == "__main__":
    main()