from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from ml.risk.preprocess import PRODUCTION_FEATURE_ORDER

router = APIRouter()

MODEL_PATH = Path(__file__).parent.parent / "models" / "risk_model.joblib"

_model = None


class WeatherFeatures(BaseModel):
    lat: float
    lon: float
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float
    wind_speed_kmh: float

    def as_feature_row(self) -> list[float]:
        """Builds the feature vector in PRODUCTION_FEATURE_ORDER, so training
        and inference can never silently drift out of sync on column order.
        """
        values = {
            "Temperature": self.temperature_c,
            "RH": self.humidity_pct,
            "Rain": self.rainfall_mm,
            "Ws": self.wind_speed_kmh,
        }
        return [values[col] for col in PRODUCTION_FEATURE_ORDER]


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        import joblib

        _model = joblib.load(MODEL_PATH)
    return _model


def _rule_based_fallback(f: WeatherFeatures) -> float:
    """0-1 score from a simple heuristic, used until a model has been trained.

    TODO: replace with an XGBoost/Random Forest model trained on historical
    fire + weather data (e.g. a NASA FIRMS + Open-Meteo combination).
    """
    score = 0.0
    score += max(0.0, (f.temperature_c - 25) / 20) * 0.35
    score += max(0.0, (40 - f.humidity_pct) / 40) * 0.35
    score += max(0.0, (5 - f.rainfall_mm) / 5) * 0.2
    score += min(f.wind_speed_kmh / 50, 1.0) * 0.1
    return min(max(score, 0.0), 1.0)


def _label(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


@router.post("")
def predict_risk(features: WeatherFeatures):
    model = _load_model()

    if model is not None:
        score = float(model.predict_proba([features.as_feature_row()])[0][1])
    else:
        score = _rule_based_fallback(features)

    return {
        "risk_score": round(score, 3),
        "risk_label": _label(score),
        "model": "trained" if model is not None else "rule-based-fallback",
    }
