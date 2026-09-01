"""Evaluate the Week 6 pilot defence effect on the recommender.

Extends Azad's Clean vs Random vs Average attack-effect evaluation
(experiments/evaluate_attack_effect.py) with the two defended
conditions, so the full comparison is:

    clean  ->  random  ->  random_defended
           ->  average ->  average_defended

Uses the exact same evaluation users, target movie, and Top-K as the
attack-effect evaluation so results are directly comparable.
"""

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from evaluation.attack_metrics import hit_rate, target_rank, target_score  # noqa: E402
from recommender.baseline_recommender import (  # noqa: E402
    build_user_item_matrix,
    build_user_similarity_matrix,
    calculate_user_means,
    predict_rating,
    recommend_movies,
)


TARGET_MOVIE_ID = 758
TOP_K = 10

CLEAN_PATH = PROJECT_ROOT / "data" / "processed" / "train_ratings.csv"
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test_ratings.csv"

RANDOM_ATTACK_PATH = PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "random_pilot.csv"
AVERAGE_ATTACK_PATH = PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "average_pilot.csv"

RANDOM_DEFENDED_PATH = PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "random_defended.csv"
AVERAGE_DEFENDED_PATH = PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "average_defended.csv"

RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
PER_USER_OUTPUT = RESULTS_DIR / "defence_effect_pilot_per_user.csv"
SUMMARY_OUTPUT = RESULTS_DIR / "defence_effect_pilot_summary.csv"


def build_recommender_state(ratings: pd.DataFrame):
    user_item_matrix = build_user_item_matrix(ratings)
    user_means = calculate_user_means(user_item_matrix)
    similarity_matrix = build_user_similarity_matrix(user_item_matrix, user_means)
    return user_item_matrix, similarity_matrix, user_means


def get_evaluation_users(test_ratings: pd.DataFrame, clean_train: pd.DataFrame) -> list[int]:
    """Genuine users with the target movie held out in the fixed test set."""
    target_test = test_ratings[test_ratings["movie_id"] == TARGET_MOVIE_ID]
    candidate_users = sorted(int(u) for u in target_test["user_id"].unique())

    evaluation_users = []
    for user_id in candidate_users:
        in_train = clean_train[
            (clean_train["user_id"] == user_id) & (clean_train["movie_id"] == TARGET_MOVIE_ID)
        ]
        if in_train.empty:
            evaluation_users.append(user_id)

    if not evaluation_users:
        raise ValueError("No valid held-out evaluation users were found.")
    return evaluation_users


def evaluate_condition(condition_name: str, ratings: pd.DataFrame, evaluation_users: list[int]) -> list[dict]:
    user_item_matrix, similarity_matrix, user_means = build_recommender_state(ratings)

    results = []
    total_movies = len(user_item_matrix.columns)

    for user_id in evaluation_users:
        predicted_target_score = predict_rating(
            user_id=user_id,
            movie_id=TARGET_MOVIE_ID,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
        )

        recommendations = recommend_movies(
            user_id=user_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
            top_n=total_movies,
        )

        recommended_movie_ids = [item["movie_id"] for item in recommendations]
        predicted_scores = {item["movie_id"]: item["predicted_rating"] for item in recommendations}

        rank = target_rank(recommended_movie_ids, TARGET_MOVIE_ID)
        score = target_score(predicted_scores, TARGET_MOVIE_ID)

        if score is None and predicted_target_score is not None:
            score = float(predicted_target_score)

        hit_at_10 = rank is not None and rank <= TOP_K

        results.append(
            {
                "condition": condition_name,
                "user_id": user_id,
                "target_movie_id": TARGET_MOVIE_ID,
                "target_score": score,
                "target_rank": rank,
                "hit_at_10": hit_at_10,
                "target_predictable": predicted_target_score is not None,
            }
        )

        print(f"{condition_name:16} user={user_id:<3} score={score} rank={rank} hit@10={hit_at_10}")

    return results


def build_summary(per_user_results: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for condition, group in per_user_results.groupby("condition", sort=False):
        valid_scores = group["target_score"].dropna()
        valid_ranks = group["target_rank"].dropna()
        hits = group["hit_at_10"].tolist()

        summary_rows.append(
            {
                "condition": condition,
                "evaluation_users": len(group),
                "predictable_users": int(group["target_predictable"].sum()),
                "mean_target_score": valid_scores.mean() if not valid_scores.empty else None,
                "mean_target_rank": valid_ranks.mean() if not valid_ranks.empty else None,
                "median_target_rank": valid_ranks.median() if not valid_ranks.empty else None,
                "hit_rate_at_10": hit_rate(hits),
            }
        )
    return pd.DataFrame(summary_rows)


def main() -> None:
    clean_train = pd.read_csv(CLEAN_PATH)
    test_ratings = pd.read_csv(TEST_PATH)
    random_attacked = pd.read_csv(RANDOM_ATTACK_PATH)
    average_attacked = pd.read_csv(AVERAGE_ATTACK_PATH)
    random_defended = pd.read_csv(RANDOM_DEFENDED_PATH)
    average_defended = pd.read_csv(AVERAGE_DEFENDED_PATH)

    evaluation_users = get_evaluation_users(test_ratings, clean_train)

    print("Week 6 defence-effect evaluation")
    print("---------------------------------")
    print(f"Target movie: {TARGET_MOVIE_ID}")
    print("Evaluation users:", evaluation_users)

    conditions = [
        ("clean", clean_train),
        ("random", random_attacked),
        ("random_defended", random_defended),
        ("average", average_attacked),
        ("average_defended", average_defended),
    ]

    all_results = []
    for condition_name, ratings in conditions:
        print(f"\nEvaluating {condition_name.upper()} condition...")
        all_results.extend(evaluate_condition(condition_name, ratings, evaluation_users))

    per_user_results = pd.DataFrame(all_results)
    summary = build_summary(per_user_results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    per_user_results.to_csv(PER_USER_OUTPUT, index=False)
    summary.to_csv(SUMMARY_OUTPUT, index=False)

    print("\nSummary")
    print("-------")
    print(summary.to_string(index=False))

    print("\nSaved:")
    print(PER_USER_OUTPUT)
    print(SUMMARY_OUTPUT)


if __name__ == "__main__":
    main()
