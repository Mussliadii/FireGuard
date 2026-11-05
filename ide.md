I want to tackle the 2026 wildfire issue — I want to build software that can help.

## Project Plan: FireGuard AI (working title)

Track: Green Planet — Sustainability & Environmental Intelligence

### Problem Statement
Wildfires are hard to detect early and predict, so mitigation response is
often too late and environmental/economic losses grow larger. Residents
near at-risk areas also have no quick way to know when to be on alert.

### Solution: Integrated dashboard + automatic alert system
1. **Early detection** — upload an image/video/webcam feed, a CV model
   (ready-made YOLO26n, trained on the FASDD_CV dataset) detects smoke/fire
   + confidence score.
2. **Fire risk prediction** — input a location, pull weather data
   (temperature, humidity, rainfall, wind) via API, an ML model
   (XGBoost/Random Forest) outputs a risk score (Low/Medium/High) per
   area/time.
3. **Real-time monitoring** — pull active hotspot data from the NASA FIRMS
   API, show it on an interactive map.
4. **Action/Alert** — when a "Dangerous" status is detected (from module
   1/2/3), the system finds registered users within a certain radius (e.g.
   10km, haversine distance) of the location and sends a **Web Push
   Notification**.

### Deployment Architecture (Vercel)
Vercel isn't suited to running heavy ML models (YOLOv8/torch) directly, so
it's split into 2 layers:

- **Frontend + orchestration — Vercel (Next.js)**
  - Dashboard UI, interactive map (Leaflet/Mapbox)
  - API routes: user + location registration, web push subscription
  - Vercel Cron Job: periodically polls the inference backend + FIRMS/weather
    APIs, computes radius, triggers push notifications (via `web-push` +
    VAPID keys)
  - Database: Supabase (Postgres) — stores users, locations, push subscriptions
- **Inference backend — HuggingFace Spaces / Render (FastAPI)**
  - Image detection endpoint (YOLOv8)
  - Risk prediction endpoint (XGBoost/Random Forest)
  - Called by Vercel API routes over HTTP

### Tech Stack
- Next.js (React) + Tailwind — frontend, deployed on Vercel
- Vercel Cron Jobs + Vercel Postgres/Supabase — orchestration & user data
- `web-push` (VAPID) — Web Push Notification
- FastAPI + Python (YOLOv8, scikit-learn/XGBoost) — inference backend,
  deployed on HuggingFace Spaces/Render
- Leaflet/Mapbox GL — interactive map
- NASA FIRMS API (hotspots), Open-Meteo/BMKG API (weather)

### Status
- [x] Set up repo structure (separate Next.js frontend + FastAPI backend)
- [x] Found & verified the detection dataset (switched to **FASDD_CV**, 95k
      YOLO-format images, downloadable directly with no account needed — see
      `backend/ml/detect/README.md`)
- [x] Found, downloaded, & cleaned the risk dataset (UCI Algerian Forest
      Fires) — see `backend/ml/risk/README.md`
- [x] Unit tests for data cleaning (`backend/tests/test_preprocess.py`, 4/4 pass)
- [x] Wrote the risk training pipeline (raw vs FWI ablation, 3 models, CV) —
      `backend/ml/risk/train.py`
- [x] Ran real risk model training — XGBoost, test F1 **0.963**, ROC-AUC
      **0.998** (see table in the main README). End-to-end `/predict-risk`
      endpoint test passed 3/3.
- [x] Wrote the YOLOv8 detection training pipeline —
      `backend/ml/detect/train.py`
- [x] Downloaded the FASDD_CV dataset (95,126 images, fully verified: image
      count matches label count per split, valid YOLO label format)
- [x] Found & fixed a relative-path resolution bug in ultralytics (see
      `backend/ml/detect/dataset.py`), proven with a 1-epoch CPU smoke test
      (20 images) that successfully saved a checkpoint
- [x] **Decision:** use the ready-made `seawsurf/fire_yolo` checkpoint
      (YOLO26n, trained on the same FASDD_CV dataset, mAP50 0.774, CC BY 4.0)
      as the production model — not training from scratch, since there's no
      local GPU. Already downloaded to `backend/models/wildfire-smoke.pt`.
      The in-house training pipeline remains available for further
      fine-tuning later.
- [ ] **Not yet verified**: real inference from the model — this dev sandbox
      blocks executing a freshly downloaded model file (a safety policy).
      Needs manual testing: `uvicorn main:app --reload` then try the
      `/detect` endpoint with a real image.
- [x] Upgraded frontend dependencies to safe versions (Next 14→16, React
      18→19) — the old versions had 1 critical + 1 high vulnerability in
      Next.js; now 0 vulnerabilities. `next lint` was removed in Next 16,
      replaced with a manual ESLint flat config (`eslint.config.mjs`).
- [x] Built the real-time monitoring module (map + FIRMS) —
      `components/Map.tsx` fetches from `/api/hotspots`, falls back to
      sample data if `NASA_FIRMS_MAP_KEY` isn't set
- [x] Built the image detection form (`DetectForm.tsx`, upload + bounding
      box overlay via canvas) and the risk prediction form (`RiskForm.tsx`,
      auto-fetch weather from Open-Meteo) — proxied through Next.js API
      routes
- [x] Built the user registration system + location opt-in + push subscribe
      (`AlertSignup.tsx` + API route)
- [x] Built the radius alert cron job + push sending (logic is in place, the
      danger-point source is still a placeholder)
- [x] **End-to-end integration verified for real**: `npm run build` &
      `npm run lint` clean (0 errors/warnings), dev server runs, the
      `/api/predict-risk` endpoint tested through the full proxy chain
      (frontend → Next API route → FastAPI backend → real XGBoost model)
      with correct results for both high- and low-risk cases. The
      `/api/detect` endpoint couldn't be tested end-to-end in this sandbox
      (same as before — blocked from loading the YOLO model); needs manual
      testing by the user.
- [x] Translated all project writing (code comments, docs, UI text) to
      English, and redesigned the website with a more professional layout
      (design-system CSS, header/footer, reusable styling instead of inline
      styles)
- [ ] Deploy to Vercel (frontend) + HuggingFace Spaces/Render (backend)
- [ ] `git init` + push to a public GitHub repo (required for submission)
- [ ] Full README + screenshot/demo GIF
