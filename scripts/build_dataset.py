"""Rebuild `ames_housing.csv` from the Kaggle "House Prices" dataset.

Run only when the feature selection changes — the CSV is committed, so training
never needs network access:

    python scripts/build_dataset.py

The source has 81 columns; the app keeps 14 that a person can reason about and
fill into a form. `GarageType` is kept partly because its 81 missing values give
the pipeline's imputer something real to do.
"""

from pathlib import Path

import pandas as pd
from sklearn.datasets import fetch_openml

NUMERIC = [
    "OverallQual",
    "GrLivArea",
    "YearBuilt",
    "YearRemodAdd",
    "TotalBsmtSF",
    "GarageCars",
    "FullBath",
    "LotArea",
]
CATEGORICAL = [
    "Neighborhood",
    "HouseStyle",
    "ExterQual",
    "KitchenQual",
    "CentralAir",
    "GarageType",
]
TARGET = "SalePrice"

OUTPUT = Path(__file__).resolve().parent.parent / "ames_housing.csv"


def main() -> None:
    frame = fetch_openml(name="house_prices", as_frame=True).frame
    subset = frame[NUMERIC + CATEGORICAL + [TARGET]].copy()
    for column in NUMERIC + [TARGET]:
        subset[column] = pd.to_numeric(subset[column])

    subset.to_csv(OUTPUT, index=False)
    print(f"Wrote {OUTPUT.name}: {len(subset)} rows, {subset.shape[1]} columns")
    print(f"  missing values: {int(subset.isna().sum().sum())}")
    print(f"  {TARGET}: {subset[TARGET].min():,.0f} - {subset[TARGET].max():,.0f}")


if __name__ == "__main__":
    main()
