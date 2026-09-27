"""Robustness comparison orchestration for the RMRS research interface.

This service prepares a controlled comparison between:

1. Clean
2. Without Robustness / Attacked
3. With Robustness / Defended

The service does not implement another recommender, attack generator,
detector, defence algorithm, or metric calculation.

It only coordinates real experiment outputs and verifies that the
attacked and defended conditions belong to the same controlled attack.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .results_loader import (
    load_defence_summary,
    load_experiment_results,
)


BASE_DIR = Path(__file__).resolve().parents[3]

ATTACKED_DATASET_DIR = (
    BASE_DIR
    / "data"
    / "attacked"
    / "attacked_datasets"
)

DEFENDED_DATASET_DIR = (
    BASE_DIR
    / "data"
    / "attacked"
    / "defended_datasets"
)

DETECTION_RESULTS_DIR = (
    BASE_DIR
    / "results"
    / "tables"
)


SUPPORTED_SCENARIOS = {
    "random": "Random Push",
    "average": "Average Push",
}


ATTACK_METADATA_FIELDS = (
    "attack_type",
    "attack_size",
    "filler_size",
    "target_movie",
    "random_seed",
)


def normalise_scenario(scenario: str) -> str:
    """Return a valid comparison scenario.

    Only Random Push and Average Push are supported by the
    controlled pilot comparison.
    """

    scenario = str(scenario).strip().lower()

    if scenario not in SUPPORTED_SCENARIOS:
        raise ValueError(
            "Scenario must be either 'random' or 'average'."
        )

    return scenario


def _find_result(
    results: list[dict],
    condition: str,
) -> dict | None:
    """Return one experiment-result row by condition."""

    return next(
        (
            row
            for row in results
            if row.get("condition") == condition
        ),
        None,
    )


def _find_defence_summary(
    defence_summary: list[dict] | None,
    scenario: str,
) -> dict | None:
    """Return the defence summary for one attack scenario."""

    if not defence_summary:
        return None

    return next(
        (
            row
            for row in defence_summary
            if str(
                row.get(
                    "scenario",
                    "",
                )
            ).lower()
            == scenario
        ),
        None,
    )


def _verify_same_attack(
    attacked: dict,
    defended: dict,
) -> bool:
    """Verify attacked and defended results use identical attack settings."""

    for field in ATTACK_METADATA_FIELDS:
        if attacked.get(field) != defended.get(field):
            raise ValueError(
                "Robustness comparison is invalid because "
                f"'{field}' differs between attacked and "
                "defended conditions."
            )

    return True


def _sha256_file(
    path: Path,
) -> str | None:
    """Return a SHA-256 fingerprint for a dataset file.

    The fingerprint gives the comparison a reproducible identifier
    for the exact attacked dataset used as the shared attack source.
    """

    if not path.exists():
        return None

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_robustness_comparison(
    scenario: str,
) -> dict | None:
    """Build the Django-ready robustness comparison object.

    Both comparison paths use the same attacked scenario:

    Without Robustness:
        attacked data -> recommender/evaluation

    With Robustness:
        same attacked data -> detection -> defence
        -> recommender/evaluation

    Existing experiment result files remain the single source of
    truth for all displayed metrics.
    """

    scenario = normalise_scenario(
        scenario
    )

    experiment_results = (
        load_experiment_results()
    )

    if not experiment_results:
        return None

    clean = _find_result(
        experiment_results,
        "clean",
    )

    attacked = _find_result(
        experiment_results,
        scenario,
    )

    defended = _find_result(
        experiment_results,
        f"{scenario}_defended",
    )

    if not all(
        (
            clean,
            attacked,
            defended,
        )
    ):
        return None

    same_attack_verified = (
        _verify_same_attack(
            attacked,
            defended,
        )
    )

    defence = _find_defence_summary(
        load_defence_summary(),
        scenario,
    )

    attacked_dataset_path = (
        ATTACKED_DATASET_DIR
        / f"{scenario}_pilot.csv"
    )

    defended_dataset_path = (
        DEFENDED_DATASET_DIR
        / f"{scenario}_defended.csv"
    )

    detection_results_path = (
        DETECTION_RESULTS_DIR
        / f"{scenario}_detection_results.csv"
    )

    attack_metadata = {
        "attack_type": attacked.get(
            "attack_type"
        ),
        "attack_size": attacked.get(
            "attack_size"
        ),
        "filler_size": attacked.get(
            "filler_size"
        ),
        "target_movie": attacked.get(
            "target_movie"
        ),
        "random_seed": attacked.get(
            "random_seed"
        ),
    }

    if defence:
        attack_metadata[
            "suspicious_profiles_detected"
        ] = defence.get(
            "suspicious_profiles_detected"
        )

        attack_metadata[
            "users_before"
        ] = defence.get(
            "users_before"
        )

        attack_metadata[
            "users_removed"
        ] = defence.get(
            "users_removed"
        )

    return {
        "scenario": scenario,

        "scenario_label": (
            SUPPORTED_SCENARIOS[
                scenario
            ]
        ),

        "attack": attack_metadata,

        "same_attack_verified": (
            same_attack_verified
        ),

        "attack_source": {
            "dataset": str(
                attacked_dataset_path.relative_to(
                    BASE_DIR
                )
            ),
            "sha256": _sha256_file(
                attacked_dataset_path
            ),
        },

        "clean": clean,

        "without_robustness": (
            attacked
        ),

        "with_robustness": (
            defended
        ),

        "defence": defence,

        "provenance": {
            "without_robustness_source": str(
                attacked_dataset_path.relative_to(
                    BASE_DIR
                )
            ),

            "with_robustness_attack_source": str(
                attacked_dataset_path.relative_to(
                    BASE_DIR
                )
            ),

            "detection_results": str(
                detection_results_path.relative_to(
                    BASE_DIR
                )
            ),

            "defended_dataset": str(
                defended_dataset_path.relative_to(
                    BASE_DIR
                )
            ),
        },
    }