#!/usr/bin/env python3
"""
Test Case 1: Complete Save Functionality Test
Tests all save operations for the Passdown System
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:7071/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{test_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*50}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.ENDC}")

def test_save_functionality():
    """Test all save operations"""
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🧪 SAVE FUNCTIONALITY TEST SUITE")
    print("Testing all save operations for Passdown System")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    results = {
        'safety': False,
        'kudos': False,
        'today': False,
        'yesterday': False
    }
    
    # Test 1: Safety Issues Save
    print_test_header("Test 1: Safety Issues Save")
    try:
        safety_data = {
            'issue': 'Test safety issue - Equipment malfunction',
            'person': 'John Smith',
            'action': 'Immediate equipment inspection scheduled'
        }
        
        print_info("Sending safety issue data...")
        response = requests.post(f"{BASE_URL}/safety", json=safety_data)
        
        if response.status_code in [200, 201]:
            print_success("Safety issue saved successfully!")
            print_info(f"Response: {response.json()}")
            results['safety'] = True
        else:
            print_error(f"Failed to save safety issue. Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            
    except Exception as e:
        print_error(f"Safety save test failed: {str(e)}")
    
    # Test 2: Kudos Save
    print_test_header("Test 2: Kudos Save")
    try:
        kudos_data = {
            'name': 'Sarah Johnson',
            'action': 'Excellent problem-solving and teamwork during equipment failure',
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
    
    # Final summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    if save_results:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL SAVE FUNCTIONALITY TESTS COMPLETED SUCCESSFULLY!{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ All save operations working correctly{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.RED}❌ Save operations have issues{Colors.ENDC}")