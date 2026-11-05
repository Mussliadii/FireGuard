"""Loads the trained risk model and predicts a fire-risk score.

Reuses backend/ml/risk/preprocess.PRODUCTION_FEATURE_ORDER as the single
source of truth for feature order, so this app and the training pipeline
can never silently drift out of sync (see that module's docstring for why
that bug class matters).
"""

import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.risk.preprocess import PRODUCTION_FEATURE_ORDER  # noqa: E402

MODEL_PATH = BACKEND_DIR / "models" / "risk_model.joblib"


@dataclass
class RiskInput:
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    wind_speed_kmh: float

    def as_feature_row(self) -> list[float]:
        values = {
            "Temperature": self.temperature_c,
            "RH": self.humidity_pct,
            "Rain": self.rainfall_mm,
            "Ws": self.wind_speed_kmh,
        }
        return [values[col] for col in PRODUCTION_FEATURE_ORDER]


def _rule_based_fallback(features: RiskInput) -> float:
    """Same heuristic as backend/routers/risk.py, used if the model file
    isn't present (e.g. a fresh checkout before `python -m ml.risk.train`).
    """
    score = 0.0
    score += max(0.0, (features.temperature_c - 25) / 20) * 0.35
    score += max(0.0, (40 - features.humidity_pct) / 40) * 0.35
    score += max(0.0, (5 - features.rainfall_mm) / 5) * 0.2
    score += min(features.wind_speed_kmh / 50, 1.0) * 0.1
    return min(max(score, 0.0), 1.0)


def _label(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def load_model():
    if not MODEL_PATH.exists():
        return None
    import joblib

    return joblib.load(MODEL_PATH)


def predict_risk(model, features: RiskInput) -> dict:
    if model is not None:
        score = float(model.predict_proba([features.as_feature_row()])[0][1])
        source = "trained"
    else:
        score = _rule_based_fallback(features)
        source = "rule-based-fallback"

    return {"risk_score": round(score, 3), "risk_label": _label(score), "model": source}
