import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tracking.tracker import TrafficTracker


def test_tracker_register_and_update():
    tracker = TrafficTracker()
    detections = [
        {"bbox": [100, 100, 200, 200], "class_name": "car"},
        {"bbox": [300, 300, 400, 400], "class_name": "truck"},
    ]

    tracks = tracker.update(detections)
    assert len(tracks) == 2
    assert tracks[0]["track_id"] == 0
    assert tracks[1]["track_id"] == 1


def test_tracker_disappearance():
    tracker = TrafficTracker(max_disappeared=2)
    detections = [{"bbox": [100, 100, 200, 200], "class_name": "car"}]

    tracker.update(detections)  # Frame 1: Registered
    tracker.update([])          # Frame 2: Missing (count=1)
    tracks = tracker.update([]) # Frame 3: Missing (count=2, deregistered)

    assert len(tracks) == 0
