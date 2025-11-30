import requests
import time

BASE_URL = "http://localhost:8080"

def test_asig():
    # Wait for server
    for _ in range(10):
        try:
            requests.get(BASE_URL)
            break
        except:
            time.sleep(1)
    
    # Check index.html
    response = requests.get(BASE_URL)
    print(f"Index: {response.status_code}")
    if response.status_code == 200 and "<html" in response.text:
        print("Index served successfully")
    else:
        print("Failed to serve index")

    # Check API
    response = requests.get(f"{BASE_URL}/api/")
    print(f"API Root: {response.status_code}")
    if response.status_code == 200:
        print("API served successfully")

if __name__ == "__main__":
    test_asig()
