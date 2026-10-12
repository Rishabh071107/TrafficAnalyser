import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.traffic.counter import VehicleCounter


def test_vehicle_counter_line_crossing():
    counter = VehicleCounter(line_y_ratio=0.5)
    frame_height = 480
    # line_y = 240

    # Frame 1: Vehicle above line
    counter.process_tracks([{"track_id": 1, "centroid": (100, 200)}], frame_height)
    assert counter.inbound_count == 0

    # Frame 2: Vehicle moves below line -> Inbound cross
    counts = counter.process_tracks([{"track_id": 1, "centroid": (100, 260)}], frame_height)
    assert counts["inbound"] == 1
    assert counts["total"] == 1
