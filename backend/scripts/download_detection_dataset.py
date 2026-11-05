"""Download the FASDD_CV fire/smoke detection dataset (YOLO format).

Source: https://huggingface.co/datasets/seawsurf/fire_smoke_dataset_fasdd_cv
(a Roboflow-exported mirror of the FASDD_CV benchmark — same images/labels,
just packaged with a ready-to-use data.yaml and train/valid/test split).

Citation: Wang, M., Yue, P., Jiang, L., Yu, D., Tuo, T., & Li, J. (2025). An
open flame and smoke detection dataset for deep learning in remote sensing
based fire detection. Geo-spatial Information Science, 28(2), 511-526.
https://doi.org/10.1080/10095020.2024.2347922

~3.4GB zip, ~95k images. Streams to disk in chunks (never buffers the whole
file in memory) and extracts in place. Takes a while on a normal connection
— run with `nohup` or in a background shell if needed.
"""

import urllib.request
import zipfile
from pathlib import Path

DATASET_URL = (
    "https://huggingface.co/datasets/seawsurf/fire_smoke_dataset_fasdd_cv"
    "/resolve/main/FASDD_CV.zip"
)
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
ZIP_PATH = RAW_DIR / "FASDD_CV.zip"
EXTRACT_DIR = RAW_DIR / "fasdd_cv"
CHUNK_SIZE = 1024 * 1024  # 1 MiB


def download(url: str, dest: Path) -> None:
    with urllib.request.urlopen(url, timeout=60) as response:
        total = int(response.headers.get("Content-Length", 0))
        written = 0
        with open(dest, "wb") as f:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                written += len(chunk)
                if total:
                    pct = written / total * 100
                    print(f"\r{written / 1e6:,.0f} / {total / 1e6:,.0f} MB ({pct:.1f}%)", end="")
    print()


def main() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not ZIP_PATH.exists():
        print(f"Downloading {DATASET_URL} -> {ZIP_PATH}")
        download(DATASET_URL, ZIP_PATH)
    else:
        print(f"{ZIP_PATH} already exists, skipping download.")

    if not EXTRACT_DIR.exists():
        print(f"Extracting to {EXTRACT_DIR} ...")
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(EXTRACT_DIR)
    else:
        print(f"{EXTRACT_DIR} already exists, skipping extraction.")

    print(f"Dataset ready at: {EXTRACT_DIR}")
    return EXTRACT_DIR


if __name__ == "__main__":
    main()
