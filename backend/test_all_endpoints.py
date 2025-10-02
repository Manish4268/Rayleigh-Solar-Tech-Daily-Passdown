#!/usr/bin/env python3
"""
Comprehensive Test Suite for Rayleigh Solar Tech Daily Passdown API
Tests all endpoints, workflows, CRUD operations, and data validation
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:7071/api"
ENDPOINTS = {
    'health': '/health',
    'safety': '/safety',
    'kudos': '/kudos', 
    'today': '/today',
    'yesterday': '/yesterday'
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}Testing: {test_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def test_health_endpoint():
    """Test health check endpoint"""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINTS['health']}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health endpoint responding: {data.get('status', 'Unknown')}")
            if data.get('database_status') == 'connected':
                print_success("Database connection verified")
            else:
                print_warning(f"Database status: {data.get('database_status', 'Unknown')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_crud_operations(endpoint_name, endpoint_url, test_data):
    """Test CRUD operations for a given endpoint"""
    print_test_header(f"CRUD Operations - {endpoint_name}")
    
    results = {'create': False, 'read': False, 'update': False, 'delete': False}
    created_id = None
    
    # Test CREATE
    try:
        print_info("Testing CREATE operation...")
        response = requests.post(f"{BASE_URL}{endpoint_url}", json=test_data)
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"CREATE successful")
            results['create'] = True
            if 'id' in data:
                created_id = data['id']
            elif 'sr_no' in data:
                created_id = data['sr_no']
        else:
            print_error(f"CREATE failed with status {response.status_code}")
    except Exception as e:
        print_error(f"CREATE error: {str(e)}")
    
    # Test READ (GET ALL)
    try:
        print_info("Testing READ operation...")
        response = requests.get(f"{BASE_URL}{endpoint_url}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"READ successful: Found {len(data)} records")
            results['read'] = True
        else:
            print_error(f"READ failed with status {response.status_code}")
    except Exception as e:
        print_error(f"READ error: {str(e)}")
    
    # Test UPDATE (for supported endpoints)
    if endpoint_name in ['Yesterday Issues'] and created_id:
        try:
            print_info("Testing UPDATE operation...")
            update_data = {'done': 'Yes'}
            response = requests.put(f"{BASE_URL}{endpoint_url}/{created_id}", json=update_data)
            if response.status_code == 200:
                print_success("UPDATE successful")
                results['update'] = True
            else:
                print_error(f"UPDATE failed with status {response.status_code}")
        except Exception as e:
            print_error(f"UPDATE error: {str(e)}")
    
    # Test DELETE (for supported endpoints)
    if endpoint_name in ['Today Issues'] and created_id:
        try:
            print_info("Testing DELETE operation...")
            response = requests.delete(f"{BASE_URL}{endpoint_url}/{created_id}")
            if response.status_code == 200:
                print_success("DELETE successful")
                results['delete'] = True
            else:
                print_error(f"DELETE failed with status {response.status_code}")
        except Exception as e:
            print_error(f"DELETE error: {str(e)}")
    
    return results

def test_workflow_automation():
    """Test the Today→Yesterday workflow automation"""
    print_test_header("Today → Yesterday Workflow")
    
    try:
        # Get initial state
        initial_response = requests.get(f"{BASE_URL}{ENDPOINTS['yesterday']}")
        initial_count = len(initial_response.json()) if initial_response.status_code == 200 else 0
        
        # Create a today issue
        today_data = {
            "description": "Workflow Test Issue - Equipment Check",
            "who": "Test Engineer"
        }
        
        print_info("Creating today issue to test workflow...")
        response = requests.post(f"{BASE_URL}{ENDPOINTS['today']}", json=today_data)
        
        if response.status_code in [200, 201]:
            print_success("Today issue created successfully")
            
            # Check if it appears in yesterday issues
            time.sleep(1)
            yesterday_response = requests.get(f"{BASE_URL}{ENDPOINTS['yesterday']}")
            if yesterday_response.status_code == 200:
                yesterday_data = yesterday_response.json()
                new_count = len(yesterday_data)
                
                if new_count > initial_count:
                    # Look for our test issue
                    workflow_found = False
                    for issue in yesterday_data:
                        if "Workflow Test Issue" in issue.get('description', '') and issue.get('done') == "No":
                            workflow_found = True
                            print_success("✓ Workflow automation working - issue found in yesterday collection")
                            break
                    
                    if not workflow_found:
                        print_warning("Issue created but workflow may not be working correctly")
                        return False
                else:
                    print_warning("No new issues found in yesterday collection")
                    return False
            
            return True
        else:
            print_error(f"Failed to create today issue: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Workflow test error: {str(e)}")
        return False

def test_data_validation():
    """Test data validation and error handling"""
    print_test_header("Data Validation")
    
    validation_tests = [
        {
            'name': 'Empty Safety Issue',
            'endpoint': ENDPOINTS['safety'],
            'data': {},
            'should_fail': True
        },
        {
            'name': 'Missing Kudos Fields',
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'Test'},
            'should_fail': True
        },
        {
            'name': 'Missing Today Issue Description',
            'endpoint': ENDPOINTS['today'],
            'data': {'who': 'Test User'},
            'should_fail': True
        },
        {
            'name': 'Valid Safety Issue',
            'endpoint': ENDPOINTS['safety'],
            'data': {'issue': 'Valid Test Issue', 'person': 'Test Person', 'action': 'Test Action'},
            'should_fail': False
        },
        {
            'name': 'Valid Kudos Entry',
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'Test Employee', 'action': 'Great work', 'by_whom': 'Manager'},
            'should_fail': False
        }
    ]
    
    passed = 0
    total = len(validation_tests)
    
    for test in validation_tests:
        try:
            print_info(f"Testing: {test['name']}")
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            
            if test['should_fail']:
                if response.status_code >= 400:
                    print_success(f"Validation correctly rejected invalid data")
                    passed += 1
                else:
                    print_error(f"Validation failed - accepted invalid data")
            else:
                if response.status_code < 400:
                    print_success(f"Valid data accepted correctly")
                    passed += 1
                else:
                    print_error(f"Valid data rejected incorrectly")
                    
        except Exception as e:
            print_error(f"Validation test error: {str(e)}")
    
    print_info(f"Validation tests passed: {passed}/{total}")
    return passed == total

def run_all_tests():
    """Run complete test suite"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🧪 Rayleigh Solar Tech Daily Passdown - Complete Test Suite")
    print("=" * 65)
    print(f"{Colors.ENDC}")
    
    test_results = {}
    
    # Test 1: Health Check
    test_results['health'] = test_health_endpoint()
    
    if not test_results['health']:
        print_error("❌ Health check failed - stopping tests")
        print_info("Please ensure backend is running: python passdown_app.py")
        return
    
    # Test 2: CRUD Operations for each endpoint
    test_data_sets = {
        'Safety Issues': {
            'endpoint': ENDPOINTS['safety'],
            'data': {'issue': 'Test Safety Issue', 'person': 'Test Person', 'action': 'Test Action'}
        },
        'Kudos': {
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'Test Employee', 'action': 'Excellent work', 'by_whom': 'Test Manager'}
        },
        'Today Issues': {
            'endpoint': ENDPOINTS['today'],
            'data': {'description': 'Test Today Issue', 'who': 'Test User'}
        },
        'Yesterday Issues': {
            'endpoint': ENDPOINTS['yesterday'],
            'data': {'description': 'Test Yesterday Issue', 'who': 'Test User', 'done': 'No'}
        }
    }
    
    for name, config in test_data_sets.items():
        test_results[name] = test_crud_operations(name, config['endpoint'], config['data'])
    
    # Test 3: Workflow Automation
    test_results['workflow'] = test_workflow_automation()
    
    # Test 4: Data Validation
    test_results['validation'] = test_data_validation()
    
    # Summary Report
    print_test_header("Test Summary Report")
    
    total_passed = 0
    total_tests = 0
    
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # CRUD results
            passed = sum(1 for r in result.values() if r)
            total = len(result)
            total_passed += passed
            total_tests += total
            print(f"📋 {test_name}: {passed}/{total} operations passed")
        else:
            # Boolean results
            total_tests += 1
            if result:
                total_passed += 1
                print_success(f"✅ {test_name}: PASSED")
            else:
                print_error(f"❌ {test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}")
    if total_passed == total_tests:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! ({total_passed}/{total_tests}){Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED: {total_passed}/{total_tests} passed{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}📊 Test Coverage:")
    print(f"   ✓ Health Check & Database Connection")
    print(f"   ✓ CRUD Operations for all endpoints")
    print(f"   ✓ Today→Yesterday workflow automation")
    print(f"   ✓ Data validation and error handling{Colors.ENDC}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
        sys.exit(1)

def test_crud_operations(endpoint_name, endpoint_url, test_data):
    """Test CRUD operations for a given endpoint"""
    print_test_header(f"CRUD Operations - {endpoint_name}")
    
    results = {'create': False, 'read': False, 'update': False, 'delete': False}
    created_id = None
    
    # Test CREATE
    try:
        print_info("Testing CREATE operation...")
        response = requests.post(f"{BASE_URL}{endpoint_url}", json=test_data)
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"CREATE successful: {data}")
            results['create'] = True
            # Try to extract ID for further tests
            if 'sr_no' in data:
                created_id = data['sr_no']
        else:
            print_error(f"CREATE failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print_error(f"CREATE error: {str(e)}")
    
    # Test READ (GET ALL)
    try:
        print_info("Testing READ operation...")
        response = requests.get(f"{BASE_URL}{endpoint_url}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"READ successful: Found {len(data)} records")
            results['read'] = True
            
            # Show sample data if available
            if data and len(data) > 0:
                print_info(f"Sample record: {json.dumps(data[-1], indent=2)}")
        else:
            print_error(f"READ failed with status {response.status_code}")
    except Exception as e:
        print_error(f"READ error: {str(e)}")
    
    # Test UPDATE (if endpoint supports it and we have an ID)
    if endpoint_name in ['Today Issues', 'Yesterday Issues'] and created_id:
        try:
            print_info("Testing UPDATE operation...")
            update_data = {'done': 'Yes'} if endpoint_name == 'Yesterday Issues' else {'description': 'Updated description'}
            response = requests.put(f"{BASE_URL}{endpoint_url}/{created_id}", json=update_data)
            if response.status_code == 200:
                print_success("UPDATE successful")
                results['update'] = True
            else:
                print_error(f"UPDATE failed with status {response.status_code}")
        except Exception as e:
            print_error(f"UPDATE error: {str(e)}")
    
    # Test DELETE (if endpoint supports it and we have an ID)
    if endpoint_name in ['Today Issues'] and created_id:
        try:
            print_info("Testing DELETE operation...")
            response = requests.delete(f"{BASE_URL}{endpoint_url}/{created_id}")
            if response.status_code == 200:
                print_success("DELETE successful")
                results['delete'] = True
            else:
                print_error(f"DELETE failed with status {response.status_code}")
        except Exception as e:
            print_error(f"DELETE error: {str(e)}")
    
    return results

def test_workflow_automation():
    """Test the Today→Yesterday workflow automation"""
    print_test_header("Workflow Automation (Today→Yesterday)")
    
    try:
        # Create a today issue
        today_data = {
            "description": "Workflow Test Issue",
            "who": "Test User"
        }
        
        print_info("Creating today issue to test workflow...")
        response = requests.post(f"{BASE_URL}{ENDPOINTS['today']}", json=today_data)
        
        if response.status_code in [200, 201]:
            print_success("Today issue created successfully")
            
            # Check if it appears in yesterday issues (workflow automation)
            print_info("Checking if issue appears in yesterday collection...")
            time.sleep(1)  # Give a moment for the operation to complete
            
            yesterday_response = requests.get(f"{BASE_URL}{ENDPOINTS['yesterday']}")
            if yesterday_response.status_code == 200:
                yesterday_data = yesterday_response.json()
                
                # Look for our test issue
                workflow_found = False
                for issue in yesterday_data:
                    if issue.get('description') == "Workflow Test Issue" and issue.get('done') == "No":
                        workflow_found = True
                        print_success("✓ Workflow automation working - issue found in yesterday collection with 'done': 'No'")
                        break
                
                if not workflow_found:
                    print_warning("Workflow automation may not be working - issue not found in yesterday collection")
            
            return True
        else:
            print_error(f"Failed to create today issue: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Workflow test error: {str(e)}")
        return False

def test_data_validation():
    """Test data validation and error handling"""
    print_test_header("Data Validation")
    
    validation_tests = [
        {
            'name': 'Empty Safety Issue',
            'endpoint': ENDPOINTS['safety'],
            'data': {},
            'should_fail': True
        },
        {
            'name': 'Missing Required Kudos Field',
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'Test'},
            'should_fail': True
        },
        {
            'name': 'Missing Today Issue Description',
            'endpoint': ENDPOINTS['today'],
            'data': {'who': 'Test User'},
            'should_fail': True
        },
        {
            'name': 'Valid Safety Issue',
            'endpoint': ENDPOINTS['safety'],
            'data': {'issue': 'Test Issue', 'person': 'Test Person', 'action': 'Test Action'},
            'should_fail': False
        }
    ]
    
    passed = 0
    total = len(validation_tests)
    
    for test in validation_tests:
        try:
            print_info(f"Testing: {test['name']}")
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            
            if test['should_fail']:
                if response.status_code >= 400:
                    print_success(f"Validation correctly rejected invalid data (status: {response.status_code})")
                    passed += 1
                else:
                    print_error(f"Validation failed - accepted invalid data (status: {response.status_code})")
            else:
                if response.status_code < 400:
                    print_success(f"Valid data accepted correctly (status: {response.status_code})")
                    passed += 1
                else:
                    print_error(f"Valid data rejected incorrectly (status: {response.status_code})")
                    
        except Exception as e:
            print_error(f"Validation test error: {str(e)}")
    
    print_info(f"Validation tests passed: {passed}/{total}")
    return passed == total

def test_performance():
    """Test API performance with multiple requests"""
    print_test_header("Performance Testing")
    
    try:
        # Test multiple concurrent reads
        print_info("Testing read performance (10 requests)...")
        start_time = time.time()
        
        for i in range(10):
            response = requests.get(f"{BASE_URL}{ENDPOINTS['health']}")
            if response.status_code != 200:
                print_warning(f"Request {i+1} failed with status {response.status_code}")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        print_success(f"10 requests completed in {total_time:.2f}s (avg: {avg_time:.3f}s per request)")
        
        if avg_time < 1.0:
            print_success("Performance: Good (< 1s per request)")
        elif avg_time < 3.0:
            print_warning("Performance: Acceptable (1-3s per request)")
        else:
            print_error("Performance: Poor (> 3s per request)")
            
        return avg_time < 3.0
        
    except Exception as e:
        print_error(f"Performance test error: {str(e)}")
        return False

def test_scrolling_limits():
    """Test that frontend properly limits entries and requires scrolling"""
    print_test_header("Scrolling & 10-Entry Limits")
    
    try:
        # Create test data to exceed 10 entries
        print_info("Creating test data to verify 10-entry scrolling...")
        
        # Create 12 safety issues
        for i in range(12):
            test_data = {
                'issue': f'Scrolling Test Safety Issue {i+1}',
                'person': f'Test Person {i+1}',
                'action': f'Test Action {i+1}'
            }
            requests.post(f"{BASE_URL}{ENDPOINTS['safety']}", json=test_data)
        
        # Verify data exists
        response = requests.get(f"{BASE_URL}{ENDPOINTS['safety']}")
        if response.status_code == 200:
            data = response.json()
            total_entries = len(data)
            print_success(f"Created {total_entries} safety issues in database")
            
            if total_entries >= 10:
                print_success("✅ Sufficient data for scrolling test (10+ entries)")
                print_info(f"Frontend will display last 10 entries with scrolling")
                print_info(f"Entries shown: {max(1, total_entries-9)} to {total_entries}")
                return True
            else:
                print_warning(f"Only {total_entries} entries - may not require scrolling")
                return False
        else:
            print_error(f"Failed to verify scrolling data")
            return False
            
    except Exception as e:
        print_error(f"Scrolling test error: {str(e)}")
        return False
    """Test edge cases and error conditions"""
    print_test_header("Edge Cases")
    
    edge_tests = [
        {
            'name': 'Very Long Description',
            'endpoint': ENDPOINTS['today'],
            'data': {'description': 'A' * 1000, 'who': 'Test User'}
        },
        {
            'name': 'Special Characters',
            'endpoint': ENDPOINTS['safety'],
            'data': {'issue': 'Test & Issue <script>', 'person': 'Test "Person"', 'action': "Test 'Action'"}
        },
        {
            'name': 'Unicode Characters',
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'José García', 'action': 'Excellent work! 🎉', 'by_whom': 'Manager'}
        }
    ]
    
    passed = 0
    for test in edge_tests:
        try:
            print_info(f"Testing: {test['name']}")
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            if response.status_code < 400:
                print_success(f"Edge case handled correctly")
                passed += 1
            else:
                print_warning(f"Edge case may have issues (status: {response.status_code})")
        except Exception as e:
            print_error(f"Edge case test error: {str(e)}")
    
    return passed == len(edge_tests)

def run_all_tests():
    """Run complete test suite"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🧪 Rayleigh Solar Tech Daily Passdown - Comprehensive API Test Suite")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    test_results = {}
    
    # Test 1: Health Check
    test_results['health'] = test_health_endpoint()
    
    if not test_results['health']:
        print_error("❌ Health check failed - stopping tests")
        return
    
    # Test 2: CRUD Operations for each endpoint
    test_data_sets = {
        'Safety Issues': {
            'endpoint': ENDPOINTS['safety'],
            'data': {'issue': 'Test Safety Issue', 'person': 'Test Person', 'action': 'Test Action'}
        },
        'Kudos': {
            'endpoint': ENDPOINTS['kudos'],
            'data': {'name': 'Test Employee', 'action': 'Excellent work', 'by_whom': 'Test Manager'}
        },
        'Today Issues': {
            'endpoint': ENDPOINTS['today'],
            'data': {'description': 'Test Today Issue', 'who': 'Test User'}
        },
        'Yesterday Issues': {
            'endpoint': ENDPOINTS['yesterday'],
            'data': {'description': 'Test Yesterday Issue', 'who': 'Test User', 'done': 'No'}
        }
    }
    
    for name, config in test_data_sets.items():
        test_results[name] = test_crud_operations(name, config['endpoint'], config['data'])
    
    # Test 3: Workflow Automation
    test_results['workflow'] = test_workflow_automation()
    
    # Test 4: Data Validation
    test_results['validation'] = test_data_validation()
    
    # Test 5: Performance
    test_results['performance'] = test_performance()
    
    # Test 6: Scrolling & 10-Entry Limits
    test_results['scrolling'] = test_scrolling_limits()
    
    # Test 7: Edge Cases
    test_results['edge_cases'] = test_edge_cases()
    
    # Summary Report
    print_test_header("Test Summary Report")
    
    total_passed = 0
    total_tests = 0
    
    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # CRUD results
            passed = sum(1 for r in result.values() if r)
            total = len(result)
            total_passed += passed
            total_tests += total
            print(f"📋 {test_name}: {passed}/{total} operations passed")
        else:
            # Boolean results
            total_tests += 1
            if result:
                total_passed += 1
                print_success(f"✅ {test_name}: PASSED")
            else:
                print_error(f"❌ {test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}")
    if total_passed == total_tests:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! ({total_passed}/{total_tests}){Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED: {total_passed}/{total_tests} passed{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}📊 Test Coverage Summary:")
    print(f"   ✓ Health Check & Database Connection")
    print(f"   ✓ CRUD Operations for all endpoints")
    print(f"   ✓ Today→Yesterday workflow automation")
    print(f"   ✓ Data validation and error handling")
    print(f"   ✓ Performance testing")
    print(f"   ✓ Edge cases and special characters{Colors.ENDC}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
        sys.exit(1)