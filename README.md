# Traffic Monitoring & Analysis System

An end-to-end computer vision and deep learning solution for real-time traffic monitoring, vehicle detection, multi-object tracking, speed estimation, vehicle counting, and road congestion density analysis powered by YOLO and modern computer vision algorithms.

---

## 🌟 Key Features

- **Vehicle Detection**: Detect cars, buses, trucks, motorcycles, and bicycles with YOLO models.
- **Multi-Object Tracking**: Track unique vehicle trajectories using ByteTrack / SORT tracking logic.
- **Vehicle Counting**: Count inbound and outbound traffic using dynamic virtual line crossing and region of interest (ROI) zones.
- **Speed Estimation**: Estimate vehicle speeds ($km/h$) using frame rate calibration and pixel distance vectors.
- **Congestion Analysis**: Calculate real-time road density and output traffic flow status (Free Flow, Moderate, Heavy, Standstill).
- **REST API Deployment**: Containerized FastAPI server exposing endpoints for frame inference and batch video analysis.
- **Modular Architecture**: Clean separation of data processing, training, inference, tracking, domain metrics, and UI visualization.

---

## 📁 Directory Structure

```text
traffic-monitoring/
│
├── README.md                  # Project overview & documentation
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── LICENSE                    # Software license
│
├── configs/                   # System configuration files
│   ├── data.yaml              # Dataset classes and split paths
│   └── model.yaml             # Detection, tracking & speed parameters
│
├── data/                      # Datasets directory
│   ├── raw/                   # Raw original dataset archives
│   ├── processed/             # Preprocessed images & YOLO labels
│   └── external/              # External traffic benchmark datasets
│
├── models/                    # Model weights repository
│   ├── pretrained/            # Base YOLO checkpoints (e.g. yolo11n.pt)
│   └── trained/               # Fine-tuned weights (e.g. best.pt)
│
├── src/                       # Core Python packages
│   ├── data/                  # Dataset downloader, preparer & validator
│   ├── training/              # Model training wrapper & evaluator
│   ├── detection/             # Object detector module
│   ├── tracking/              # Multi-object tracker module
│   ├── traffic/               # Vehicle counter, speed estimator & congestion monitor
│   └── utils/                 # Video processing & visualization helpers
│
├── scripts/                   # Command line interface (CLI) tools
│   ├── train.py               # Model training script
│   ├── evaluate.py            # Evaluation & metrics script
│   └── predict.py             # Inference, tracking & traffic analysis pipeline
│
├── notebooks/                 # Jupyter analysis notebooks
│   ├── 01_dataset_analysis.ipynb
│   ├── 02_training.ipynb
│   └── 03_model_testing.ipynb
│
├── tests/                     # Unit test suite
│   ├── test_detector.py
│   ├── test_tracker.py
│   └── test_counter.py
│
├── inputs/                    # Input media storage
│   └── videos/                # Source traffic video files
│
├── outputs/                   # Analysis outputs
│   ├── detections/            # Rendered detection videos
│   ├── tracking/              # Trajectory rendering outputs
│   └── reports/               # Traffic analysis CSV/JSON reports
│
├── experiments/               # Experiment tracking & model logs
│   ├── exp001_yolo11n/
│   ├── exp002_yolo11s/
│   └── exp003_augmented/
│
├── ui/                        # Bespoke Sage & Cream Gradio Interface
│   ├── app.py                 # Gradio application definition & layout
│   ├── theme.py               # Custom Sage Green & Cream design system theme
│   ├── custom.css             # Multi-font typography & editorial card CSS
│   └── components/            # Dataset selector & telemetry cards
│
├── run_app.py                 # Unified Dual-Runner (Flask + Gradio)
│
└── deployment/                # Production API & Containerization
    ├── Dockerfile             # Production Docker container definition
    ├── docker-compose.yml     # Multi-container service setup
    └── api/
        ├── app.py             # FastAPI HTTP service
        └── flask_app.py       # Flask REST service
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch the Web Observatory UI & Flask Backend (Sage Green & Cream)

Run the unified interface orchestrator:

```bash
python run_app.py
```

- **Gradio Frontend (Bespoke Sage & Cream UI)**: `http://localhost:7860`
- **Flask REST Backend**: `http://localhost:5000`

> **Interactive Workflow:**
> 1. Click **"🌿 Load Video Dataset"** to discover streams with generated thumbnails and metadata.
> 2. Select any video from the dataset choices — the input preview loads and output video is selected/updated.
> 3. Click **"⚡ Execute Traffic Analysis"** to run vehicle detection, ByteTrack tracking, speed estimation, counting line crossings, and density analysis.
> 4. View side-by-side input and output video players, live telemetry KPI badges, vehicle distribution breakdown, and export CSV telemetry reports.

### 3. Run Command-Line Inference (Optional)

Process a video file directly via CLI:

```bash
python scripts/predict.py --source inputs/videos/traffic.mp4 --weights models/trained/best.pt --show
```

### 3. Model Training

Train a YOLO model on your traffic dataset:

```bash
python scripts/train.py --data configs/data.yaml --model yolo11n.pt --epochs 50 --imgsz 640
```

### 4. Evaluate Model Performance

```bash
python scripts/evaluate.py --weights models/trained/best.pt --data configs/data.yaml
```

---

## 🐳 Deployment with Docker & REST API

Run the API locally:

```bash
python deployment/api/app.py
```

Or deploy using Docker Compose:

```bash
docker-compose -f deployment/docker-compose.yml up --build
```

Access API Documentation at `http://localhost:8000/docs`.

---

## 🧪 Testing

Run pytest unit tests:

```bash
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///d:/TrafficAnalyser/LICENSE) file for details.
