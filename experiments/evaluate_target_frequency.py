"""Supplementary target-frequency evaluation for the Robustness Comparison.

Why this exists
---------------
The primary attack-effect metrics (experiments/evaluate_defence_effect.py)
are measured on the 7 genuine users who have the target movie held out in
the fixed test set. With only 7 users, Hit Rate@10 is 0.0 in every
condition, so it cannot show attack damage or defence recovery.

This script measures *target frequency* -- how often the target movie
appears in genuine users' Top-K lists -- over a wider, fixed, seeded
sample of genuine users. It is reported alongside (never instead of) the
primary 7-user metrics.

Fairness rules (same as the rest of the comparison)
---------------------------------------------------
- Same recommender: reuses build_recommender_state() from
  evaluate_defence_effect.py, i.e. Asraful's baseline user-based CF with
  the same cosine similarity, Top-K neighbours and minimum-neighbour rule.
- Same users in every condition: the sample is drawn once from the clean
  genuine training data (users who have not rated the target movie) and
  reused unchanged for clean, attacked and defended conditions.
- Only the training data changes between conditions.

Outputs
-------
results/tables/target_frequency_per_user.csv
results/tables/target_frequency_summary.csv
"""

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from evaluation.attack_metrics import target_rank  # noqa: E402
from experiments.evaluate_defence_effect import build_recommender_state  # noqa: E402
from experiments.evaluate_recommender_metrics import CONDITION_PATHS  # noqa: E402
from recommender.baseline_recommender import recommend_movies  # noqa: E402


ATTACK_CONFIG_PATH = PROJECT_ROOT / "experiments" / "configs" / "attack_config.json"

RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
PER_USER_OUTPUT = RESULTS_DIR / "target_frequency_per_user.csv"
SUMMARY_OUTPUT = RESULTS_DIR / "target_frequency_summary.csv"

DEFAULT_SAMPLE_SIZE = 100
K_VALUES = (10, 50, 100)


def load_attack_config() -> dict:
    with ATTACK_CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def select_sample_users(clean_train: pd.DataFrame, target_movie_id: int,
                        sample_size: int, seed: int) -> list[int]:
    """Fixed seeded sample of genuine users who have not rated the target
    movie in the clean training data (so the target is a candidate for
    their recommendation list in every condition)."""

    raters = set(clean_train.loc[clean_train["movie_id"] == target_movie_id, "user_id"])
    eligible = sorted(int(u) for u in clean_train["user_id"].unique() if u not in raters)

    if sample_size >= len(eligible):
        return eligible

    rng = np.random.RandomState(seed)
    chosen = rng.choice(eligible, size=sample_size, replace=False)
    return sorted(int(u) for u in chosen)


def evaluate_condition(args: tuple) -> list[dict]:
    """Rank the target movie for every sampled user under one condition."""

    condition_name, train_path, users, target_movie_id = args
    start = time.time()

    ratings = pd.read_csv(train_path)
    user_item_matrix, similarity_matrix, user_means = build_recommender_state(ratings)
    total_movies = len(user_item_matrix.columns)

    rows = []
    for user_id in users:
        recommendations = recommend_movies(
            user_id=user_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
            top_n=total_movies,
        )
        ranked_ids = [item["movie_id"] for item in recommendations]
        rank = target_rank(ranked_ids, target_movie_id)

        row = {
            "condition": condition_name,
            "user_id": user_id,
            "target_movie_id": target_movie_id,
            "target_rank": rank,
            "candidate_movies": len(ranked_ids),
        }
        for k in K_VALUES:
            row[f"hit_at_{k}"] = rank is not None and rank <= k
        rows.append(row)

    print(f"{condition_name:16} {len(users)} users ranked in {time.time() - start:.1f}s", flush=True)
    return rows


def build_summary(per_user: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for condition, group in per_user.groupby("condition", sort=False):
        ranks = group["target_rank"].dropna()
        row = {
            "condition": condition,
            "sample_users": len(group),
            "ranked_users": int(group["target_rank"].notna().sum()),
            "mean_target_rank": ranks.mean() if not ranks.empty else None,
            "median_target_rank": ranks.median() if not ranks.empty else None,
        }
        for k in K_VALUES:
            # Denominator is every sampled user: an unrankable target counts as a miss.
            row[f"target_freq_at_{k}"] = group[f"hit_at_{k}"].astype(bool).mean()
        summary_rows.append(row)
    return pd.DataFrame(summary_rows)


def main(sample_size: int = DEFAULT_SAMPLE_SIZE, workers: int = 2) -> None:
    config = load_attack_config()
    target_movie_id = int(config["target_movie_id"])
    seed = int(config["random_seed"])

    clean_train = pd.read_csv(CONDITION_PATHS["clean"])
    users = select_sample_users(clean_train, target_movie_id, sample_size, seed)

    print("Target-frequency evaluation (supplementary, wider genuine-user sample)")
    print("-----------------------------------------------------------------------")
    print(f"Target movie: {target_movie_id} | seed: {seed} | sample users: {len(users)}")

    jobs = [(name, path, users, target_movie_id) for name, path in CONDITION_PATHS.items()]

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(evaluate_condition, jobs))
    else:
        results = [evaluate_condition(job) for job in jobs]

    per_user = pd.DataFrame([row for rows in results for row in rows])
    per_user["target_rank"] = per_user["target_rank"].astype("Int64")
    summary = build_summary(per_user)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    per_user.to_csv(PER_USER_OUTPUT, index=False)
    summary.to_csv(SUMMARY_OUTPUT, index=False)

    print("\nSummary")
    print("-------")
    print(summary.to_string(index=False))
    print(f"\nSaved: {PER_USER_OUTPUT}\nSaved: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    parser.add_argument("--workers", type=int, default=2)
    cli = parser.parse_args()
    main(sample_size=cli.sample_size, workers=cli.workers)
