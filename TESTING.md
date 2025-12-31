# API Testing

## Quick Start

Run all tests with the automated script:

```bash
./run_tests.sh
```

This will:
1. Start the FastAPI server (if not running)
2. Run all API endpoint tests
3. Generate a detailed report
4. Stop the server (if it started it)

## Manual Testing

If server is already running:

```bash
python test_api.py
```

## Test Coverage

The test suite covers:

### ✅ Public Endpoints
- Health check
- Root endpoint
- Bank listing

### ✅ Authentication
- Bank registration
- Bank login
- Donor login
- Unauthorized access protection
- Invalid credentials handling
- Duplicate registration prevention

### ✅ Bank Endpoints
- Get profile
- Update profile
- Upload certification documents
- Create consent templates (all 4)
- Get consent templates
- Update counseling configuration
- Get donors list

### ✅ Donor Endpoints
- Lead creation
- Account creation
- Profile management

### ✅ File Uploads
- PDF validation
- Certification uploads
- Test report uploads

### ✅ State Machine
- State transition validation
- Bank authority checks

## Test Reports

After running tests, check:
- **Console output**: Real-time test results with ✅/❌ indicators
- **test_report.json**: Detailed JSON report with all test results
- **server.log**: Server logs (if started by script)

## Test Report Format

```json
{
  "passed": [...],
  "failed": [
    {
      "test": "Test Name",
      "endpoint": "/api/path",
      "method": "POST",
      "error": "Error details",
      "timestamp": "2025-12-31T..."
    }
  ],
  "total": 16,
  "timestamp": "2025-12-31T..."
}
```

## Requirements

Install test dependencies:
```bash
pip install requests
```

## Environment

Tests run against `http://localhost:8000` by default.

To test against different environment:
```python
# Edit test_api.py
BASE_URL = "http://your-server:port"
```
