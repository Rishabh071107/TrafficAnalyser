import os
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Any, Union


class TrafficDetector:
    """Wrapper around YOLO model for vehicle and object detection."""

    def __init__(
        self,
        weights_path: str = "models/trained/best.pt",
        conf_thresh: float = 0.25,
        iou_thresh: float = 0.45,
        imgsz: int = 480,
        device: Union[str, int] = "cpu",
    ):
        """Initialize TrafficDetector model instance.

        Args:
            weights_path: Path to YOLO weights file (.pt).
            conf_thresh: Confidence detection threshold.
            iou_thresh: Non-maximum suppression IoU threshold.
            imgsz: Inference resolution (smaller = faster).
            device: Computing device ('cpu', 0, 'cuda').
        """
        if not os.path.exists(weights_path):
            print(f"Warning: Weights file '{weights_path}' not found. Falling back to 'yolo11n.pt'")
            weights_path = "yolo11n.pt"

        self.weights_path = weights_path
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.imgsz = imgsz
        self.device = device
        self.model = YOLO(self.weights_path)

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Perform object detection on a single image frame.

        Args:
            image: Input BGR image frame as numpy array.

        Returns:
            List of detected object dictionaries with keys:
            ['bbox', 'confidence', 'class_id', 'class_name']
        """
        results = self.model(
            image,
            conf=self.conf_thresh,
            iou=self.iou_thresh,
            imgsz=self.imgsz,
            device=self.device,
            verbose=False,
        )

        detections = []
        if not results or len(results) == 0:
            return detections

        boxes = results[0].boxes
        names = results[0].names

        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().item())
            cls_id = int(box.cls[0].cpu().item())
            cls_name = names.get(cls_id, str(cls_id))

            detections.append({
                "bbox": [float(x) for x in xyxy],
                "confidence": conf,
                "class_id": cls_id,
                "class_name": cls_name,
            })

        return detections


if __name__ == "__main__":
    detector = TrafficDetector()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = detector.detect(dummy_frame)
    print(f"Detection test completed on dummy frame: {len(res)} objects detected.")
