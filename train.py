"""Train every model from the notebook and persist artifacts for the UI.

Run once before launching the app (or whenever `BSP.csv` changes):

    python train.py

Writes to `artifacts/`:
    models/<slug>.joblib   fitted end-to-end pipeline (preprocessing + estimator)
    metrics.json           MAE / MSE / RMSE / R2 per model on the hold-out split
    predictions.json       y_true + per-model y_pred, for the diagnostic plots
    schema.json            feature contract used to generate the input form
"""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import config


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(config.DATA_FILE)
    df = df.drop(columns=[c for c in config.DROP_COLUMNS if c in df.columns])
    return df.drop(columns=[config.TARGET]), df[config.TARGET]


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    # `.tolist()` matters: pandas returns a string-dtype Index that sklearn's
    # column selector cannot interpret.
    numeric = X.select_dtypes(include=np.number).columns.tolist()
    categorical = X.select_dtypes(exclude=np.number).columns.tolist()

    numeric_steps = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical_steps = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [("num", numeric_steps, numeric), ("cat", categorical_steps, categorical)]
    )


def evaluate(y_true, y_pred) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MSE": mse,
        "RMSE": float(np.sqrt(mse)),
        "R2": float(r2_score(y_true, y_pred)),
    }


def describe_features(X: pd.DataFrame) -> list[dict]:
    """Feature contract the UI turns into input widgets."""
    schema = []
    for column in X.columns:
        series = X[column]
        if pd.api.types.is_numeric_dtype(series):
            is_integer = bool(pd.api.types.is_integer_dtype(series))
            median = float(series.median())
            schema.append(
                {
                    "name": column,
                    "kind": "number",
                    "minimum": float(series.min()),
                    "maximum": float(series.max()),
                    "default": round(median) if is_integer else round(median, 2),
                    "integer": is_integer,
                }
            )
        else:
            choices = sorted(series.dropna().astype(str).unique().tolist())
            schema.append(
                {
                    "name": column,
                    "kind": "category",
                    "choices": choices,
                    "default": str(series.mode().iloc[0]),
                }
            )
    return schema


def main() -> None:
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )
    print(f"Loaded {len(X)} rows | train {len(X_train)} | test {len(X_test)}")

    metrics: dict[str, dict[str, float]] = {}
    predictions: dict[str, list[float]] = {}

    for name, estimator in config.build_models().items():
        pipeline = Pipeline(
            [("preprocessor", build_preprocessor(X)), ("model", estimator)]
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        metrics[name] = evaluate(y_test, y_pred)
        predictions[name] = [float(v) for v in y_pred]
        # compress=3 takes the five pipelines from 68 MB to ~14 MB, small enough
        # to ship with the Space so it never has to train during startup.
        joblib.dump(
            pipeline, config.MODELS_DIR / f"{config.slugify(name)}.joblib", compress=3
        )
        print(f"  {name:<20} R2={metrics[name]['R2']:.4f}  MAE={metrics[name]['MAE']:.4f}")

    config.METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    config.PREDICTIONS_FILE.write_text(
        json.dumps(
            {"y_true": [float(v) for v in y_test], "y_pred": predictions}, indent=2
        ),
        encoding="utf-8",
    )
    config.SCHEMA_FILE.write_text(
        json.dumps(
            {"target": config.TARGET, "features": describe_features(X)}, indent=2
        ),
        encoding="utf-8",
    )
    print(f"\nArtifacts written to {config.ARTIFACTS}")


if __name__ == "__main__":
    main()
