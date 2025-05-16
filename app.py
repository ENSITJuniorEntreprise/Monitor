from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to ensure the thread starts only once
heartbeat_thread_started = False
thread_lock = threading.Lock()

def fetch_heartbeat():
    """
    Background process to fetch heartbeat data every 3 seconds
    """
    while True:
        try:
            response = requests.get('https://machawiyahala.com/api/heart-beat', timeout=5)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Heartbeat data received: {data}")
        except requests.RequestException as e:
            logger.error(f"Error fetching heartbeat: {e}")
        time.sleep(30)

def start_heartbeat_thread():
    """
    Start the heartbeat thread if it hasn't been started yet
    """
    global heartbeat_thread_started
    with thread_lock:
        if not heartbeat_thread_started:
            heartbeat_thread = threading.Thread(target=fetch_heartbeat, daemon=True)
            heartbeat_thread.start()
            heartbeat_thread_started = True
            logger.info("Heartbeat thread started")

@app.get('/')
def index():
    return jsonify({"message": "Welcome to the Monitor Service!"})

# Start the background thread when the app is loaded
start_heartbeat_thread()

if __name__ == '__main__':
    app.run(debug=True)