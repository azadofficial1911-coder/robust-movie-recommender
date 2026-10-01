"""Tests for the Robustness Comparison evidence (Member 4 -- Defence + Evaluation).

Two kinds of test:
  1. The real committed evidence passes every verifier check.
  2. The verifier FAILS when the evidence is tampered with, so a pass means
     something (defence using ground truth, stale figures, edited numbers...).

Run with:  python -m pytest tests/test_robustness_evidence.py
"""

import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.research.services.results_loader import load_experiment_results  # noqa: E402
from experiments.build_experiment_results import ALL_FIELDS, RESULT_FIELDS  # noqa: E402
from experiments.evaluate_target_frequency import select_sample_users  # noqa: E402
from experiments.verify_robustness_evidence import FAIL, PASS, run_checks  # noqa: E402

REQUIRED = [
    PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "random_defended.csv",
    PROJECT_ROOT / "results" / "experiment_results.csv",
]
pytestmark = pytest.mark.skipif(
    not all(p.exists() for p in REQUIRED), reason="experiment outputs not generated yet"
)


def _statuses(root: Path) -> dict:
    return {c["check"]: c["status"] for c in run_checks(root)}


@pytest.fixture(scope="module")
def evidence_copy(tmp_path_factory) -> Path:
    """A private copy of the evidence files that a test may tamper with."""
    base = tmp_path_factory.mktemp("evidence")
    for rel in ("data/processed", "data/attacked", "results", "experiments/configs", "static/images/research"):
        shutil.copytree(PROJECT_ROOT / rel, base / rel)
    return base


@pytest.fixture
def tampered(evidence_copy, tmp_path) -> Path:
    root = tmp_path / "root"
    shutil.copytree(evidence_copy, root)
    return root


# --------------------------------------------------------------------------
# 1. The real evidence
# --------------------------------------------------------------------------

def test_committed_evidence_passes_every_check():
    failures = [c for c in run_checks(PROJECT_ROOT) if c["status"] == FAIL]
    assert failures == [], failures


def test_master_file_keeps_original_schema_first():
    master = pd.read_csv(PROJECT_ROOT / "results" / "experiment_results.csv")
    assert ALL_FIELDS[: len(RESULT_FIELDS)] == RESULT_FIELDS
    assert list(master.columns) == ALL_FIELDS
    assert list(master["condition"]) == ["clean", "random", "random_defended", "average", "average_defended"]


def test_master_file_marks_which_side_used_the_defence():
    master = pd.read_csv(PROJECT_ROOT / "results" / "experiment_results.csv").set_index("condition")
    assert not master.loc["random", "defence_applied"]
    assert master.loc["random_defended", "defence_applied"]
    assert master.loc["random", "users_removed"] == 0
    assert master.loc["random_defended", "users_removed"] == master.loc["random_defended", "suspicious_profiles_detected"]
    # Same attack on both sides of the comparison.
    for col in ("attack_type", "attack_size", "filler_size", "target_movie", "random_seed", "fake_profiles_injected"):
        assert master.loc["random", col] == master.loc["random_defended", col]
        assert master.loc["average", col] == master.loc["average_defended", col]


def test_loader_turns_blank_cells_into_none():
    rows = {r["condition"]: r for r in load_experiment_results()}
    assert rows["clean"]["detection_precision"] is None      # no detector on clean data
    assert rows["random_defended"]["detection_precision"] is not None


def test_target_frequency_sample_is_fixed_and_valid():
    train = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "train_ratings.csv")
    first = select_sample_users(train, 758, 100, 42)
    assert first == select_sample_users(train, 758, 100, 42)
    assert len(first) == 100
    raters = set(train.loc[train["movie_id"] == 758, "user_id"])
    assert not raters & set(first)


# --------------------------------------------------------------------------
# 2. The verifier catches bad evidence
# --------------------------------------------------------------------------

def test_detects_defence_that_used_ground_truth(tampered):
    # Simulate a detector miss: one fake profile predicted genuine. A correct
    # defence must keep that profile. Leaving the defended file unchanged
    # (i.e. still "perfect") is exactly what using true_label would produce.
    detection_path = tampered / "results" / "tables" / "random_detection_results.csv"
    detection = pd.read_csv(detection_path)
    missed = detection.index[detection["predicted_label"] == "suspicious"][0]
    detection.loc[missed, "predicted_label"] = "genuine"
    detection.to_csv(detection_path, index=False)

    statuses = _statuses(tampered)
    assert statuses["defended_equals_attacked_minus_predicted[random]"] == FAIL
    assert statuses["defended_equals_attacked_minus_predicted[average]"] == PASS


def test_detects_genuine_ratings_removed_by_defence(tampered):
    path = tampered / "data" / "attacked" / "defended_datasets" / "average_defended.csv"
    defended = pd.read_csv(path)
    defended[defended["user_id"] != defended["user_id"].iloc[0]].to_csv(path, index=False)

    statuses = _statuses(tampered)
    assert statuses["defended_equals_attacked_minus_predicted[average]"] == FAIL
    assert statuses["defence_summary_recompute[average]"] == FAIL


def test_detects_hand_edited_result_value(tampered):
    path = tampered / "results" / "experiment_results.csv"
    master = pd.read_csv(path)
    master.loc[master["condition"] == "random_defended", "target_rank"] = 1100.0
    master.to_csv(path, index=False)

    assert _statuses(tampered)["master_results_match_sources"] == FAIL


def test_detects_stale_figure_served_by_django(tampered):
    served = tampered / "static" / "images" / "research" / "target_rank_comparison.png"
    served.write_bytes(served.read_bytes() + b"stale")

    assert _statuses(tampered)["served_figures_match_generated"] == FAIL


def test_detects_attacked_dataset_overwritten(tampered):
    shutil.copy2(
        tampered / "data" / "attacked" / "defended_datasets" / "random_defended.csv",
        tampered / "data" / "attacked" / "attacked_datasets" / "random_pilot.csv",
    )
    statuses = _statuses(tampered)
    assert statuses["attacked_dataset_preserved[random]"] == FAIL
    assert statuses["attacked_is_clean_plus_fakes[random]"] == FAIL


def test_detects_test_set_leaking_into_training(tampered):
    test = pd.read_csv(tampered / "data" / "processed" / "test_ratings.csv")
    path = tampered / "data" / "processed" / "train_ratings.csv"
    pd.concat([pd.read_csv(path), test.head(5)]).to_csv(path, index=False)

    assert _statuses(tampered)["same_genuine_test_set"] == FAIL
