import os
import shutil
import random
from typing import Tuple, List


def prepare_yolo_dataset(
    raw_dir: str = "data/raw/original_dataset",
    processed_dir: str = "data/processed",
    split_ratio: Tuple[float, float, float] = (0.7, 0.2, 0.1),
    seed: int = 42,
) -> None:
    """Split raw images and labels into train/val/test directories formatted for YOLO.

    Args:
        raw_dir: Directory containing raw images and labels.
        processed_dir: Output root directory for train/val/test splits.
        split_ratio: (train, val, test) proportions.
        seed: Random seed for reproducible splitting.
    """
    random.seed(seed)
    train_r, val_r, test_r = split_ratio
    assert abs(train_r + val_r + test_r - 1.0) < 1e-5, "Split ratios must sum to 1.0"

    subdirs = ["images/train", "images/val", "images/test", "labels/train", "labels/val", "labels/test"]
    for sd in subdirs:
        os.makedirs(os.path.join(processed_dir, sd), exist_ok=True)

    if not os.path.exists(raw_dir):
        print(f"Raw dataset directory {raw_dir} does not exist. Created empty structure.")
        return

    images: List[str] = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if not images:
        print(f"No images found in {raw_dir}. Initialized empty split folders in {processed_dir}.")
        return

    random.shuffle(images)
    n = len(images)
    n_train = int(n * train_r)
    n_val = int(n * val_r)

    splits = {
        "train": images[:n_train],
        "val": images[n_train:n_train + n_val],
        "test": images[n_train + n_val:],
    }

    for split_name, img_list in splits.items():
        for img_name in img_list:
            base_name, _ = os.path.splitext(img_name)
            label_name = f"{base_name}.txt"

            # Copy image
            src_img = os.path.join(raw_dir, img_name)
            dst_img = os.path.join(processed_dir, "images", split_name, img_name)
            shutil.copy2(src_img, dst_img)

            # Copy label if exists
            src_lbl = os.path.join(raw_dir, label_name)
            dst_lbl = os.path.join(processed_dir, "labels", split_name, label_name)
            if os.path.exists(src_lbl):
                shutil.copy2(src_lbl, dst_lbl)

    print(f"Dataset preparation complete. Train: {len(splits['train'])}, Val: {len(splits['val'])}, Test: {len(splits['test'])}")


if __name__ == "__main__":
    prepare_yolo_dataset()
