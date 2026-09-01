"""Suspicious-user detection services for the RMRS research module.

Week 6 implements the first explainable behavioural detector for the
controlled Random Push and Average Push experiments.

Ground-truth labels are never used to calculate behavioural features
or suspicion scores. They are attached only after prediction so the
detector can be evaluated independently.
"""

from dataclasses import dataclass

import pandas as pd


CANDIDATE_FEATURES = (
    "rating_deviation",
    "profile_size",
    "extreme_rating_ratio",
    "target_item_behaviour",
)


PILOT_FEATURE_WEIGHTS = {
    "rating_deviation": 0.20,
    "profile_size": 0.20,
    "extreme_rating_ratio": 0.15,
    "target_item_behaviour": 0.45,
}


@dataclass(frozen=True)
class DetectionResult:
    """Standard detection result for one analysed user."""

    user_id: int
    suspicion_score: float
    predicted_label: str
    true_label: str | None = None


def validate_suspicion_score(score: float) -> None:
    """Validate that a suspicion score is between 0 and 1."""

    if not 0.0 <= score <= 1.0:
        raise ValueError(
            "suspicion_score must be between 0.0 and 1.0."
        )


def validate_threshold(threshold: float) -> None:
    """Validate that the classification threshold is between 0 and 1."""

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0.0 and 1.0."
        )


def classify_score(
    score: float,
    threshold: float = 0.5,
) -> str:
    """Classify a suspicion score as genuine or suspicious."""

    validate_suspicion_score(score)
    validate_threshold(threshold)

    if score >= threshold:
        return "suspicious"

    return "genuine"


def _validate_detection_inputs(
    ratings: pd.DataFrame,
    movie_statistics: pd.DataFrame,
    target_movie_id: int,
    rating_min: int,
    rating_max: int,
) -> None:
    """Validate the inputs required by the behavioural detector."""

    if not isinstance(ratings, pd.DataFrame):
        raise TypeError(
            "ratings must be a pandas DataFrame."
        )

    if not isinstance(movie_statistics, pd.DataFrame):
        raise TypeError(
            "movie_statistics must be a pandas DataFrame."
        )

    if ratings.empty:
        raise ValueError(
            "ratings cannot be empty."
        )

    if movie_statistics.empty:
        raise ValueError(
            "movie_statistics cannot be empty."
        )

    required_rating_columns = {
        "user_id",
        "movie_id",
        "rating",
    }

    missing_rating_columns = required_rating_columns.difference(
        ratings.columns
    )

    if missing_rating_columns:
        raise ValueError(
            "ratings is missing required columns: "
            + ", ".join(
                sorted(missing_rating_columns)
            )
        )

    required_statistics_columns = {
        "movie_id",
        "mean_rating",
    }

    missing_statistics_columns = (
        required_statistics_columns.difference(
            movie_statistics.columns
        )
    )

    if missing_statistics_columns:
        raise ValueError(
            "movie_statistics is missing required columns: "
            + ", ".join(
                sorted(missing_statistics_columns)
            )
        )

    if target_movie_id <= 0:
        raise ValueError(
            "target_movie_id must be a positive integer."
        )

    if rating_min >= rating_max:
        raise ValueError(
            "rating_min must be smaller than rating_max."
        )

    if not ratings["rating"].between(
        rating_min,
        rating_max,
    ).all():
        raise ValueError(
            "ratings contains values outside the configured rating range."
        )


def extract_detection_features(
    ratings: pd.DataFrame,
    movie_statistics: pd.DataFrame,
    target_movie_id: int,
    rating_min: int = 1,
    rating_max: int = 5,
) -> pd.DataFrame:
    """Calculate explainable behavioural features for each user.

    Raw features:
    - profile_size:
      number of ratings submitted by the user.
    - rating_deviation:
      mean absolute difference between user ratings and genuine item means.
    - extreme_rating_ratio:
      proportion of ratings at the minimum or maximum rating.
    - target_item_behaviour:
      1 when the user gives the target the maximum push rating, otherwise 0.

    Two raw features are converted into normalised suspicion features:
    - profile_size_feature measures concentration of identical profile sizes.
    - rating_deviation_feature is high when ratings closely imitate item means.
    """

    _validate_detection_inputs(
        ratings,
        movie_statistics,
        target_movie_id,
        rating_min,
        rating_max,
    )

    working = ratings[
        [
            "user_id",
            "movie_id",
            "rating",
        ]
    ].copy(deep=True)

    statistics = (
        movie_statistics[
            [
                "movie_id",
                "mean_rating",
            ]
        ]
        .drop_duplicates(
            subset=["movie_id"]
        )
        .copy()
    )

    statistics["movie_id"] = (
        statistics["movie_id"].astype(int)
    )

    statistics["mean_rating"] = (
        statistics["mean_rating"].astype(float)
    )

    mean_rating_by_movie = dict(
        zip(
            statistics["movie_id"],
            statistics["mean_rating"],
        )
    )

    working["item_mean"] = (
        working["movie_id"].map(
            mean_rating_by_movie
        )
    )

    if working["item_mean"].isna().any():
        missing_movie_ids = sorted(
            int(movie_id)
            for movie_id in working.loc[
                working["item_mean"].isna(),
                "movie_id",
            ].unique()
        )

        raise ValueError(
            "movie_statistics has no mean_rating for movie IDs: "
            + ", ".join(
                str(movie_id)
                for movie_id in missing_movie_ids[:10]
            )
        )

    working["absolute_item_deviation"] = (
        working["rating"].astype(float)
        - working["item_mean"]
    ).abs()

    working["is_extreme"] = (
        working["rating"].isin(
            [
                rating_min,
                rating_max,
            ]
        )
    ).astype(float)

    profile_size = (
        working.groupby("user_id")
        .size()
        .rename("profile_size")
    )

    rating_deviation = (
        working.groupby("user_id")[
            "absolute_item_deviation"
        ]
        .mean()
        .rename("rating_deviation")
    )

    extreme_rating_ratio = (
        working.groupby("user_id")[
            "is_extreme"
        ]
        .mean()
        .rename("extreme_rating_ratio")
    )

    feature_table = pd.concat(
        [
            profile_size,
            rating_deviation,
            extreme_rating_ratio,
        ],
        axis=1,
    ).reset_index()

    # Synthetic batches often contain many users with exactly the same
    # profile size. This converts that concentration into a 0-1 signal.
    profile_size_frequency = (
        feature_table["profile_size"]
        .value_counts()
    )

    maximum_frequency = int(
        profile_size_frequency.max()
    )

    feature_table["profile_size_feature"] = (
        feature_table["profile_size"]
        .map(profile_size_frequency)
        .astype(float)
        / maximum_frequency
    )

    # Lower deviation from genuine item means means stronger imitation
    # of normal item-rating behaviour.
    rating_range = float(
        rating_max - rating_min
    )

    feature_table["rating_deviation_feature"] = (
        1.0
        - (
            feature_table["rating_deviation"]
            / rating_range
        ).clip(
            lower=0.0,
            upper=1.0,
        )
    )

    target_rows = working[
        working["movie_id"]
        == target_movie_id
    ]

    target_max_rating_users = set(
        int(user_id)
        for user_id in target_rows.loc[
            target_rows["rating"]
            == rating_max,
            "user_id",
        ].unique()
    )

    feature_table["target_item_behaviour"] = (
        feature_table["user_id"]
        .apply(
            lambda user_id: (
                1.0
                if int(user_id)
                in target_max_rating_users
                else 0.0
            )
        )
    )

    return feature_table[
        [
            "user_id",
            "profile_size",
            "rating_deviation",
            "extreme_rating_ratio",
            "target_item_behaviour",
            "profile_size_feature",
            "rating_deviation_feature",
        ]
    ].sort_values(
        "user_id"
    ).reset_index(
        drop=True
    )


def calculate_suspicion_scores(
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the Week 6 pilot suspicion score."""

    required_columns = {
        "user_id",
        "profile_size_feature",
        "rating_deviation_feature",
        "extreme_rating_ratio",
        "target_item_behaviour",
    }

    missing_columns = required_columns.difference(
        features.columns
    )

    if missing_columns:
        raise ValueError(
            "features is missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    scored = features.copy(deep=True)

    scored["suspicion_score"] = (
        PILOT_FEATURE_WEIGHTS[
            "rating_deviation"
        ]
        * scored["rating_deviation_feature"]
        + PILOT_FEATURE_WEIGHTS[
            "profile_size"
        ]
        * scored["profile_size_feature"]
        + PILOT_FEATURE_WEIGHTS[
            "extreme_rating_ratio"
        ]
        * scored["extreme_rating_ratio"]
        + PILOT_FEATURE_WEIGHTS[
            "target_item_behaviour"
        ]
        * scored["target_item_behaviour"]
    )

    scored["suspicion_score"] = (
        scored["suspicion_score"]
        .clip(
            lower=0.0,
            upper=1.0,
        )
    )

    return scored


def detect_suspicious_users(
    ratings,
    threshold: float = 0.5,
    *,
    movie_statistics=None,
    target_movie_id=None,
    true_labels=None,
    rating_min: int = 1,
    rating_max: int = 5,
):
    """Analyse user behaviour and return DetectionResult records.

    Ground truth is optional and is attached only after predictions
    have been calculated. It never contributes to feature extraction
    or suspicion-score calculation.
    """

    validate_threshold(threshold)

    if movie_statistics is None:
        raise ValueError(
            "movie_statistics is required for detection."
        )

    if target_movie_id is None:
        raise ValueError(
            "target_movie_id is required for detection."
        )

    features = extract_detection_features(
        ratings=ratings,
        movie_statistics=movie_statistics,
        target_movie_id=int(
            target_movie_id
        ),
        rating_min=rating_min,
        rating_max=rating_max,
    )

    scored = calculate_suspicion_scores(
        features
    )

    label_by_user = {}

    if true_labels is not None:
        if not isinstance(
            true_labels,
            pd.DataFrame,
        ):
            raise TypeError(
                "true_labels must be a pandas DataFrame."
            )

        required_label_columns = {
            "user_id",
            "true_label",
        }

        missing_label_columns = (
            required_label_columns.difference(
                true_labels.columns
            )
        )

        if missing_label_columns:
            raise ValueError(
                "true_labels is missing required columns: "
                + ", ".join(
                    sorted(
                        missing_label_columns
                    )
                )
            )

        label_by_user = dict(
            zip(
                true_labels["user_id"].astype(int),
                true_labels["true_label"].astype(str),
            )
        )

    results = []

    for row in scored.itertuples():
        score = float(
            row.suspicion_score
        )

        validate_suspicion_score(score)

        predicted_label = classify_score(
            score,
            threshold,
        )

        user_id = int(
            row.user_id
        )

        results.append(
            DetectionResult(
                user_id=user_id,
                suspicion_score=round(
                    score,
                    6,
                ),
                predicted_label=predicted_label,
                true_label=label_by_user.get(
                    user_id
                ),
            )
        )

    return results