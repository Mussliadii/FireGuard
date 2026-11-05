"""Loads the YOLO fire/smoke detection checkpoint and runs inference.

See backend/ml/detect/README.md for where wildfire-smoke.pt comes from
(a ready-made checkpoint, not trained in this repo) and its accuracy.
"""

from pathlib import Path

from PIL import Image

MODEL_PATH = Path(__file__).parent.parent / "backend" / "models" / "wildfire-smoke.pt"
CONFIDENCE_DANGER_THRESHOLD = 0.5


def load_model():
    if not MODEL_PATH.exists():
        return None
    from ultralytics import YOLO

    return YOLO(str(MODEL_PATH))


def detect(model, image: Image.Image) -> dict:
    results = model.predict(image, verbose=False)[0]

    detections = []
    max_confidence = 0.0
    for box in results.boxes:
        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]
        detections.append({"label": label, "confidence": confidence})
        max_confidence = max(max_confidence, confidence)

    # Results.plot() draws the boxes/labels for us (BGR numpy array -> RGB).
    annotated = results.plot()[:, :, ::-1]

    return {
        "detections": detections,
        "is_danger": max_confidence >= CONFIDENCE_DANGER_THRESHOLD,
        "max_confidence": max_confidence,
        "annotated_image": annotated,
    }
