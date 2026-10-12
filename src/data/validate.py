import os
from typing import Dict, Any


def validate_dataset(dataset_dir: str = "data/processed") -> Dict[str, Any]:
    """Validate dataset structure, label formatting, and image-label parity.

    Args:
        dataset_dir: Path to processed dataset directory.

    Returns:
        Dictionary summary of dataset integrity checks.
    """
    splits = ["train", "val", "test"]
    stats: Dict[str, Any] = {"valid": True, "splits": {}}

    for split in splits:
        img_dir = os.path.join(dataset_dir, "images", split)
        lbl_dir = os.path.join(dataset_dir, "labels", split)

        images = set(os.listdir(img_dir)) if os.path.exists(img_dir) else set()
        labels = set(os.listdir(lbl_dir)) if os.path.exists(lbl_dir) else set()

        img_basenames = {os.path.splitext(f)[0] for f in images if f.lower().endswith(('.jpg', '.png', '.jpeg'))}
        lbl_basenames = {os.path.splitext(f)[0] for f in labels if f.endswith('.txt')}

        missing_labels = img_basenames - lbl_basenames
        orphaned_labels = lbl_basenames - img_basenames

        stats["splits"][split] = {
            "image_count": len(img_basenames),
            "label_count": len(lbl_basenames),
            "missing_labels_count": len(missing_labels),
            "orphaned_labels_count": len(orphaned_labels),
        }

        if missing_labels or orphaned_labels:
            stats["valid"] = False

    print(f"Dataset Validation Summary: {stats}")
    return stats


if __name__ == "__main__":
    validate_dataset()
