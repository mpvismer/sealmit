def test_create_project(client):
    response = client.post("/api/projects/", json={"name": "TestProject", "levels": ["User", "System"]})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestProject"
    assert "User" in [l["name"] if isinstance(l, dict) else l for l in data["levels"]]

def test_create_duplicate_project(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    response = client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    assert response.status_code == 400

def test_list_projects(client):
    client.post("/api/projects/", json={"name": "Proj1", "levels": ["User"]})
    client.post("/api/projects/", json={"name": "Proj2", "levels": ["User"]})
    
    response = client.get("/api/projects/")
    assert response.status_code == 200
    projects = response.json()
    assert "Proj1" in projects
    assert "Proj2" in projects

def test_get_project(client):
    client.post("/api/projects/", json={"name": "TestProject", "levels": ["User"]})
    
    response = client.get("/api/projects/TestProject")
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["name"] == "TestProject"

def test_get_nonexistent_project(client):
    response = client.get("/api/projects/NonExistent")
    assert response.status_code == 404
