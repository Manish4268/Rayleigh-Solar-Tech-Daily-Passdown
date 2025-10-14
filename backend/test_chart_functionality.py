#!/usr/bin/env python3
"""
Test Case 2: Chart Functionality Test
Tests chart data loading and parameter functionality
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

def test_chart_parameters():
    """Test chart parameters endpoint"""
    print_test_header("Test 1: Chart Parameters Loading")
    
    try:
        print_info("Requesting available chart parameters...")
        response = requests.get(f"{BASE_URL}/charts/parameters")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and 'parameters' in data:
                parameters = data['parameters']
                print_success(f"Successfully loaded {len(parameters)} parameters")
                print_info(f"Available parameters: {', '.join(parameters)}")
                
                # Validate expected parameters
                expected_params = ['PCE', 'FF', 'V_oc', 'I_sc', 'temperature', 'pressure']
                found_params = [p for p in expected_params if p in parameters]
                
                if len(found_params) >= 4:
                    print_success(f"Found {len(found_params)} expected parameters")
                    return True, parameters
                else:
                    print_error(f"Only found {len(found_params)} expected parameters")
                    return False, parameters
            else:
                print_error("Invalid response format - missing 'parameters' field")
                return False, []
        else:
            print_error(f"Failed to load parameters. Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, []
            
    except Exception as e:
        print_error(f"Parameters test failed: {str(e)}")
        return False, []

def test_chart_data(parameters):
    """Test chart data endpoints for different parameters"""
    print_test_header("Test 2: Chart Data Loading")
    
    if not parameters:
        print_error("No parameters available for testing")
        return False
    
    test_params = parameters[:5]  # Test first 5 parameters
    successful_tests = 0
    
    for param in test_params:
        try:
            print_info(f"Testing chart data for parameter: {param}")
            response = requests.get(f"{BASE_URL}/charts/data/{param}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    chart_data = data['data']
                    
                    if isinstance(chart_data, list) and len(chart_data) > 0:
                        print_success(f"{param}: Successfully loaded {len(chart_data)} data points")
                        
                        # Validate data structure
                        first_point = chart_data[0]
                        required_fields = ['batch', 'min', 'max', 'median', 'mean']
                        
                        if all(field in first_point for field in required_fields):
                            print_success(f"{param}: Data structure is valid")
                            successful_tests += 1
                        else:
                            print_error(f"{param}: Invalid data structure")
                    else:
                        print_error(f"{param}: No chart data received")
                else:
                    print_error(f"{param}: Invalid response format")
            else:
                print_error(f"{param}: Failed to load data. Status: {response.status_code}")
                
        except Exception as e:
            print_error(f"{param}: Chart data test failed - {str(e)}")
    
    success_rate = (successful_tests / len(test_params)) * 100
    print(f"\n{Colors.BOLD}Chart Data Test Results: {successful_tests}/{len(test_params)} parameters tested successfully ({success_rate:.1f}%){Colors.ENDC}")
    
    return successful_tests >= len(test_params) * 0.8  # 80% success rate

def test_chart_data_quality(parameters):
    """Test the quality and realism of chart data"""
    print_test_header("Test 3: Chart Data Quality Check")
    
    if not parameters:
        print_error("No parameters available for quality testing")
        return False
    
    # Test specific parameters for data quality
    quality_tests = ['PCE', 'FF', 'V_oc', 'temperature']
    available_quality_tests = [p for p in quality_tests if p in parameters]
    
    if not available_quality_tests:
        print_info("Using first available parameter for quality test")
        available_quality_tests = [parameters[0]]
    
    quality_passed = 0
    
    for param in available_quality_tests:
        try:
            print_info(f"Testing data quality for: {param}")
            response = requests.get(f"{BASE_URL}/charts/data/{param}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    chart_data = data['data']
                    
                    # Quality checks
                    quality_checks = {
                        'has_multiple_batches': len(chart_data) >= 2,
                        'has_statistical_data': all('std' in point for point in chart_data),
                        'has_count_data': all('count' in point for point in chart_data),
                        'realistic_ranges': all(point['min'] <= point['max'] for point in chart_data),
                        'median_in_range': all(point['min'] <= point['median'] <= point['max'] for point in chart_data)
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    print_info(f"{param}: Quality checks passed: {passed_checks}/{total_checks}")
                    
                    for check_name, passed in quality_checks.items():
                        status = "✓" if passed else "✗"
                        color = Colors.GREEN if passed else Colors.RED
                        print(f"  {color}{status} {check_name.replace('_', ' ').title()}{Colors.ENDC}")
                    
                    if passed_checks >= total_checks * 0.8:  # 80% of checks must pass
                        print_success(f"{param}: Data quality is good")
                        quality_passed += 1
                    else:
                        print_error(f"{param}: Data quality issues detected")
                else:
                    print_error(f"{param}: Could not retrieve data for quality check")
                    
        except Exception as e:
            print_error(f"{param}: Quality test failed - {str(e)}")
    
    quality_success_rate = (quality_passed / len(available_quality_tests)) * 100
    print(f"\n{Colors.BOLD}Data Quality Results: {quality_passed}/{len(available_quality_tests)} parameters passed quality checks ({quality_success_rate:.1f}%){Colors.ENDC}")
    
    return quality_passed >= len(available_quality_tests) * 0.8

def test_chart_functionality():
    """Main chart functionality test"""
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("📊 CHART FUNCTIONALITY TEST SUITE")
    print("Testing chart data loading and parameter functionality")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    # Test 1: Parameters loading
    params_success, parameters = test_chart_parameters()
    
    # Test 2: Chart data loading
    data_success = test_chart_data(parameters) if params_success else False
    
    # Test 3: Data quality
    quality_success = test_chart_data_quality(parameters) if params_success else False
    
    # Test Summary
    print_test_header("CHART FUNCTIONALITY TEST RESULTS")
    
    tests = {
        'Parameters Loading': params_success,
        'Chart Data Loading': data_success,
        'Data Quality Check': quality_success
    }
    
    passed_tests = sum(tests.values())
    total_tests = len(tests)
    
    for test_name, passed in tests.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{test_name}: {status}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Summary: {passed_tests}/{total_tests} chart tests passed{Colors.ENDC}")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL CHART FUNCTIONALITY TESTS PASSED!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some chart tests failed.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    print("📊 Starting Chart Functionality Test Suite...")
    
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
    
    # Run chart functionality tests
    chart_results = test_chart_functionality()
    
    # Final summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("📊 FINAL CHART TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    if chart_results:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL CHART FUNCTIONALITY TESTS COMPLETED SUCCESSFULLY!{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Chart parameters loading correctly{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Chart data endpoints working{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Data quality is good{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME CHART TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.RED}❌ Check chart endpoints and data generation{Colors.ENDC}")