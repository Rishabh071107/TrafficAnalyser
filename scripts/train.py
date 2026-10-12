import argparse
import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.train import train_model


def parse_args():
    parser = argparse.ArgumentParser(description="Train Traffic Monitoring YOLO Model")
    parser.add_argument("--data", type=str, default="configs/data.yaml", help="Path to data yaml config")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Base pretrained model weights")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--project", type=str, default="experiments", help="Experiment storage directory")
    parser.add_argument("--name", type=str, default="exp001_yolo11n", help="Run name")
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
    train_model(
        data_config=resolve_path(args.data),
        model_weights=resolve_path(args.model),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=resolve_path(args.project),
        name=args.name,
    )


if __name__ == "__main__":
    main()
