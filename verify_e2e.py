"""
End-to-end test for SEALMit backend API.
Tests complete workflow: create project, add artifacts, create traces, commit.
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def wait_for_server():
    """Wait for server to be ready."""
    print("Waiting for server...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✓ Server is ready")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("✗ Server not available")
    return False

def test_create_project():
    """Test project creation."""
    print("\n=== Testing Project Creation ===")
    project_config = {
        "name": "TestE2EProject",
        "levels": ["User", "System", "Performance"]
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_config)
    print(f"Create Project: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    print("✓ Project created successfully")
    return True

def test_create_requirements():
    """Test creating requirements at different levels."""
    print("\n=== Testing Requirements Creation ===")
    requirements = [
        {"type": "requirement", "title": "User shall login", "level": "User"},
        {"type": "requirement", "title": "System shall authenticate", "level": "System"},
        {"type": "requirement", "title": "Response time < 2s", "level": "Performance"}
    ]
    
    req_ids = []
    for req in requirements:
        response = requests.post(f"{BASE_URL}/artifacts/TestE2EProject/artifacts", json=req)
        if response.status_code != 200:
            print(f"✗ Failed to create requirement: {req['title']}")
            print(f"Error: {response.text}")
            return None
        req_id = response.json()["id"]
        req_ids.append(req_id)
        print(f"✓ Created requirement: {req['title']} (ID: {req_id[:8]}...)")
    
    return req_ids

def test_create_risks():
    """Test creating risk hazards and causes."""
    print("\n=== Testing Risk Management ===")
    hazard = {
        "type": "risk_hazard",
        "title": "Unauthorized access",
        "description": "User gains unauthorized access to system",
        "severity": "High"
    }
    response = requests.post(f"{BASE_URL}/artifacts/TestE2EProject/artifacts", json=hazard)
    if response.status_code != 200:
        print(f"✗ Failed to create hazard")
        return None, None
    hazard_id = response.json()["id"]
    print(f"✓ Created hazard: {hazard['title']} (ID: {hazard_id[:8]}...)")
    
    cause = {
        "type": "risk_cause",
        "title": "Weak password policy",
        "description": "Users can set weak passwords",
        "probability": "Medium"
    }
    response = requests.post(f"{BASE_URL}/artifacts/TestE2EProject/artifacts", json=cause)
    if response.status_code != 200:
        print(f"✗ Failed to create cause")
        return hazard_id, None
    cause_id = response.json()["id"]
    print(f"✓ Created cause: {cause['title']} (ID: {cause_id[:8]}...)")
    
    return hazard_id, cause_id

def test_create_verification():
    """Test creating verification activities."""
    print("\n=== Testing Verification Activities ===")
    verification = {
        "type": "verification_activity",
        "title": "Login test",
        "description": "Test user login functionality",
        "method": "test",
        "procedure": "1. Enter credentials 2. Click login 3. Verify success",
        "passed": True
    }
    response = requests.post(f"{BASE_URL}/artifacts/TestE2EProject/artifacts", json=verification)
    if response.status_code != 200:
        print(f"✗ Failed to create verification")
        return None
    ver_id = response.json()["id"]
    print(f"✓ Created verification: {verification['title']} (ID: {ver_id[:8]}...)")
    return ver_id

def test_create_traces(req_ids, hazard_id, cause_id, ver_id):
    """Test creating traceability links."""
    print("\n=== Testing Traceability ===")
    traces = [
        {"source_id": ver_id, "target_id": req_ids[0], "type": "verifies", "description": "Verification verifies user requirement"},
        {"source_id": cause_id, "target_id": hazard_id, "type": "causes", "description": "Weak password causes unauthorized access"},
        {"source_id": req_ids[1], "target_id": hazard_id, "type": "mitigates", "description": "Authentication mitigates unauthorized access"}
    ]
    
    for trace in traces:
        response = requests.post(f"{BASE_URL}/artifacts/TestE2EProject/traces", json=trace)
        if response.status_code != 200:
            print(f"✗ Failed to create trace: {trace['type']}")
            print(f"Error: {response.text}")
            return False
        print(f"✓ Created trace: {trace['type']}")
    
    return True

def test_commit():
    """Test committing changes to Git."""
    print("\n=== Testing Git Commit ===")
    response = requests.post(
        f"{BASE_URL}/artifacts/TestE2EProject/commit",
        json={"message": "E2E test: Added requirements, risks, verification, and traces"}
    )
    if response.status_code != 200:
        print(f"✗ Failed to commit")
        print(f"Error: {response.text}")
        return False
    print("✓ Changes committed to Git")
    return True

def test_get_project():
    """Test retrieving complete project state."""
    print("\n=== Testing Project Retrieval ===")
    response = requests.get(f"{BASE_URL}/projects/TestE2EProject")
    if response.status_code != 200:
        print(f"✗ Failed to get project")
        return False
    
    data = response.json()
    print(f"✓ Retrieved project with:")
    print(f"  - {len(data['artifacts'])} artifacts")
    print(f"  - {len(data['traces'])} traces")
    print(f"  - Levels: {', '.join(data['config']['levels'])}")
    return True

def run_tests():
    """Run all end-to-end tests."""
    print("=" * 60)
    print("SEALMit End-to-End Test Suite")
    print("=" * 60)
    
    if not wait_for_server():
        print("\n✗ FAILED: Server not available")
        return False
    
    # Run tests
    if not test_create_project():
        return False
    
    req_ids = test_create_requirements()
    if not req_ids:
        return False
    
    hazard_id, cause_id = test_create_risks()
    if not hazard_id or not cause_id:
        return False
    
    ver_id = test_create_verification()
    if not ver_id:
        return False
    
    if not test_create_traces(req_ids, hazard_id, cause_id, ver_id):
        return False
    
    if not test_commit():
        return False
    
    if not test_get_project():
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
