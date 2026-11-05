# Dataset & methodology: fire risk prediction

**Source:** [UCI Algerian Forest Fires Dataset](https://archive.ics.uci.edu/dataset/547/algerian+forest+fires+dataset)
(244 daily observations, 2 regions in Algeria, June–September 2012).
**Citation:** Abid, Faroudja. (2019). Algerian Forest Fires Dataset. UCI
Machine Learning Repository. https://doi.org/10.24432/C5KW4N

## Data cleaning
The raw CSV isn't a clean table — see `preprocess.py` for details, in short:
- The file contains 2 per-region blocks, each with its own title line and
  repeated header (not a regular `region` column) → parsed into an explicit
  `region` column.
- Column names carry stray whitespace (`" RH"`, `"Rain "`, etc.) → trimmed.
- **One malformed row** was found by validating column count per row
  (14/07/2012, Sidi-Bel Abbes region): a missing comma merges DC and ISI into
  a single token (`"14.6 9"`). Fixed explicitly rather than dropped, since
  the value can be reconstructed with certainty from the token's position.
- All of the above steps have unit tests in `tests/test_preprocess.py`,
  including an integration check against the real dataset file (244 rows,
  label split 138 fire / 106 not fire — matches the UCI documentation).

## Ablation: raw features vs. Fire Weather Index (FWI) features
The dataset provides 2 feature groups:
- **raw** — Temperature, RH, Ws, Rain: obtainable instantly from a weather
  API (Open-Meteo) with no history required.
- **full** — raw + FFMC, DMC, DC, ISI, BUI, FWI: Canadian Fire Weather Index
  System indices. These indices are **cumulative** (computed recursively from
  prior days' weather), so they can't be obtained from a single weather API
  call — implementing the FWI formulas separately would be required.

`train.py` trains both feature sets separately and compares their test-set
results. The production model (used by `backend/routers/risk.py`) uses the
**raw** feature set, with the accuracy trade-off documented explicitly in
`data/processed/risk_model_metrics.json` — not silently assumed away.

## Model & evaluation
- 3 algorithms compared per feature set: Logistic Regression (interpretable
  baseline), Random Forest, XGBoost.
- Small grid per model (the dataset is only 244 rows — a large grid would
  just overfit the CV folds rather than improve generalization).
- Stratified 5-fold CV on the training split (80%) for model + hyperparameter
  selection; a single held-out test evaluation (20%), stratified, with a
  fixed `random_state=42` for reproducibility.
- Metrics: accuracy, precision, recall, F1, ROC-AUC + confusion matrix plot.

## Running it
```bash
cd backend
python3 scripts/download_risk_dataset.py   # already run, see data/raw/
python -m ml.risk.train
```
Output: `models/risk_model.joblib` (used by the API), `data/processed/risk_model_metrics.json`,
`data/processed/confusion_matrix_{raw,full}.png`.

## Limitations & next steps
- 244 rows from Algeria, not Indonesia — good for proving out the
  methodology (clean pipeline, ablation, sound model selection), but for
  accuracy that's relevant to the Kalimantan/Sumatra context, this should
  ideally be re-fine-tuned with historical NASA FIRMS hotspot data
  (Indonesia) + historical Open-Meteo weather. Documented as future work in
  the main README, not claimed as already done.
