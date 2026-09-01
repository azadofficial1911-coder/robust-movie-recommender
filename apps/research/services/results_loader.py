"""Loads real Week 6 defence/evaluation results for the Django presentation
layer.

This module only reads files already produced by the research scripts
(experiments/apply_defence.py, evaluate_defence_effect.py,
evaluate_recommender_metrics.py, build_experiment_results.py) -- it never
calculates a metric itself and never invents a value. If a results file
does not exist yet, the corresponding loader returns None (or an empty
list), and the view/template falls back to the existing "pending"
presentation.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]

RESULTS_DIR = BASE_DIR / "results"
TABLES_DIR = RESULTS_DIR / "tables"

EXPERIMENT_RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"
DEFENCE_SUMMARY_PATH = TABLES_DIR / "defence_summary_pilot.csv"

CONDITION_LABELS = {
    "clean": "Clean",
    "random": "Random Push (Attacked)",
    "random_defended": "Random Push (Defended)",
    "average": "Average Push (Attacked)",
    "average_defended": "Average Push (Defended)",
}

CONDITION_ORDER = ["clean", "random", "random_defended", "average", "average_defended"]

# Static image paths for {% static %}, matching static/images/research/
RESULT_FIGURES = [
    {
        "file": "images/research/clean_attacked_defended.png",
        "title": "Clean vs Attacked vs Defended -- RMSE / MAE",
    },
    {
        "file": "images/research/target_rank_comparison.png",
        "title": "Target Movie Rank -- Clean vs Attacked vs Defended",
    },
    {
        "file": "images/research/target_hit_rate.png",
        "title": "Target Hit Rate @10 -- Clean vs Attacked vs Defended",
    },
    {
        "file": "images/research/detection_metrics.png",
        "title": "Detection Performance",
    },
    {
        "file": "images/research/confusion_matrix.png",
        "title": "Detection Confusion Matrix",
    },
]


def _read_csv_safely(path: Path) -> pd.DataFrame | None:
    """Return the CSV as a DataFrame, or None if it doesn't exist or is empty."""
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return None
    return df if not df.empty else None


def load_defence_summary() -> list[dict] | None:
    """Return one row per attack scenario: users/ratings before & after,
    defence method, suspicious profiles detected."""

    df = _read_csv_safely(DEFENCE_SUMMARY_PATH)
    if df is None:
        return None
    return df.to_dict(orient="records")


def load_experiment_results() -> list[dict] | None:
    """Return one row per condition (clean, random, random_defended,
    average, average_defended) from the real master results file, in a
    fixed display order with a human-readable label attached."""

    df = _read_csv_safely(EXPERIMENT_RESULTS_PATH)
    if df is None:
        return None

    df = df.set_index("condition")
    rows = []
    for condition in CONDITION_ORDER:
        if condition not in df.index:
            continue
        row = df.loc[condition].to_dict()
        row["condition"] = condition
        row["condition_label"] = CONDITION_LABELS.get(condition, condition)
        rows.append(row)

    return rows or None


def load_result_figures() -> list[dict]:
    """Return the figure list for the template -- only entries whose
    underlying file actually exists on disk are included."""

    static_root = BASE_DIR / "static"
    return [fig for fig in RESULT_FIGURES if (static_root / fig["file"]).exists()]
