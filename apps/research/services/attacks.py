"""Shilling attack interfaces for the RMRS research module.

Week 1 defines the configuration, validation rules, and interfaces for
Random Push and Average Push attacks.

Actual MovieLens fake-profile generation will be implemented once the
processed ratings and movie statistics are available.
"""

from dataclasses import dataclass
from typing import Literal


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
):
    """Generate synthetic Random Push profiles.

    Planned implementation:
    1. Calculate the required number of fake users.
    2. Assign new user IDs after the maximum genuine user ID.
    3. Give the target movie the maximum push rating.
    4. Select filler movies.
    5. Generate filler ratings around the global rating average.
    6. Return the generated fake ratings.

    Full implementation requires the processed MovieLens rating dataset.
    """

    raise NotImplementedError(
        "Random Push generation requires the processed MovieLens ratings."
    )


def generate_average_push(
    ratings,
    movie_statistics,
    target_movie_id: int,
    attack_size_percent: float,
    filler_size_percent: float,
    random_seed: int = 42,
):
    """Generate synthetic Average Push profiles.

    Planned implementation:
    1. Calculate the required number of fake users.
    2. Assign new user IDs after the maximum genuine user ID.
    3. Give the target movie the maximum push rating.
    4. Select filler movies.
    5. Generate each filler rating around that movie's genuine mean rating.
    6. Return the generated fake ratings.

    Full implementation requires processed ratings and movie statistics.
    """

    raise NotImplementedError(
        "Average Push generation requires ratings and movie statistics."
    )