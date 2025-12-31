import pytest
import requests
import json
from datetime import datetime
from pathlib import Path
import io

# Configuration
BASE_URL = "http://localhost:8000"
REPORT_FILE = "test_report.json"

# Test data storage
test_data = {
    "bank": {},
    "donor": {},
    "tokens": {},
    "ids": {}
}

# Test results
test_results = {
    "passed": [],
    "failed": [],
    "total": 0,
    "timestamp": datetime.now().isoformat()
}


def log_test(name: str, passed: bool, endpoint: str, method: str, error: str = None):
    """Log test result"""
    test_results["total"] += 1
    result = {
        "test": name,
        "endpoint": endpoint,
        "method": method,
        "timestamp": datetime.now().isoformat()
    }
    
    if passed:
        test_results["passed"].append(result)
        print(f"✅ PASS: {name}")
    else:
        result["error"] = error
        test_results["failed"].append(result)
        print(f"❌ FAIL: {name} - {error}")


def create_test_pdf():
    """Create a test PDF file in memory"""
    # Simple PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF"""
    return io.BytesIO(pdf_content)


# ==================== TESTS ====================

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()["status"] == "healthy"
        log_test("Health Check", True, "/health", "GET")
    except Exception as e:
        log_test("Health Check", False, "/health", "GET", str(e))


def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        log_test("Root Endpoint", True, "/", "GET")
    except Exception as e:
        log_test("Root Endpoint", False, "/", "GET", str(e))


def test_bank_registration():
    """Test bank registration"""
    try:
        test_data["bank"] = {
            "email": f"testbank_{datetime.now().timestamp()}@example.com",
            "password": "SecurePassword123!",
            "name": "Test Bank"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/bank/register",
            params=test_data["bank"]
        )
        
        if response.status_code != 201:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            raise AssertionError(f"Expected 201, got {response.status_code}. Response: {error_detail}")
        
        data = response.json()
        assert "access_token" in data
        assert data["user_type"] == "bank"
        
        test_data["tokens"]["bank"] = data["access_token"]
        test_data["ids"]["bank"] = data["user_id"]
        
        log_test("Bank Registration", True, "/api/auth/bank/register", "POST")
    except Exception as e:
        log_test("Bank Registration", False, "/api/auth/bank/register", "POST", str(e))


def test_bank_login():
    """Test bank login"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/bank/login",
            json={
                "email": test_data["bank"]["email"],
                "password": test_data["bank"]["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        log_test("Bank Login", True, "/api/auth/bank/login", "POST")
    except Exception as e:
        log_test("Bank Login", False, "/api/auth/bank/login", "POST", str(e))


def test_bank_profile():
    """Test get bank profile"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        response = requests.get(f"{BASE_URL}/api/bank/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_data["bank"]["email"]
        log_test("Bank Profile", True, "/api/bank/me", "GET")
    except Exception as e:
        log_test("Bank Profile", False, "/api/bank/me", "GET", str(e))


def test_bank_update_profile():
    """Test update bank profile"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        response = requests.put(
            f"{BASE_URL}/api/bank/me",
            headers=headers,
            json={
                "phone": "+1234567890",
                "address": "123 Test Street, Test City"
            }
        )
        assert response.status_code == 200
        log_test("Bank Update Profile", True, "/api/bank/me", "PUT")
    except Exception as e:
        log_test("Bank Update Profile", False, "/api/bank/me", "PUT", str(e))


def test_bank_upload_certification():
    """Test bank certification upload"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        files = {"file": ("test_cert.pdf", create_test_pdf(), "application/pdf")}
        
        response = requests.post(
            f"{BASE_URL}/api/bank/certification/upload",
            headers=headers,
            files=files
        )
        assert response.status_code == 200
        log_test("Bank Upload Certification", True, "/api/bank/certification/upload", "POST")
    except Exception as e:
        log_test("Bank Upload Certification", False, "/api/bank/certification/upload", "POST", str(e))


def test_create_consent_template():
    """Test create consent template"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        
        for i in range(1, 5):  # Create 4 templates
            response = requests.post(
                f"{BASE_URL}/api/bank/consents/templates",
                headers=headers,
                json={
                    "title": f"Consent Form {i}",
                    "content": f"This is consent form {i} content. By signing, you agree to...",
                    "order": i,
                    "version": "1.0"
                }
            )
            assert response.status_code == 201
        
        log_test("Create Consent Templates", True, "/api/bank/consents/templates", "POST")
    except Exception as e:
        log_test("Create Consent Templates", False, "/api/bank/consents/templates", "POST", str(e))


def test_get_consent_templates():
    """Test get consent templates"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        response = requests.get(
            f"{BASE_URL}/api/bank/consents/templates",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        log_test("Get Consent Templates", True, "/api/bank/consents/templates", "GET")
    except Exception as e:
        log_test("Get Consent Templates", False, "/api/bank/consents/templates", "GET", str(e))


def test_list_banks_public():
    """Test public bank listing"""
    try:
        response = requests.get(f"{BASE_URL}/api/public/banks")
        assert response.status_code == 200
        # Newly registered bank won't appear (not verified/subscribed yet)
        log_test("List Banks (Public)", True, "/api/public/banks", "GET")
    except Exception as e:
        log_test("List Banks (Public)", False, "/api/public/banks", "GET", str(e))


def test_donor_lead_creation():
    """Test donor lead creation"""
    try:
        test_data["donor"] = {
            "bank_id": test_data["ids"]["bank"],
            "first_name": "John",
            "last_name": "Doe",
            "email": f"donor_{datetime.now().timestamp()}@example.com",
            "phone": "+1987654321",
            "medical_interest_info": {
                "blood_type": "O+",
                "height": "180cm",
                "weight": "75kg"
            }
        }
        
        # This will fail because bank is not verified/subscribed yet
        response = requests.post(
            f"{BASE_URL}/api/donor/lead",
            json=test_data["donor"]
        )
        
        # Expected to fail with 400
        if response.status_code == 400:
            log_test("Donor Lead Creation (Expected Validation)", True, "/api/donor/lead", "POST")
        else:
            log_test("Donor Lead Creation", False, "/api/donor/lead", "POST", 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Donor Lead Creation", False, "/api/donor/lead", "POST", str(e))


def test_unauthorized_access():
    """Test unauthorized access to protected endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/api/bank/me")
        assert response.status_code == 403 or response.status_code == 401
        log_test("Unauthorized Access Protection", True, "/api/bank/me", "GET")
    except Exception as e:
        log_test("Unauthorized Access Protection", False, "/api/bank/me", "GET", str(e))


def test_invalid_login():
    """Test invalid login credentials"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/bank/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        log_test("Invalid Login Protection", True, "/api/auth/bank/login", "POST")
    except Exception as e:
        log_test("Invalid Login Protection", False, "/api/auth/bank/login", "POST", str(e))


def test_duplicate_bank_registration():
    """Test duplicate bank registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/bank/register",
            params={
                "email": test_data["bank"]["email"],
                "password": "AnotherPassword123!",
                "name": "Duplicate Bank"
            }
        )
        assert response.status_code == 400
        log_test("Duplicate Registration Protection", True, "/api/auth/bank/register", "POST")
    except Exception as e:
        log_test("Duplicate Registration Protection", False, "/api/auth/bank/register", "POST", str(e))


def test_bank_get_donors():
    """Test get bank's donors"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        response = requests.get(f"{BASE_URL}/api/bank/donors", headers=headers)
        # Will fail because bank is not subscribed
        assert response.status_code in [200, 403]
        log_test("Get Bank Donors", True, "/api/bank/donors", "GET")
    except Exception as e:
        log_test("Get Bank Donors", False, "/api/bank/donors", "GET", str(e))


def test_counseling_config():
    """Test update counseling configuration"""
    try:
        headers = {"Authorization": f"Bearer {test_data['tokens']['bank']}"}
        response = requests.put(
            f"{BASE_URL}/api/bank/counseling/config",
            headers=headers,
            json={
                "methods": ["call", "video", "email"],
                "time_slots": [
                    {"day": "Monday", "start": "09:00", "end": "17:00"},
                    {"day": "Tuesday", "start": "09:00", "end": "17:00"}
                ],
                "auto_approve": False
            }
        )
        # Will fail if not subscribed
        assert response.status_code in [200, 403]
        log_test("Update Counseling Config", True, "/api/bank/counseling/config", "PUT")
    except Exception as e:
        log_test("Update Counseling Config", False, "/api/bank/counseling/config", "PUT", str(e))


# ==================== TEST RUNNER ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 ARTPRIV API TEST SUITE")
    print("="*60 + "\n")
    
    # Run tests in order
    test_health_check()
    test_root_endpoint()
    test_bank_registration()
    test_bank_login()
    test_bank_profile()
    test_bank_update_profile()
    test_bank_upload_certification()
    test_create_consent_template()
    test_get_consent_templates()
    test_list_banks_public()
    test_donor_lead_creation()
    test_unauthorized_access()
    test_invalid_login()
    test_duplicate_bank_registration()
    test_bank_get_donors()
    test_counseling_config()
    
    # Generate report
    generate_report()


def generate_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("📊 TEST REPORT")
    print("="*60 + "\n")
    
    total = test_results["total"]
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ({success_rate:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Timestamp: {test_results['timestamp']}\n")
    
    if failed > 0:
        print("❌ FAILED TESTS:")
        print("-" * 60)
        for result in test_results["failed"]:
            print(f"\nTest: {result['test']}")
            print(f"Endpoint: {result['method']} {result['endpoint']}")
            print(f"Error: {result['error']}")
    
    # Save to JSON
    with open(REPORT_FILE, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {REPORT_FILE}")
    print("="*60 + "\n")
    
    # Return exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        generate_report()
        sys.exit(1)
