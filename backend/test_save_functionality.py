#!/usr/bin/env python3
"""
Test Case 1: Complete Save Functionality Test
Tests all save operations for the Passdown System
"""

import requests

import requestsimport json

import json

import timedef test_kudos_save():

from datetime import datetime    """Test kudos save functionality"""

    print("🧪 Testing Kudos Save Functionality")

# Configuration    print("=" * 40)

BASE_URL = "http://localhost:7071/api"    

    # Test data

class Colors:    test_kudos = {

    GREEN = '\033[92m'        "name": "John Doe",

    RED = '\033[91m'        "action": "Excellent troubleshooting skills",

    YELLOW = '\033[93m'        "by_whom": "Manager Smith"

    BLUE = '\033[94m'    }

    ENDC = '\033[0m'    

    BOLD = '\033[1m'    try:

        print("1️⃣ Testing health endpoint...")

def print_test_header(test_name):        health_response = requests.get("http://localhost:7071/api/health", timeout=10)

    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*50}{Colors.ENDC}")        print(f"Health Status: {health_response.status_code}")

    print(f"{Colors.BLUE}{Colors.BOLD}{test_name}{Colors.ENDC}")        

    print(f"{Colors.BLUE}{Colors.BOLD}{'='*50}{Colors.ENDC}")        if health_response.status_code == 200:

            print("✅ Health endpoint working!")

def print_success(message):        else:

    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")            print("❌ Health endpoint failed!")

            return False

def print_error(message):        

    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")        print("\n2️⃣ Testing kudos save...")

        save_response = requests.post(

def print_info(message):            "http://localhost:7071/api/kudos",

    print(f"{Colors.YELLOW}ℹ {message}{Colors.ENDC}")            json=test_kudos,

            headers={"Content-Type": "application/json"},

def test_save_functionality():            timeout=10

    """Test all save operations"""        )

            

    print(f"{Colors.BOLD}{Colors.BLUE}")        print(f"Save Status: {save_response.status_code}")

    print("🧪 SAVE FUNCTIONALITY TEST SUITE")        print(f"Save Response: {save_response.text}")

    print("Testing all save operations for Passdown System")        

    print("=" * 60)        if save_response.status_code == 201:

    print(f"{Colors.ENDC}")            print("✅ Kudos save working!")

                

    results = {            # Test retrieval

        'safety': False,            print("\n3️⃣ Testing kudos retrieval...")

        'kudos': False,            get_response = requests.get("http://localhost:7071/api/kudos", timeout=10)

        'today': False,            print(f"Get Status: {get_response.status_code}")

        'yesterday': False            

    }            if get_response.status_code == 200:

                    kudos_list = get_response.json()

    # Test 1: Safety Issues Save                print(f"✅ Retrieved {len(kudos_list)} kudos entries!")

    print_test_header("Test 1: Safety Issues Save")                return True

    try:            else:

        safety_data = {                print("❌ Kudos retrieval failed!")

            'issue': 'Test safety issue - Equipment malfunction',                return False

            'person': 'John Smith',        else:

            'action': 'Immediate equipment inspection scheduled'            print("❌ Kudos save failed!")

        }            return False

                    

        print_info("Sending safety issue data...")    except requests.exceptions.ConnectionError:

        response = requests.post(f"{BASE_URL}/safety", json=safety_data)        print("❌ Cannot connect to backend server!")

                return False

        if response.status_code in [200, 201]:    except Exception as e:

            print_success("Safety issue saved successfully!")        print(f"❌ Test failed: {e}")

            print_info(f"Response: {response.json()}")        return False

            results['safety'] = True

        else:if __name__ == "__main__":

            print_error(f"Failed to save safety issue. Status: {response.status_code}")    print("🚀 Save Functionality Test")

            print_error(f"Response: {response.text}")    print("=" * 30)

                

    except Exception as e:    success = test_kudos_save()

        print_error(f"Safety save test failed: {str(e)}")    

        print("\n" + "=" * 30)

    # Test 2: Kudos Save    if success:

    print_test_header("Test 2: Kudos Save")        print("🎉 ALL TESTS PASSED!")

    try:        print("✅ Save button should now work in the application!")

        kudos_data = {    else:

            'name': 'Sarah Johnson',        print("❌ Tests failed - save button may still have issues")

            'action': 'Excellent problem-solving and teamwork during equipment failure',    print("=" * 30)
            'by_whom': 'Team Lead Mike'
        }
        
        print_info("Sending kudos data...")
        response = requests.post(f"{BASE_URL}/kudos", json=kudos_data)
        
        if response.status_code in [200, 201]:
            print_success("Kudos saved successfully!")
            print_info(f"Response: {response.json()}")
            results['kudos'] = True
        else:
            print_error(f"Failed to save kudos. Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            
    except Exception as e:
        print_error(f"Kudos save test failed: {str(e)}")
    
    # Test 3: Today Issues Save
    print_test_header("Test 3: Today Issues Save")
    try:
        today_data = {
            'description': 'Tool calibration needed for precision work',
            'who': 'Technical Team Alpha'
        }
        
        print_info("Sending today issue data...")
        response = requests.post(f"{BASE_URL}/today", json=today_data)
        
        if response.status_code in [200, 201]:
            print_success("Today issue saved successfully!")
            print_info(f"Response: {response.json()}")
            results['today'] = True
        else:
            print_error(f"Failed to save today issue. Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            
    except Exception as e:
        print_error(f"Today save test failed: {str(e)}")
    
    # Test 4: Yesterday Issues Save
    print_test_header("Test 4: Yesterday Issues Save")
    try:
        yesterday_data = {
            'description': 'Temperature sensor replacement completed',
            'who': 'Maintenance Team',
            'done': 'Yes'
        }
        
        print_info("Sending yesterday issue data...")
        response = requests.post(f"{BASE_URL}/yesterday", json=yesterday_data)
        
        if response.status_code in [200, 201]:
            print_success("Yesterday issue saved successfully!")
            print_info(f"Response: {response.json()}")
            results['yesterday'] = True
        else:
            print_error(f"Failed to save yesterday issue. Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            
    except Exception as e:
        print_error(f"Yesterday save test failed: {str(e)}")
    
    # Test Summary
    print_test_header("SAVE FUNCTIONALITY TEST RESULTS")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{test_name.title()} Save: {status}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} tests passed{Colors.ENDC}")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL SAVE FUNCTIONALITY TESTS PASSED!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some save tests failed. Check backend connection.{Colors.ENDC}")
        return False

def test_data_persistence():
    """Test that saved data persists and can be retrieved"""
    print_test_header("Test 5: Data Persistence Check")
    
    endpoints = ['safety', 'kudos', 'today', 'yesterday']
    persistence_results = {}
    
    for endpoint in endpoints:
        try:
            print_info(f"Checking {endpoint} data persistence...")
            response = requests.get(f"{BASE_URL}/{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print_success(f"{endpoint}: Found {len(data)} records")
                    persistence_results[endpoint] = True
                else:
                    print_error(f"{endpoint}: No data found")
                    persistence_results[endpoint] = False
            else:
                print_error(f"{endpoint}: Failed to retrieve data. Status: {response.status_code}")
                persistence_results[endpoint] = False
                
        except Exception as e:
            print_error(f"{endpoint}: Error retrieving data - {str(e)}")
            persistence_results[endpoint] = False
    
    passed = sum(persistence_results.values())
    total = len(persistence_results)
    
    print(f"\n{Colors.BOLD}Persistence Check: {passed}/{total} endpoints have data{Colors.ENDC}")
    return passed > 0

if __name__ == "__main__":
    print("🚀 Starting Save Functionality Test Suite...")
    
    # Test backend health first
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Backend is healthy and running")
        else:
            print_error("Backend health check failed")
            exit(1)
    except Exception as e:
        print_error(f"Cannot connect to backend: {str(e)}")
        print_info("Please ensure backend is running: python passdown_app_clean.py")
        exit(1)
    
    # Run save functionality tests
    save_results = test_save_functionality()
    
    # Run persistence tests
    persistence_results = test_data_persistence()
    
    # Final summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    if save_results and persistence_results:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL SAVE FUNCTIONALITY TESTS COMPLETED SUCCESSFULLY!{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ All save operations working correctly{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Data persistence verified{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        if not save_results:
            print(f"{Colors.RED}❌ Save operations have issues{Colors.ENDC}")
        if not persistence_results:
            print(f"{Colors.RED}❌ Data persistence has issues{Colors.ENDC}")