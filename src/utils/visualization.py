import cv2
import numpy as np
from typing import List, Dict, Any, Optional


class Visualizer:
    """Visualizes traffic detection, tracking, speeds, line counts, and congestion overlays."""

    def __init__(
        self,
        line_color: tuple = (0, 255, 255),
        box_color: tuple = (0, 255, 0),
        text_color: tuple = (255, 255, 255),
    ):
        self.line_color = line_color
        self.box_color = box_color
        self.text_color = text_color

    def draw_tracks(
        self,
        frame: np.ndarray,
        tracks: List[Dict[str, Any]],
        speeds: Optional[Dict[int, float]] = None,
    ) -> np.ndarray:
        """Draw bounding boxes, track IDs, object classes, and speed badges.

        Args:
            frame: Input image matrix.
            tracks: List of active track dicts.
            speeds: Map of track_id -> speed in km/h.

        Returns:
            Annotated image frame.
        """
        annotated = frame.copy()

        for trk in tracks:
            track_id = trk["track_id"]
            x1, y1, x2, y2 = [int(v) for v in trk["bbox"]]
            cls_name = trk.get("class_name", "vehicle")

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), self.box_color, 2)

            # Label text
            speed_str = f" | {speeds[track_id]} km/h" if speeds and track_id in speeds else ""
            label = f"#{track_id} {cls_name}{speed_str}"

            # Label background badge
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 6), (x1 + tw + 6, y1), self.box_color, -1)
            cv2.putText(
                annotated,
                label,
                (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        return annotated

    def draw_counting_line(self, frame: np.ndarray, line_y_ratio: float = 0.6) -> np.ndarray:
        """Draw virtual counting line across frame."""
        h, w, _ = frame.shape
        line_y = int(h * line_y_ratio)
        cv2.line(frame, (0, line_y), (w, line_y), self.line_color, 3)
        cv2.putText(
            frame,
            "COUNTING LINE",
            (10, line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            self.line_color,
            2,
        )
        return frame

    def draw_dashboard(
        self,
        frame: np.ndarray,
        counts: Dict[str, int],
        congestion_info: Dict[str, Any],
    ) -> np.ndarray:
        """Render HUD dashboard showing counts and traffic status."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (320, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        # Dashboard Text
        cv2.putText(frame, f"Inbound: {counts.get('inbound', 0)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Outbound: {counts.get('outbound', 0)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Total Vehicles: {counts.get('total', 0)}", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        status = congestion_info.get("status", "Unknown")
        color_map = {
            "Free Flow": (0, 255, 0),
            "Moderate Traffic": (0, 255, 255),
            "Heavy Traffic": (0, 165, 255),
            "Standstill / Congested": (0, 0, 255),
        }
        status_color = color_map.get(status, (255, 255, 255))
        cv2.putText(frame, f"Status: {status}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

        return frame


if __name__ == "__main__":
    visualizer = Visualizer()
    print("Visualizer module initialized.")
