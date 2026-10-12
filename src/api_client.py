import os
import sys
import requests
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


class TrafficApiClient:
    """Client bridge for communicating with the Python Flask Traffic Analyser Backend."""

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")
        self._fallback_mode = False

    def is_backend_online(self) -> bool:
        """Check if the Flask backend server is alive and responding."""
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def load_dataset_videos(self) -> List[Dict[str, Any]]:
        """Request the video dataset list from Flask backend, with graceful local fallback."""
        if self.is_backend_online():
            try:
                resp = requests.get(f"{self.base_url}/api/dataset/videos", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("videos", [])
            except Exception as e:
                print(f"[ApiClient] Backend query failed: {e}. Falling back to internal engine.")

        # Fallback to direct DatasetManager
        from src.utils.dataset_manager import DatasetManager
        mgr = DatasetManager()
        return mgr.list_videos()

    def run_analysis(
        self,
        video_path: str,
        conf_thresh: float = 0.25,
        imgsz: int = 640,
        frame_stride: int = 1,
        line_y: float = 0.5,
        max_frames: Optional[int] = None,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """Trigger video analysis via Flask backend or internal pipeline engine."""
        payload = {
            "source": video_path,
            "conf": conf_thresh,
            "imgsz": imgsz,
            "frame_stride": frame_stride,
            "line_y": line_y,
            "max_frames": max_frames,
        }

        # If remote Flask server is reachable and no frame-by-frame UI progress callback required
        if self.is_backend_online() and progress_callback is None:
            try:
                resp = requests.post(f"{self.base_url}/api/analyze", json=payload, timeout=300)
                if resp.status_code == 200:
                    return resp.json().get("data", {})
            except Exception as e:
                print(f"[ApiClient] Flask analyze request error: {e}. Running local pipeline.")

        # Direct pipeline execution
        from src.traffic.pipeline import TrafficAnalysisPipeline
        pipeline = TrafficAnalysisPipeline()
        return pipeline.process_video(
            source_path=video_path,
            conf_thresh=conf_thresh,
            imgsz=imgsz,
            frame_stride=frame_stride,
            line_y_ratio=line_y,
            max_frames=max_frames,
            progress_callback=progress_callback,
        )
