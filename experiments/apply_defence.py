"""Apply the Week 6 primary defence (remove suspicious profiles) to both
pilot attack scenarios, using the real detection output handed over by
Azad (Member 3).

For each scenario (random, average):
    attacked dataset  ->  detection results  ->  remove predicted-suspicious
    profiles  ->  defended dataset

Defence decisions use predicted_label only. true_label is never read by
this script's defence logic -- it exists in the detection file purely so
Azad's detector could be evaluated, and is not consulted here.
"""

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from defence.remove_profiles import (  # noqa: E402
    defence_summary,
    get_suspicious_user_ids,
    remove_suspicious_profiles,
)


ATTACKED_DATASET_DIR = PROJECT_ROOT / "data" / "attacked" / "attacked_datasets"
DETECTION_RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
DEFENDED_DATASET_DIR = PROJECT_ROOT / "data" / "attacked" / "defended_datasets"
SUMMARY_OUTPUT = PROJECT_ROOT / "results" / "tables" / "defence_summary_pilot.csv"

SCENARIOS = ("random", "average")


def apply_defence_to_scenario(scenario_name: str) -> dict:
    """Apply the primary defence to one attack scenario and save the result."""

    attacked_path = ATTACKED_DATASET_DIR / f"{scenario_name}_pilot.csv"
    detection_path = DETECTION_RESULTS_DIR / f"{scenario_name}_detection_results.csv"
    defended_path = DEFENDED_DATASET_DIR / f"{scenario_name}_defended.csv"

    attacked = pd.read_csv(attacked_path)
    detection_results = pd.read_csv(detection_path)

    # Defence uses predicted_label only -- true_label in detection_results
    # is present for evaluating the detector, not for making this decision.
    suspicious_ids = get_suspicious_user_ids(
        detection_results,
        label_column="predicted_label",
        suspicious_label="suspicious",
    )

    defended = remove_suspicious_profiles(attacked, suspicious_ids)

    summary = defence_summary(attacked, defended)
    summary["scenario"] = scenario_name
    summary["defence_method"] = "remove_suspicious_profiles"
    summary["suspicious_profiles_detected"] = len(suspicious_ids)

    DEFENDED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    defended.to_csv(defended_path, index=False)

    print(f"\n{scenario_name.title()} Push -- defence applied")
    print(f"  Users before:  {summary['users_before']}")
    print(f"  Users removed: {summary['users_removed']}")
    print(f"  Users after:   {summary['users_after']}")
    print(f"  Ratings before: {summary['ratings_before']}")
    print(f"  Ratings after:  {summary['ratings_after']}")
    print(f"  Ratings removed: {summary['ratings_removed']}")
    print(f"  Defended dataset saved to: {defended_path}")

    return summary


def main() -> None:
    print("Week 6 defence application")
    print("---------------------------")

    summaries = [apply_defence_to_scenario(scenario) for scenario in SCENARIOS]

    summary_table = pd.DataFrame(summaries)[
        [
            "scenario",
            "defence_method",
            "suspicious_profiles_detected",
            "users_before",
            "users_removed",
            "users_after",
            "ratings_before",
            "ratings_removed",
            "ratings_after",
        ]
    ]

    SUMMARY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    summary_table.to_csv(SUMMARY_OUTPUT, index=False)

    print("\nDefence summary")
    print("---------------")
    print(summary_table.to_string(index=False))
    print(f"\nSaved: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
