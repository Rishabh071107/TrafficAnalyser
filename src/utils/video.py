import cv2
import os
from typing import Generator, Tuple, Optional


class VideoHandler:
    """Utility for reading video streams and writing output video files."""

    def __init__(self, video_path: str):
        """Initialize VideoHandler.

        Args:
            video_path: Path to input video file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input video file '{video_path}' not found.")

        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video source '{video_path}'.")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = float(self.cap.get(cv2.CAP_PROP_FPS))
        if self.fps <= 0:
            self.fps = 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def frame_generator(self) -> Generator[Tuple[int, cv2.Mat], None, None]:
        """Yield frame index and frame matrix sequentially."""
        frame_idx = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame_idx, frame
            frame_idx += 1

    def create_writer(self, output_path: str, codec: str = "mp4v") -> cv2.VideoWriter:
        """Create OpenCV VideoWriter instance matching input dimensions and FPS.

        Args:
            output_path: Path to save rendered video file.
            codec: FourCC video codec string (default 'mp4v').

        Returns:
            Configured cv2.VideoWriter object.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        return writer

    def release(self) -> None:
        """Release underlying OpenCV capture object."""
        if self.cap:
            self.cap.release()


if __name__ == "__main__":
    print("VideoHandler utility initialized.")
