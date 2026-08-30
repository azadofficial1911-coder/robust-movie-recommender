from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent.parent

RATINGS_FILE = BASE_DIR / "data" / "processed" / "ratings_clean.csv"

TRAIN_FILE = BASE_DIR / "data" / "processed" / "train_ratings.csv"
TEST_FILE = BASE_DIR / "data" / "processed" / "test_ratings.csv"

RANDOM_SEED = 42
TEST_SIZE = 0.20


def create_train_test_split():
    """
    Create a reproducible train/test split of genuine MovieLens ratings.

    Every user and every movie must remain represented in the training set.
    The resulting test set can then be reused for clean, attacked,
    and defended experiments.
    """

    ratings = pd.read_csv(RATINGS_FILE)

    train_data, test_data = train_test_split(
        ratings,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        shuffle=True,
    )

    # ---------------------------------------------------------
    # Ensure every user appearing in the full dataset also
    # appears in the training set.
    # ---------------------------------------------------------

    all_users = set(ratings["user_id"].unique())
    train_users = set(train_data["user_id"].unique())

    missing_users = all_users - train_users

    for user_id in missing_users:
        candidate_rows = test_data[
            test_data["user_id"] == user_id
        ]

        if not candidate_rows.empty:
            row_index = candidate_rows.index[0]

            train_data = pd.concat(
                [train_data, test_data.loc[[row_index]]]
            )

            test_data = test_data.drop(row_index)

    # ---------------------------------------------------------
    # Ensure every movie appearing in the full dataset also
    # appears in the training set.
    # ---------------------------------------------------------

    all_movies = set(ratings["movie_id"].unique())
    train_movies = set(train_data["movie_id"].unique())

    missing_movies = all_movies - train_movies

    for movie_id in missing_movies:
        candidate_rows = test_data[
            test_data["movie_id"] == movie_id
        ]

        if not candidate_rows.empty:
            row_index = candidate_rows.index[0]

            train_data = pd.concat(
                [train_data, test_data.loc[[row_index]]]
            )

            test_data = test_data.drop(row_index)

    # Reset indexes after moving rows.
    train_data = train_data.reset_index(drop=True)
    test_data = test_data.reset_index(drop=True)

    # Save the fixed datasets.
    train_data.to_csv(TRAIN_FILE, index=False)
    test_data.to_csv(TEST_FILE, index=False)

    print("Train/Test split created successfully.")
    print()
    print("Random seed:", RANDOM_SEED)
    print("Requested test size:", TEST_SIZE)
    print()

    print("Training ratings:", len(train_data))
    print("Test ratings:", len(test_data))
    print()

    print("Training users:", train_data["user_id"].nunique())
    print("Test users:", test_data["user_id"].nunique())
    print()

    print("Training movies:", train_data["movie_id"].nunique())
    print("Test movies:", test_data["movie_id"].nunique())
    print()

    print(
        "Minimum training ratings per user:",
        train_data.groupby("user_id").size().min(),
    )

    print()
    print("Saved training data to:")
    print(TRAIN_FILE)

    print()
    print("Saved test data to:")
    print(TEST_FILE)


if __name__ == "__main__":
    create_train_test_split()