from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from apps.movies.models import WebsiteRating


BASE_DIR = Path(__file__).resolve().parents[3]

TRAIN_FILE = BASE_DIR / "data" / "processed" / "train_ratings.csv"
MOVIE_STATS_FILE = BASE_DIR / "data" / "processed" / "movie_statistics.csv"

TOP_K_NEIGHBORS = 30
MIN_NEIGHBORS = 3


def get_recommendations(user_id: int, top_n: int = 10) -> list[dict]:
    """
    Generate personalised recommendations for a real Django website user.

    The website user's saved ratings are compared with genuine MovieLens
    users from the fixed training dataset.
    """

    # ---------------------------------------------------------
    # 1. Load the website user's real ratings.
    # ---------------------------------------------------------

    website_ratings = list(
        WebsiteRating.objects.filter(user_id=user_id).values(
            "movie_id",
            "rating",
        )
    )

    # A personalised CF model needs some rating history.
    if len(website_ratings) < 3:
        return []

    user_profile = pd.DataFrame(website_ratings)

    # ---------------------------------------------------------
    # 2. Load genuine MovieLens training data.
    # ---------------------------------------------------------

    train_ratings = pd.read_csv(TRAIN_FILE)

    user_item_matrix = train_ratings.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating",
    )

    movie_stats = pd.read_csv(MOVIE_STATS_FILE)

    # ---------------------------------------------------------
    # 3. Find movies shared between the website user and
    #    MovieLens training data.
    # ---------------------------------------------------------

    website_movie_ids = set(user_profile["movie_id"])

    common_movies = [
        movie_id
        for movie_id in website_movie_ids
        if movie_id in user_item_matrix.columns
    ]

    if len(common_movies) < 3:
        return []

    # Website-user ratings for common movies.
    website_series = (
        user_profile[
            user_profile["movie_id"].isin(common_movies)
        ]
        .set_index("movie_id")["rating"]
        .reindex(common_movies)
        .astype(float)
    )

    website_mean = website_series.mean()

    website_centred = (
        website_series - website_mean
    )

    # ---------------------------------------------------------
    # 4. Calculate similarity between the website user
    #    and each MovieLens user.
    # ---------------------------------------------------------

    similarities = {}

    for movie_user_id, row in user_item_matrix[
        common_movies
    ].iterrows():

        neighbour_ratings = row.dropna()

        shared_movies = neighbour_ratings.index.intersection(
            website_series.index
        )

        if len(shared_movies) < 2:
            continue

        active_values = website_series.loc[
            shared_movies
        ]

        neighbour_values = neighbour_ratings.loc[
            shared_movies
        ]

        active_centred = (
            active_values - active_values.mean()
        ).values.reshape(1, -1)

        neighbour_centred = (
            neighbour_values - neighbour_values.mean()
        ).values.reshape(1, -1)

        # Skip profiles with no rating variation.
        if (
            (active_centred == 0).all()
            or (neighbour_centred == 0).all()
        ):
            continue

        similarity = cosine_similarity(
            active_centred,
            neighbour_centred,
        )[0][0]

        if similarity > 0:
            similarities[movie_user_id] = float(similarity)

    if not similarities:
        return []

    similarity_series = pd.Series(similarities).sort_values(
        ascending=False
    )

    # Keep the most similar users.
    similarity_series = similarity_series.head(
        TOP_K_NEIGHBORS
    )

    # ---------------------------------------------------------
    # 5. Predict ratings for movies the website user
    #    has not already rated.
    # ---------------------------------------------------------

    rated_movie_ids = set(
        user_profile["movie_id"]
    )

    recommendations = []

    for movie_id in user_item_matrix.columns:

        if movie_id in rated_movie_ids:
            continue

        neighbour_ratings = user_item_matrix.loc[
            similarity_series.index,
            movie_id,
        ].dropna()

        if len(neighbour_ratings) < MIN_NEIGHBORS:
            continue

        relevant_similarities = similarity_series.loc[
            neighbour_ratings.index
        ]

        neighbour_means = user_item_matrix.loc[
            neighbour_ratings.index
        ].mean(axis=1)

        deviations = (
            neighbour_ratings - neighbour_means
        )

        denominator = relevant_similarities.abs().sum()

        if denominator == 0:
            continue

        weighted_deviation = (
            relevant_similarities * deviations
        ).sum() / denominator

        prediction = (
            website_mean + weighted_deviation
        )

        prediction = max(
            1.0,
            min(5.0, prediction),
        )

        movie_row = movie_stats[
            movie_stats["movie_id"] == movie_id
        ]

        if movie_row.empty:
            continue

        recommendations.append(
            {
                "movie_id": int(movie_id),
                "title": str(
                    movie_row.iloc[0]["title"]
                ),
                "predicted_rating": round(
                    float(prediction),
                    4,
                ),
            }
        )

    # ---------------------------------------------------------
    # 6. Return highest predicted movies.
    # ---------------------------------------------------------

    recommendations.sort(
        key=lambda item: item["predicted_rating"],
        reverse=True,
    )

    return recommendations[:top_n]