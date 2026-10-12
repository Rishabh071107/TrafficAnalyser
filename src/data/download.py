import os
import urllib.request
from typing import Optional


def download_dataset(output_dir: str = "data/raw", source_url: Optional[str] = None) -> str:
    """Download traffic sample dataset or raw data archive.

    Args:
        output_dir: Directory where raw dataset will be saved.
        source_url: Custom download URL for the dataset.

    Returns:
        Path to downloaded dataset directory or file.
    """
    os.makedirs(output_dir, exist_ok=True)
    if not source_url:
        print(f"No download URL provided. Dataset placeholder initialized at {output_dir}")
        return output_dir

    dest_path = os.path.join(output_dir, "dataset.zip")
    print(f"Downloading dataset from {source_url} -> {dest_path}")
    urllib.request.urlretrieve(source_url, dest_path)
    print("Download completed successfully.")
    return dest_path


if __name__ == "__main__":
    download_dataset()
