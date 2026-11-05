"""Download the UCI Algerian Forest Fires Dataset used for risk prediction.

Source: https://archive.ics.uci.edu/dataset/547/algerian+forest+fires+dataset
Citation: Abid, Faroudja (2019). Algerian Forest Fires Dataset. UCI ML Repository.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/547/"
    "algerian+forest+fires+dataset.zip"
)
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"


def download_and_extract() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATASET_URL} ...")
    with urllib.request.urlopen(DATASET_URL, timeout=30) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        zf.extractall(RAW_DIR)

    csv_path = RAW_DIR / "Algerian_forest_fires_dataset_UPDATE.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Extraction finished but {csv_path.name} was not found in {RAW_DIR}"
        )

    print(f"Dataset ready at: {csv_path}")
    return csv_path


if __name__ == "__main__":
    download_and_extract()
