"""Fine-tune YOLOv8 for fire/smoke detection on the FASDD_CV dataset.

Transfer learning from COCO-pretrained weights (not training from scratch):
with ~95k images FASDD_CV is large enough that fewer epochs are needed than
a from-scratch run would take, which matters on a 48-hour hackathon clock.

Citation: Wang, M., Yue, P., Jiang, L., Yu, D., Tuo, T., & Li, J. (2025). An
open flame and smoke detection dataset for deep learning in remote sensing
based fire detection. Geo-spatial Information Science, 28(2), 511-526.
https://doi.org/10.1080/10095020.2024.2347922

Reference point: a community checkpoint on this exact dataset (but a
different, newer architecture — YOLO26n, not YOLOv8n) reports mAP50 0.772
(huggingface.co/weslleyskah/fire_smoke_box). Useful to sanity-check order of
magnitude, not a number to match exactly since the architecture differs.

Prerequisites:
    1. python scripts/download_detection_dataset.py (downloads + extracts
       into backend/data/raw/fasdd_cv/ — ~3.4GB, see ml/detect/README.md)
    2. pip install -r requirements.txt (pulls in ultralytics/torch)
    3. A GPU. On CPU this dataset is impractically slow — use Google Colab
       (free T4) or a Kaggle Notebook (free P100) if the local machine has
       none.

Usage:
    python -m ml.detect.train --epochs 40 --model yolov8n.pt
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

from ml.detect.dataset import DATASET_DIR, resolved_data_yaml

RUNS_DIR = Path(__file__).parent.parent.parent / "runs" / "detect"
MODEL_DIR = Path(__file__).parent.parent.parent / "models"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="Starting checkpoint: yolov8n.pt (fastest) or yolov8s.pt (more accurate)",
    )
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--patience", type=int, default=10, help="early-stopping patience")
    return parser.parse_args()


def main():
    args = parse_args()

    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_DIR}. "
            "Run: python scripts/download_detection_dataset.py"
        )

    model = YOLO(args.model)
    results = model.train(
        data=str(resolved_data_yaml()),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        project=str(RUNS_DIR),
        name="fasdd_cv_finetune",
        exist_ok=True,
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    target = MODEL_DIR / "wildfire-smoke.pt"
    target.write_bytes(best_weights.read_bytes())
    print(f"Best weights copied to {target}")


if __name__ == "__main__":
    main()
