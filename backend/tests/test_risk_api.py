"""End-to-end smoke test for /predict-risk against the actual trained model.

Skipped if models/risk_model.joblib hasn't been produced yet (run
`python -m ml.risk.train` first) — this is an integration check on top of
the fallback-vs-trained branch already covered implicitly by routers/risk.py.

Run: python3 -m unittest tests.test_risk_api -v
"""

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from routers.risk import MODEL_PATH

HOT_DRY_WINDY = {
    "lat": -2.5,
    "lon": 113.0,
    "temperature_c": 34.0,
    "humidity_pct": 35.0,
    "rainfall_mm": 0.0,
    "wind_speed_kmh": 20.0,
}

COOL_HUMID_RAINY = {
    "lat": -2.5,
    "lon": 113.0,
    "temperature_c": 24.0,
    "humidity_pct": 85.0,
    "rainfall_mm": 10.0,
    "wind_speed_kmh": 5.0,
}


class RiskApiTests(unittest.TestCase):
    def setUp(self):
        if not Path(MODEL_PATH).exists():
            self.skipTest(f"{MODEL_PATH} not present — run `python -m ml.risk.train` first")
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_hot_dry_windy_scores_high_risk(self):
        response = self.client.post("/predict-risk", json=HOT_DRY_WINDY)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["model"], "trained")
        self.assertGreater(body["risk_score"], 0.5)
        self.assertEqual(body["risk_label"], "high")

    def test_cool_humid_rainy_scores_low_risk(self):
        response = self.client.post("/predict-risk", json=COOL_HUMID_RAINY)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertLess(body["risk_score"], 0.5)
        self.assertEqual(body["risk_label"], "low")


if __name__ == "__main__":
    unittest.main()
