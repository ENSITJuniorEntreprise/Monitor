from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Dynamically load all WEBSITE_URLX and WEBSITE_NAMEX from .env
websites = []
index = 1
while True:
    url = os.getenv(f'WEBSITE_URL{index}')
    name = os.getenv(f'WEBSITE_NAME{index}')
    if not url:  # Stop when no more WEBSITE_URLX is found
        break
    websites.append({'url': url.rstrip('/') + '/api/heart-beat', 'name': name or f'website{index}'})
    index += 1

# Validate that at least one website is configured
if not websites:
    logger.error("No websites configured in .env file")
    raise ValueError("No websites configured in .env file")
else:
    logger.info(f"Loaded {len(websites)} websites: {[w['name'] for w in websites]}")

# Global flag to ensure the thread starts only once
heartbeat_thread_started = False
thread_lock = threading.Lock()

def fetch_heartbeat():
    """
    Background process to fetch heartbeat data from all configured websites every 3 seconds
    """
    while True:
        for website in websites:
            url = website['url']
            name = website['name']
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Heartbeat data received from <{name}> ({url}): {data}")
            except requests.RequestException as e:
                logger.error(f"Error fetching heartbeat from <{name}> ({url}): {e}")
        time.sleep(30)  # Wait 3 seconds before next cycle

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

@app.get('/api/heart-beat')
def heart_beat():
    """
    Endpoint to check if the service is running
    """
    return jsonify({"status": "running"})

# Start the background thread when the app is loaded
start_heartbeat_thread()

if __name__ == '__main__':
    app.run(debug=True)