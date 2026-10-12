import math
from typing import Dict, List, Any, Tuple


class SpeedEstimator:
    """Estimates vehicle speeds in km/h based on pixel displacements over time."""

    def __init__(self, fps: float = 30.0, pixel_to_meter: float = 0.05):
        """Initialize speed estimator.

        Args:
            fps: Video frames per second.
            pixel_to_meter: Calibration factor converting pixels to meters.
        """
        self.fps = fps
        self.pixel_to_meter = pixel_to_meter
        self.track_history: Dict[int, List[Tuple[float, float, float]]] = {}  # id -> [(x, y, timestamp)]

    def update(self, tracks: List[Dict[str, Any]], current_time: float) -> Dict[int, float]:
        """Compute estimated speeds for active tracks.

        Args:
            tracks: List of track dicts with 'track_id' and 'centroid'.
            current_time: Current video timestamp in seconds.

        Returns:
            Dict mapping track_id -> speed_kmh.
        """
        speeds: Dict[int, float] = {}

        for trk in tracks:
            track_id = trk["track_id"]
            cx, cy = trk["centroid"]

            if track_id not in self.track_history:
                self.track_history[track_id] = []

            self.track_history[track_id].append((cx, cy, current_time))

            # Maintain history window of last 10 points
            if len(self.track_history[track_id]) > 10:
                self.track_history[track_id].pop(0)

            history = self.track_history[track_id]
            if len(history) >= 2:
                x1, y1, t1 = history[0]
                x2, y2, t2 = history[-1]

                dt = t2 - t1
                if dt > 0:
                    pixel_dist = math.hypot(x2 - x1, y2 - y1)
                    meters = pixel_dist * self.pixel_to_meter
                    speed_mps = meters / dt
                    speed_kmh = speed_mps * 3.6
                    speeds[track_id] = round(speed_kmh, 1)
                else:
                    speeds[track_id] = 0.0
            else:
                speeds[track_id] = 0.0

        return speeds


if __name__ == "__main__":
    estimator = SpeedEstimator(fps=30, pixel_to_meter=0.05)
    speeds = estimator.update([{"track_id": 1, "centroid": (100, 100)}], current_time=0.0)
    print(f"Speed estimator test: {speeds}")
