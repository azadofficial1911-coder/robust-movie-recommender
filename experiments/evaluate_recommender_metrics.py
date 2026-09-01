"""Evaluate recommendation-quality metrics (RMSE, MAE) across the fixed
genuine test set for all five Week 6 conditions:

    clean, random, random_defended, average, average_defended

Reuses Asraful's baseline collaborative-filtering recommender exactly as
evaluate_baseline.py does for the clean condition, applied to each
condition's training data in turn.
"""

import sys
import time
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from evaluation.recommender_metrics import mae, rmse  # noqa: E402
from recommender.baseline_recommender import (  # noqa: E402
    build_user_item_matrix,
    build_user_similarity_matrix,
    calculate_user_means,
    predict_rating,
)


TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test_ratings.csv"

CONDITION_PATHS = {
    "clean": PROJECT_ROOT / "data" / "processed" / "train_ratings.csv",
    "random": PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "random_pilot.csv",
    "random_defended": PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "random_defended.csv",
    "average": PROJECT_ROOT / "data" / "attacked" / "attacked_datasets" / "average_pilot.csv",
    "average_defended": PROJECT_ROOT / "data" / "attacked" / "defended_datasets" / "average_defended.csv",
}

RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
OUTPUT_PATH = RESULTS_DIR / "recommender_metrics_pilot.csv"


def evaluate_condition(condition_name: str, train_path: Path, test_data: pd.DataFrame) -> dict:
    start = time.time()

    train_ratings = pd.read_csv(train_path)
    user_item_matrix = build_user_item_matrix(train_ratings)
    user_means = calculate_user_means(user_item_matrix)
    similarity_matrix = build_user_similarity_matrix(user_item_matrix, user_means)

    actual_ratings = []
    predicted_ratings = []

    for row in test_data.itertuples(index=False):
        prediction = predict_rating(
            user_id=row.user_id,
            movie_id=row.movie_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
        )
        if prediction is None:
            continue
        actual_ratings.append(float(row.rating))
        predicted_ratings.append(float(prediction))

    total_test_ratings = len(test_data)
    predicted_count = len(predicted_ratings)
    coverage = (predicted_count / total_test_ratings) * 100 if total_test_ratings else 0.0

    result = {
        "condition": condition_name,
        "total_test_ratings": total_test_ratings,
        "predictions_produced": predicted_count,
        "coverage_percent": round(coverage, 2),
        "rmse": rmse(actual_ratings, predicted_ratings) if predicted_ratings else None,
        "mae": mae(actual_ratings, predicted_ratings) if predicted_ratings else None,
        "seconds": round(time.time() - start, 1),
    }

    print(
        f"{condition_name:16} coverage={result['coverage_percent']}% "
        f"rmse={result['rmse']} mae={result['mae']} ({result['seconds']}s)"
    )

    return result


def main() -> None:
    test_data = pd.read_csv(TEST_PATH)

    print("Week 6 recommender-metrics evaluation (RMSE / MAE)")
    print("----------------------------------------------------")
    print(f"Fixed test set size: {len(test_data)}")

    rows = [
        evaluate_condition(name, path, test_data)
        for name, path in CONDITION_PATHS.items()
    ]

    results = pd.DataFrame(rows)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_PATH, index=False)

    print("\nResults")
    print("-------")
    print(results.to_string(index=False))
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
