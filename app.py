from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get('/')
def index():
    return jsonify({"message": "Welcome to the Monitor Service!"})

@app.get('/api/heart-beat')
def send_heartbeat():
    """
    Endpoint to send heartbeat data
    """
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    heartbeat_thread = threading.Thread(target=fetch_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    app.run(debug=True)