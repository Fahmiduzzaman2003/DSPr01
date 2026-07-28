"""Shared configuration: paths, dataset schema and the model zoo.

Kept separate from `train.py` / `main.py` so the training script and the API
always agree on model names, artifact locations and the feature contract.
"""

from pathlib import Path

from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).parent
# Ames Housing (Kaggle "House Prices"), fetched via sklearn's OpenML mirror and
# cut down to 14 interpretable columns. See scripts/build_dataset.py.
DATA_FILE = ROOT / "ames_housing.csv"

ARTIFACTS = ROOT / "artifacts"
MODELS_DIR = ARTIFACTS / "models"
METRICS_FILE = ARTIFACTS / "metrics.json"
SCHEMA_FILE = ARTIFACTS / "schema.json"
PREDICTIONS_FILE = ARTIFACTS / "predictions.json"
IMPORTANCES_FILE = ARTIFACTS / "importances.json"

APP_TITLE = "House Price Predictor"
APP_SUBTITLE = (
    "Ames Housing (Kaggle) — {n} regression models predict a home's sale price "
    "from 14 of its characteristics."
)

TARGET = "SalePrice"
TARGET_LABEL = "sale price"
DROP_COLUMNS = []

# How the predicted value and the error metrics are rendered in the UI.
TARGET_PREFIX = "$"
TARGET_DECIMALS = 0

# Human-readable form labels; anything missing falls back to a title-cased column.
FEATURE_LABELS = {
    "OverallQual": "Overall quality (1-10)",
    "GrLivArea": "Above-ground living area (sq ft)",
    "YearBuilt": "Year built",
    "YearRemodAdd": "Year remodelled",
    "TotalBsmtSF": "Basement area (sq ft)",
    "GarageCars": "Garage capacity (cars)",
    "FullBath": "Full bathrooms",
    "LotArea": "Lot size (sq ft)",
    "Neighborhood": "Neighborhood",
    "HouseStyle": "House style",
    "ExterQual": "Exterior quality (Ex/Gd/TA/Fa)",
    "KitchenQual": "Kitchen quality (Ex/Gd/TA/Fa)",
    "CentralAir": "Central air conditioning",
    "GarageType": "Garage type",
}

TEST_SIZE = 0.2
RANDOM_STATE = 42


def build_models() -> dict:
    """The estimators being compared (fresh instances each call).

    SVR relies on the feature scaling already done by the numeric transformer —
    an RBF kernel is distance-based, so unscaled `LotArea` would drown out
    everything else. It also needs the *target* scaled: `C` and `epsilon` are in
    target units, and against a sale price in the hundreds of thousands the
    defaults leave every point inside the epsilon tube. Untransformed it scores
    R² -0.02 (worse than predicting the mean); wrapped, 0.85.

    The ensembles deliberately keep their original three base learners so the
    figures reported for them stay comparable across runs.
    """
    linear = LinearRegression()
    forest = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)
    boosting = GradientBoostingRegressor(n_estimators=100, random_state=RANDOM_STATE)
    base = [("lr", linear), ("rf", forest), ("gb", boosting)]

    return {
        "Linear Regression": linear,
        "Random Forest": forest,
        "Gradient Boosting": boosting,
        "Support Vector Regression": TransformedTargetRegressor(
            regressor=SVR(kernel="rbf", C=1.0, epsilon=0.1),
            transformer=StandardScaler(),
        ),
        "Voting Ensemble": VotingRegressor(estimators=base),
        "Stacking Ensemble": StackingRegressor(
            estimators=base, final_estimator=Ridge()
        ),
    }


def slugify(model_name: str) -> str:
    """Filename-safe key for a model name (`Random Forest` -> `random_forest`)."""
    return model_name.lower().replace(" ", "_")


# Metrics shown in the UI. `lower_is_better` drives ranking and chart emphasis.
METRICS = {
    "MAE": {"label": "Mean Absolute Error", "lower_is_better": True},
    "MSE": {"label": "Mean Squared Error", "lower_is_better": True},
    "RMSE": {"label": "Root Mean Squared Error", "lower_is_better": True},
    "R2": {"label": "R² Score", "lower_is_better": False},
}

# Metric used to pick the headline "best" model.
PRIMARY_METRIC = "R2"

# Traffic-light ramp, best -> worst. Every step clears 3:1 contrast against a
# light surface. Served to the frontend so both sides share one source of truth.
RANK_RAMP = ["#1a7f37", "#2e9e4f", "#b8860b", "#e8702a", "#c62828"]
