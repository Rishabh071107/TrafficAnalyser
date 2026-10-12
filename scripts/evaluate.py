import argparse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.evaluate import evaluate_model


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate Traffic Monitoring Model")
    parser.add_argument("--weights", type=str, default="models/trained/best.pt", help="Path to trained model weights")
    parser.add_argument("--data", type=str, default="configs/data.yaml", help="Path to dataset yaml config")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution size")
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"], help="Dataset split to evaluate")
    return parser.parse_args()


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resolve_path(path_str: str) -> str:
    if os.path.isabs(path_str) or os.path.exists(path_str):
        return path_str
    root_path = os.path.abspath(os.path.join(PROJECT_ROOT, path_str))
    if os.path.exists(root_path):
        return root_path
    return root_path


def main():
    args = parse_args()
    evaluate_model(
        weights=resolve_path(args.weights),
        data_config=resolve_path(args.data),
        imgsz=args.imgsz,
        split=args.split,
    )


if __name__ == "__main__":
    main()
