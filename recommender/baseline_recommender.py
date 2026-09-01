from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_FILE = BASE_DIR / "data" / "processed" / "train_ratings.csv"
MOVIE_STATS_FILE = BASE_DIR / "data" / "processed" / "movie_statistics.csv"

TOP_K_NEIGHBORS = 30
MIN_NEIGHBORS = 3


def load_training_data():
    """
    Load the fixed genuine training ratings.
    """
    return pd.read_csv(TRAIN_FILE)


def build_user_item_matrix(ratings):
    """
    Create a user-item matrix.

    Rows = users
    Columns = movies
    Values = ratings
    """
    return ratings.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating",
    )


def calculate_user_means(user_item_matrix):
    """
    Calculate each user's average rating.

    These means are used for mean-centred collaborative filtering.
    """
    return user_item_matrix.mean(axis=1)


def build_user_similarity_matrix(
    user_item_matrix,
    user_means,
):
    """
    Calculate cosine similarity using mean-centred user ratings.
    """

    centred_matrix = user_item_matrix.sub(
        user_means,
        axis=0,
    )

    filled_matrix = centred_matrix.fillna(0)

    similarity = cosine_similarity(filled_matrix)

    similarity_matrix = pd.DataFrame(
        similarity,
        index=user_item_matrix.index,
        columns=user_item_matrix.index,
    )

    return similarity_matrix


def predict_rating(
    user_id,
    movie_id,
    user_item_matrix,
    similarity_matrix,
    user_means,
    top_k=TOP_K_NEIGHBORS,
    min_neighbors=MIN_NEIGHBORS,
):
    """
    Predict a rating using mean-centred
    user-based collaborative filtering.
    """

    if user_id not in user_item_matrix.index:
        return None

    if movie_id not in user_item_matrix.columns:
        return None

    movie_ratings = user_item_matrix[movie_id].dropna()

    movie_ratings = movie_ratings.drop(
        labels=[user_id],
        errors="ignore",
    )

    if movie_ratings.empty:
        return None

    similarities = similarity_matrix.loc[
        user_id,
        movie_ratings.index,
    ]

    # Keep only positive similarities.
    positive_mask = similarities > 0

    similarities = similarities[positive_mask]

    if similarities.empty:
        return None

    movie_ratings = movie_ratings.loc[
        similarities.index
    ]

    # Sort neighbours by similarity.
    similarities = similarities.sort_values(
        ascending=False
    )

    # Keep only the K most similar users.
    similarities = similarities.head(top_k)

    movie_ratings = movie_ratings.loc[
        similarities.index
    ]

    if len(similarities) < min_neighbors:
        return None

    neighbour_means = user_means.loc[
        similarities.index
    ]

    deviations = (
        movie_ratings - neighbour_means
    )

    denominator = similarities.abs().sum()

    if denominator == 0:
        return None

    weighted_deviation = (
        similarities * deviations
    ).sum() / denominator

    predicted_rating = (
        user_means.loc[user_id]
        + weighted_deviation
    )

    predicted_rating = max(
        1.0,
        min(5.0, predicted_rating),
    )

    return float(predicted_rating)


def recommend_movies(
    user_id,
    user_item_matrix,
    similarity_matrix,
    user_means,
    top_n=10,
):
    """
    Generate Top-N unseen movie recommendations.
    """

    if user_id not in user_item_matrix.index:
        return []

    movie_stats = pd.read_csv(MOVIE_STATS_FILE)

    user_ratings = user_item_matrix.loc[user_id]

    unseen_movie_ids = user_ratings[
        user_ratings.isna()
    ].index

    recommendations = []

    for movie_id in unseen_movie_ids:

        predicted_rating = predict_rating(
            user_id=user_id,
            movie_id=movie_id,
            user_item_matrix=user_item_matrix,
            similarity_matrix=similarity_matrix,
            user_means=user_means,
        )

        if predicted_rating is None:
            continue

        movie_row = movie_stats[
            movie_stats["movie_id"] == movie_id
        ]

        if movie_row.empty:
            continue

        title = movie_row.iloc[0]["title"]

        recommendations.append(
            {
                "movie_id": int(movie_id),
                "title": title,
                "predicted_rating": round(
                    predicted_rating,
                    4,
                ),
            }
        )

    recommendations.sort(
        key=lambda item: item["predicted_rating"],
        reverse=True,
    )

    return recommendations[:top_n]


if __name__ == "__main__":

    ratings = load_training_data()

    user_item_matrix = build_user_item_matrix(
        ratings
    )

    user_means = calculate_user_means(
        user_item_matrix
    )

    similarity_matrix = (
        build_user_similarity_matrix(
            user_item_matrix,
            user_means,
        )
    )

    print(
        "Baseline recommender created successfully."
    )

    print()
    print(
        "Training ratings:",
        len(ratings),
    )

    print(
        "User-item matrix shape:",
        user_item_matrix.shape,
    )

    print(
        "User-similarity matrix shape:",
        similarity_matrix.shape,
    )

    test_user = 196

    recommendations = recommend_movies(
        user_id=test_user,
        user_item_matrix=user_item_matrix,
        similarity_matrix=similarity_matrix,
        user_means=user_means,
        top_n=10,
    )

    print()
    print(
        f"Top recommendations for user {test_user}:"
    )

    for rank, item in enumerate(
        recommendations,
        start=1,
    ):
        print(
            rank,
            item["movie_id"],
            item["title"],
            item["predicted_rating"],
        )