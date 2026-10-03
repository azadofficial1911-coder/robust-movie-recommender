from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from apps.movies.models import WebsiteRating


BASE_DIR = Path(__file__).resolve().parents[3]

TRAIN_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "train_ratings.csv"
)

MOVIE_STATS_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "movie_statistics.csv"
)

TOP_K_NEIGHBORS = 30
MIN_NEIGHBORS = 3

REQUIRED_RATING_COLUMNS = {
    "user_id",
    "movie_id",
    "rating",
}


def _prepare_training_ratings(
    ratings_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Return the ratings dataset used by the recommender.

    If ratings_data is supplied, the exact supplied dataset is used.
    Otherwise the existing clean MovieLens training dataset is loaded.

    This allows the same recommender implementation to run against:

    - clean ratings
    - attacked ratings
    - defended ratings

    without changing the recommendation algorithm.
    """

    if ratings_data is None:
        ratings = pd.read_csv(TRAIN_FILE)
    else:
        if not isinstance(
            ratings_data,
            pd.DataFrame,
        ):
            raise TypeError(
                "ratings_data must be a pandas DataFrame "
                "or None."
            )

        ratings = ratings_data.copy()

    missing_columns = (
        REQUIRED_RATING_COLUMNS
        - set(ratings.columns)
    )

    if missing_columns:
        raise ValueError(
            "Ratings data is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if ratings.empty:
        raise ValueError(
            "Ratings data cannot be empty."
        )

    ratings["user_id"] = pd.to_numeric(
        ratings["user_id"],
        errors="raise",
    ).astype(int)

    ratings["movie_id"] = pd.to_numeric(
        ratings["movie_id"],
        errors="raise",
    ).astype(int)

    ratings["rating"] = pd.to_numeric(
        ratings["rating"],
        errors="raise",
    ).astype(float)

    return ratings


def _load_movie_stats() -> pd.DataFrame:
    """
    Load movie metadata used for the existing website
    title and the demo display-name fallback.
    """

    movie_stats = pd.read_csv(
        MOVIE_STATS_FILE
    )

    if "movie_id" not in movie_stats.columns:
        raise ValueError(
            "movie_statistics.csv must contain "
            "a movie_id column."
        )

    movie_stats["movie_id"] = pd.to_numeric(
        movie_stats["movie_id"],
        errors="raise",
    ).astype(int)

    return movie_stats


def _load_website_profile(
    user_id: int,
) -> pd.DataFrame:
    """
    Load the logged-in website user's ratings.

    This preserves the existing WebsiteRating-based
    personalisation behaviour.
    """

    website_ratings = list(
        WebsiteRating.objects.filter(
            user_id=user_id
        ).values(
            "movie_id",
            "rating",
        )
    )

    if not website_ratings:
        return pd.DataFrame(
            columns=[
                "movie_id",
                "rating",
            ]
        )

    profile = pd.DataFrame(
        website_ratings
    )

    profile["movie_id"] = pd.to_numeric(
        profile["movie_id"],
        errors="raise",
    ).astype(int)

    profile["rating"] = pd.to_numeric(
        profile["rating"],
        errors="raise",
    ).astype(float)

    return profile


def _normalise_candidate_ids(
    candidate_movie_ids: Iterable[int] | None,
) -> set[int] | None:
    """
    Convert an optional candidate movie collection
    into stable integer backend IDs.
    """

    if candidate_movie_ids is None:
        return None

    return {
        int(movie_id)
        for movie_id in candidate_movie_ids
    }


def _normalise_display_names(
    display_name_map: Mapping[int, str] | None,
) -> dict[int, str]:
    """
    Convert an optional backend-ID -> display-name
    mapping into a normalised dictionary.

    The alias affects presentation only. It never
    changes the backend movie ID used for scoring.
    """

    if display_name_map is None:
        return {}

    return {
        int(movie_id): str(display_name)
        for movie_id, display_name
        in display_name_map.items()
    }


def get_recommendations(
    user_id: int,
    top_n: int = 10,
    ratings_data: pd.DataFrame | None = None,
    candidate_movie_ids: Iterable[int] | None = None,
    display_name_map: Mapping[int, str] | None = None,
) -> list[dict]:
    """
    Generate personalised recommendations for a
    real Django website user.

    The exact same user-based collaborative-filtering
    implementation can operate on clean, attacked,
    or defended training ratings.

    Parameters
    ----------
    user_id:
        Django website user ID.

    top_n:
        Number of highest-ranked recommendations
        to return.

    ratings_data:
        Optional training ratings DataFrame.

        When None, the existing clean training file
        is loaded.

        When supplied, the exact provided DataFrame
        is used. This enables clean / attacked /
        defended comparison using one recommender.

    candidate_movie_ids:
        Optional backend movie IDs that restrict
        which movies can appear in the returned
        recommendation list.

        This will be used for the controlled
        38-movie demonstration catalogue.

    display_name_map:
        Optional mapping:

            movie_id -> presentation display name

        Example:

            {
                50: "Good Movie 1",
                758: "Targeted Movie 1",
            }

        Aliases do not affect recommendation scores
        or backend IDs.

    Returns
    -------
    list[dict]

        Ranked recommendation objects containing:

        - movie_id
        - display_name
        - predicted_score
        - rank
        - reason

        Legacy fields are also retained:

        - title
        - predicted_rating

        so the existing website remains compatible
        during the refactor.
    """

    if top_n < 1:
        return []

    # ---------------------------------------------------------
    # 1. Load the real website user's rating profile.
    # ---------------------------------------------------------

    user_profile = _load_website_profile(
        user_id=user_id
    )

    # Preserve the existing minimum-history rule.
    if len(user_profile) < 3:
        return []

    # ---------------------------------------------------------
    # 2. Load clean / attacked / defended training data.
    # ---------------------------------------------------------

    train_ratings = _prepare_training_ratings(
        ratings_data=ratings_data
    )

    user_item_matrix = (
        train_ratings.pivot_table(
            index="user_id",
            columns="movie_id",
            values="rating",
        )
    )

    movie_stats = _load_movie_stats()

    candidate_ids = (
        _normalise_candidate_ids(
            candidate_movie_ids
        )
    )

    display_names = (
        _normalise_display_names(
            display_name_map
        )
    )

    # ---------------------------------------------------------
    # 3. Find movies shared by the website user and the
    #    supplied recommender dataset.
    # ---------------------------------------------------------

    website_movie_ids = set(
        user_profile["movie_id"]
    )

    common_movies = [
        int(movie_id)
        for movie_id in website_movie_ids
        if movie_id
        in user_item_matrix.columns
    ]

    # Preserve the existing minimum-overlap rule.
    if len(common_movies) < 3:
        return []

    website_series = (
        user_profile[
            user_profile["movie_id"].isin(
                common_movies
            )
        ]
        .set_index("movie_id")["rating"]
        .reindex(common_movies)
        .astype(float)
    )

    website_mean = float(
        website_series.mean()
    )

    # ---------------------------------------------------------
    # 4. Calculate similarity between the website user
    #    and users in the supplied ratings dataset.
    #
    #    IMPORTANT:
    #    This preserves the existing recommender maths.
    # ---------------------------------------------------------

    similarities = {}

    for (
        movie_user_id,
        row,
    ) in user_item_matrix[
        common_movies
    ].iterrows():

        neighbour_ratings = (
            row.dropna()
        )

        shared_movies = (
            neighbour_ratings.index
            .intersection(
                website_series.index
            )
        )

        if len(shared_movies) < 2:
            continue

        active_values = (
            website_series.loc[
                shared_movies
            ]
        )

        neighbour_values = (
            neighbour_ratings.loc[
                shared_movies
            ]
        )

        active_centred = (
            active_values
            - active_values.mean()
        ).values.reshape(
            1,
            -1,
        )

        neighbour_centred = (
            neighbour_values
            - neighbour_values.mean()
        ).values.reshape(
            1,
            -1,
        )

        # Preserve the existing behaviour:
        # skip profiles with no rating variation.
        if (
            (active_centred == 0).all()
            or
            (neighbour_centred == 0).all()
        ):
            continue

        similarity = (
            cosine_similarity(
                active_centred,
                neighbour_centred,
            )[0][0]
        )

        # Preserve positive-neighbour logic.
        if similarity > 0:
            similarities[
                int(movie_user_id)
            ] = float(similarity)

    if not similarities:
        return []

    similarity_series = (
        pd.Series(similarities)
        .sort_values(
            ascending=False
        )
    )

    # Preserve Top-K = 30.
    similarity_series = (
        similarity_series.head(
            TOP_K_NEIGHBORS
        )
    )

    # ---------------------------------------------------------
    # 5. Predict unseen movie ratings using the same
    #    weighted user-based CF prediction formula.
    # ---------------------------------------------------------

    rated_movie_ids = set(
        int(movie_id)
        for movie_id
        in user_profile["movie_id"]
    )

    recommendations = []

    for raw_movie_id in (
        user_item_matrix.columns
    ):

        movie_id = int(
            raw_movie_id
        )

        # User has already rated this movie.
        if movie_id in rated_movie_ids:
            continue

        # Optional 38-item demo candidate filter.
        if (
            candidate_ids is not None
            and movie_id
            not in candidate_ids
        ):
            continue

        neighbour_ratings = (
            user_item_matrix.loc[
                similarity_series.index,
                raw_movie_id,
            ]
            .dropna()
        )

        # Preserve minimum-neighbour rule.
        if (
            len(neighbour_ratings)
            < MIN_NEIGHBORS
        ):
            continue

        relevant_similarities = (
            similarity_series.loc[
                neighbour_ratings.index
            ]
        )

        neighbour_means = (
            user_item_matrix.loc[
                neighbour_ratings.index
            ]
            .mean(axis=1)
        )

        deviations = (
            neighbour_ratings
            - neighbour_means
        )

        denominator = (
            relevant_similarities
            .abs()
            .sum()
        )

        if denominator == 0:
            continue

        weighted_deviation = (
            (
                relevant_similarities
                * deviations
            ).sum()
            / denominator
        )

        prediction = (
            website_mean
            + weighted_deviation
        )

        # Preserve 1-5 rating range.
        prediction = max(
            1.0,
            min(
                5.0,
                float(prediction),
            ),
        )

        movie_row = movie_stats[
            movie_stats["movie_id"]
            == movie_id
        ]

        if movie_row.empty:
            continue

        original_title = str(
            movie_row.iloc[0]["title"]
        )

        display_name = (
            display_names.get(
                movie_id,
                original_title,
            )
        )

        rounded_prediction = round(
            float(prediction),
            4,
        )

        recommendations.append(
            {
                # Stable backend identifier.
                "movie_id": movie_id,

                # New frontend-safe field.
                "display_name": display_name,

                # New standard score field.
                "predicted_score": (
                    rounded_prediction
                ),

                # Added after sorting.
                "rank": None,

                # Truthful generic explanation.
                "reason": (
                    "Recommended from rating "
                    "patterns of users with "
                    "similar preferences."
                ),

                # -----------------------------------------
                # Legacy compatibility fields.
                # Existing templates/code can continue
                # working until the frontend is updated.
                # -----------------------------------------
                "title": original_title,
                "predicted_rating": (
                    rounded_prediction
                ),
            }
        )

    # ---------------------------------------------------------
    # 6. Rank recommendations.
    # ---------------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item["predicted_score"]
        ),
        reverse=True,
    )

    recommendations = (
        recommendations[:top_n]
    )

    for rank, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        recommendation["rank"] = rank

    return recommendations