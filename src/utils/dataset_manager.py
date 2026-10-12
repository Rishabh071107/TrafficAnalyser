import os
import cv2
import json
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "inputs", "videos")
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, "inputs", "thumbnails")


class DatasetManager:
    """Manages the discovery, indexing, thumbnail generation, and metadata of video datasets."""

    def __init__(self, videos_dir: Optional[str] = None, thumbnails_dir: Optional[str] = None):
        self.videos_dir = videos_dir or VIDEOS_DIR
        self.thumbnails_dir = thumbnails_dir or THUMBNAILS_DIR
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

    def generate_sample_clips_if_needed(self) -> None:
        """If only one primary video exists, generate a couple of lightweight sample clips for quick dataset preview."""
        primary_path = os.path.join(self.videos_dir, "traffic.mp4")
        clip1_path = os.path.join(self.videos_dir, "highway_flow_sample.mp4")
        clip2_path = os.path.join(self.videos_dir, "junction_density_sample.mp4")

        if os.path.exists(primary_path) and (not os.path.exists(clip1_path) or not os.path.exists(clip2_path)):
            cap = cv2.VideoCapture(primary_path)
            if not cap.isOpened():
                return

            fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            # Create clip 1: frames 0 to 120 (~5 seconds)
            if not os.path.exists(clip1_path):
                out1 = cv2.VideoWriter(clip1_path, fourcc, fps, (width, height))
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                for _ in range(120):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out1.write(frame)
                out1.release()

            # Create clip 2: frames 200 to 320 (~5 seconds)
            if not os.path.exists(clip2_path):
                out2 = cv2.VideoWriter(clip2_path, fourcc, fps, (width, height))
                cap.set(cv2.CAP_PROP_POS_FRAMES, 200)
                for _ in range(120):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out2.write(frame)
                out2.release()

            cap.release()

    def get_thumbnail_path(self, video_name: str) -> str:
        """Get or generate thumbnail image for a video."""
        base_name = os.path.splitext(video_name)[0]
        thumb_name = f"{base_name}_thumb.jpg"
        thumb_path = os.path.join(self.thumbnails_dir, thumb_name)

        if os.path.exists(thumb_path):
            return thumb_path

        video_path = os.path.join(self.videos_dir, video_name)
        if not os.path.exists(video_path):
            return ""

        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            # Grab frame at 10% of total frames
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            target_frame = max(0, min(15, total - 1))
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if ret and frame is not None:
                # Resize to standard thumbnail size (480x270)
                thumb_img = cv2.resize(frame, (480, 270), interpolation=cv2.INTER_AREA)
                cv2.imwrite(thumb_path, thumb_img)
            cap.release()

        return thumb_path if os.path.exists(thumb_path) else ""

    def list_videos(self) -> List[Dict[str, Any]]:
        """List all available videos in the dataset with rich metadata."""
        self.generate_sample_clips_if_needed()
        valid_exts = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
        videos = []

        if not os.path.exists(self.videos_dir):
            return []

        for fname in sorted(os.listdir(self.videos_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in valid_exts:
                continue

            vpath = os.path.join(self.videos_dir, fname)
            try:
                size_mb = round(os.path.getsize(vpath) / (1024 * 1024), 2)
            except OSError:
                size_mb = 0.0

            cap = cv2.VideoCapture(vpath)
            duration_sec = 0.0
            fps = 30.0
            width, height = 0, 0
            frame_count = 0

            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if fps > 0:
                    duration_sec = round(frame_count / fps, 2)
                cap.release()

            thumb_path = self.get_thumbnail_path(fname)

            display_title = (
                fname.replace("_", " ")
                .replace(".mp4", "")
                .replace(".avi", "")
                .title()
            )

            videos.append({
                "filename": fname,
                "title": display_title,
                "path": vpath,
                "size_mb": size_mb,
                "duration_seconds": duration_sec,
                "formatted_duration": f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}",
                "resolution": f"{width}x{height}",
                "fps": round(fps, 1),
                "frame_count": frame_count,
                "thumbnail_path": thumb_path,
            })

        return videos
