"""Build the editable Word lab report.

    python scripts/build_report_figures.py    # diagrams first (once)
    python scripts/make_report.py

Writes `report/ML_Lab_Report.docx`. Every metric is read from `artifacts/` at
build time, so re-running after a retrain refreshes the numbers rather than
leaving stale ones in the prose.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Run from anywhere: make `config` and the report modules importable.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from docx import Document
from docx.shared import Pt

import build_report as helpers
import report_content as content
import report_models as models
import report_results as results

OUTPUT = ROOT / "report" / "ML_Lab_Report.docx"

BODY = [
    content.introduction,
    content.objectives,
    content.problem_statement,
    content.dataset_description,
    content.requirements,
    models.models_used,
    results.methodology,
    results.preprocessing,
    results.model_training,
    results.model_evaluation,
    results.user_input,
    results.prediction,
    results.interpretability,
    results.user_interface,
    results.visualization,
    results.sample_output,
    results.deployment,
    results.advantages,
    results.limitations,
    results.future_work,
    results.result,
    results.conclusion,
]


def main() -> None:
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)

    content.cover_page(doc)
    content.table_of_contents(doc)
    for section in BODY:
        section(doc)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({size_kb:.0f} KB)")
    print(f"  sections:      {len(BODY)}")
    print(f"  models covered: {len(helpers.RANKING)}")


if __name__ == "__main__":
    main()
