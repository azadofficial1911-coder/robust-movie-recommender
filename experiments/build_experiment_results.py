"""Build the master Week 6 experiment_results.csv from the real pilot
outputs produced by:

    experiments/evaluate_recommender_metrics.py  (rmse, mae)
    experiments/evaluate_defence_effect.py        (target_rank, target_score, hit_rate)
    experiments/run_detection.py                  (detection precision/recall/f1/fpr)   [Azad]

One row is written per condition (clean, random, random_defended,
average, average_defended). Detection metrics only apply to attacked and
defended conditions (there is no detector decision to score for clean
data), so those columns are left blank for the clean row.

This script never invents a metric -- it only reads and reshapes the
CSVs already produced by real runs of the scripts above. If any of
those files are missing, it fails clearly rather than filling gaps.
"""

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_TABLES_DIR = PROJECT_ROOT / "results" / "tables"
RECOMMENDER_METRICS_PATH = RESULTS_TABLES_DIR / "recommender_metrics_pilot.csv"
DEFENCE_EFFECT_SUMMARY_PATH = RESULTS_TABLES_DIR / "defence_effect_pilot_summary.csv"
DETECTION_METRICS_PATH = RESULTS_TABLES_DIR / "detection_metrics_pilot.csv"
ATTACK_CONFIG_PATH = PROJECT_ROOT / "experiments" / "configs" / "attack_config.json"

MASTER_OUTPUT = PROJECT_ROOT / "results" / "experiment_results.csv"

RESULT_FIELDS = [
    "experiment_id", "condition", "attack_type", "attack_size", "filler_size",
    "target_movie", "random_seed", "defence_method",
    "rmse", "mae", "precision_at_k", "recall_at_k",
    "target_rank", "target_score", "hit_rate",
    "detection_precision", "detection_recall", "detection_f1", "false_positive_rate",
]

# Maps each condition to (attack_type it belongs to, defence_method applied, detection scenario key)
CONDITION_META = {
    "clean": {"attack_type": "", "defence_method": "", "detection_scenario": None},
    "random": {"attack_type": "random", "defence_method": "", "detection_scenario": "random"},
    "random_defended": {"attack_type": "random", "defence_method": "remove_suspicious_profiles", "detection_scenario": "random"},
    "average": {"attack_type": "average", "defence_method": "", "detection_scenario": "average"},
    "average_defended": {"attack_type": "average", "defence_method": "remove_suspicious_profiles", "detection_scenario": "average"},
}


def load_inputs():
    import json

    if not RECOMMENDER_METRICS_PATH.exists():
        raise FileNotFoundError(
            f"{RECOMMENDER_METRICS_PATH} not found. "
            "Run experiments/evaluate_recommender_metrics.py first."
        )
    if not DEFENCE_EFFECT_SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"{DEFENCE_EFFECT_SUMMARY_PATH} not found. "
            "Run experiments/evaluate_defence_effect.py first."
        )
    if not DETECTION_METRICS_PATH.exists():
        raise FileNotFoundError(
            f"{DETECTION_METRICS_PATH} not found. "
            "Run experiments/run_detection.py first (Azad's script)."
        )

    recommender_metrics = pd.read_csv(RECOMMENDER_METRICS_PATH).set_index("condition")
    defence_effect = pd.read_csv(DEFENCE_EFFECT_SUMMARY_PATH).set_index("condition")
    detection_metrics = pd.read_csv(DETECTION_METRICS_PATH).set_index("scenario")

    with ATTACK_CONFIG_PATH.open(encoding="utf-8") as f:
        attack_config = json.load(f)

    return recommender_metrics, defence_effect, detection_metrics, attack_config


def build_rows(experiment_id: str) -> list[dict]:
    recommender_metrics, defence_effect, detection_metrics, attack_config = load_inputs()

    rows = []

    for condition, meta in CONDITION_META.items():
        row = {field: "" for field in RESULT_FIELDS}

        row["experiment_id"] = experiment_id
        row["condition"] = condition
        row["attack_type"] = meta["attack_type"]
        row["attack_size"] = attack_config.get("attack_size_percent", "") if meta["attack_type"] else ""
        row["filler_size"] = attack_config.get("filler_size_percent", "") if meta["attack_type"] else ""
        row["target_movie"] = attack_config.get("target_movie_id", "")
        row["random_seed"] = attack_config.get("random_seed", "")
        row["defence_method"] = meta["defence_method"]

        if condition in recommender_metrics.index:
            row["rmse"] = recommender_metrics.loc[condition, "rmse"]
            row["mae"] = recommender_metrics.loc[condition, "mae"]

        if condition in defence_effect.index:
            row["target_rank"] = defence_effect.loc[condition, "mean_target_rank"]
            row["target_score"] = defence_effect.loc[condition, "mean_target_score"]
            row["hit_rate"] = defence_effect.loc[condition, "hit_rate_at_10"]

        scenario = meta["detection_scenario"]
        if scenario is not None and scenario in detection_metrics.index:
            row["detection_precision"] = detection_metrics.loc[scenario, "precision"]
            row["detection_recall"] = detection_metrics.loc[scenario, "recall"]
            row["detection_f1"] = detection_metrics.loc[scenario, "f1"]
            row["false_positive_rate"] = detection_metrics.loc[scenario, "false_positive_rate"]

        rows.append(row)

    return rows


def main(experiment_id: str = "EXP001_PILOT") -> None:
    rows = build_rows(experiment_id)
    results = pd.DataFrame(rows, columns=RESULT_FIELDS)

    MASTER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(MASTER_OUTPUT, index=False)

    print("Master experiment_results.csv built from real Week 6 pilot outputs")
    print("---------------------------------------------------------------------")
    print(results.to_string(index=False))
    print(f"\nSaved: {MASTER_OUTPUT}")


if __name__ == "__main__":
    main()
