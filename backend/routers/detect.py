import io
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from PIL import Image

router = APIRouter()

MODEL_PATH = Path(__file__).parent.parent / "models" / "wildfire-smoke.pt"
CONFIDENCE_DANGER_THRESHOLD = 0.5

_model = None


def _load_model():
    global _model
    if _model is None:
        from ultralytics import YOLO

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No model found at {MODEL_PATH}. Fine-tune YOLOv8 on the "
                "FASDD_CV dataset (see ml/detect/README.md) and place the .pt file here."
            )
        _model = YOLO(str(MODEL_PATH))
    return _model


@router.post("")
async def detect_fire(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    model = _load_model()
    results = model.predict(image, verbose=False)[0]

    detections = []
    max_confidence = 0.0
    for box in results.boxes:
        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]
        detections.append(
            {
                "label": label,
                "confidence": confidence,
                "bbox": [round(x, 2) for x in box.xyxy[0].tolist()],
            }
        )
        max_confidence = max(max_confidence, confidence)

    return {
        "detections": detections,
        "is_danger": max_confidence >= CONFIDENCE_DANGER_THRESHOLD,
        "max_confidence": max_confidence,
    }
