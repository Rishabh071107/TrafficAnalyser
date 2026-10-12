import pytest
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.detection.detector import TrafficDetector


def test_detector_initialization():
    detector = TrafficDetector(weights_path="models/trained/best.pt")
    assert detector is not None
    assert detector.conf_thresh == 0.25


def test_detector_empty_frame():
    detector = TrafficDetector(weights_path="models/trained/best.pt")
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    results = detector.detect(dummy_frame)
    assert isinstance(results, list)
