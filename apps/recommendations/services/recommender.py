from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from apps.movies.models import WebsiteRating


BASE_DIR = Path(__file__).resolve().parents[3]

TRAIN_FILE = BASE_DIR / "data" / "processed" / "train_ratings.csv"
MOVIE_STATS_FILE = BASE_DIR / "data" / "processed" / "movie_statistics.csv"

TOP_K_NEIGHBORS = 30
MIN_NEIGHBORS = 3


def _load_training_ratings(training_ratings=None) -> pd.DataFrame:
    """Return a defensive copy of the requested training dataset."""

    if training_ratings is None:
        return pd.read_csv(TRAIN_FILE)

    if not isinstance(training_ratings, pd.DataFrame):
        raise TypeError("training_ratings must be a pandas DataFrame.")

    required_columns = {"user_id", "movie_id", "rating"}
    missing_columns = required_columns.difference(training_ratings.columns)

    if missing_columns:
        raise ValueError(
            "training_ratings is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    return training_ratings[
        ["user_id", "movie_id", "rating"]
    ].copy(deep=True)


def _load_movie_stats(movie_stats=None) -> pd.DataFrame:
    """Return movie metadata/statistics for recommendation output."""

    if movie_stats is None:
        return pd.read_csv(MOVIE_STATS_FILE)

    if not isinstance(movie_stats, pd.DataFrame):
        raise TypeError("movie_stats must be a pandas DataFrame.")

    required_columns = {"movie_id"}
    missing_columns = required_columns.difference(movie_stats.columns)

    if missing_columns:
        raise ValueError(
            "movie_stats is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    return movie_stats.copy(deep=True)


def get_recommendations(
    user_id: int,
    top_n: int = 10,
    *,
    training_ratings=None,
    movie_stats=None,
    candidate_movie_ids=None,
) -> list[dict]:
    """
    Generate personalised recommendations for a real Django website user.

    By default this uses the fixed genuine MovieLens training dataset.
    Research/demo callers may pass an alternative ratings DataFrame so the
    exact same collaborative-filtering logic can be evaluated on clean,
    attacked, and defended data.
    """

    website_ratings = list(
        WebsiteRating.objects.filter(user_id=user_id).values(
            "movie_id",
            "rating",
        )
    )

    if len(website_ratings) < 3:
        return []

    user_profile = pd.DataFrame(website_ratings)

    train_ratings = _load_training_ratings(
        training_ratings
    )

    user_item_matrix = train_ratings.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating",
    )

    movie_stats_frame = _load_movie_stats(
        movie_stats
    )

    website_movie_ids = set(
        user_profile["movie_id"].astype(int)
    )

    common_movies = [
        int(movie_id)
        for movie_id in website_movie_ids
        if int(movie_id) in user_item_matrix.columns
    ]

    if len(common_movies) < 3:
        return []

    website_series = (
        user_profile[
            user_profile["movie_id"].isin(common_movies)
        ]
        .set_index("movie_id")["rating"]
        .reindex(common_movies)
        .astype(float)
    )

    website_mean = website_series.mean()

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

    similarity_series = pd.Series(
        similarities
    ).sort_values(
        ascending=False
    ).head(
        TOP_K_NEIGHBORS
    )

    rated_movie_ids = set(
        user_profile["movie_id"].astype(int)
    )

    allowed_movie_ids = None

    if candidate_movie_ids is not None:
        allowed_movie_ids = {
            int(movie_id)
            for movie_id in candidate_movie_ids
        }

    recommendations = []

    for movie_id in user_item_matrix.columns:

        movie_id = int(movie_id)

        if movie_id in rated_movie_ids:
            continue

        if (
            allowed_movie_ids is not None
            and movie_id not in allowed_movie_ids
        ):
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

        movie_row = movie_stats_frame[
            movie_stats_frame["movie_id"] == movie_id
        ]

        title = f"Movie {movie_id}"

        if (
            not movie_row.empty
            and "title" in movie_stats_frame.columns
        ):
            title = str(
                movie_row.iloc[0]["title"]
            )

        recommendations.append(
            {
                "movie_id": movie_id,
                "title": title,
                "predicted_rating": round(
                    float(prediction),
                    4,
                ),
            }
        )

    recommendations.sort(
        key=lambda item: item["predicted_rating"],
        reverse=True,
    )

    return recommendations[:top_n]
