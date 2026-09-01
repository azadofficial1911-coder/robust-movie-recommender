"""Shilling attack services for the RMRS research module.

The module defines shared attack configuration and validation together
with reproducible Random Push and Average Push profile generation for
the MovieLens experiment pipeline.

Week 6 implements the attack generators using the fixed genuine
training data while keeping synthetic attacker profiles separate from
genuine users.
"""

import random
from dataclasses import dataclass
from typing import Literal

import pandas as pd


AttackType = Literal["random", "average"]


@dataclass(frozen=True)
class AttackConfig:
    """Configuration shared by Random Push and Average Push attacks."""

    attack_type: AttackType
    target_movie_id: int | None
    attack_size_percent: float | None
    filler_size_percent: float | None
    target_rating: int = 5
    random_seed: int = 42


def validate_attack_config(config: AttackConfig) -> list[str]:
    """Return validation errors for an attack configuration."""

    errors: list[str] = []

    if config.attack_type not in {"random", "average"}:
        errors.append("attack_type must be 'random' or 'average'.")

    if config.target_movie_id is not None and config.target_movie_id <= 0:
        errors.append("target_movie_id must be a positive integer.")

    if config.attack_size_percent is not None:
        if not 0 < config.attack_size_percent <= 100:
            errors.append(
                "attack_size_percent must be greater than 0 and at most 100."
            )

    if config.filler_size_percent is not None:
        if not 0 < config.filler_size_percent <= 100:
            errors.append(
                "filler_size_percent must be greater than 0 and at most 100."
            )

    if not 1 <= config.target_rating <= 5:
        errors.append("target_rating must be between 1 and 5.")

    if config.random_seed < 0:
        errors.append("random_seed cannot be negative.")

    return errors


def calculate_fake_user_count(
    genuine_user_count: int,
    attack_size_percent: float,
) -> int:
    """Calculate the number of fake users for a selected attack size."""

    if genuine_user_count <= 0:
        raise ValueError("genuine_user_count must be greater than 0.")

    if not 0 < attack_size_percent <= 100:
        raise ValueError(
            "attack_size_percent must be greater than 0 and at most 100."
        )

    return round(genuine_user_count * attack_size_percent / 100)


def generate_random_push(
    ratings,
    target_movie_id: int,
    attack_size_percent: float,
    filler_size_percent: float,
    global_average_rating: float,
    random_seed: int = 42,
    target_rating: int = 5,
    rating_min: int = 1,
    rating_max: int = 5,
):
    """Generate reproducible synthetic Random Push fake-user profiles.

    Each synthetic user:
    - receives a new numeric user ID after the maximum genuine user ID;
    - rates the selected target movie with the configured push rating;
    - rates a percentage of the remaining movie catalogue as filler items;
    - receives filler ratings sampled around the genuine global mean.

    The input ratings DataFrame is never modified in place.

    Returns:
        pandas.DataFrame with columns:
        user_id, movie_id, rating, attack_type, target_movie_id
    """

    if not isinstance(ratings, pd.DataFrame):
        raise TypeError("ratings must be a pandas DataFrame.")

    required_columns = {"user_id", "movie_id", "rating"}
    missing_columns = required_columns.difference(ratings.columns)

    if missing_columns:
        raise ValueError(
            "ratings is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if ratings.empty:
        raise ValueError("ratings cannot be empty.")

    if target_movie_id <= 0:
        raise ValueError("target_movie_id must be a positive integer.")

    if target_movie_id not in set(ratings["movie_id"]):
        raise ValueError(
            f"target_movie_id {target_movie_id} does not exist in ratings."
        )

    if not 0 < attack_size_percent <= 100:
        raise ValueError(
            "attack_size_percent must be greater than 0 and at most 100."
        )

    if not 0 < filler_size_percent <= 100:
        raise ValueError(
            "filler_size_percent must be greater than 0 and at most 100."
        )

    if rating_min >= rating_max:
        raise ValueError("rating_min must be smaller than rating_max.")

    if not rating_min <= target_rating <= rating_max:
        raise ValueError(
            "target_rating must be inside the configured rating range."
        )

    if not rating_min <= global_average_rating <= rating_max:
        raise ValueError(
            "global_average_rating must be inside the configured rating range."
        )

    if random_seed < 0:
        raise ValueError("random_seed cannot be negative.")

    genuine_user_count = ratings["user_id"].nunique()

    fake_user_count = calculate_fake_user_count(
        genuine_user_count,
        attack_size_percent,
    )

    if fake_user_count <= 0:
        raise ValueError(
            "attack_size_percent produced zero synthetic users."
        )

    eligible_movie_ids = sorted(
        int(movie_id)
        for movie_id in ratings["movie_id"].unique()
        if int(movie_id) != target_movie_id
    )

    if not eligible_movie_ids:
        raise ValueError(
            "No eligible filler movies remain after excluding the target."
        )

    filler_count = round(
        len(eligible_movie_ids) * filler_size_percent / 100
    )

    if filler_count <= 0:
        raise ValueError(
            "filler_size_percent produced zero filler movies."
        )

    if filler_count > len(eligible_movie_ids):
        raise ValueError(
            "Requested filler count exceeds the available movie catalogue."
        )

    max_genuine_user_id = int(ratings["user_id"].max())

    # Use the genuine rating distribution as the spread around the
    # supplied global average rather than an arbitrary fixed deviation.
    genuine_rating_std = float(
        ratings["rating"].astype(float).std(ddof=0)
    )

    if pd.isna(genuine_rating_std):
        genuine_rating_std = 0.0

    rng = random.Random(random_seed)

    fake_rows = []

    for fake_offset in range(1, fake_user_count + 1):
        fake_user_id = max_genuine_user_id + fake_offset

        # Every fake profile strongly promotes the selected target.
        fake_rows.append(
            {
                "user_id": fake_user_id,
                "movie_id": target_movie_id,
                "rating": target_rating,
                "attack_type": "random",
                "target_movie_id": target_movie_id,
            }
        )

        filler_movie_ids = rng.sample(
            eligible_movie_ids,
            k=filler_count,
        )

        for filler_movie_id in filler_movie_ids:
            sampled_rating = rng.gauss(
                global_average_rating,
                genuine_rating_std,
            )

            filler_rating = int(round(sampled_rating))

            filler_rating = max(
                rating_min,
                min(rating_max, filler_rating),
            )

            fake_rows.append(
                {
                    "user_id": fake_user_id,
                    "movie_id": filler_movie_id,
                    "rating": filler_rating,
                    "attack_type": "random",
                    "target_movie_id": target_movie_id,
                }
            )

    return pd.DataFrame(
        fake_rows,
        columns=[
            "user_id",
            "movie_id",
            "rating",
            "attack_type",
            "target_movie_id",
        ],
    )


def generate_average_push(
    ratings,
    movie_statistics,
    target_movie_id: int,
    attack_size_percent: float,
    filler_size_percent: float,
    random_seed: int = 42,
    target_rating: int = 5,
    rating_min: int = 1,
    rating_max: int = 5,
):
    """Generate reproducible synthetic Average Push fake-user profiles.

    Each synthetic user:
    - receives a new numeric user ID after the maximum genuine user ID;
    - rates the selected target movie with the configured push rating;
    - rates a percentage of the remaining movie catalogue as filler items;
    - receives filler ratings sampled around each filler movie's mean rating.

    The input DataFrames are never modified in place.

    Returns:
        pandas.DataFrame with columns:
        user_id, movie_id, rating, attack_type, target_movie_id
    """

    if not isinstance(ratings, pd.DataFrame):
        raise TypeError("ratings must be a pandas DataFrame.")

    if not isinstance(movie_statistics, pd.DataFrame):
        raise TypeError("movie_statistics must be a pandas DataFrame.")

    required_rating_columns = {"user_id", "movie_id", "rating"}
    missing_rating_columns = required_rating_columns.difference(
        ratings.columns
    )

    if missing_rating_columns:
        raise ValueError(
            "ratings is missing required columns: "
            + ", ".join(sorted(missing_rating_columns))
        )

    required_statistics_columns = {"movie_id", "mean_rating"}
    missing_statistics_columns = required_statistics_columns.difference(
        movie_statistics.columns
    )

    if missing_statistics_columns:
        raise ValueError(
            "movie_statistics is missing required columns: "
            + ", ".join(sorted(missing_statistics_columns))
        )

    if ratings.empty:
        raise ValueError("ratings cannot be empty.")

    if movie_statistics.empty:
        raise ValueError("movie_statistics cannot be empty.")

    if target_movie_id <= 0:
        raise ValueError("target_movie_id must be a positive integer.")

    if target_movie_id not in set(ratings["movie_id"]):
        raise ValueError(
            f"target_movie_id {target_movie_id} does not exist in ratings."
        )

    if not 0 < attack_size_percent <= 100:
        raise ValueError(
            "attack_size_percent must be greater than 0 and at most 100."
        )

    if not 0 < filler_size_percent <= 100:
        raise ValueError(
            "filler_size_percent must be greater than 0 and at most 100."
        )

    if rating_min >= rating_max:
        raise ValueError("rating_min must be smaller than rating_max.")

    if not rating_min <= target_rating <= rating_max:
        raise ValueError(
            "target_rating must be inside the configured rating range."
        )

    if random_seed < 0:
        raise ValueError("random_seed cannot be negative.")

    genuine_user_count = ratings["user_id"].nunique()

    fake_user_count = calculate_fake_user_count(
        genuine_user_count,
        attack_size_percent,
    )

    if fake_user_count <= 0:
        raise ValueError(
            "attack_size_percent produced zero synthetic users."
        )

    statistics = (
        movie_statistics[["movie_id", "mean_rating"]]
        .drop_duplicates(subset=["movie_id"])
        .copy()
    )

    statistics["movie_id"] = statistics["movie_id"].astype(int)
    statistics["mean_rating"] = statistics["mean_rating"].astype(float)

    mean_rating_by_movie = dict(
        zip(
            statistics["movie_id"],
            statistics["mean_rating"],
        )
    )

    eligible_movie_ids = sorted(
        int(movie_id)
        for movie_id in ratings["movie_id"].unique()
        if (
            int(movie_id) != target_movie_id
            and int(movie_id) in mean_rating_by_movie
        )
    )

    if not eligible_movie_ids:
        raise ValueError(
            "No eligible filler movies have available mean ratings."
        )

    filler_count = round(
        len(eligible_movie_ids) * filler_size_percent / 100
    )

    if filler_count <= 0:
        raise ValueError(
            "filler_size_percent produced zero filler movies."
        )

    if filler_count > len(eligible_movie_ids):
        raise ValueError(
            "Requested filler count exceeds the available movie catalogue."
        )

    max_genuine_user_id = int(ratings["user_id"].max())

    global_rating_std = float(
        ratings["rating"].astype(float).std(ddof=0)
    )

    if pd.isna(global_rating_std):
        global_rating_std = 0.0

    item_rating_std = (
        ratings.groupby("movie_id")["rating"]
        .std(ddof=0)
        .to_dict()
    )

    rng = random.Random(random_seed)

    fake_rows = []

    for fake_offset in range(1, fake_user_count + 1):
        fake_user_id = max_genuine_user_id + fake_offset

        fake_rows.append(
            {
                "user_id": fake_user_id,
                "movie_id": target_movie_id,
                "rating": target_rating,
                "attack_type": "average",
                "target_movie_id": target_movie_id,
            }
        )

        filler_movie_ids = rng.sample(
            eligible_movie_ids,
            k=filler_count,
        )

        for filler_movie_id in filler_movie_ids:
            item_mean = mean_rating_by_movie[filler_movie_id]

            if not rating_min <= item_mean <= rating_max:
                raise ValueError(
                    f"mean_rating for movie {filler_movie_id} "
                    "is outside the configured rating range."
                )

            item_std = item_rating_std.get(
                filler_movie_id,
                global_rating_std,
            )

            if pd.isna(item_std):
                item_std = global_rating_std

            sampled_rating = rng.gauss(
                item_mean,
                float(item_std),
            )

            filler_rating = int(round(sampled_rating))

            filler_rating = max(
                rating_min,
                min(rating_max, filler_rating),
            )

            fake_rows.append(
                {
                    "user_id": fake_user_id,
                    "movie_id": filler_movie_id,
                    "rating": filler_rating,
                    "attack_type": "average",
                    "target_movie_id": target_movie_id,
                }
            )

    return pd.DataFrame(
        fake_rows,
        columns=[
            "user_id",
            "movie_id",
            "rating",
            "attack_type",
            "target_movie_id",
        ],
    )