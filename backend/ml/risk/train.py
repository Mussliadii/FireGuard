"""Train and compare fire-risk classifiers on the Algerian Forest Fires Dataset.

Two feature sets are compared as an ablation study:

- ``raw``: Temperature, RH, Rain, Ws — everything the production API can get
  instantly from a weather API (Open-Meteo), with no history required.
- ``full``: raw + the Canadian FWI System indices (FFMC, DMC, DC, ISI, BUI,
  FWI) already present in the dataset. These indices are NOT a weather-API
  call away in production: they are cumulative, computed day-over-day from
  prior weather, so using them live would require implementing the FWI
  recursion ourselves. Comparing the two feature sets quantifies what that
  engineering work would actually be worth in accuracy.

For each feature set, three model families are compared with stratified
5-fold cross-validation on the training split, a small hyperparameter grid
per model, selection by mean CV F1, then a single held-out test evaluation
of the winner. With only 244 rows, a large grid would just overfit the CV
folds, so the grids below are deliberately small.

Usage:
    python -m ml.risk.train
"""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from ml.risk.preprocess import (
    ALL_FEATURE_COLUMNS,
    LABEL_COLUMN,
    PRODUCTION_FEATURE_ORDER,
    load_clean_dataframe,
)

RAW_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / (
    "Algerian_forest_fires_dataset_UPDATE.csv"
)
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent.parent.parent / "models"
RANDOM_STATE = 42

MODEL_GRIDS = {
    "logistic_regression": (
        Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))]),
        {"clf__C": [0.1, 1.0, 10.0]},
    ),
    "random_forest": (
        RandomForestClassifier(random_state=RANDOM_STATE),
        {"n_estimators": [100, 300], "max_depth": [3, 5, None]},
    ),
    "xgboost": (
        XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss"),
        {"n_estimators": [100, 200], "max_depth": [2, 3, 4], "learning_rate": [0.05, 0.1]},
    ),
}


def _evaluate_on_test(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
    }


def _run_feature_set(name: str, X, y, cv) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    best_name, best_estimator, best_cv_f1 = None, None, -1.0
    candidate_cv_scores = {}

    for model_name, (estimator, grid) in MODEL_GRIDS.items():
        search = GridSearchCV(estimator, grid, scoring="f1", cv=cv, n_jobs=-1)
        search.fit(X_train, y_train)
        candidate_cv_scores[model_name] = round(search.best_score_, 4)
        if search.best_score_ > best_cv_f1:
            best_cv_f1 = search.best_score_
            best_name = model_name
            best_estimator = search.best_estimator_

    test_metrics = _evaluate_on_test(best_estimator, X_test, y_test)

    cm_path = PROCESSED_DIR / f"confusion_matrix_{name}.png"
    ConfusionMatrixDisplay.from_estimator(
        best_estimator, X_test, y_test, display_labels=["not fire", "fire"]
    )
    plt.title(f"Confusion Matrix — {name} features ({best_name})")
    plt.savefig(cm_path, bbox_inches="tight")
    plt.close()

    return {
        "feature_set": name,
        "features": list(X.columns),
        "cv_f1_by_model": candidate_cv_scores,
        "best_model": best_name,
        "best_cv_f1": round(best_cv_f1, 4),
        "test_metrics": test_metrics,
        "fitted_estimator": best_estimator,
        "confusion_matrix_path": str(cm_path),
    }


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = load_clean_dataframe(RAW_DATA_PATH)
    df.to_csv(PROCESSED_DIR / "clean_fires.csv", index=False)
    y = df[LABEL_COLUMN]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    results["raw"] = _run_feature_set("raw", df[PRODUCTION_FEATURE_ORDER], y, cv)
    results["full"] = _run_feature_set("full", df[ALL_FEATURE_COLUMNS], y, cv)

    # Production model: the "raw" feature set, since it's the only one that
    # can be satisfied directly from Open-Meteo without recomputing the FWI System.
    production_model = results["raw"]["fitted_estimator"]
    joblib.dump(production_model, MODEL_DIR / "risk_model.joblib")

    summary = {
        name: {k: v for k, v in r.items() if k != "fitted_estimator"}
        for name, r in results.items()
    }
    with open(PROCESSED_DIR / "risk_model_metrics.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(
        f"\nProduction model saved: {MODEL_DIR / 'risk_model.joblib'} "
        f"({results['raw']['best_model']}, test F1={results['raw']['test_metrics']['f1']})"
    )
    print(
        "Accuracy cost of NOT using FWI indices in production: "
        f"{results['full']['test_metrics']['f1']} (full) vs "
        f"{results['raw']['test_metrics']['f1']} (raw) F1."
    )


if __name__ == "__main__":
    main()
