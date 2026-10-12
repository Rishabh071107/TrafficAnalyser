import os
import sys
import unittest
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from deployment.api.flask_app import app


class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_flask_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "online")
        self.assertIn("model_weights", data)

    def test_flask_dataset_videos(self):
        response = self.client.get("/api/dataset/videos")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("videos", data)
        self.assertGreaterEqual(len(data["videos"]), 1)

    def test_flask_analyze_missing_source(self):
        response = self.client.post("/api/analyze", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["status"], "error")

    def test_flask_analyze_execution(self):
        response = self.client.post(
            "/api/analyze",
            json={
                "source": "inputs/videos/highway_flow_sample.mp4",
                "conf": 0.25,
                "imgsz": 320,
                "max_frames": 5,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        self.assertIn("output_video", data["data"])
        self.assertIn("counts", data["data"])


if __name__ == "__main__":
    unittest.main()
