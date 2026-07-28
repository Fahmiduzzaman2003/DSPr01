"""FastAPI backend for the HSC result predictor.

Serves the model metadata, per-model predictions and diagnostic data that the
React frontend renders. Run locally with:

    uvicorn main:app --reload --port 8000

Artifacts come from `train.py` and must exist before start — building them here
would delay the port bind and trip a platform health check.
"""

from __future__ import annotations

import json
import os

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config

app = FastAPI(title="HSC Result Predictor API", version="1.0.0")

# The frontend is deployed to a different origin, so the browser needs CORS.
# Set ALLOWED_ORIGINS to a comma-separated list to lock this down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Artifacts ---------------------------------------------------------------
def _load_json(path):
    if not path.exists():
        raise RuntimeError(f"{path.name} missing — run `python train.py` first.")
    return json.loads(path.read_text(encoding="utf-8"))


METRICS: dict[str, dict[str, float]] = _load_json(config.METRICS_FILE)
HOLDOUT: dict = _load_json(config.PREDICTIONS_FILE)
IMPORTANCES: dict[str, list[dict]] = _load_json(config.IMPORTANCES_FILE)
FEATURES: list[dict] = _load_json(config.SCHEMA_FILE)["features"]

# Models ranked best to worst on the primary metric — drives every rank colour.
MODEL_RANKING: list[str] = sorted(
    METRICS, key=lambda name: METRICS[name][config.PRIMARY_METRIC], reverse=True
)
BEST_MODEL = MODEL_RANKING[0]

MODELS = {
    name: joblib.load(config.MODELS_DIR / f"{config.slugify(name)}.joblib")
    for name in MODEL_RANKING
}


# --- Schemas -----------------------------------------------------------------
class PredictRequest(BaseModel):
    values: dict[str, object]


# --- Routes ------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "models": len(MODELS)}


@app.get("/api/config")
def get_config() -> dict:
    """Everything the UI needs to render before the user does anything."""
    return {
        "targetLabel": config.TARGET_LABEL,
        "testSizePercent": int(config.TEST_SIZE * 100),
        "features": [
            {**feature, "label": config.FEATURE_LABELS.get(feature["name"], feature["name"])}
            for feature in FEATURES
        ],
        "modelRanking": MODEL_RANKING,
        "bestModel": BEST_MODEL,
        "metrics": METRICS,
        "metricSpecs": config.METRICS,
        "primaryMetric": config.PRIMARY_METRIC,
        "rankColors": config.RANK_RAMP,
    }


@app.post("/api/predict")
def predict(request: PredictRequest) -> dict:
    """Score one student with every model, returned best-model-first."""
    missing = [f["name"] for f in FEATURES if f["name"] not in request.values]
    if missing:
        raise HTTPException(400, f"Missing features: {', '.join(missing)}")

    row = pd.DataFrame([{f["name"]: request.values[f["name"]] for f in FEATURES}])
    for feature in FEATURES:
        if feature["kind"] == "number":
            row[feature["name"]] = pd.to_numeric(row[feature["name"]], errors="coerce")

    predictions = [
        {
            "model": name,
            "rank": index + 1,
            "value": float(MODELS[name].predict(row)[0]),
            "r2": METRICS[name]["R2"],
        }
        for index, name in enumerate(MODEL_RANKING)
    ]
    values = [p["value"] for p in predictions]
    return {
        "predictions": predictions,
        "bestModel": BEST_MODEL,
        "headline": predictions[0]["value"],
        "mean": float(np.mean(values)),
    }


@app.get("/api/diagnostics/{model_name}")
def diagnostics(model_name: str) -> dict:
    """Hold-out scatter points and a binned residual histogram for one model."""
    if model_name not in HOLDOUT["y_pred"]:
        raise HTTPException(404, f"Unknown model: {model_name}")

    y_true = np.asarray(HOLDOUT["y_true"], dtype=float)
    y_pred = np.asarray(HOLDOUT["y_pred"][model_name], dtype=float)
    residuals = y_pred - y_true

    # Binned server-side so the client just draws bars.
    counts, edges = np.histogram(residuals, bins=40)
    centers = (edges[:-1] + edges[1:]) / 2

    return {
        "model": model_name,
        "rank": MODEL_RANKING.index(model_name) + 1,
        "points": [
            {"actual": float(a), "predicted": float(p)} for a, p in zip(y_true, y_pred)
        ],
        "residualBins": [
            {"error": float(c), "count": int(n)} for c, n in zip(centers, counts)
        ],
        "residualMean": float(residuals.mean()),
        "residualStd": float(residuals.std()),
    }


@app.get("/api/importance/{model_name}")
def importance(model_name: str) -> dict:
    """Permutation importance for one model, most important feature first."""
    if model_name not in IMPORTANCES:
        raise HTTPException(404, f"Unknown model: {model_name}")

    rows = IMPORTANCES[model_name]
    # Negative scores mean shuffling the column *helped* — noise, not signal.
    total = sum(max(row["importance"], 0.0) for row in rows) or 1.0

    features = [
        {
            **row,
            # The form labels carry parenthetical hints that are too long for an
            # axis, so trim to the part before the bracket.
            "label": config.FEATURE_LABELS.get(row["feature"], row["feature"]).split(" (")[0],
            "share": max(row["importance"], 0.0) / total * 100,
        }
        for row in rows
    ]
    return {
        "model": model_name,
        "rank": MODEL_RANKING.index(model_name) + 1,
        "features": features,
        "metric": "R² lost when the column is shuffled",
    }


if __name__ == "__main__":
    import uvicorn

    # Render/Railway inject PORT; default matches the frontend's dev proxy.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
