from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REQUIRED_TOTAL = 38
REQUIRED_GOOD = 5
REQUIRED_TARGET = 3
REQUIRED_RANDOM = 30

VALID_ROLES = {
    "good",
    "target",
    "random",
}


@dataclass(frozen=True)
class DemoCatalogueItem:
    """
    One stable demo-catalogue entry.

    movie_id:
        Stable backend MovieLens ID used for scoring.

    display_name:
        Presentation-safe alias shown to the user.

    role:
        One of:
        - good
        - target
        - random
    """

    movie_id: int
    display_name: str
    role: str


def validate_catalogue(
    items: Iterable[DemoCatalogueItem],
) -> list[DemoCatalogueItem]:
    """
    Validate the final 38-item catalogue.

    Rules:
    - exactly 38 items
    - exactly 5 good
    - exactly 3 target
    - exactly 30 random
    - backend movie IDs must be unique
    - display names must be unique
    - roles must be valid
    - IDs must be positive integers
    """

    catalogue = list(items)

    if len(catalogue) != REQUIRED_TOTAL:
        raise ValueError(
            "Demo catalogue must contain exactly "
            f"{REQUIRED_TOTAL} movies. "
            f"Received {len(catalogue)}."
        )

    movie_ids = [
        item.movie_id
        for item in catalogue
    ]

    display_names = [
        item.display_name
        for item in catalogue
    ]

    if len(set(movie_ids)) != len(movie_ids):
        raise ValueError(
            "Demo catalogue contains duplicate "
            "backend movie IDs."
        )

    if len(set(display_names)) != len(
        display_names
    ):
        raise ValueError(
            "Demo catalogue contains duplicate "
            "display names."
        )

    for item in catalogue:
        if not isinstance(item.movie_id, int):
            raise TypeError(
                "Every movie_id must be an integer."
            )

        if item.movie_id <= 0:
            raise ValueError(
                "Every movie_id must be positive."
            )

        if not item.display_name.strip():
            raise ValueError(
                "Every display_name must be non-empty."
            )

        if item.role not in VALID_ROLES:
            raise ValueError(
                f"Invalid role '{item.role}'. "
                f"Expected one of "
                f"{sorted(VALID_ROLES)}."
            )

    good_count = sum(
        item.role == "good"
        for item in catalogue
    )

    target_count = sum(
        item.role == "target"
        for item in catalogue
    )

    random_count = sum(
        item.role == "random"
        for item in catalogue
    )

    if good_count != REQUIRED_GOOD:
        raise ValueError(
            "Demo catalogue must contain exactly "
            f"{REQUIRED_GOOD} good movies. "
            f"Received {good_count}."
        )

    if target_count != REQUIRED_TARGET:
        raise ValueError(
            "Demo catalogue must contain exactly "
            f"{REQUIRED_TARGET} targeted movies. "
            f"Received {target_count}."
        )

    if random_count != REQUIRED_RANDOM:
        raise ValueError(
            "Demo catalogue must contain exactly "
            f"{REQUIRED_RANDOM} random movies. "
            f"Received {random_count}."
        )

    return catalogue


def get_candidate_movie_ids(
    items: Iterable[DemoCatalogueItem],
) -> list[int]:
    """
    Return stable backend IDs for candidate filtering.
    """

    catalogue = validate_catalogue(items)

    return [
        item.movie_id
        for item in catalogue
    ]


def get_display_name_map(
    items: Iterable[DemoCatalogueItem],
) -> dict[int, str]:
    """
    Return backend movie ID -> presentation alias.
    """

    catalogue = validate_catalogue(items)

    return {
        item.movie_id: item.display_name
        for item in catalogue
    }


def get_role_map(
    items: Iterable[DemoCatalogueItem],
) -> dict[int, str]:
    """
    Return backend movie ID -> catalogue role.
    """

    catalogue = validate_catalogue(items)

    return {
        item.movie_id: item.role
        for item in catalogue
    }


def get_target_movie_ids(
    items: Iterable[DemoCatalogueItem],
) -> list[int]:
    """
    Return the three calibrated target movie IDs.
    """

    catalogue = validate_catalogue(items)

    return [
        item.movie_id
        for item in catalogue
        if item.role == "target"
    ]


def build_catalogue(
    good_ids: Iterable[int],
    target_ids: Iterable[int],
    random_ids: Iterable[int],
) -> list[DemoCatalogueItem]:
    """
    Build the final presentation catalogue from
    calibrated backend IDs.

    The actual IDs must come from the team's
    calibration process. This function does not
    choose or manipulate movie IDs.

    Display aliases are generated automatically:

    Good Movie 1 ... Good Movie 5
    Targeted Movie 1 ... Targeted Movie 3
    Random Movie 1 ... Random Movie 30
    """

    good_ids = [
        int(movie_id)
        for movie_id in good_ids
    ]

    target_ids = [
        int(movie_id)
        for movie_id in target_ids
    ]

    random_ids = [
        int(movie_id)
        for movie_id in random_ids
    ]

    if len(good_ids) != REQUIRED_GOOD:
        raise ValueError(
            f"Expected {REQUIRED_GOOD} good IDs."
        )

    if len(target_ids) != REQUIRED_TARGET:
        raise ValueError(
            f"Expected {REQUIRED_TARGET} target IDs."
        )

    if len(random_ids) != REQUIRED_RANDOM:
        raise ValueError(
            f"Expected {REQUIRED_RANDOM} random IDs."
        )

    catalogue = []

    for index, movie_id in enumerate(
        good_ids,
        start=1,
    ):
        catalogue.append(
            DemoCatalogueItem(
                movie_id=movie_id,
                display_name=(
                    f"Good Movie {index}"
                ),
                role="good",
            )
        )

    for index, movie_id in enumerate(
        target_ids,
        start=1,
    ):
        catalogue.append(
            DemoCatalogueItem(
                movie_id=movie_id,
                display_name=(
                    f"Targeted Movie {index}"
                ),
                role="target",
            )
        )

    for index, movie_id in enumerate(
        random_ids,
        start=1,
    ):
        catalogue.append(
            DemoCatalogueItem(
                movie_id=movie_id,
                display_name=(
                    f"Random Movie {index}"
                ),
                role="random",
            )
        )

    return validate_catalogue(
        catalogue
    )