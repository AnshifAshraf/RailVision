# RailVision 🚆👁️
### AI-Based Real-Time Train Crowd Detection & Monitoring System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv)
![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-black?style=for-the-badge&logo=flask)
![Django](https://img.shields.io/badge/Django-REST%20Backend-green?style=for-the-badge&logo=django)

---

## 📌 Project Overview
**RailVision** is an intelligent computer vision solution designed to monitor passenger density inside train compartments in real-time. By leveraging edge camera feeds and deep learning (YOLOv8), the system accurately detects passengers, calculates occupancy percentages, and categorizes crowd density into clear levels:
- 🟢 **Low Density (< 50%)** — Ample seating/space available.
- 🟡 **Medium Density (50% – 80%)** — Moderate occupancy.
- 🔴 **High Density / Overcrowded (> 80%)** — Immediate overcrowding alerts triggered.

The data is logged into local databases and broadcast to interactive passenger dashboards and railway authority control interfaces to optimize passenger boarding, prevent stampedes, and improve commuter safety.

---

## 🌟 Key Features
- **Real-Time Human Detection:** Utilizes lightweight `YOLOv8n` for high FPS human detection and bounding box localization on video streams.
- **Dynamic Region of Interest (ROI):** Focuses detection strictly on active compartment corridors, aisles, and doorways, eliminating background noise.
- **Crowd Density Evaluation:** Calculates real-time occupancy percentages relative to maximum carriage capacity.
- **Overcrowding Alerts:** Automatically flags alert states when occupancy exceeds safety thresholds (e.g., 80%).
- **Dual Architecture (Flask & Django):**
  - **Flask Web Interface:** Real-time web video streaming, live statistics (`/api/stats`), and 30-minute rolling history (`/api/history`).
  - **Django REST Backend:** Centralized API endpoints (`/api/occupancy/`) for multi-carriage tracking and database management.
- **Local SQLite Logging:** Periodic background worker thread persisting historical occupancy trends every 5 seconds.

---

## 🏗️ System Architecture
```
[ Mobile / CCTV Camera Feed ]
            │
            ▼
[ VideoStreamProcessor (OpenCV) ] ── (ROI Cropping / Preprocessing)
            │
            ▼
[ RailVisionDetector (YOLOv8n) ]  ── (Person Detection & Bounding Boxes)
            │
            ▼
[ CrowdAnalyzer ]                 ── (Headcount vs Capacity → Density % & Alert)
            │
    ┌───────┴────────────────────────┐
    ▼                                ▼
[ LocalLogger (SQLite DB) ]   [ Live Web Dashboard (Flask + JS) ]
```

---

## 📁 Repository Structure
```
├── railvision_core/
│   ├── detector.py          # YOLOv8 passenger detector module
│   ├── video_processor.py   # Video stream capture, FPS management & ROI processing
│   ├── crowd_analyzer.py    # Occupancy rate calculation & safety alert logic
│   └── database.py          # SQLite local logging handler
├── railvision_backend/      # Django REST framework backend for multi-train tracking
│   ├── api/
│   ├── railvision_backend/
│   └── manage.py
├── static/                  # Web dashboard styling and interactive JavaScript
│   ├── css/style.css
│   └── js/script.js
├── templates/               # Flask HTML templates
│   ├── index.html           # Live monitoring dashboard
│   └── config.html          # ROI configuration interface
├── app.py                   # Main Flask application with live web streaming
├── main.py                  # Standalone OpenCV desktop monitor with live feed
├── yolov8n.pt               # Pretrained YOLOv8 nano model weights
├── requirements.txt         # Project dependencies
├── Raiil_View_SRS.pdf       # Software Requirements Specification (SRS) document
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed:
```bash
python --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/AnshifAshraf/RailVision.git
cd RailVision
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install requirements:
pip install -r requirements.txt
```

---

## 💻 Running the Application

### Option A: Interactive Web Dashboard (Flask)
Runs the background AI detection thread, SQLite logger, and hosts the web interface:
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```
- Live stats endpoint: `http://localhost:5000/api/stats`
- History logs endpoint: `http://localhost:5000/api/history`

### Option B: Standalone Desktop Feed (OpenCV)
Runs a real-time OpenCV window with bounding boxes, headcounts, and live density indicators:
```bash
python main.py
```
- Press `q` to exit the video stream.

---

## 📊 Endpoints & API

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main passenger crowd monitoring dashboard |
| `/api/stats` | `GET` | JSON payload of current headcount, density %, and alert state |
| `/api/history` | `GET` | Historical crowd log data for the last 30 minutes |
| `/config` | `GET` | ROI camera calibration panel |

---

## 👥 Contributors & Academic Context
- **Institution:** College of Engineering and Management Punnapra (APJ Abdul Kalam Technological University)
- **Prepared By Group 9:**
  - Muhammed Anshif K T ([@AnshifAshraf](https://github.com/AnshifAshraf))
  - Nandan Haridas
  - Ihsan Ahmed
  - Sarang S
- **Project Guide:** Prof. Saleena S

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
