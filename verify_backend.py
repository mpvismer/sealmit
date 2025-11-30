import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_api():
    # Wait for server
    for _ in range(10):
        try:
            requests.get("http://localhost:8000/")
            break
        except:
            time.sleep(1)
    
    # Create Project
    project_config = {
        "name": "TestProject",
        "levels": ["User", "System"]
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_config)
    print(f"Create Project: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return

    # Create Requirement
    req = {
        "type": "requirement",
        "title": "System must be fast",
        "level": "System"
    }
    response = requests.post(f"{BASE_URL}/artifacts/TestProject/artifacts", json=req)
    print(f"Create Artifact: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return
    req_id = response.json()["id"]

    # Commit
    response = requests.post(f"{BASE_URL}/artifacts/TestProject/commit", json={"message": "First commit"})
    print(f"Commit: {response.status_code}")

if __name__ == "__main__":
    test_api()
