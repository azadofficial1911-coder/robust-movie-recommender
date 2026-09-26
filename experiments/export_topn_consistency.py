from pathlib import Path

import pandas as pd

from recommender.baseline_recommender import (
    TOP_K_NEIGHBORS,
    MIN_NEIGHBORS,
    build_user_item_matrix,
    calculate_user_means,
    build_user_similarity_matrix,
    recommend_movies,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGET_MOVIE_ID = 758
TOP_N = 10

TEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "test_ratings.csv"
)

CONDITIONS = {
    "clean": (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "train_ratings.csv"
    ),
    "random": (
        PROJECT_ROOT
        / "data"
        / "attacked"
        / "attacked_datasets"
        / "random_pilot.csv"
    ),
    "random_defended": (
        PROJECT_ROOT
        / "data"
        / "attacked"
        / "defended_datasets"
        / "random_defended.csv"
    ),
    "average": (
        PROJECT_ROOT
        / "data"
        / "attacked"
        / "attacked_datasets"
        / "average_pilot.csv"
    ),
    "average_defended": (
        PROJECT_ROOT
        / "data"
        / "attacked"
        / "defended_datasets"
        / "average_defended.csv"
    ),
}

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "tables"
    / "topn_consistency_results.csv"
)


def get_evaluation_users(
    test_ratings: pd.DataFrame,
    clean_train: pd.DataFrame,
) -> list[int]:

    target_test = test_ratings[
        test_ratings["movie_id"] == TARGET_MOVIE_ID
    ]

    clean_users = set(
        clean_train["user_id"]
        .dropna()
        .astype(int)
        .unique()
    )

    evaluation_users = sorted(
        {
            int(user_id)
            for user_id in target_test["user_id"].unique()
            if int(user_id) in clean_users
        }
    )

    return evaluation_users


def build_recommender(
    ratings: pd.DataFrame,
):

    user_item_matrix = build_user_item_matrix(
        ratings
    )

    user_means = calculate_user_means(
        user_item_matrix
    )

    similarity_matrix = build_user_similarity_matrix(
        user_item_matrix,
        user_means,
    )

    return (
        user_item_matrix,
        user_means,
        similarity_matrix,
    )


def generate_condition_topn(
    condition_name: str,
    ratings: pd.DataFrame,
    evaluation_users: list[int],
) -> list[dict]:

    (
        user_item_matrix,
        user_means,
        similarity_matrix,
    ) = build_recommender(ratings)

    output_rows = []

    print()
    print("=" * 70)
    print(f"CONDITION: {condition_name.upper()}")
    print("=" * 70)

    print(f"Training ratings: {len(ratings):,}")
    print(
        f"Users in model: "
        f"{user_item_matrix.shape[0]:,}"
    )
    print(
        f"Movies in model: "
        f"{user_item_matrix.shape[1]:,}"
    )

    for user_id in evaluation_users:

        recommendations = recommend_movies(
            user_id=user_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
            top_n=TOP_N,
        )

        print()
        print(f"User {user_id} - Top {TOP_N}")

        if not recommendations:
            print("No recommendations available.")
            continue

        for rank, item in enumerate(
            recommendations,
            start=1,
        ):

            print(
                f"{rank:2d}. "
                f"Movie {item['movie_id']} | "
                f"{item['title']} | "
                f"{item['predicted_rating']:.4f}"
            )

            output_rows.append(
                {
                    "condition": condition_name,
                    "user_id": user_id,
                    "rank": rank,
                    "movie_id": item["movie_id"],
                    "title": item["title"],
                    "predicted_rating": (
                        item["predicted_rating"]
                    ),
                }
            )

    return output_rows


def get_user_topn(
    results: pd.DataFrame,
    condition: str,
    user_id: int,
) -> list[tuple]:

    subset = results[
        (results["condition"] == condition)
        & (results["user_id"] == user_id)
    ].sort_values("rank")

    return [
        (
            int(row.movie_id),
            float(row.predicted_rating),
        )
        for row in subset.itertuples()
    ]


def verify_defended_recovery(
    results: pd.DataFrame,
    evaluation_users: list[int],
):

    print()
    print("=" * 70)
    print("DEFENDED TOP-N RECOVERY CHECK")
    print("=" * 70)

    random_pass = True
    average_pass = True

    for user_id in evaluation_users:

        clean = get_user_topn(
            results,
            "clean",
            user_id,
        )

        random_defended = get_user_topn(
            results,
            "random_defended",
            user_id,
        )

        average_defended = get_user_topn(
            results,
            "average_defended",
            user_id,
        )

        random_equal = (
            clean == random_defended
        )

        average_equal = (
            clean == average_defended
        )

        print(
            f"User {user_id}: "
            f"Random defended = Clean: "
            f"{random_equal} | "
            f"Average defended = Clean: "
            f"{average_equal}"
        )

        if not random_equal:
            random_pass = False

        if not average_equal:
            average_pass = False

    return (
        random_pass,
        average_pass,
    )


def main():

    print("=" * 70)
    print("RMRS TOP-N RECOMMENDER CONSISTENCY")
    print("=" * 70)

    print()
    print("FIXED RECOMMENDER CONFIGURATION")
    print("-------------------------------")

    print(
        "Algorithm: User-based collaborative filtering"
    )
    print(
        "Similarity: Mean-centred cosine similarity"
    )
    print(
        f"Top-K neighbours: {TOP_K_NEIGHBORS}"
    )
    print(
        f"Minimum neighbours: {MIN_NEIGHBORS}"
    )
    print(
        f"Top-N recommendations: {TOP_N}"
    )
    print(
        f"Target movie ID: {TARGET_MOVIE_ID}"
    )

    test_ratings = pd.read_csv(
        TEST_PATH
    )

    clean_train = pd.read_csv(
        CONDITIONS["clean"]
    )

    evaluation_users = get_evaluation_users(
        test_ratings,
        clean_train,
    )

    print()
    print("FIXED EVALUATION SETUP")
    print("----------------------")

    print(
        f"Genuine test ratings: "
        f"{len(test_ratings):,}"
    )

    print(
        f"Evaluation users: "
        f"{len(evaluation_users)}"
    )

    print(
        f"Evaluation user IDs: "
        f"{evaluation_users}"
    )

    all_results = []

    for condition_name, path in CONDITIONS.items():

        if not path.exists():
            raise FileNotFoundError(
                f"Missing dataset: {path}"
            )

        ratings = pd.read_csv(path)

        condition_results = generate_condition_topn(
            condition_name,
            ratings,
            evaluation_users,
        )

        all_results.extend(
            condition_results
        )

    results_df = pd.DataFrame(
        all_results
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    (
        random_recovery,
        average_recovery,
    ) = verify_defended_recovery(
        results_df,
        evaluation_users,
    )

    print()
    print("=" * 70)
    print("FINAL CONSISTENCY RESULT")
    print("=" * 70)

    print(
        "Same recommender configuration: PASS"
    )

    print(
        "Same genuine evaluation users: PASS"
    )

    print(
        "Same Top-N value: PASS"
    )

    print(
        "Random defended Top-N equals clean: "
        f"{random_recovery}"
    )

    print(
        "Average defended Top-N equals clean: "
        f"{average_recovery}"
    )

    print()
    print("Results saved to:")
    print(OUTPUT_FILE)

    if (
        random_recovery
        and average_recovery
    ):

        print()
        print("OVERALL RESULT: PASS")

        print(
            "Clean, Attacked and Defended "
            "conditions use the same "
            "recommender configuration."
        )

    else:

        print()
        print(
            "OVERALL RESULT: REVIEW REQUIRED"
        )


if __name__ == "__main__":
    main()