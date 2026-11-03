import time
import threading
import cv2
import numpy as np
from flask import Flask, render_template, jsonify, Response, request
from railvision_core.detector import RailVisionDetector
from railvision_core.video_processor import VideoStreamProcessor
from railvision_core.crowd_analyzer import CrowdAnalyzer
from railvision_core.database import LocalLogger

app = Flask(__name__)

# Shared memory state (thread-safe by default in CPython due to GIL)
shared_state = {
    "headcount": 0,
    "density": 0.0,
    "max_capacity": 150,
    "entry_rate": 14,
    "exit_rate": 4,
    "overcrowded": False
}

print("Initializing AI Modules for Web Stream...")
detector = RailVisionDetector(model_version="yolov8n.pt")
# Define a simple dummy ROI
roi_polygon = [[160, 160], [480, 160], [480, 480], [160, 480]]
analyzer = CrowdAnalyzer(max_capacity=150, alert_threshold=0.80)

print("Initializing SQLite Database Logger...")
db_logger = LocalLogger(db_path="railvision_local.db")

def background_logging():
    """Background thread to log metrics to SQLite every 5 seconds."""
    # Dummy static identifiers for the prototype
    train_id = "TR-101"
    carriage_id = "C-3"
    
    while True:
        # Wait 5 seconds between logs
        time.sleep(5)
        
        # Write the current global metrics to the local database
        db_logger.log_metrics(
            train_id=train_id,
            carriage_id=carriage_id,
            headcount=shared_state["headcount"],
            density=shared_state["density"],
            alert_status=shared_state["overcrowded"]
        )
        # print("Logged metrics to Local DB.")

def continuous_processing_loop():
    print("[SYSTEM] Starting AI Background Thread...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera failed to open! Is it locked by another process?")
        
    while True:
        try:
            # Buffer clear grab
            cap.grab()
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
                
            headcount, bounding_boxes = detector.detect_passengers(frame)
            analysis = analyzer.evaluate_crowd(headcount)
            
            shared_state["headcount"] = headcount
            shared_state["density"] = analysis['density']
            shared_state["overcrowded"] = analysis['alert_status']
            
            print(f"[AI] Frame processed. Count: {shared_state['headcount']}")
        except Exception as e:
            print(f"[ERROR] AI Pipeline crashed: {e}")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats')
def stats():
    return jsonify(shared_state)

@app.route('/api/history')
def history():
    logs = db_logger.get_recent_logs(minutes=30)
    return jsonify(logs)

@app.route('/config')
def config_roi():
    return render_template('config.html')

@app.route('/api/frame')
def api_frame():
    return Response(status=404)

@app.route('/api/set_roi', methods=['POST'])
def api_set_roi():
    return jsonify({"status": "error", "message": "ROI dynamically disabled."}), 400

if __name__ == '__main__':
    # Start the 5-second background database logging thread
    logging_thread = threading.Thread(target=background_logging, daemon=True)
    logging_thread.start()
    
    print("[SYSTEM] Initializing Thread...")
    threading.Thread(target=continuous_processing_loop, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
