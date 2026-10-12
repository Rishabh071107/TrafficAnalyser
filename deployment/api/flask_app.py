import os
import sys
import uuid
import threading
from typing import Dict, Any
from flask import Flask, jsonify, request, send_file, send_from_directory, abort

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.utils.dataset_manager import DatasetManager
from src.traffic.pipeline import TrafficAnalysisPipeline

app = Flask(__name__)
dataset_mgr = DatasetManager()
pipeline = TrafficAnalysisPipeline()

# In-memory storage for jobs and latest analysis
ANALYSIS_JOBS: Dict[str, Dict[str, Any]] = {}
LATEST_REPORT: Dict[str, Any] = {}


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "Traffic Analyser Flask Backend",
        "version": "1.0.0",
        "model_weights": pipeline.weights_path,
        "weights_exist": os.path.exists(pipeline.weights_path),
    })


@app.route("/api/dataset/videos", methods=["GET"])
def list_dataset_videos():
    """Discover and return all videos in the dataset with metadata and thumbnails."""
    try:
        videos = dataset_mgr.list_videos()
        return jsonify({
            "status": "success",
            "count": len(videos),
            "videos": videos,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analyze", methods=["POST"])
def analyze_video():
    """Process a selected video with YOLO detection, tracking, speed, and congestion analysis."""
    global LATEST_REPORT
    data = request.get_json(silent=True) or {}

    source = data.get("source") or data.get("video_path")
    if not source:
        return jsonify({"status": "error", "message": "Missing 'source' parameter"}), 400

    # Resolve full path if relative or just a filename
    if not os.path.isabs(source):
        candidate = os.path.join(dataset_mgr.videos_dir, source)
        if os.path.exists(candidate):
            source = candidate
        else:
            candidate = os.path.join(PROJECT_ROOT, source)
            if os.path.exists(candidate):
                source = candidate

    if not os.path.exists(source):
        return jsonify({"status": "error", "message": f"Video not found: {source}"}), 404

    conf_thresh = float(data.get("conf", 0.25))
    imgsz = int(data.get("imgsz", 640))
    frame_stride = int(data.get("frame_stride", 1))
    line_y = float(data.get("line_y", 0.5))
    max_frames = data.get("max_frames")
    if max_frames is not None:
        max_frames = int(max_frames)

    job_id = str(uuid.uuid4())[:8]
    ANALYSIS_JOBS[job_id] = {"status": "processing", "progress": 0}

    def progress_tracker(frame_idx, total_frames, fps, interim):
        pct = round((frame_idx / total_frames) * 100, 1) if total_frames > 0 else 0
        ANALYSIS_JOBS[job_id] = {
            "status": "processing",
            "progress": pct,
            "current_frame": frame_idx,
            "total_frames": total_frames,
            "fps": fps,
            "interim_metrics": interim,
        }

    try:
        output_filename = f"analyzed_{job_id}_{os.path.basename(source)}"
        out_dir = os.path.join(PROJECT_ROOT, "outputs", "tracking")
        os.makedirs(out_dir, exist_ok=True)
        target_output = os.path.join(out_dir, output_filename)

        result = pipeline.process_video(
            source_path=source,
            output_path=target_output,
            conf_thresh=conf_thresh,
            imgsz=imgsz,
            frame_stride=frame_stride,
            line_y_ratio=line_y,
            max_frames=max_frames,
            progress_callback=progress_tracker,
        )

        result["job_id"] = job_id
        ANALYSIS_JOBS[job_id] = {"status": "completed", "result": result}
        LATEST_REPORT = result

        return jsonify({"status": "success", "job_id": job_id, "data": result})

    except Exception as e:
        ANALYSIS_JOBS[job_id] = {"status": "failed", "error": str(e)}
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_status(job_id: str):
    job = ANALYSIS_JOBS.get(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    return jsonify(job)


@app.route("/api/reports/latest", methods=["GET"])
def get_latest_report():
    if not LATEST_REPORT:
        return jsonify({"status": "empty", "message": "No reports generated yet"}), 404
    return jsonify({"status": "success", "report": LATEST_REPORT})


@app.route("/api/media/video", methods=["GET"])
def serve_video():
    """Stream a video file requested via query parameter ?path=..."""
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        abort(404, description="Video not found")
    return send_file(path, mimetype="video/mp4", as_attachment=False)


@app.route("/api/media/thumbnail", methods=["GET"])
def serve_thumbnail():
    """Serve a thumbnail image via ?path=..."""
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        abort(404, description="Thumbnail not found")
    return send_file(path, mimetype="image/jpeg", as_attachment=False)


def run_flask_server(host="127.0.0.1", port=5000, debug=False):
    """Run Flask development server."""
    print(f"[Flask Backend] Starting Traffic Analyser API on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    run_flask_server()
