# Detection model: fire_yolo (ready-made checkpoint)

**Decision:** used directly as the production model (`backend/models/wildfire-smoke.pt`),
rather than training from scratch — it's already fully trained on the exact
same dataset we verified (FASDD_CV), and this machine has no GPU.

**Source:** [huggingface.co/seawsurf/fire_yolo](https://huggingface.co/seawsurf/fire_yolo)
**License:** CC BY 4.0.
**Architecture:** YOLO26n (base model `yolo26n.pt`, Ultralytics' newest variant).

**Metrics (recomputed directly from this model's own `results.csv`, epoch
78 — the same epoch as the downloaded `best.pt` checkpoint, selected via
`patience=30` early-stopping out of 100 total epochs):**

| Metric | Value |
|---|---|
| mAP50 | 0.774 |
| mAP50-95 | 0.527 |
| Precision | 0.783 |
| Recall | 0.674 |

Training parameters (from the model's own `args.yaml`): epochs=100, imgsz=640,
batch=256, workers=12, patience=30, full FASDD_CV dataset (95,126 images).

**Dataset citation (still required — the model was trained on this
dataset):**
> Wang, M., Yue, P., Jiang, L., Yu, D., Tuo, T., & Li, J. (2025). An open
> flame and smoke detection dataset for deep learning in remote sensing
> based fire detection. *Geo-spatial Information Science*, 28(2), 511-526.
> https://doi.org/10.1080/10095020.2024.2347922

## How to get this model
```bash
cd backend
curl -L -o models/wildfire-smoke.pt \
  https://huggingface.co/seawsurf/fire_yolo/resolve/main/weights/best.pt
```

## Verification
The file has been verified as safe to a limited extent in this development
environment:
- Its ZIP archive structure is normal (standard `torch.save`: `data.pkl` +
  tensor shards `data/N`), no suspicious entries.
- HuggingFace flags this file "caution" in its automated scan — but
  **official** checkpoints from Ultralytics itself (`yolov8n.pt`,
  `yolo26n.pt`, etc., which `ultralytics` auto-downloads on every transfer
  learning run) get the exact same "caution" label. So this is a common
  false positive for all ultralytics checkpoints (they contain custom
  classes, not just plain tensors), not a sign this specific file is
  unusually dangerous.

**Not yet verifiable in this session:** fully loading the model (`YOLO(path)`)
for a real inference test — this development sandbox blocks executing code
from a file freshly downloaded from the internet (a system-level safety
measure, applying to ANY downloaded model, not just ours). Run this test
yourself as a normal part of the regular dev loop:
```bash
cd backend
source venv/bin/activate   # or: bash scripts/setup_env.sh first if not done yet
python -c "from ultralytics import YOLO; m = YOLO('models/wildfire-smoke.pt'); print(m.names)"
uvicorn main:app --reload
# then test the /detect endpoint with curl -F "file=@sample.jpg" http://localhost:8000/detect
```

## Optional: further fine-tuning
The in-house training pipeline is still available if you want to continue
training this checkpoint with additional data later (e.g. Indonesian
wildfire photos) — see `train.py`, `evaluate.py`, `dataset.py`, and the
FASDD_CV dataset already fully downloaded at `data/raw/fasdd_cv/` (95,126
images, fully verified — see this README's git history for verification
details). Run `python -m ml.detect.train --model models/wildfire-smoke.pt`
to continue from this checkpoint instead of from COCO `yolov8n.pt`/`yolo26n.pt`.
