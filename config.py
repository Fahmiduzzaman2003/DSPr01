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
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "BSP.csv"

ARTIFACTS = ROOT / "artifacts"
MODELS_DIR = ARTIFACTS / "models"
METRICS_FILE = ARTIFACTS / "metrics.json"
SCHEMA_FILE = ARTIFACTS / "schema.json"
PREDICTIONS_FILE = ARTIFACTS / "predictions.json"

TARGET = "hsc_result"
TARGET_LABEL = "HSC result"
DROP_COLUMNS = ["date"]

# Human-readable form labels; anything missing falls back to a title-cased column.
FEATURE_LABELS = {
    "gender": "Gender",
    "age": "Age",
    "address": "Home area",
    "famsize": "Family size (LE3 = 3 or fewer, GT3 = more than 3)",
    "Pstatus": "Parents living together or apart",
    "M_Edu": "Mother's education level (0-4)",
    "F_Edu": "Father's education level (0-4)",
    "M_Job": "Mother's job",
    "F_Job": "Father's job",
    "relationship": "In a relationship",
    "smoker": "Smoker",
    "tuition_fee": "Yearly tuition fee",
    "time_friends": "Time spent with friends (1-5)",
    "ssc_result": "SSC result",
}

TEST_SIZE = 0.2
RANDOM_STATE = 42


def build_models() -> dict:
    """The estimators being compared (fresh instances each call).

    SVR relies on the scaling already done by the numeric transformer — an RBF
    kernel is distance-based, so unscaled features would let `tuition_fee`
    (~71,000) drown out everything else.

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
        "Support Vector Regression": SVR(kernel="rbf", C=1.0, epsilon=0.1),
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
