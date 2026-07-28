"""Render the diagrams embedded in the lab report.

    python scripts/build_report_figures.py

Writes PNGs to `report/figures/`. Uses plotly + kaleido, both already required
by the project, so no extra dependency.
"""

from pathlib import Path

import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "report" / "figures"

INK = "#0b0b0b"
MUTED = "#52514e"
SURFACE = "#fcfcfb"
FONT = "system-ui, -apple-system, Segoe UI, sans-serif"

PIPELINE_STAGES = [
    ("Ames Housing\nCSV", "#1a7f37"),
    ("Data\npreprocessing", "#2e9e4f"),
    ("Train / test\nsplit (80/20)", "#7a9b3a"),
    ("Model training\n(6 models)", "#b8860b"),
    ("Model\nevaluation", "#d47a1c"),
    ("Persist\nartifacts", "#e8702a"),
    ("FastAPI\nbackend", "#d8542a"),
    ("React\ninterface", "#c62828"),
]

PREPROCESS_ROWS = [
    ("8 numeric columns", "median impute → StandardScaler", "8 scaled columns", "#1a7f37"),
    ("6 categorical columns", "mode impute → OneHotEncoder", "49 indicator columns", "#b8860b"),
]


def _box(fig, x0, x1, y0, y1, text, color, text_color="#ffffff", size=12):
    fig.add_shape(
        type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
        line=dict(color=color, width=2), fillcolor=color, layer="below",
    )
    fig.add_annotation(
        x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=text, showarrow=False,
        font=dict(family=FONT, size=size, color=text_color), align="center",
    )


def pipeline_diagram() -> go.Figure:
    """Left-to-right flow of the whole project, one box per stage."""
    fig = go.Figure()
    width, gap = 1.0, 0.28
    for index, (label, color) in enumerate(PIPELINE_STAGES):
        x0 = index * (width + gap)
        _box(fig, x0, x0 + width, 0, 0.62, label, color)
        if index < len(PIPELINE_STAGES) - 1:
            fig.add_annotation(
                x=x0 + width + gap / 2, y=0.31, ax=x0 + width, ay=0.31,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=2,
                arrowcolor=MUTED, text="",
            )

    total = len(PIPELINE_STAGES) * (width + gap) - gap
    fig.update_layout(
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        margin=dict(l=10, r=10, t=10, b=10), height=150,
        xaxis=dict(visible=False, range=[-0.2, total + 0.2]),
        yaxis=dict(visible=False, range=[-0.12, 0.74]),
        showlegend=False,
    )
    return fig


def preprocessing_diagram() -> go.Figure:
    """How the two column types are transformed and recombined."""
    fig = go.Figure()
    for row, (source, transform, result, color) in enumerate(PREPROCESS_ROWS):
        y0 = 1.15 - row * 0.75
        y1 = y0 + 0.5
        _box(fig, 0.0, 2.3, y0, y1, source, color, size=12)
        _box(fig, 2.9, 6.2, y0, y1, transform, "#f2f3f2", INK, size=12)
        _box(fig, 6.8, 9.2, y0, y1, result, color, size=12)
        for ax0, x in ((2.3, 2.9), (6.2, 6.8)):
            fig.add_annotation(
                x=x, y=(y0 + y1) / 2, ax=ax0, ay=(y0 + y1) / 2,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor=MUTED, text="",
            )

    _box(fig, 9.8, 12.4, 0.55, 1.35, "57 model\ninput columns", "#2a78d6", size=12)
    for row in range(2):
        y = 1.4 - row * 0.75
        fig.add_annotation(
            x=9.8, y=0.95, ax=9.2, ay=y, xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor=MUTED, text="",
        )

    fig.update_layout(
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        margin=dict(l=10, r=10, t=10, b=10), height=230,
        xaxis=dict(visible=False, range=[-0.3, 12.7]),
        yaxis=dict(visible=False, range=[0.25, 1.75]),
        showlegend=False,
    )
    return fig


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for name, figure, width, height in [
        ("pipeline", pipeline_diagram(), 1500, 150),
        ("preprocessing", preprocessing_diagram(), 1400, 230),
    ]:
        path = FIGURES / f"{name}.png"
        figure.write_image(path, width=width, height=height, scale=2)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
