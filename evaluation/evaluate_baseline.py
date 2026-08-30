from pathlib import Path

import pandas as pd

from evaluation.recommender_metrics import mae, rmse
from recommender.baseline_recommender import (
    build_user_item_matrix,
    build_user_similarity_matrix,
    calculate_user_means,
    load_training_data,
    predict_rating,
)


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_FILE = BASE_DIR / "data" / "processed" / "test_ratings.csv"


def evaluate_baseline():
    """
    Evaluate the baseline collaborative-filtering recommender
    using the fixed genuine MovieLens test set.
    """

    print("Loading training data...")

    train_ratings = load_training_data()

    print("Building user-item matrix...")

    user_item_matrix = build_user_item_matrix(
        train_ratings
    )

    user_means = calculate_user_means(
        user_item_matrix
    )

    print("Building user similarity matrix...")

    similarity_matrix = build_user_similarity_matrix(
        user_item_matrix,
        user_means,
    )

    print("Loading fixed test set...")

    test_data = pd.read_csv(TEST_FILE)

    actual_ratings = []
    predicted_ratings = []

    total_test_ratings = len(test_data)

    print("Generating test predictions...")

    for row in test_data.itertuples(index=False):

        prediction = predict_rating(
            user_id=row.user_id,
            movie_id=row.movie_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
        )

        # Some predictions may not have enough neighbours.
        if prediction is None:
            continue

        actual_ratings.append(
            float(row.rating)
        )

        predicted_ratings.append(
            float(prediction)
        )

    predicted_count = len(predicted_ratings)

    coverage = (
        predicted_count / total_test_ratings
    ) * 100

    print()
    print("===== BASELINE EVALUATION =====")
    print()

    print(
        "Total test ratings:",
        total_test_ratings,
    )

    print(
        "Predictions produced:",
        predicted_count,
    )

    print(
        "Prediction coverage:",
        f"{coverage:.2f}%",
    )

    if predicted_count == 0:
        print(
            "No predictions available for evaluation."
        )
        return

    baseline_rmse = rmse(
        actual_ratings,
        predicted_ratings,
    )

    baseline_mae = mae(
        actual_ratings,
        predicted_ratings,
    )

    print()
    print(
        "RMSE:",
        round(baseline_rmse, 4),
    )

    print(
        "MAE:",
        round(baseline_mae, 4),
    )


if __name__ == "__main__":
    evaluate_baseline()