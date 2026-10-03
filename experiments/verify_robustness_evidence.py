"""Verify the Robustness Comparison evidence and write a traceable manifest.

Run after the experiment scripts (or via run_robustness_evaluation.py):

    python experiments/verify_robustness_evidence.py

Every check below re-derives a fact directly from the data/result files,
independently of the scripts that produced them. The script exits with a
non-zero status if any check FAILS, so it can gate a merge or a demo.

What is proven
--------------
Fair comparison
  - The attacked datasets are the clean genuine training data plus the
    injected fake profiles and nothing else.
  - Random Push and Average Push use the same attack settings (target,
    number of fake profiles, profile size, target rating).
  - Every condition is evaluated on the same fixed genuine test set and
    the same evaluation users.
  - The recommender parameters recorded in the results are the ones in
    recommender/baseline_recommender.py.

Defence
  - Each defended dataset is exactly its attacked dataset minus the users
    the detector *predicted* as suspicious (row-for-row).
  - Ground-truth labels have no influence on the defence: re-running it
    with true_label deliberately corrupted gives the identical output.
  - The attacked datasets were not overwritten by the defence.

Traceability
  - Detection metrics, defence counts and per-user summaries recompute
    to the values stored in the result tables.
  - Every metric in results/experiment_results.csv matches the source
    table it was copied from.
  - The figures served by Django are byte-identical to the generated ones.

Output: results/evidence_manifest.json (SHA-256 of every input and output
file, the fixed experimental setup, and the result of every check).
"""

import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SCENARIOS = ("random", "average")
CONDITIONS = ("clean", "random", "random_defended", "average", "average_defended")
REL_TOL = 1e-9
ABS_TOL = 1e-12

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"


class Paths:
    """All file locations, relative to a project root (overridable for tests)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        data = self.root / "data"
        tables = self.root / "results" / "tables"

        self.train = data / "processed" / "train_ratings.csv"
        self.test = data / "processed" / "test_ratings.csv"
        self.attack_config = self.root / "experiments" / "configs" / "attack_config.json"
        self.detection_config = self.root / "experiments" / "configs" / "detection_config.json"

        self.attacked = {s: data / "attacked" / "attacked_datasets" / f"{s}_pilot.csv" for s in SCENARIOS}
        self.fake_profiles = {s: data / "attacked" / "fake_profiles" / f"{s}_pilot.csv" for s in SCENARIOS}
        self.labels = {s: data / "attacked" / "labels" / f"{s}_pilot_labels.csv" for s in SCENARIOS}
        self.detection = {s: tables / f"{s}_detection_results.csv" for s in SCENARIOS}
        self.defended = {s: data / "attacked" / "defended_datasets" / f"{s}_defended.csv" for s in SCENARIOS}

        self.training = {
            "clean": self.train,
            "random": self.attacked["random"],
            "random_defended": self.defended["random"],
            "average": self.attacked["average"],
            "average_defended": self.defended["average"],
        }

        self.detection_metrics = tables / "detection_metrics_pilot.csv"
        self.defence_summary = tables / "defence_summary_pilot.csv"
        self.recommender_metrics = tables / "recommender_metrics_pilot.csv"
        self.effect_per_user = tables / "defence_effect_pilot_per_user.csv"
        self.effect_summary = tables / "defence_effect_pilot_summary.csv"
        self.attack_effect_summary = tables / "attack_effect_pilot_summary.csv"
        self.tf_per_user = tables / "target_frequency_per_user.csv"
        self.tf_summary = tables / "target_frequency_summary.csv"
        self.master = self.root / "results" / "experiment_results.csv"

        self.figures_dir = self.root / "results" / "figures"
        self.static_figures_dir = self.root / "static" / "images" / "research"
        self.manifest = self.root / "results" / "evidence_manifest.json"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _close(a, b) -> bool:
    """Numeric equality with a tolerance for float summation noise; blanks equal blanks."""
    a_blank = a is None or (isinstance(a, float) and math.isnan(a)) or a == ""
    b_blank = b is None or (isinstance(b, float) and math.isnan(b)) or b == ""
    if a_blank or b_blank:
        return a_blank and b_blank
    try:
        return math.isclose(float(a), float(b), rel_tol=REL_TOL, abs_tol=ABS_TOL)
    except (TypeError, ValueError):
        return str(a) == str(b)


def _rating_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Canonical (user, movie, rating) rows for set-style comparison."""
    return (
        df[["user_id", "movie_id", "rating"]]
        .astype({"user_id": int, "movie_id": int, "rating": float})
        .sort_values(["user_id", "movie_id"])
        .reset_index(drop=True)
    )


def _same_rows(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    return _rating_rows(a).equals(_rating_rows(b))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _result(name: str, status: str, detail: str) -> dict:
    return {"check": name, "status": status, "detail": detail}


class Evidence:
    """Lazy, cached access to every file the checks need."""

    def __init__(self, paths: Paths):
        self.p = paths
        self._cache = {}

    def csv(self, path: Path) -> pd.DataFrame:
        key = str(path)
        if key not in self._cache:
            self._cache[key] = pd.read_csv(path)
        return self._cache[key]

    def json(self, path: Path) -> dict:
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def fake_ids(self, scenario: str) -> set:
        labels = self.csv(self.p.labels[scenario])
        return set(labels.loc[labels["true_label"] == "suspicious", "user_id"].astype(int))

    def predicted_ids(self, scenario: str) -> set:
        det = self.csv(self.p.detection[scenario])
        return set(det.loc[det["predicted_label"] == "suspicious", "user_id"].astype(int))


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_attacked_is_clean_plus_fakes(ev: Evidence) -> list[dict]:
    out = []
    clean = ev.csv(ev.p.train)
    for s in SCENARIOS:
        attacked = ev.csv(ev.p.attacked[s])
        fakes = ev.fake_ids(s)
        genuine_part = attacked[~attacked["user_id"].isin(fakes)]
        fake_part = attacked[attacked["user_id"].isin(fakes)]
        profiles = ev.csv(ev.p.fake_profiles[s])
        ok = _same_rows(genuine_part, clean) and _same_rows(fake_part, profiles)
        out.append(_result(
            f"attacked_is_clean_plus_fakes[{s}]",
            PASS if ok else FAIL,
            f"{len(attacked)} attacked rows = {len(clean)} clean genuine rows + "
            f"{len(fake_part)} rows from {len(fakes)} fake profiles"
            + ("" if ok else " -- MISMATCH: attacked data is not clean data + fake profiles"),
        ))
    return out


def check_same_attack_setup(ev: Evidence) -> list[dict]:
    config = ev.json(ev.p.attack_config)
    target = int(config["target_movie_id"])
    summary = {}
    problems = []
    for s in SCENARIOS:
        profiles = ev.csv(ev.p.fake_profiles[s])
        per_profile = profiles.groupby("user_id").size()
        target_ratings = profiles.loc[profiles["movie_id"] == target, "rating"]
        summary[s] = {
            "fake_profiles": int(profiles["user_id"].nunique()),
            "ratings_per_profile": sorted(set(int(x) for x in per_profile)),
            "target_rating": sorted(set(float(x) for x in target_ratings)),
            "profiles_rating_target": int(profiles.loc[profiles["movie_id"] == target, "user_id"].nunique()),
        }
        if summary[s]["fake_profiles"] != len(ev.fake_ids(s)):
            problems.append(f"{s} fake profile file and ground-truth labels disagree on the number of fake users")
        if set(profiles["attack_type"]) != {s}:
            problems.append(f"{s} profiles have attack_type {sorted(set(profiles['attack_type']))}")
        if set(profiles["target_movie_id"].astype(int)) != {target}:
            problems.append(f"{s} profiles do not all target movie {target}")
        if summary[s]["profiles_rating_target"] != summary[s]["fake_profiles"]:
            problems.append(f"not every {s} fake profile rates the target movie")

    a, b = summary["random"], summary["average"]
    for key in ("fake_profiles", "ratings_per_profile", "target_rating"):
        if a[key] != b[key]:
            problems.append(f"random vs average differ on {key}: {a[key]} vs {b[key]}")

    detail = (
        f"target movie {target}, {a['fake_profiles']} fake profiles per scenario, "
        f"{a['ratings_per_profile']} ratings each, target rated {a['target_rating']}"
    )
    return [_result("same_attack_setup_across_scenarios", FAIL if problems else PASS,
                    detail + ("" if not problems else " -- " + "; ".join(problems)))]


def check_defence_uses_predictions(ev: Evidence) -> list[dict]:
    from defence.remove_profiles import get_suspicious_user_ids, remove_suspicious_profiles

    out = []
    for s in SCENARIOS:
        attacked = ev.csv(ev.p.attacked[s])
        defended = ev.csv(ev.p.defended[s])
        predicted = ev.predicted_ids(s)

        # 1. Independent re-derivation: attacked minus predicted-suspicious users.
        expected = attacked[~attacked["user_id"].isin(predicted)]
        exact = _same_rows(defended, expected)
        out.append(_result(
            f"defended_equals_attacked_minus_predicted[{s}]",
            PASS if exact else FAIL,
            f"{len(attacked)} - rows of {len(predicted)} predicted-suspicious users = {len(defended)} defended rows"
            + ("" if exact else " -- MISMATCH"),
        ))

        # 2. Ground truth has no influence: corrupt true_label and re-run the defence.
        detection = ev.csv(ev.p.detection[s]).copy()
        detection["true_label"] = detection["true_label"].map(
            {"suspicious": "genuine", "genuine": "suspicious"}
        )
        rerun = remove_suspicious_profiles(attacked, get_suspicious_user_ids(detection))
        independent = _same_rows(rerun, defended)
        out.append(_result(
            f"defence_ignores_true_label[{s}]",
            PASS if independent else FAIL,
            "re-running the defence with every true_label flipped gives the identical defended dataset"
            if independent else "defence output changed when true_label was corrupted",
        ))

        # 3. The attacked dataset was not overwritten by the defence step.
        fakes = ev.fake_ids(s)
        still_attacked = (
            ev.p.attacked[s].resolve() != ev.p.defended[s].resolve()
            and fakes.issubset(set(attacked["user_id"].astype(int)))
        )
        out.append(_result(
            f"attacked_dataset_preserved[{s}]",
            PASS if still_attacked else FAIL,
            f"{ev.p.attacked[s].name} still contains all {len(fakes)} fake profiles; "
            f"defended data written separately to {ev.p.defended[s].name}"
            if still_attacked else "attacked dataset is missing fake profiles or shares a path with the defended one",
        ))
    return out


def check_same_test_set(ev: Evidence) -> list[dict]:
    test = ev.csv(ev.p.test)
    test_pairs = set(zip(test["user_id"].astype(int), test["movie_id"].astype(int)))
    all_fakes = set().union(*(ev.fake_ids(s) for s in SCENARIOS))
    problems = []

    for condition in CONDITIONS:
        train = ev.csv(ev.p.training[condition])
        overlap = test_pairs & set(zip(train["user_id"].astype(int), train["movie_id"].astype(int)))
        if overlap:
            problems.append(f"{condition}: {len(overlap)} test (user, movie) pairs also in training")

    if set(test["user_id"].astype(int)) & all_fakes:
        problems.append("test set contains fake users")

    rec = ev.csv(ev.p.recommender_metrics).set_index("condition")
    for condition in CONDITIONS:
        if condition not in rec.index:
            problems.append(f"{condition} missing from {ev.p.recommender_metrics.name}")
        elif int(rec.loc[condition, "total_test_ratings"]) != len(test):
            problems.append(f"{condition} evaluated on {rec.loc[condition, 'total_test_ratings']} ratings, test set has {len(test)}")

    return [_result(
        "same_genuine_test_set",
        FAIL if problems else PASS,
        f"all 5 conditions scored on the same {len(test)} genuine test ratings; no train/test leakage"
        if not problems else "; ".join(problems),
    )]


def check_same_evaluation_users(ev: Evidence) -> list[dict]:
    out = []
    for label, path in (("primary", ev.p.effect_per_user), ("target_frequency", ev.p.tf_per_user)):
        if not path.exists():
            out.append(_result(f"same_evaluation_users[{label}]",
                               FAIL if label == "primary" else WARN, f"{path.name} not found"))
            continue
        per_user = ev.csv(path)
        user_sets = {c: tuple(sorted(g["user_id"].astype(int))) for c, g in per_user.groupby("condition")}
        missing = [c for c in CONDITIONS if c not in user_sets]
        identical = not missing and len(set(user_sets.values())) == 1
        n = len(next(iter(user_sets.values()))) if user_sets else 0
        out.append(_result(
            f"same_evaluation_users[{label}]",
            PASS if identical else FAIL,
            f"identical {n} genuine users in all 5 conditions" if identical
            else f"user lists differ between conditions (missing: {missing})",
        ))
    return out


def check_detection_metrics(ev: Evidence) -> list[dict]:
    from evaluation.detection_metrics import detection_metrics

    stored = ev.csv(ev.p.detection_metrics).set_index("scenario")
    out = []
    for s in SCENARIOS:
        det = ev.csv(ev.p.detection[s])
        recomputed = detection_metrics(det["true_label"].tolist(), det["predicted_label"].tolist())
        row = stored.loc[s]
        mismatches = [k for k in ("tp", "fp", "tn", "fn", "precision", "recall", "f1", "false_positive_rate")
                      if not _close(recomputed[k], row[k])]
        # The labels the detector was scored against must be the attack's ground truth.
        labels = ev.csv(ev.p.labels[s]).set_index("user_id")["true_label"]
        merged = det.set_index("user_id")["true_label"]
        if not merged.sort_index().equals(labels.sort_index()):
            mismatches.append("true_label differs from attack ground-truth labels")
        out.append(_result(
            f"detection_metrics_recompute[{s}]",
            FAIL if mismatches else PASS,
            f"TP={recomputed['tp']} FP={recomputed['fp']} TN={recomputed['tn']} FN={recomputed['fn']}, "
            f"precision={recomputed['precision']:.3f} recall={recomputed['recall']:.3f} "
            f"F1={recomputed['f1']:.3f} FPR={recomputed['false_positive_rate']:.3f}"
            + ("" if not mismatches else f" -- stored value differs: {mismatches}"),
        ))
    return out


def check_defence_summary(ev: Evidence) -> list[dict]:
    stored = ev.csv(ev.p.defence_summary).set_index("scenario")
    out = []
    for s in SCENARIOS:
        attacked = ev.csv(ev.p.attacked[s])
        defended = ev.csv(ev.p.defended[s])
        recomputed = {
            "suspicious_profiles_detected": len(ev.predicted_ids(s)),
            "users_before": attacked["user_id"].nunique(),
            "users_after": defended["user_id"].nunique(),
            "ratings_before": len(attacked),
            "ratings_after": len(defended),
        }
        recomputed["users_removed"] = recomputed["users_before"] - recomputed["users_after"]
        recomputed["ratings_removed"] = recomputed["ratings_before"] - recomputed["ratings_after"]
        mismatches = [k for k, v in recomputed.items() if not _close(v, stored.loc[s, k])]
        out.append(_result(
            f"defence_summary_recompute[{s}]",
            FAIL if mismatches else PASS,
            f"{recomputed['users_removed']} users / {recomputed['ratings_removed']} ratings removed "
            f"({recomputed['users_before']}→{recomputed['users_after']} users)"
            + ("" if not mismatches else f" -- stored value differs: {mismatches}"),
        ))
    return out


def check_per_user_summaries(ev: Evidence) -> list[dict]:
    from evaluation.attack_metrics import hit_rate

    out = []
    per_user = ev.csv(ev.p.effect_per_user)
    summary = ev.csv(ev.p.effect_summary).set_index("condition")
    mismatches = []
    for c, g in per_user.groupby("condition"):
        expected = {
            "evaluation_users": len(g),
            "mean_target_score": g["target_score"].dropna().mean(),
            "mean_target_rank": g["target_rank"].dropna().mean(),
            "median_target_rank": g["target_rank"].dropna().median(),
            "hit_rate_at_10": hit_rate(g["hit_at_10"].tolist()),
        }
        mismatches += [f"{c}.{k}" for k, v in expected.items() if not _close(v, summary.loc[c, k])]
    out.append(_result("target_metrics_recompute_from_per_user",
                       FAIL if mismatches else PASS,
                       "mean/median target rank, target score and hit rate recompute from per-user rows"
                       + ("" if not mismatches else f" -- differs: {mismatches}")))

    # Azad's attack-effect run and the defence-effect run must agree on the shared conditions.
    if ev.p.attack_effect_summary.exists():
        attack = ev.csv(ev.p.attack_effect_summary).set_index("condition")
        diffs = [f"{c}.{k}" for c in attack.index for k in attack.columns
                 if c in summary.index and k in summary.columns and not _close(attack.loc[c, k], summary.loc[c, k])]
        out.append(_result("attack_and_defence_runs_agree",
                           FAIL if diffs else PASS,
                           f"clean/random/average rows identical in {ev.p.attack_effect_summary.name} and "
                           f"{ev.p.effect_summary.name}" + ("" if not diffs else f" -- differs: {diffs}")))

    if ev.p.tf_per_user.exists() and ev.p.tf_summary.exists():
        tf = ev.csv(ev.p.tf_per_user)
        tf_sum = ev.csv(ev.p.tf_summary).set_index("condition")
        diffs = []
        for c, g in tf.groupby("condition"):
            ranks = g["target_rank"].dropna()
            expected = {"sample_users": len(g), "mean_target_rank": ranks.mean(), "median_target_rank": ranks.median()}
            for k in (10, 50, 100):
                expected[f"target_freq_at_{k}"] = g[f"hit_at_{k}"].astype(bool).mean()
            diffs += [f"{c}.{k}" for k, v in expected.items() if not _close(v, tf_sum.loc[c, k])]
        out.append(_result("target_frequency_recompute_from_per_user",
                           FAIL if diffs else PASS,
                           "target frequency @10/@50/@100 and ranks recompute from per-user rows"
                           + ("" if not diffs else f" -- differs: {diffs}")))
    else:
        out.append(_result("target_frequency_recompute_from_per_user", WARN,
                           "target frequency files not found (run experiments/evaluate_target_frequency.py)"))
    return out


def check_master_matches_sources(ev: Evidence) -> list[dict]:
    from recommender.baseline_recommender import MIN_NEIGHBORS, TOP_K_NEIGHBORS

    master = ev.csv(ev.p.master).set_index("condition")
    rec = ev.csv(ev.p.recommender_metrics).set_index("condition")
    eff = ev.csv(ev.p.effect_summary).set_index("condition")
    det = ev.csv(ev.p.detection_metrics).set_index("scenario")
    dsum = ev.csv(ev.p.defence_summary).set_index("scenario")
    tf = ev.csv(ev.p.tf_summary).set_index("condition") if ev.p.tf_summary.exists() else None
    config = ev.json(ev.p.attack_config)

    mapping = [  # (master column, source frame, source column, key: 'condition' | 'scenario')
        ("rmse", rec, "rmse", "condition"),
        ("mae", rec, "mae", "condition"),
        ("coverage_percent", rec, "coverage_percent", "condition"),
        ("target_rank", eff, "mean_target_rank", "condition"),
        ("target_score", eff, "mean_target_score", "condition"),
        ("hit_rate", eff, "hit_rate_at_10", "condition"),
        ("evaluation_users", eff, "evaluation_users", "condition"),
        ("median_target_rank", eff, "median_target_rank", "condition"),
        ("detection_precision", det, "precision", "scenario"),
        ("detection_recall", det, "recall", "scenario"),
        ("detection_f1", det, "f1", "scenario"),
        ("false_positive_rate", det, "false_positive_rate", "scenario"),
    ]
    if tf is not None:
        mapping += [
            ("target_freq_at_10", tf, "target_freq_at_10", "condition"),
            ("target_freq_at_50", tf, "target_freq_at_50", "condition"),
            ("target_freq_at_100", tf, "target_freq_at_100", "condition"),
            ("target_freq_mean_rank", tf, "mean_target_rank", "condition"),
        ]

    problems, compared = [], 0
    missing_columns = [m[0] for m in mapping if m[0] not in master.columns]
    if missing_columns:
        return [_result("master_results_match_sources", FAIL,
                        f"{ev.p.master.name} is missing columns {missing_columns} -- "
                        "rebuild it with experiments/build_experiment_results.py")]

    for condition in CONDITIONS:
        if condition not in master.index:
            problems.append(f"missing row {condition}")
            continue
        row = master.loc[condition]
        scenario = "" if condition == "clean" else condition.split("_")[0]

        for col, frame, src_col, key in mapping:
            lookup = condition if key == "condition" else scenario
            if key == "scenario" and not scenario:
                continue
            compared += 1
            if not _close(row[col], frame.loc[lookup, src_col]):
                problems.append(f"{condition}.{col}")

        if condition.endswith("_defended"):
            for col in ("suspicious_profiles_detected", "users_removed", "ratings_removed"):
                compared += 1
                if not _close(row[col], dsum.loc[scenario, col]):
                    problems.append(f"{condition}.{col}")

        for col, expected in (("top_k_neighbours", TOP_K_NEIGHBORS), ("min_neighbours", MIN_NEIGHBORS),
                              ("target_movie", config["target_movie_id"]), ("random_seed", config["random_seed"])):
            compared += 1
            if not _close(row[col], expected):
                problems.append(f"{condition}.{col}")

    return [_result("master_results_match_sources",
                    FAIL if problems else PASS,
                    f"{compared} values in {ev.p.master.name} match their source tables and config"
                    if not problems else f"values differ from source: {problems}")]


def check_figures_in_sync(ev: Evidence) -> list[dict]:
    served = sorted(ev.p.static_figures_dir.glob("*.png")) if ev.p.static_figures_dir.exists() else []
    if not served:
        return [_result("served_figures_match_generated", WARN, "no figures in static/images/research")]
    problems = []
    for fig in served:
        generated = ev.p.figures_dir / fig.name
        if not generated.exists():
            problems.append(f"{fig.name} has no generated source in results/figures")
        elif _sha256(fig) != _sha256(generated):
            problems.append(f"{fig.name} differs from results/figures (stale copy)")
    return [_result("served_figures_match_generated",
                    FAIL if problems else PASS,
                    f"{len(served)} figures served by Django are byte-identical to results/figures"
                    if not problems else "; ".join(problems))]


ALL_CHECKS = [
    check_attacked_is_clean_plus_fakes,
    check_same_attack_setup,
    check_defence_uses_predictions,
    check_same_test_set,
    check_same_evaluation_users,
    check_detection_metrics,
    check_defence_summary,
    check_per_user_summaries,
    check_master_matches_sources,
    check_figures_in_sync,
]


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

def _file_entry(p: Paths, path: Path) -> dict:
    entry = {"path": path.relative_to(p.root).as_posix(), "exists": path.exists()}
    if path.exists():
        entry["sha256"] = _sha256(path)
        entry["bytes"] = path.stat().st_size
        if path.suffix == ".csv":
            with path.open("rb") as f:
                entry["rows"] = max(sum(1 for _ in f) - 1, 0)
    return entry


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                              text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def build_manifest(ev: Evidence, checks: list[dict]) -> dict:
    from recommender.baseline_recommender import MIN_NEIGHBORS, TOP_K_NEIGHBORS

    p = ev.p
    inputs = [p.train, p.test, p.attack_config, p.detection_config]
    for s in SCENARIOS:
        inputs += [p.fake_profiles[s], p.labels[s], p.attacked[s], p.detection[s]]
    outputs = [p.defended[s] for s in SCENARIOS] + [
        p.defence_summary, p.detection_metrics, p.recommender_metrics, p.effect_per_user,
        p.effect_summary, p.tf_per_user, p.tf_summary, p.master,
    ] + sorted(p.figures_dir.glob("*.png"))

    effect = ev.csv(p.effect_per_user)
    setup = {
        "attack_config": ev.json(p.attack_config),
        "detection_config": ev.json(p.detection_config),
        "recommender": {
            "algorithm": "user-based collaborative filtering, mean-centred cosine similarity",
            "module": "recommender/baseline_recommender.py",
            "top_k_neighbours": TOP_K_NEIGHBORS,
            "min_neighbours": MIN_NEIGHBORS,
            "rating_range": [1.0, 5.0],
        },
        "defence": {
            "method": "remove_suspicious_profiles",
            "module": "defence/remove_profiles.py",
            "decision_column": "predicted_label",
        },
        "primary_evaluation_users": sorted(int(u) for u in effect["user_id"].unique()),
    }
    if p.tf_per_user.exists():
        setup["target_frequency_sample_users"] = sorted(int(u) for u in ev.csv(p.tf_per_user)["user_id"].unique())

    counts = {s: sum(c["status"] == s for c in checks) for s in (PASS, WARN, FAIL)}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(p.root),
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "status": FAIL if counts[FAIL] else PASS,
        "summary": counts,
        "setup": setup,
        "checks": checks,
        "inputs": [_file_entry(p, f) for f in inputs],
        "outputs": [_file_entry(p, f) for f in outputs],
    }


def run_checks(root: Path = PROJECT_ROOT) -> list[dict]:
    ev = Evidence(Paths(root))
    results = []
    for check in ALL_CHECKS:
        try:
            results.extend(check(ev))
        except Exception as exc:  # a crashing check is a failed check, not a crashed verifier
            results.append(_result(check.__name__, FAIL, f"{type(exc).__name__}: {exc}"))
    return results


def main(root: Path = PROJECT_ROOT, write_manifest: bool = True) -> int:
    paths = Paths(root)
    ev = Evidence(paths)
    checks = run_checks(root)

    print("Robustness Comparison -- evidence verification")
    print("----------------------------------------------")
    for c in checks:
        print(f"[{c['status']}] {c['check']}: {c['detail']}")

    manifest = build_manifest(ev, checks)
    if write_manifest:
        paths.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"\nManifest: {paths.manifest}")

    s = manifest["summary"]
    print(f"\n{s[PASS]} passed, {s[WARN]} warnings, {s[FAIL]} failed -> {manifest['status']}")
    return 1 if s[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
