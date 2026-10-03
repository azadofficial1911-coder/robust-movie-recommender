"""Build the master experiment_results.csv -- the single source of truth for
the Evaluation Dashboard and the Robustness Comparison page.

It only reads and reshapes CSVs already produced by real runs of:

    experiments/evaluate_recommender_metrics.py  (rmse, mae, coverage)
    experiments/evaluate_defence_effect.py        (target_rank, target_score, hit_rate, eval users)
    experiments/run_detection.py                  (detection metrics + confusion counts)   [Azad]
    experiments/apply_defence.py                  (users / ratings removed)
    experiments/evaluate_target_frequency.py      (supplementary target frequency; optional)

One row is written per condition (clean, random, random_defended, average,
average_defended).

Column groups
-------------
1. The original Week 6 schema (unchanged names and order, so existing
   loaders, templates and generate_reports.py keep working).
2. Robustness-comparison evidence columns appended after it: defence
   counts, detection confusion counts, coverage, evaluation-user counts,
   recommender parameters and supplementary target frequency.

Detection metrics are attached to both the attacked and defended rows of a
scenario because they describe the detector's performance on that
scenario's attacked data; `defence_applied` says whether the detector's
decisions were actually used to build the training data for that row.

This script never invents a metric. Required inputs that are missing make
it fail clearly; the optional target-frequency file, if missing, leaves
its columns blank.
"""

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from recommender.baseline_recommender import MIN_NEIGHBORS, TOP_K_NEIGHBORS  # noqa: E402


RESULTS_TABLES_DIR = PROJECT_ROOT / "results" / "tables"
RECOMMENDER_METRICS_PATH = RESULTS_TABLES_DIR / "recommender_metrics_pilot.csv"
DEFENCE_EFFECT_SUMMARY_PATH = RESULTS_TABLES_DIR / "defence_effect_pilot_summary.csv"
DETECTION_METRICS_PATH = RESULTS_TABLES_DIR / "detection_metrics_pilot.csv"
DEFENCE_SUMMARY_PATH = RESULTS_TABLES_DIR / "defence_summary_pilot.csv"
TARGET_FREQUENCY_PATH = RESULTS_TABLES_DIR / "target_frequency_summary.csv"
ATTACK_CONFIG_PATH = PROJECT_ROOT / "experiments" / "configs" / "attack_config.json"
LABELS_DIR = PROJECT_ROOT / "data" / "attacked" / "labels"

TRAINING_DATA_PATHS = {
    "clean": PROJECT_ROOT / "data" / "processed" / "train_ratings.csv",
    "random": PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "random_pilot.csv",
    "random_defended": PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "random_defended.csv",
    "average": PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "average_pilot.csv",
    "average_defended": PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "average_defended.csv",
}

MASTER_OUTPUT = PROJECT_ROOT / "results" / "experiment_results.csv"

# 1. Original Week 6 schema -- do not rename or reorder.
RESULT_FIELDS = [
    "experiment_id", "condition", "attack_type", "attack_size", "filler_size",
    "target_movie", "random_seed", "defence_method",
    "rmse", "mae", "precision_at_k", "recall_at_k",
    "target_rank", "target_score", "hit_rate",
    "detection_precision", "detection_recall", "detection_f1", "false_positive_rate",
]

# 2. Robustness-comparison evidence columns (appended).
EVIDENCE_FIELDS = [
    "scenario", "defence_applied",
    "top_k_neighbours", "min_neighbours",
    "training_users", "training_ratings",
    "total_test_ratings", "predictions_produced", "coverage_percent",
    "evaluation_users", "predictable_users", "median_target_rank",
    "fake_profiles_injected",
    "detection_threshold", "detection_tp", "detection_fp", "detection_tn", "detection_fn",
    "suspicious_profiles_detected", "users_removed", "ratings_removed",
    "target_freq_sample_users", "target_freq_at_10", "target_freq_at_50",
    "target_freq_at_100", "target_freq_mean_rank", "target_freq_median_rank",
]

ALL_FIELDS = RESULT_FIELDS + EVIDENCE_FIELDS

# Maps each condition to the attack scenario it belongs to and whether the
# detection + defence layer was applied to its training data.
CONDITION_META = {
    "clean": {"scenario": "", "defence_applied": False},
    "random": {"scenario": "random", "defence_applied": False},
    "random_defended": {"scenario": "random", "defence_applied": True},
    "average": {"scenario": "average", "defence_applied": False},
    "average_defended": {"scenario": "average", "defence_applied": True},
}

DEFENCE_METHOD = "remove_suspicious_profiles"


def _require(path: Path, hint: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. {hint}")


def load_inputs() -> dict:
    _require(RECOMMENDER_METRICS_PATH, "Run experiments/evaluate_recommender_metrics.py first.")
    _require(DEFENCE_EFFECT_SUMMARY_PATH, "Run experiments/evaluate_defence_effect.py first.")
    _require(DETECTION_METRICS_PATH, "Run experiments/run_detection.py first (Azad's script).")
    _require(DEFENCE_SUMMARY_PATH, "Run experiments/apply_defence.py first.")

    with ATTACK_CONFIG_PATH.open(encoding="utf-8") as f:
        attack_config = json.load(f)

    target_frequency = None
    if TARGET_FREQUENCY_PATH.exists():
        target_frequency = pd.read_csv(TARGET_FREQUENCY_PATH).set_index("condition")
    else:
        print(
            f"NOTE: {TARGET_FREQUENCY_PATH.name} not found -- target_freq_* columns "
            "left blank. Run experiments/evaluate_target_frequency.py to fill them."
        )

    fake_counts = {}
    for scenario in ("random", "average"):
        labels_path = LABELS_DIR / f"{scenario}_pilot_labels.csv"
        _require(labels_path, "Run experiments/generate_attacked_data.py first (Azad's script).")
        labels = pd.read_csv(labels_path)
        # Ground truth is used here only to *report* how many fake profiles
        # were injected -- never to decide what the defence removes.
        fake_counts[scenario] = int((labels["true_label"] == "suspicious").sum())

    return {
        "recommender": pd.read_csv(RECOMMENDER_METRICS_PATH).set_index("condition"),
        "effect": pd.read_csv(DEFENCE_EFFECT_SUMMARY_PATH).set_index("condition"),
        "detection": pd.read_csv(DETECTION_METRICS_PATH).set_index("scenario"),
        "defence": pd.read_csv(DEFENCE_SUMMARY_PATH).set_index("scenario"),
        "target_frequency": target_frequency,
        "attack_config": attack_config,
        "fake_counts": fake_counts,
    }


def build_rows(experiment_id: str) -> list[dict]:
    inputs = load_inputs()
    recommender = inputs["recommender"]
    effect = inputs["effect"]
    detection = inputs["detection"]
    defence = inputs["defence"]
    target_frequency = inputs["target_frequency"]
    attack_config = inputs["attack_config"]

    rows = []

    for condition, meta in CONDITION_META.items():
        scenario = meta["scenario"]
        defended = meta["defence_applied"]
        row = {field: "" for field in ALL_FIELDS}

        # --- fixed experimental setup -------------------------------------
        row["experiment_id"] = experiment_id
        row["condition"] = condition
        row["scenario"] = scenario
        row["attack_type"] = scenario
        row["attack_size"] = attack_config.get("attack_size_percent", "") if scenario else ""
        row["filler_size"] = attack_config.get("filler_size_percent", "") if scenario else ""
        row["target_movie"] = attack_config.get("target_movie_id", "")
        row["random_seed"] = attack_config.get("random_seed", "")
        row["defence_method"] = DEFENCE_METHOD if defended else ""
        row["defence_applied"] = defended
        row["top_k_neighbours"] = TOP_K_NEIGHBORS
        row["min_neighbours"] = MIN_NEIGHBORS

        # --- training data actually fed to the recommender ------------------
        training = pd.read_csv(TRAINING_DATA_PATHS[condition], usecols=["user_id"])
        row["training_users"] = int(training["user_id"].nunique())
        row["training_ratings"] = int(len(training))

        # --- RMSE / MAE on the fixed genuine test set ------------------------
        if condition in recommender.index:
            rec = recommender.loc[condition]
            row["rmse"] = rec["rmse"]
            row["mae"] = rec["mae"]
            row["total_test_ratings"] = int(rec["total_test_ratings"])
            row["predictions_produced"] = int(rec["predictions_produced"])
            row["coverage_percent"] = rec["coverage_percent"]

        # --- target movie metrics on the 7 held-out evaluation users --------
        if condition in effect.index:
            eff = effect.loc[condition]
            row["target_rank"] = eff["mean_target_rank"]
            row["target_score"] = eff["mean_target_score"]
            row["hit_rate"] = eff["hit_rate_at_10"]
            row["evaluation_users"] = int(eff["evaluation_users"])
            row["predictable_users"] = int(eff["predictable_users"])
            row["median_target_rank"] = eff["median_target_rank"]

        # --- supplementary target frequency (wider sample) -----------------
        if target_frequency is not None and condition in target_frequency.index:
            tf = target_frequency.loc[condition]
            row["target_freq_sample_users"] = int(tf["sample_users"])
            row["target_freq_at_10"] = tf["target_freq_at_10"]
            row["target_freq_at_50"] = tf["target_freq_at_50"]
            row["target_freq_at_100"] = tf["target_freq_at_100"]
            row["target_freq_mean_rank"] = tf["mean_target_rank"]
            row["target_freq_median_rank"] = tf["median_target_rank"]

        if scenario:
            row["fake_profiles_injected"] = inputs["fake_counts"][scenario]

            # --- detector performance on this scenario's attacked data -----
            if scenario in detection.index:
                det = detection.loc[scenario]
                row["detection_precision"] = det["precision"]
                row["detection_recall"] = det["recall"]
                row["detection_f1"] = det["f1"]
                row["false_positive_rate"] = det["false_positive_rate"]
                row["detection_threshold"] = det["threshold"]
                for key in ("tp", "fp", "tn", "fn"):
                    row[f"detection_{key}"] = int(det[key])

            # --- what the defence removed ---------------------------------
            if defended:
                if scenario not in defence.index:
                    raise ValueError(f"No defence summary row for scenario '{scenario}'.")
                dsum = defence.loc[scenario]
                row["suspicious_profiles_detected"] = int(dsum["suspicious_profiles_detected"])
                row["users_removed"] = int(dsum["users_removed"])
                row["ratings_removed"] = int(dsum["ratings_removed"])
            else:
                # Without robustness: the attacked data goes straight into the
                # recommender, so nothing is removed.
                row["users_removed"] = 0
                row["ratings_removed"] = 0

        rows.append(row)

    return rows


def main(experiment_id: str = "EXP001_PILOT") -> None:
    rows = build_rows(experiment_id)
    results = pd.DataFrame(rows, columns=ALL_FIELDS)

    MASTER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(MASTER_OUTPUT, index=False)

    print("Master experiment_results.csv built from real experiment outputs")
    print("-----------------------------------------------------------------")
    print(results[RESULT_FIELDS].to_string(index=False))
    print(f"\n+ {len(EVIDENCE_FIELDS)} robustness-evidence columns")
    print(f"Saved: {MASTER_OUTPUT}")


if __name__ == "__main__":
    main()
