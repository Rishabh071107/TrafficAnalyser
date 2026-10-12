import numpy as np
from typing import List, Dict, Any


class TrafficTracker:
    """Multi-object vehicle tracker keeping persistent track IDs across frames."""

    def __init__(self, max_disappeared: int = 30, distance_threshold: float = 75.0):
        """Initialize centroid & Euclidean association multi-object tracker.

        Args:
            max_disappeared: Maximum consecutive frames a track can be missing before deletion.
            distance_threshold: Maximum pixel distance for associating detections to existing tracks.
        """
        self.next_object_id = 0
        self.objects: Dict[int, np.ndarray] = {}  # track_id -> centroid (x, y)
        self.bboxes: Dict[int, List[float]] = {}   # track_id -> [x1, y1, x2, y2]
        self.class_names: Dict[int, str] = {}      # track_id -> class_name
        self.disappeared: Dict[int, int] = {}       # track_id -> missing frame count
        self.max_disappeared = max_disappeared
        self.distance_threshold = distance_threshold

    def register(self, centroid: np.ndarray, bbox: List[float], class_name: str) -> int:
        """Register a new object track."""
        track_id = self.next_object_id
        self.objects[track_id] = centroid
        self.bboxes[track_id] = bbox
        self.class_names[track_id] = class_name
        self.disappeared[track_id] = 0
        self.next_object_id += 1
        return track_id

    def deregister(self, track_id: int) -> None:
        """Deregister lost object track."""
        del self.objects[track_id]
        del self.bboxes[track_id]
        del self.class_names[track_id]
        del self.disappeared[track_id]

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update tracker state given current frame detections.

        Args:
            detections: List of detection dicts containing 'bbox' and 'class_name'.

        Returns:
            List of track dicts with keys: ['track_id', 'bbox', 'centroid', 'class_name']
        """
        if len(detections) == 0:
            for track_id in list(self.disappeared.keys()):
                self.disappeared[track_id] += 1
                if self.disappeared[track_id] > self.max_disappeared:
                    self.deregister(track_id)
            return self.get_active_tracks()

        input_centroids = np.zeros((len(detections), 2), dtype="int")
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            cX = int((x1 + x2) / 2.0)
            cY = int((y1 + y2) / 2.0)
            input_centroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i, det in enumerate(detections):
                self.register(input_centroids[i], det["bbox"], det.get("class_name", "vehicle"))
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Calculate pairwise distance matrix
            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - input_centroids, axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                if D[row, col] > self.distance_threshold:
                    continue

                track_id = object_ids[row]
                self.objects[track_id] = input_centroids[col]
                self.bboxes[track_id] = detections[col]["bbox"]
                self.class_names[track_id] = detections[col].get("class_name", "vehicle")
                self.disappeared[track_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])) - used_rows
            unused_cols = set(range(0, D.shape[1])) - used_cols

            for row in unused_rows:
                track_id = object_ids[row]
                self.disappeared[track_id] += 1
                if self.disappeared[track_id] > self.max_disappeared:
                    self.deregister(track_id)

            for col in unused_cols:
                self.register(input_centroids[col], detections[col]["bbox"], detections[col].get("class_name", "vehicle"))

        return self.get_active_tracks()

    def get_active_tracks(self) -> List[Dict[str, Any]]:
        """Return list of active tracks."""
        tracks = []
        for track_id in self.objects:
            tracks.append({
                "track_id": track_id,
                "bbox": self.bboxes[track_id],
                "centroid": self.objects[track_id].tolist(),
                "class_name": self.class_names[track_id],
            })
        return tracks


if __name__ == "__main__":
    tracker = TrafficTracker()
    sample_dets = [
        {"bbox": [100, 100, 200, 200], "class_name": "car"},
        {"bbox": [300, 300, 400, 400], "class_name": "truck"},
    ]
    tracks = tracker.update(sample_dets)
    print(f"Tracker test: {len(tracks)} active tracks assigned.")
