import os
import sys
import time
import subprocess
import cv2
import torch
from typing import Dict, Any, Optional, Callable

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.detection.detector import TrafficDetector
from src.tracking.tracker import TrafficTracker
from src.traffic.counter import VehicleCounter
from src.traffic.speed import SpeedEstimator
from src.traffic.congestion import CongestionAnalyzer
from src.utils.video import VideoHandler
from src.utils.visualization import Visualizer

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None


class TrafficAnalysisPipeline:
    """End-to-end traffic detection, tracking, speed calculation, counting, and visualization pipeline."""

    def __init__(self, weights_path: Optional[str] = None):
        if weights_path is None:
            default_weights = os.path.join(PROJECT_ROOT, "models", "trained", "best.pt")
            self.weights_path = default_weights if os.path.exists(default_weights) else "yolo11n.pt"
        else:
            self.weights_path = weights_path

    def _convert_to_browser_mp4(self, raw_video_path: str, target_video_path: str) -> str:
        """Transcode video to standard H.264/AAC for HTML5 and Gradio player compatibility."""
        if not FFMPEG_EXE or not os.path.exists(raw_video_path):
            return raw_video_path

        try:
            cmd = [
                FFMPEG_EXE,
                "-y",
                "-i", raw_video_path,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                target_video_path,
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            if result.returncode == 0 and os.path.exists(target_video_path) and os.path.getsize(target_video_path) > 0:
                return target_video_path
        except Exception as e:
            print(f"[Pipeline] FFmpeg transcode warning: {e}")

        return raw_video_path

    def process_video(
        self,
        source_path: str,
        output_path: Optional[str] = None,
        conf_thresh: float = 0.25,
        imgsz: int = 640,
        frame_stride: int = 1,
        line_y_ratio: float = 0.5,
        max_frames: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, float, Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Execute inference, tracking, counting and speed analysis on a video.

        Args:
            source_path: Path to source video file.
            output_path: Destination path for output video.
            conf_thresh: YOLO detection confidence threshold.
            imgsz: Model inference dimension.
            frame_stride: Frame skipping stride for detection.
            line_y_ratio: Virtual counting line vertical position (0.0 to 1.0).
            max_frames: Optional maximum frames to process (useful for preview).
            progress_callback: Function called every frame with (frame_idx, total_frames, fps, current_metrics).

        Returns:
            Dictionary containing metrics, counts, speeds, congestion, and file paths.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source video not found: {source_path}")

        if output_path is None:
            os.makedirs(os.path.join(PROJECT_ROOT, "outputs", "tracking"), exist_ok=True)
            fname = os.path.splitext(os.path.basename(source_path))[0]
            output_path = os.path.join(PROJECT_ROOT, "outputs", "tracking", f"analyzed_{fname}.mp4")

        raw_output_path = output_path.replace(".mp4", "_raw.mp4")

        handler = VideoHandler(source_path)
        detector = TrafficDetector(weights_path=self.weights_path, conf_thresh=conf_thresh, imgsz=imgsz)
        tracker = TrafficTracker()
        counter = VehicleCounter(line_y_ratio=line_y_ratio)
        speed_estimator = SpeedEstimator(fps=handler.fps)
        congestion_analyzer = CongestionAnalyzer()
        visualizer = Visualizer()

        writer = handler.create_writer(raw_output_path)

        total_frames = handler.total_frames
        if max_frames and max_frames > 0:
            total_frames = min(total_frames, max_frames)

        last_detections = []
        speed_records = []
        congestion_levels = []
        class_breakdown: Dict[str, int] = {}
        unique_vehicle_ids = set()

        start_time = time.time()
        processed_frames = 0

        with torch.inference_mode():
            for frame_idx, frame in handler.frame_generator():
                if max_frames and frame_idx >= max_frames:
                    break

                current_time = frame_idx / handler.fps

                # 1. Detection
                if frame_idx % frame_stride == 0:
                    last_detections = detector.detect(frame)

                detections = last_detections

                # 2. Tracking
                active_tracks = tracker.update(detections)
                for trk in active_tracks:
                    tid = trk["track_id"]
                    unique_vehicle_ids.add(tid)
                    cname = trk.get("class_name", "vehicle")
                    class_breakdown[cname] = class_breakdown.get(cname, 0)

                # 3. Speed Estimation
                speeds = speed_estimator.update(active_tracks, current_time)
                for spd in speeds.values():
                    if spd > 0:
                        speed_records.append(spd)

                # 4. Counting
                counts = counter.process_tracks(active_tracks, handler.height)

                # 5. Congestion Analysis
                congestion_info = congestion_analyzer.analyze(len(active_tracks))
                congestion_levels.append(congestion_info.get("status", "Unknown"))

                # 6. Visualization Overlay
                frame = visualizer.draw_tracks(frame, active_tracks, speeds)
                frame = visualizer.draw_counting_line(frame, line_y_ratio=line_y_ratio)
                frame = visualizer.draw_dashboard(frame, counts, congestion_info)

                writer.write(frame)
                processed_frames += 1

                elapsed = time.time() - start_time
                curr_fps = round(processed_frames / elapsed, 2) if elapsed > 0 else 0.0

                if progress_callback:
                    interim = {
                        "frame": frame_idx + 1,
                        "total_frames": total_frames,
                        "fps": curr_fps,
                        "in_count": counts.get("in", 0),
                        "out_count": counts.get("out", 0),
                        "total_counted": counts.get("total", 0),
                        "active_tracked": len(active_tracks),
                        "congestion": congestion_info.get("status", "Free Flow"),
                    }
                    progress_callback(frame_idx + 1, total_frames, curr_fps, interim)

        handler.release()
        writer.release()

        # Re-encode to browser-compatible H.264
        final_video_path = self._convert_to_browser_mp4(raw_output_path, output_path)
        if final_video_path != raw_output_path and os.path.exists(raw_output_path):
            try:
                os.remove(raw_output_path)
            except OSError:
                pass

        total_elapsed = time.time() - start_time
        avg_speed = round(sum(speed_records) / len(speed_records), 1) if speed_records else 0.0
        max_speed = round(max(speed_records), 1) if speed_records else 0.0

        # Most prevalent congestion status
        dominant_congestion = "Free Flow"
        if congestion_levels:
            dominant_congestion = max(set(congestion_levels), key=congestion_levels.count)

        summary = {
            "status": "completed",
            "video_source": source_path,
            "output_video": final_video_path,
            "total_frames_processed": processed_frames,
            "total_elapsed_seconds": round(total_elapsed, 2),
            "average_fps": round(processed_frames / total_elapsed, 2) if total_elapsed > 0 else 0.0,
            "total_unique_vehicles": len(unique_vehicle_ids),
            "counts": {
                "inbound": counts.get("in", 0),
                "outbound": counts.get("out", 0),
                "total": counts.get("total", 0),
            },
            "speed_metrics": {
                "average_kmh": avg_speed,
                "max_kmh": max_speed,
                "samples_count": len(speed_records),
            },
            "congestion": {
                "status": dominant_congestion,
                "peak_density": max(1, len(active_tracks) if 'active_tracks' in locals() else 0),
            },
            "classes_detected": class_breakdown,
        }

        return summary
