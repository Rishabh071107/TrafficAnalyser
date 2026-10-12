from ultralytics import YOLO
from typing import Dict, Any, Optional


def train_model(
    data_config: str = "configs/data.yaml",
    model_weights: str = "yolo11n.pt",
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 16,
    project: str = "experiments",
    name: str = "exp001_yolo11n",
    extra_params: Optional[Dict[str, Any]] = None,
) -> Any:
    """Train YOLO model on specified traffic dataset configuration.

    Args:
        data_config: Path to dataset YAML configuration file.
        model_weights: Path or name of base weights (e.g., yolo11n.pt).
        epochs: Number of training epochs.
        imgsz: Image resolution size.
        batch: Batch size per GPU/CPU device.
        project: Directory for experiment tracking.
        name: Name of experiment run.
        extra_params: Additional hyperparameters for YOLO train method.

    Returns:
        Ultralytics training results object.
    """
    params = {
        "data": data_config,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "project": project,
        "name": name,
    }
    if extra_params:
        params.update(extra_params)

    print(f"Starting YOLO training with base weights '{model_weights}'...")
    model = YOLO(model_weights)
    results = model.train(**params)
    print(f"Training finished. Models saved under {project}/{name}")
    return results


if __name__ == "__main__":
    train_model()
