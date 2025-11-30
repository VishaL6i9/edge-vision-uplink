-----

# Edge Vision Uplink (Reflex Edition)



**Edge Vision Uplink** is a comprehensive fleet management platform designed for real-time monitoring and advanced video auditing of autonomous edge devices. Built entirely in **Python** using the **Reflex** framework, it demonstrates the power of a unified stack for both high-performance backend processing and reactive frontend interfaces.

-----

## 📖 Executive Summary

This platform bridges the gap between edge robotics and cloud management. It ingests high-frequency telemetry via MQTT for real-time dashboards and processes video streams via HTTP for automated safety auditing using Computer Vision.

**Core Objectives:**

1.  **Unified Stack:** Eliminate context switching by using Python for the UI (Reflex), Backend (FastAPI), and Data Processing.
2.  **Real-Time State:** Leverage Reflex's WebSocket capabilities to push edge telemetry to the UI instantly.
3.  **Automated Auditing:** Detect safety incidents in uploaded footage using YOLOv8 without manual review.

-----

## 🏗 System Architecture

The system operates as a single deployable unit orchestrating a Reflex App Server alongside critical infrastructure services.

```mermaid
graph TD
    subgraph "Edge Layer"
        A[Mock ROS2 Robot] -->|Telemetry (JSON)| B(MQTT Broker - Mosquitto)
        A -->|Video Upload (HTTP)| C[Reflex App Server]
    end
    
    subgraph "Cloud/Server Layer"
        B -->|Subscribe| C
        C -->|State Updates (WebSocket)| G[Web Dashboard]
        
        C -->|Store Video| D[(MinIO Object Storage)]
        C -->|Persist Metadata| E[(MongoDB)]
        
        subgraph "Async Processing"
            C -.->|YOLOv8 Analysis| D
            C -.->|Log Incident| E
        end
    end
```

### Data Pipelines

#### 1\. The Telemetry Bridge (Hot Path)

* **Protocol:** MQTT (via `paho-mqtt`)
* **Flow:** Robots publish position/battery data -\> Mosquitto -\> Reflex Background Thread -\> Global State Update -\> UI.
* **Latency:** Sub-second updates via WebSockets.

#### 2\. The Vision Audit (Cold Path)

* **Protocol:** HTTP POST (Multipart)
* **Flow:** Robot uploads video -\> MinIO Storage -\> YOLOv8 Inference -\> Incident Detection -\> MongoDB Entry -\> UI Notification.
* **Logic:** Asynchronous background tasks process video to detect hazards (People, Obstacles) and flag "Near Miss" events.

-----

## 🛠 Technology Stack

This project utilizes a **Pure Python** stack to reduce cognitive load and streamline development.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | **Reflex** | Wraps FastAPI (Backend) and React (Frontend). |
| **Database** | **Motor (MongoDB)** | Async persistence for incident logs. |
| **Messaging** | **Paho-MQTT** | Telemetry ingestion from edge nodes. |
| **Vision** | **YOLOv8** | Object detection and safety auditing. |
| **Storage** | **MinIO (Boto3)** | S3-compatible storage for raw video footage. |
| **Validation** | **Pydantic** | Data validation and settings management. |

-----

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* Docker & Docker Compose

### 1\. Clone & Initialize

```bash
git clone https://github.com/your-username/edge-vision-uplink.git
cd edge-vision-uplink
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2\. Launch Infrastructure

Start the database, broker, and object storage containers:

```bash
docker-compose up -d
```

* **Mosquitto:** `localhost:1883`
* **MinIO:** `localhost:9000` (Console: `9001`)
* **MongoDB:** `localhost:27017`

### 3\. Run the Application

Initialize and run the Reflex development server:

```bash
reflex init
reflex run
```

The application will be available at **`http://localhost:3000`**.

### 4\. Start Simulation

To see data flowing, run the mock robot script in a separate terminal:

```bash
python scripts/mock_bot.py
```

This script simulates a robot navigating an environment, publishing MQTT telemetry and periodically uploading video clips.

-----

## 🖥 User Interface

### Mission Control (`/`)

* **Live Map:** Visualizes `X/Y` coordinates of all active robots using `recharts`.
* **Fleet Grid:** Real-time cards displaying Battery Voltage, Status (Online/Offline), and Robot ID.

### Safety Audits (`/audits`)

* **Incident Log:** A data table listing all detected hazards (severity, timestamp).
* **Evidence Player:** Click any row to stream the associated video footage directly from MinIO.

-----

## 🔌 API Reference

The Reflex backend exposes FastAPI endpoints for edge devices.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/upload_video` | Accepts multipart video files. Triggers async YOLOv8 processing. |
| `GET` | `/ping` | Health check for edge nodes. |

-----

## 🔮 Roadmap

* **Phase 1 (Completed):** Infrastructure setup (Docker), State definition, MQTT integration.
* **Phase 2 (Completed):** Mission Control Dashboard (Map & Stat Cards).
* **Phase 3 (Current):** Video Upload API, YOLOv8 Integration, Audit UI.
* **Future:** Authentication (JWT), History Replay, Multi-robot coordination.

-----

## 📄 License

This project is licensed under the MIT License.

**Authors:** Vishal Kandakatla  
**Last Updated:** November 2025