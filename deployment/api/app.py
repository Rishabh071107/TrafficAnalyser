import os
import sys
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.detection.detector import TrafficDetector
from src.tracking.tracker import TrafficTracker
from src.traffic.congestion import CongestionAnalyzer

app = FastAPI(
    title="Traffic Monitoring & Analysis API",
    description="REST API for vehicle detection, tracking, and congestion density metrics.",
    version="1.0.0",
)

# Global model instance
weights_path = os.getenv("MODEL_WEIGHTS", "models/trained/best.pt")
detector = TrafficDetector(weights_path=weights_path if os.path.exists(weights_path) else "yolo11n.pt")
tracker = TrafficTracker()
congestion_analyzer = CongestionAnalyzer()


class DetectionResponse(BaseModel):
    object_count: int
    detections: List[Dict[str, Any]]
    congestion: Dict[str, Any]


@app.get("/")
def read_root():
    return {"message": "Traffic Monitoring REST API is running successfully", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "weights_path": detector.weights_path}


@app.post("/detect", response_model=DetectionResponse)
async def detect_vehicles(file: UploadFile = File(...)):
    """Upload an image file and receive vehicle detections and congestion analysis."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image encoding")

    detections = detector.detect(frame)
    tracks = tracker.update(detections)
    congestion_info = congestion_analyzer.analyze(len(tracks))

    return {
        "object_count": len(detections),
        "detections": detections,
        "congestion": congestion_info,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
