import argparse
import sys
import os
import cv2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.detection.detector import TrafficDetector
from src.tracking.tracker import TrafficTracker
from src.traffic.counter import VehicleCounter
from src.traffic.speed import SpeedEstimator
from src.traffic.congestion import CongestionAnalyzer
from src.utils.video import VideoHandler
from src.utils.visualization import Visualizer


import torch


def parse_args():
    parser = argparse.ArgumentParser(description="Run Traffic Detection, Tracking & Analytics Pipeline")
    parser.add_argument("--source", type=str, default="inputs/videos/traffic.mp4", help="Path to input video")
    parser.add_argument("--weights", type=str, default="models/trained/best.pt", help="Model weights path")
    parser.add_argument("--output", type=str, default="outputs/tracking/output_traffic.mp4", help="Path to save output video")
    parser.add_argument("--conf", type=float, default=0.25, help="Detection confidence threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference resolution size (640 for max accuracy)")
    parser.add_argument("--frame-stride", type=int, default=1, help="Process object detection every N frames (1 = 100% full video coverage)")
    parser.add_argument("--line-y", type=float, default=0.5, help="Counting line position ratio (0.0 to 1.0)")
    parser.add_argument("--show", action="store_true", default=True, help="Display live window tab during processing (default: True)")
    parser.add_argument("--no-show", dest="show", action="store_false", help="Disable live window display")
    return parser.parse_args()


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resolve_path(path_str: str) -> str:
    if os.path.isabs(path_str) or os.path.exists(path_str):
        return path_str
    root_path = os.path.abspath(os.path.join(PROJECT_ROOT, path_str))
    if os.path.exists(root_path):
        return root_path
    return root_path


def main():
    args = parse_args()

    source_path = resolve_path(args.source)
    weights_path = resolve_path(args.weights)
    output_path = resolve_path(args.output)

    print(f"Initializing Traffic Analysis Pipeline (100% Video Coverage)...")
    print(f"  Source Video: {source_path}")
    print(f"  Weights: {weights_path}")
    print(f"  Inference Resolution: {args.imgsz}px | Frame Stride: {args.frame_stride} (Full Coverage)")

    if not os.path.exists(source_path):
        print(f"Error: Source video file '{source_path}' does not exist.")
        return

    handler = VideoHandler(source_path)
    detector = TrafficDetector(weights_path=weights_path, conf_thresh=args.conf, imgsz=args.imgsz)
    tracker = TrafficTracker()
    counter = VehicleCounter(line_y_ratio=args.line_y)
    speed_estimator = SpeedEstimator(fps=handler.fps)
    congestion_analyzer = CongestionAnalyzer()
    visualizer = Visualizer()

    writer = handler.create_writer(output_path)
    print(f"Output video writer created: {output_path}")

    last_detections = []

    with torch.inference_mode():
        for frame_idx, frame in handler.frame_generator():
            current_time = frame_idx / handler.fps

            # 1. Detection (Run every N frames for speed optimization)
            if frame_idx % args.frame_stride == 0:
                last_detections = detector.detect(frame)
            
            detections = last_detections

            # 2. Tracking
            active_tracks = tracker.update(detections)

            # 3. Speed Estimation
            speeds = speed_estimator.update(active_tracks, current_time)

            # 4. Vehicle Counting
            counts = counter.process_tracks(active_tracks, handler.height)

            # 5. Congestion Analysis
            congestion_info = congestion_analyzer.analyze(len(active_tracks))

            # 6. Visualization
            frame = visualizer.draw_tracks(frame, active_tracks, speeds)
            frame = visualizer.draw_counting_line(frame, line_y_ratio=args.line_y)
            frame = visualizer.draw_dashboard(frame, counts, congestion_info)

            # Save frame
            writer.write(frame)

            if args.show:
                window_name = "Traffic Monitor - Live Video Detection & Tracking"
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):  # ESC or 'q' to quit
                    print("Processing interrupted by user.")
                    break
                elif key == ord(' '):  # Spacebar to pause/resume
                    cv2.waitKey(0)

    handler.release()
    writer.release()
    if args.show:
        cv2.destroyAllWindows()

    print(f"Pipeline execution completed successfully.")
    print(f"  Output saved to: {args.output}")
    print(f"  Final Traffic Summary: {counts}")


if __name__ == "__main__":
    main()
