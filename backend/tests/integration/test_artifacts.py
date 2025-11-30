def test_create_requirement(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    
    req = {
        "type": "requirement",
        "title": "Login",
        "level": "User"
    }
    response = client.post("/api/artifacts/TestProject/artifacts", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Login"
    assert data["id"] is not None
    assert data["type"] == "requirement"

def test_create_risk_hazard(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    
    hazard = {
        "type": "risk_hazard",
        "title": "Fire",
        "severity": "High"
    }
    response = client.post("/api/artifacts/TestProject/artifacts", json=hazard)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fire"
    assert data["severity"] == "High"
    assert data["type"] == "risk_hazard"

def test_create_trace(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    
    # Create requirement
    req = client.post("/api/artifacts/TestProject/artifacts", json={
        "type": "requirement", "title": "Req1", "level": "User"
    }).json()
    
    # Create verification
    ver = client.post("/api/artifacts/TestProject/artifacts", json={
        "type": "verification_activity", "title": "Test1", "method": "test"
    }).json()
    
    # Create trace
    trace = {
        "source_id": ver["id"],
        "target_id": req["id"],
        "type": "verifies"
    }
    response = client.post("/api/artifacts/TestProject/traces", json=trace)
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == ver["id"]
    assert data["target_id"] == req["id"]
    assert data["type"] == "verifies"

def test_commit_changes(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    
    response = client.post("/api/artifacts/TestProject/commit", json={"message": "Initial commit"})
    assert response.status_code == 200
