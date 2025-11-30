import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_ai():
    # Wait for server
    for _ in range(10):
        try:
            requests.get("http://localhost:8000/")
            break
        except:
            time.sleep(1)
    
    # Chat
    chat_req = {
        "message": "Hello AI",
        "history": []
    }
    response = requests.post(f"{BASE_URL}/ai/chat", json=chat_req)
    print(f"Chat: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)

if __name__ == "__main__":
    test_ai()
