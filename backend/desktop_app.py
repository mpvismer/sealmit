import webview
import threading
import sys
import os
import uvicorn
from asig_server import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="error")

if __name__ == '__main__':
    # Start the server in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Create the window
    webview.create_window('SEALMit', 'http://127.0.0.1:8080', width=1200, height=800)
    
    # Start the GUI loop
    webview.start()
