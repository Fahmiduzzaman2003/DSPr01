"""Generate the ydata-profiling EDA report served by the app's EDA tab.

Writes a self-contained HTML file to `frontend/public/eda.html`, which Vite
copies into `dist/` verbatim — so the report is a static asset with no runtime
dependency on ydata-profiling.

Run only when the dataset changes:

    python scripts/build_profile.py

ydata-profiling requires `pandas<3.0`, so it cannot be installed alongside the
app's own pandas 3. Build it in a throwaway environment:

    python -m venv edaenv
    edaenv/Scripts/pip install "pandas==2.3.3" ydata-profiling
    edaenv/Scripts/python scripts/build_profile.py
"""

from pathlib import Path

import pandas as pd
from ydata_profiling import ProfileReport

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "ames_housing.csv"
OUTPUT = ROOT / "frontend" / "public" / "eda.html"


def main() -> None:
    frame = pd.read_csv(DATA_FILE)
    report = ProfileReport(
        frame,
        title="Ames Housing — Exploratory Data Analysis",
        explorative=True,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report.to_file(OUTPUT)
    size_mb = OUTPUT.stat().st_size / 1024**2
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({size_mb:.1f} MB) from {len(frame)} rows")


if __name__ == "__main__":
    main()
