"""
Comprehensive API Test Suite
Tests all backend endpoints and validates responses for frontend consumption
"""
import requests
import json
from datetime import datetime
import sys

# API Configuration
BASE_URL = "http://localhost:7071/api"
TIMEOUT = 30  # seconds

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'-'*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'-'*80}{Colors.END}")

def print_test(name, status, details="", response_data=None):
    status_icon = f"{Colors.GREEN}✅{Colors.END}" if status == "PASS" else f"{Colors.RED}❌{Colors.END}"
    print(f"{status_icon} {Colors.BOLD}{name}{Colors.END}: ", end="")
    
    if status == "PASS":
        print(f"{Colors.GREEN}{details}{Colors.END}")
        if response_data:
            print(f"   {Colors.BLUE}Response Preview: {json.dumps(response_data, indent=2)[:200]}...{Colors.END}")
    else:
        print(f"{Colors.RED}{details}{Colors.END}")

def print_summary(passed, failed, total):
    print_header("TEST SUMMARY")
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total}")
    print(f"{Colors.GREEN}✅ Passed:{Colors.END} {passed}")
    print(f"{Colors.RED}❌ Failed:{Colors.END} {failed}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED ⚠️{Colors.END}\n")

# Test counters
passed = 0
failed = 0
total = 0

def test_endpoint(name, url, method="GET", data=None, expected_keys=None, check_success=True):
    """Generic test function for API endpoints"""
    global passed, failed, total
    total += 1
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TIMEOUT)
        
        # Check status code
        if response.status_code not in [200, 201]:
            print_test(name, "FAIL", f"Status: {response.status_code}")
            failed += 1
            return None
        
        # Parse JSON
        response_data = response.json()
        
        # Check for success field if expected
        if check_success:
            if "success" not in response_data:
                print_test(name, "FAIL", "Missing 'success' field")
                failed += 1
                return None
            
            if response_data["success"] != True:
                print_test(name, "FAIL", f"success=False, error: {response_data.get('error', 'Unknown')}")
                failed += 1
                return None
        
        # Check expected keys
        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in response_data]
            if missing_keys:
                print_test(name, "FAIL", f"Missing keys: {missing_keys}")
                failed += 1
                return None
        
        passed += 1
        
        # Create preview data
        preview = {}
        if "data" in response_data:
            data_val = response_data["data"]
            if isinstance(data_val, list):
                preview["data_count"] = len(data_val)
                if len(data_val) > 0:
                    preview["first_item"] = data_val[0]
            else:
                preview["data"] = data_val
        else:
            preview = response_data
        
        print_test(name, "PASS", f"Status: {response.status_code}", preview)
        return response_data
        
    except requests.exceptions.Timeout:
        print_test(name, "FAIL", "Request timeout")
        failed += 1
        return None
    except requests.exceptions.ConnectionError:
        print_test(name, "FAIL", "Connection error - Is the server running?")
        failed += 1
        return None
    except Exception as e:
        print_test(name, "FAIL", f"Error: {str(e)}")
        failed += 1
        return None

# ============================================================================
# START TESTS
# ============================================================================

print_header("🚀 COMPREHENSIVE API TEST SUITE")
print(f"{Colors.BOLD}Testing Backend: {BASE_URL}{Colors.END}")
print(f"{Colors.BOLD}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")

# ============================================================================
# 1. HEALTH CHECK
# ============================================================================
print_section("📡 1. HEALTH CHECK")
test_endpoint(
    "Health Check",
    f"{BASE_URL}/health",
    expected_keys=["status", "mongodb"]
)

# ============================================================================
# 2. SAFETY ISSUES API
# ============================================================================
print_section("🛡️ 2. SAFETY ISSUES API")

# Get all safety issues
safety_data = test_endpoint(
    "Get All Safety Issues",
    f"{BASE_URL}/safety",
    expected_keys=["success", "data"]
)

# Create safety issue
new_safety = {
    "description": "Test safety issue from comprehensive test",
    "date": datetime.now().strftime("%Y-%m-%d")
}
created_safety = test_endpoint(
    "Create Safety Issue",
    f"{BASE_URL}/safety",
    method="POST",
    data=new_safety,
    expected_keys=["success", "data"]
)

# Update safety issue (if we have one)
if created_safety and created_safety.get("data"):
    safety_id = created_safety["data"].get("id")
    if safety_id:
        update_data = {
            "description": "Updated test safety issue",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        test_endpoint(
            "Update Safety Issue",
            f"{BASE_URL}/safety/{safety_id}",
            method="PUT",
            data=update_data,
            expected_keys=["success"]
        )
        
        # Delete safety issue
        test_endpoint(
            "Delete Safety Issue",
            f"{BASE_URL}/safety/{safety_id}",
            method="DELETE",
            expected_keys=["success"]
        )

# ============================================================================
# 3. KUDOS API
# ============================================================================
print_section("🌟 3. KUDOS API")

# Get all kudos
kudos_data = test_endpoint(
    "Get All Kudos",
    f"{BASE_URL}/kudos",
    expected_keys=["success", "data"]
)

# Create kudos
new_kudos = {
    "name": "Test User",
    "reason": "Comprehensive API testing",
    "date": datetime.now().strftime("%Y-%m-%d")
}
created_kudos = test_endpoint(
    "Create Kudos",
    f"{BASE_URL}/kudos",
    method="POST",
    data=new_kudos,
    expected_keys=["success", "data"]
)

# Update kudos (if we have one)
if created_kudos and created_kudos.get("data"):
    kudos_id = created_kudos["data"].get("id")
    if kudos_id:
        update_data = {
            "name": "Test User Updated",
            "reason": "Updated comprehensive API testing",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        test_endpoint(
            "Update Kudos",
            f"{BASE_URL}/kudos/{kudos_id}",
            method="PUT",
            data=update_data,
            expected_keys=["success"]
        )
        
        # Delete kudos
        test_endpoint(
            "Delete Kudos",
            f"{BASE_URL}/kudos/{kudos_id}",
            method="DELETE",
            expected_keys=["success"]
        )

# ============================================================================
# 4. TODAY'S ISSUES API
# ============================================================================
print_section("📅 4. TODAY'S ISSUES API")

# Get all today's issues
today_data = test_endpoint(
    "Get All Today's Issues",
    f"{BASE_URL}/today",
    expected_keys=["success", "data"]
)

# Create today's issue
new_today = {
    "description": "Test today issue",
    "who": "Test User",
    "date": datetime.now().strftime("%Y-%m-%d")
}
created_today = test_endpoint(
    "Create Today's Issue",
    f"{BASE_URL}/today",
    method="POST",
    data=new_today,
    expected_keys=["success", "data"]
)

# Update today's issue (if we have one)
if created_today and created_today.get("data"):
    today_id = created_today["data"].get("id")
    if today_id:
        update_data = {
            "description": "Updated test today issue",
            "who": "Test User Updated",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        test_endpoint(
            "Update Today's Issue",
            f"{BASE_URL}/today/{today_id}",
            method="PUT",
            data=update_data,
            expected_keys=["success"]
        )
        
        # Delete today's issue
        test_endpoint(
            "Delete Today's Issue",
            f"{BASE_URL}/today/{today_id}",
            method="DELETE",
            expected_keys=["success"]
        )

# ============================================================================
# 5. YESTERDAY'S ISSUES API
# ============================================================================
print_section("📆 5. YESTERDAY'S ISSUES API")

# Get all yesterday's issues
yesterday_data = test_endpoint(
    "Get All Yesterday's Issues",
    f"{BASE_URL}/yesterday",
    expected_keys=["success", "data"]
)

# Create yesterday's issue
new_yesterday = {
    "description": "Test yesterday issue",
    "who": "Test User",
    "date": datetime.now().strftime("%Y-%m-%d")
}
created_yesterday = test_endpoint(
    "Create Yesterday's Issue",
    f"{BASE_URL}/yesterday",
    method="POST",
    data=new_yesterday,
    expected_keys=["success", "data"]
)

# Update yesterday's issue (if we have one)
if created_yesterday and created_yesterday.get("data"):
    yesterday_id = created_yesterday["data"].get("id")
    if yesterday_id:
        update_data = {
            "description": "Updated test yesterday issue",
            "who": "Test User Updated",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        test_endpoint(
            "Update Yesterday's Issue",
            f"{BASE_URL}/yesterday/{yesterday_id}",
            method="PUT",
            data=update_data,
            expected_keys=["success"]
        )
        
        # Delete yesterday's issue
        test_endpoint(
            "Delete Yesterday's Issue",
            f"{BASE_URL}/yesterday/{yesterday_id}",
            method="DELETE",
            expected_keys=["success"]
        )

# ============================================================================
# 6. CHART DATA API
# ============================================================================
print_section("📊 6. CHART DATA API")

# Get available parameters
params_data = test_endpoint(
    "Get Chart Parameters",
    f"{BASE_URL}/charts/parameters",
    expected_keys=["success", "parameters"]
)

# Test specific parameter data (PCE)
test_endpoint(
    "Get Chart Data - PCE",
    f"{BASE_URL}/charts/data/PCE",
    expected_keys=["success", "parameter", "data"]
)

# Test specific parameter data (FF)
test_endpoint(
    "Get Chart Data - FF",
    f"{BASE_URL}/charts/data/FF",
    expected_keys=["success", "parameter", "data"]
)

# Test specific parameter data (Max Power)
test_endpoint(
    "Get Chart Data - Max Power",
    f"{BASE_URL}/charts/data/Max Power",
    expected_keys=["success", "parameter", "data"]
)

# Get device yield data
device_yield = test_endpoint(
    "Get Device Yield Data",
    f"{BASE_URL}/charts/device-yield",
    expected_keys=["success", "data"]
)

# Get IV repeatability data
iv_repeat = test_endpoint(
    "Get IV Repeatability Data",
    f"{BASE_URL}/charts/iv-repeatability",
    expected_keys=["success", "data"]
)

# ============================================================================
# 7. FRONTEND COMPATIBILITY CHECKS
# ============================================================================
print_section("🎨 7. FRONTEND COMPATIBILITY VALIDATION")

# Validate safety issues data structure for frontend
if safety_data and safety_data.get("data"):
    data_items = safety_data["data"]
    if isinstance(data_items, list):
        if len(data_items) > 0:
            item = data_items[0]
            # Safety issues should have: id, date, and at least one of (issue/action/person)
            has_required = "id" in item and "date" in item
            has_content = any(key in item for key in ["issue", "action", "person", "description"])
            if has_required and has_content:
                print_test("Safety Issues - Frontend Compatible", "PASS", 
                          f"Data structure valid, {len(data_items)} items")
                passed += 1
            else:
                missing = []
                if "id" not in item: missing.append("id")
                if "date" not in item: missing.append("date")
                if not has_content: missing.append("content_field")
                print_test("Safety Issues - Frontend Compatible", "FAIL", 
                          f"Missing required fields: {missing}")
                failed += 1
        else:
            print_test("Safety Issues - Frontend Compatible", "PASS", 
                      "Empty list (valid)")
            passed += 1
    else:
        print_test("Safety Issues - Frontend Compatible", "FAIL", 
                  "Data is not a list")
        failed += 1
    total += 1

# Validate kudos data structure for frontend
if kudos_data and kudos_data.get("data"):
    data_items = kudos_data["data"]
    if isinstance(data_items, list):
        if len(data_items) > 0:
            item = data_items[0]
            # Kudos should have: id, name, date, and at least one of (action/reason/by_whom)
            has_required = "id" in item and "name" in item and "date" in item
            has_reason = any(key in item for key in ["action", "reason", "by_whom"])
            if has_required and has_reason:
                print_test("Kudos - Frontend Compatible", "PASS", 
                          f"Data structure valid, {len(data_items)} items")
                passed += 1
            else:
                missing = []
                if "id" not in item: missing.append("id")
                if "name" not in item: missing.append("name")
                if "date" not in item: missing.append("date")
                if not has_reason: missing.append("reason_field")
                print_test("Kudos - Frontend Compatible", "FAIL", 
                          f"Missing required fields: {missing}")
                failed += 1
        else:
            print_test("Kudos - Frontend Compatible", "PASS", 
                      "Empty list (valid)")
            passed += 1
    else:
        print_test("Kudos - Frontend Compatible", "FAIL", 
                  "Data is not a list")
        failed += 1
    total += 1

# Validate chart data structure for frontend (ParameterChart component)
if params_data and params_data.get("parameters"):
    params = params_data["parameters"]
    if isinstance(params, list) and len(params) > 0:
        print_test("Chart Parameters - Frontend Compatible", "PASS", 
                  f"{len(params)} parameters available")
        passed += 1
    else:
        print_test("Chart Parameters - Frontend Compatible", "FAIL", 
                  "Invalid parameters list")
        failed += 1
    total += 1

# Validate device yield data structure
if device_yield and device_yield.get("data"):
    data = device_yield["data"]
    if isinstance(data, dict):
        required_keys = ["batches", "parameters"]
        has_required = all(key in data for key in required_keys)
        if has_required:
            batch_count = len(data.get("batches", []))
            param_count = len(data.get("parameters", []))
            print_test("Device Yield - Frontend Compatible", "PASS", 
                      f"{batch_count} batches, {param_count} parameters")
            passed += 1
        else:
            print_test("Device Yield - Frontend Compatible", "FAIL", 
                      f"Missing required keys: {required_keys}")
            failed += 1
    else:
        print_test("Device Yield - Frontend Compatible", "FAIL", 
                  "Data is not a dict")
        failed += 1
    total += 1

# Validate IV repeatability data structure
if iv_repeat and iv_repeat.get("data"):
    data = iv_repeat["data"]
    if isinstance(data, dict):
        required_keys = ["dates", "parameters"]
        has_required = all(key in data for key in required_keys)
        if has_required:
            date_count = len(data.get("dates", []))
            param_count = len(data.get("parameters", []))
            print_test("IV Repeatability - Frontend Compatible", "PASS", 
                      f"{date_count} dates, {param_count} parameters")
            passed += 1
        else:
            print_test("IV Repeatability - Frontend Compatible", "FAIL", 
                      f"Missing required keys: {required_keys}")
            failed += 1
    else:
        print_test("IV Repeatability - Frontend Compatible", "FAIL", 
                  "Data is not a dict")
        failed += 1
    total += 1

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_summary(passed, failed, total)

# Exit with appropriate code
sys.exit(0 if failed == 0 else 1)
