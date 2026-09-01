"""Run the Week 6 pilot suspicious-user detector."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from apps.research.services.detection import (  # noqa: E402
    detect_suspicious_users,
)

from evaluation.detection_metrics import (  # noqa: E402
    detection_metrics,
)


CONFIG_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "configs"
    / "detection_config.json"
)

MOVIE_STATS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "movie_statistics.csv"
)

RANDOM_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "attacked"
    / "attacked_datasets"
    / "random_pilot.csv"
)

AVERAGE_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "attacked"
    / "attacked_datasets"
    / "average_pilot.csv"
)

RANDOM_LABEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "attacked"
    / "labels"
    / "random_pilot_labels.csv"
)

AVERAGE_LABEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "attacked"
    / "labels"
    / "average_pilot_labels.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "tables"
)

RANDOM_RESULTS_PATH = (
    RESULTS_DIR
    / "random_detection_results.csv"
)

AVERAGE_RESULTS_PATH = (
    RESULTS_DIR
    / "average_detection_results.csv"
)

SUMMARY_PATH = (
    RESULTS_DIR
    / "detection_metrics_pilot.csv"
)


def load_config() -> dict:
    """Load the Week 6 pilot detector configuration."""

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_scenario(
    scenario_name: str,
    ratings_path: Path,
    labels_path: Path,
    output_path: Path,
    movie_statistics: pd.DataFrame,
    config: dict,
) -> dict:
    """Run detection for one attacked dataset."""

    ratings = pd.read_csv(
        ratings_path
    )

    labels = pd.read_csv(
        labels_path
    )

    results = detect_suspicious_users(
        ratings=ratings,
        threshold=float(
            config["threshold"]
        ),
        movie_statistics=movie_statistics,
        target_movie_id=int(
            config["target_movie_id"]
        ),
        true_labels=labels,
        rating_min=int(
            config["rating_min"]
        ),
        rating_max=int(
            config["rating_max"]
        ),
    )

    result_table = pd.DataFrame(
        [
            asdict(result)
            for result in results
        ]
    )

    result_table = result_table[
        [
            "user_id",
            "suspicion_score",
            "predicted_label",
            "true_label",
        ]
    ].sort_values(
        "user_id"
    ).reset_index(
        drop=True
    )

    if result_table["true_label"].isna().any():
        raise RuntimeError(
            f"{scenario_name} detection results contain "
            "missing ground-truth labels."
        )

    metrics = detection_metrics(
        result_table[
            "true_label"
        ].tolist(),
        result_table[
            "predicted_label"
        ].tolist(),
    )

    suspicious_count = int(
        (
            result_table[
                "predicted_label"
            ]
            == "suspicious"
        ).sum()
    )

    result_table.to_csv(
        output_path,
        index=False,
    )

    summary = {
        "scenario": scenario_name,
        "threshold": float(
            config["threshold"]
        ),
        "users_analysed": len(
            result_table
        ),
        "suspicious_users": suspicious_count,
        **metrics,
    }

    print(
        f"\n{scenario_name.title()} Push"
    )

    print(
        "  Users analysed:",
        summary["users_analysed"],
    )

    print(
        "  Suspicious users:",
        summary["suspicious_users"],
    )

    print(
        "  Precision:",
        round(
            summary["precision"],
            4,
        ),
    )

    print(
        "  Recall:",
        round(
            summary["recall"],
            4,
        ),
    )

    print(
        "  F1:",
        round(
            summary["f1"],
            4,
        ),
    )

    print(
        "  False positive rate:",
        round(
            summary["false_positive_rate"],
            4,
        ),
    )

    print(
        "  Saved:",
        output_path,
    )

    return summary


def main() -> None:
    """Run Random and Average Push detection experiments."""

    config = load_config()

    movie_statistics = pd.read_csv(
        MOVIE_STATS_PATH
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Week 6 suspicious-user detection"
    )

    print(
        "--------------------------------"
    )

    print(
        "Target movie:",
        config["target_movie_id"],
    )

    print(
        "Threshold:",
        config["threshold"],
    )

    summary_rows = []

    summary_rows.append(
        run_scenario(
            scenario_name="random",
            ratings_path=RANDOM_DATASET_PATH,
            labels_path=RANDOM_LABEL_PATH,
            output_path=RANDOM_RESULTS_PATH,
            movie_statistics=movie_statistics,
            config=config,
        )
    )

    summary_rows.append(
        run_scenario(
            scenario_name="average",
            ratings_path=AVERAGE_DATASET_PATH,
            labels_path=AVERAGE_LABEL_PATH,
            output_path=AVERAGE_RESULTS_PATH,
            movie_statistics=movie_statistics,
            config=config,
        )
    )

    summary = pd.DataFrame(
        summary_rows
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    print(
        "\nDetection summary"
    )

    print(
        "-----------------"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        "\nSaved summary:",
        SUMMARY_PATH,
    )


if __name__ == "__main__":
    main()