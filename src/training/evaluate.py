from ultralytics import YOLO
from typing import Dict, Any


def evaluate_model(
    weights: str = "models/trained/best.pt",
    data_config: str = "configs/data.yaml",
    imgsz: int = 640,
    split: str = "val",
) -> Dict[str, Any]:
    """Evaluate trained YOLO model on validation or test dataset.

    Args:
        weights: Path to trained model weights checkpoint.
        data_config: Path to dataset YAML configuration.
        imgsz: Image resolution size.
        split: Dataset split to evaluate ('val' or 'test').

    Returns:
        Dictionary containing mAP50, mAP50-95, Precision, Recall metrics.
    """
    print(f"Evaluating model weights '{weights}' on split '{split}'...")
    model = YOLO(weights)
    metrics = model.val(data=data_config, imgsz=imgsz, split=split, verbose=True)

    results_dict = {
        "mAP50": float(metrics.box.map50),
        "mAP50-95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
    }

    print("--- Evaluation Results ---")
    for metric_name, value in results_dict.items():
        print(f"  {metric_name}: {value:.4f}")

    return results_dict


if __name__ == "__main__":
    evaluate_model()
