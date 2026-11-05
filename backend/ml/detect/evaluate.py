"""Evaluate a fine-tuned YOLO checkpoint on the FASDD_CV test split.

Produces mAP50 / mAP50-95 overall and per-class, plus a confusion matrix
plot, so the README's "Model accuracy or performance metrics" section can
cite real, reproducible numbers instead of training-log screenshots.

Usage:
    python -m ml.detect.evaluate --weights ../../models/wildfire-smoke.pt
"""

import argparse
import json
from pathlib import Path

from ultralytics import YOLO

from ml.detect.dataset import resolved_data_yaml

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", required=True, help="path to a trained .pt checkpoint")
    parser.add_argument("--split", default="test", choices=["val", "test"])
    return parser.parse_args()


def main():
    args = parse_args()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights)
    metrics = model.val(data=str(resolved_data_yaml()), split=args.split, plots=True)

    summary = {
        "split": args.split,
        "map50": round(float(metrics.box.map50), 4),
        "map50_95": round(float(metrics.box.map), 4),
        "per_class_map50": {
            name: round(float(ap), 4)
            for name, ap in zip(metrics.names.values(), metrics.box.ap50)
        },
    }

    with open(PROCESSED_DIR / "detection_model_metrics.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Plots (confusion matrix, PR curve) saved under: {metrics.save_dir}")


if __name__ == "__main__":
    main()
