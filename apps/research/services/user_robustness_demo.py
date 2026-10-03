"""Interactive robustness demonstration for real RMRS website users.

This module reuses the existing recommender, Average Push generator,
behavioural detector, and profile-removal defence. It does not replace the
formal single-target research experiments. The purpose is to create a clear
staff-facing demonstration using the same underlying algorithms.
"""

from __future__ import annotations

import pandas as pd

from apps.recommendations.services.recommender import (
    MOVIE_STATS_FILE,
    TRAIN_FILE,
    get_recommendations,
)
from apps.research.services.attacks import generate_average_push
from apps.research.services.detection import detect_suspicious_users
from defence.remove_profiles import (
    apply_from_detection_results,
    defence_summary,
)


DEMO_MOVIE_COUNT = 38
DEMO_TARGET_COUNT = 3
DEMO_GOOD_COUNT = 5
DEMO_FILLER_SIZE_PERCENT = 5.0
DEMO_ATTACK_SIZES = (
    5.0,
    10.0,
    15.0,
    20.0,
)
DEMO_THRESHOLD = 0.5


def _load_demo_sources() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    return (
        pd.read_csv(TRAIN_FILE),
        pd.read_csv(MOVIE_STATS_FILE),
    )


def _select_demo_movie_ids(
    ratings: pd.DataFrame,
    movie_stats: pd.DataFrame,
    limit: int = DEMO_MOVIE_COUNT,
) -> list[int]:
    """Pick a stable set of real MovieLens IDs for the prototype."""

    rating_ids = {
        int(movie_id)
        for movie_id
        in ratings["movie_id"]
        .dropna()
        .unique()
    }

    stats_ids = {
        int(movie_id)
        for movie_id
        in movie_stats["movie_id"]
        .dropna()
        .unique()
    }

    return sorted(
        rating_ids.intersection(
            stats_ids
        )
    )[:limit]


def _rank_map(
    results: list[dict],
) -> dict[int, int]:
    return {
        int(item["movie_id"]): rank
        for rank, item in enumerate(
            results,
            start=1,
        )
    }


def _score_map(
    results: list[dict],
) -> dict[int, float]:
    scores = {}

    for item in results:
        movie_id = int(
            item["movie_id"]
        )

        score = item.get(
            "predicted_score"
        )

        if score is None:
            score = item.get(
                "predicted_rating"
            )

        if score is not None:
            scores[movie_id] = float(
                score
            )

    return scores


def _choose_targets(
    clean_results: list[dict],
) -> list[int]:
    """Choose three lower-ranked visible candidates as demo targets."""

    if len(clean_results) < 12:
        raise ValueError(
            "At least 12 clean candidate recommendations are required "
            "to build the interactive robustness demonstration."
        )

    lower_section = clean_results[
        7:min(
            len(clean_results),
            24,
        )
    ]

    if len(lower_section) < DEMO_TARGET_COUNT:
        raise ValueError(
            "Not enough lower-ranked candidate movies are available "
            "for target selection."
        )

    indexes = [
        0,
        len(lower_section) // 2,
        len(lower_section) - 1,
    ]

    return [
        int(
            lower_section[index][
                "movie_id"
            ]
        )
        for index in indexes
    ]


def _rebase_fake_user_ids(
    fake_profiles: pd.DataFrame,
    first_user_id: int,
) -> pd.DataFrame:
    rebased = fake_profiles.copy(
        deep=True
    )

    original_user_ids = sorted(
        int(user_id)
        for user_id
        in rebased["user_id"].unique()
    )

    mapping = {
        original_user_id: (
            first_user_id + index
        )
        for index, original_user_id
        in enumerate(
            original_user_ids
        )
    }

    rebased["user_id"] = (
        rebased["user_id"]
        .astype(int)
        .map(mapping)
    )

    return rebased


def _generate_multi_target_attack(
    clean_ratings: pd.DataFrame,
    movie_stats: pd.DataFrame,
    target_movie_ids: list[int],
    attack_size_percent: float,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """Generate separate Average Push batches for three demo targets."""

    fake_batches = []

    next_fake_user_id = (
        int(
            clean_ratings[
                "user_id"
            ].max()
        )
        + 1
    )

    for (
        target_index,
        target_movie_id,
    ) in enumerate(
        target_movie_ids
    ):
        batch = generate_average_push(
            ratings=clean_ratings,
            movie_statistics=movie_stats,
            target_movie_id=int(
                target_movie_id
            ),
            attack_size_percent=(
                attack_size_percent
            ),
            filler_size_percent=(
                DEMO_FILLER_SIZE_PERCENT
            ),
            random_seed=(
                42 + target_index
            ),
        )

        batch = _rebase_fake_user_ids(
            batch,
            next_fake_user_id,
        )

        next_fake_user_id = (
            int(
                batch[
                    "user_id"
                ].max()
            )
            + 1
        )

        fake_batches.append(
            batch
        )

    fake_profiles = pd.concat(
        fake_batches,
        ignore_index=True,
    )

    attacked_ratings = pd.concat(
        [
            clean_ratings[
                [
                    "user_id",
                    "movie_id",
                    "rating",
                ]
            ].copy(
                deep=True
            ),
            fake_profiles[
                [
                    "user_id",
                    "movie_id",
                    "rating",
                ]
            ].copy(
                deep=True
            ),
        ],
        ignore_index=True,
    )

    return (
        attacked_ratings,
        fake_profiles,
    )


def _combine_detection_results(
    attacked_ratings: pd.DataFrame,
    movie_stats: pd.DataFrame,
    target_movie_ids: list[int],
) -> pd.DataFrame:
    """Flag a user if any target-specific detector marks them suspicious."""

    frames = []

    for target_movie_id in (
        target_movie_ids
    ):
        results = detect_suspicious_users(
            ratings=attacked_ratings,
            threshold=DEMO_THRESHOLD,
            movie_statistics=movie_stats,
            target_movie_id=int(
                target_movie_id
            ),
        )

        frames.append(
            pd.DataFrame(
                [
                    {
                        "user_id": result.user_id,
                        "suspicion_score": result.suspicion_score,
                        "predicted_label": result.predicted_label,
                    }
                    for result in results
                ]
            )
        )

    combined = pd.concat(
        frames,
        ignore_index=True,
    )

    aggregated = (
        combined
        .groupby(
            "user_id",
            as_index=False,
        )
        .agg(
            suspicion_score=(
                "suspicion_score",
                "max",
            ),
            suspicious_votes=(
                "predicted_label",
                lambda labels: sum(
                    label
                    == "suspicious"
                    for label
                    in labels
                ),
            ),
        )
    )

    aggregated[
        "predicted_label"
    ] = aggregated[
        "suspicious_votes"
    ].apply(
        lambda votes: (
            "suspicious"
            if int(votes) > 0
            else "genuine"
        )
    )

    return aggregated[
        [
            "user_id",
            "suspicion_score",
            "predicted_label",
            "suspicious_votes",
        ]
    ]


def _attack_is_visible(
    clean_ranks: dict[int, int],
    attacked_ranks: dict[int, int],
    target_movie_ids: list[int],
) -> bool:
    improvements = []

    for movie_id in target_movie_ids:
        clean_rank = clean_ranks.get(
            movie_id
        )

        attacked_rank = (
            attacked_ranks.get(
                movie_id
            )
        )

        if (
            clean_rank is None
            or attacked_rank is None
        ):
            improvements.append(0)
        else:
            improvements.append(
                clean_rank
                - attacked_rank
            )

    return (
        sum(
            improvement > 0
            for improvement
            in improvements
        )
        >= 2
        and max(
            improvements,
            default=0,
        )
        >= 3
    )


def _build_alias_map(
    clean_results: list[dict],
    target_movie_ids: list[int],
    candidate_movie_ids: list[int],
) -> dict[int, dict]:
    aliases = {}

    for index, movie_id in enumerate(
        target_movie_ids,
        start=1,
    ):
        aliases[
            int(movie_id)
        ] = {
            "display_name": (
                f"Targeted Movie {index}"
            ),
            "role": "target",
        }

    good_movie_ids = [
        int(item["movie_id"])
        for item in clean_results
        if int(
            item["movie_id"]
        ) not in aliases
    ][:DEMO_GOOD_COUNT]

    for index, movie_id in enumerate(
        good_movie_ids,
        start=1,
    ):
        aliases[movie_id] = {
            "display_name": (
                f"Good Movie {index}"
            ),
            "role": "good",
        }

    random_index = 1

    for movie_id in (
        candidate_movie_ids
    ):
        movie_id = int(
            movie_id
        )

        if movie_id in aliases:
            continue

        aliases[movie_id] = {
            "display_name": (
                f"Random Movie "
                f"{random_index}"
            ),
            "role": "random",
        }

        random_index += 1

    return aliases


def _decorate_results(
    results: list[dict],
    aliases: dict[int, dict],
) -> list[dict]:
    decorated = []

    for rank, item in enumerate(
        results,
        start=1,
    ):
        movie_id = int(
            item["movie_id"]
        )

        alias = aliases.get(
            movie_id,
            {
                "display_name": (
                    f"Random Movie "
                    f"{movie_id}"
                ),
                "role": "random",
            },
        )

        decorated.append(
            {
                **item,
                "rank": rank,
                "display_name": (
                    alias[
                        "display_name"
                    ]
                ),
                "role": (
                    alias[
                        "role"
                    ]
                ),
            }
        )

    return decorated


def build_user_robustness_demo(
    user_id: int,
) -> dict:
    """Build clean, attacked, detected, defended results for one website user."""

    (
        clean_ratings,
        movie_stats,
    ) = _load_demo_sources()

    candidate_movie_ids = (
        _select_demo_movie_ids(
            clean_ratings,
            movie_stats,
        )
    )

    # ---------------------------------------------------------
    # CLEAN
    #
    # Use the current recommender API from main.
    # ---------------------------------------------------------

    clean_results = (
        get_recommendations(
            user_id=user_id,
            top_n=DEMO_MOVIE_COUNT,
            ratings_data=clean_ratings,
            candidate_movie_ids=(
                candidate_movie_ids
            ),
        )
    )

    if len(clean_results) < 12:
        raise ValueError(
            "The user does not yet have enough usable recommendation "
            "candidates for the robustness demonstration."
        )

    target_movie_ids = (
        _choose_targets(
            clean_results
        )
    )

    clean_ranks = _rank_map(
        clean_results
    )

    attacked_ratings = None
    fake_profiles = None
    attacked_results = None
    selected_attack_size = None

    # ---------------------------------------------------------
    # ATTACKED
    # ---------------------------------------------------------

    for attack_size in (
        DEMO_ATTACK_SIZES
    ):
        (
            trial_attacked_ratings,
            trial_fake_profiles,
        ) = _generate_multi_target_attack(
            clean_ratings,
            movie_stats,
            target_movie_ids,
            attack_size,
        )

        trial_attacked_results = (
            get_recommendations(
                user_id=user_id,
                top_n=DEMO_MOVIE_COUNT,
                ratings_data=(
                    trial_attacked_ratings
                ),
                candidate_movie_ids=(
                    candidate_movie_ids
                ),
            )
        )

        if not trial_attacked_results:
            continue

        attacked_ratings = (
            trial_attacked_ratings
        )

        fake_profiles = (
            trial_fake_profiles
        )

        attacked_results = (
            trial_attacked_results
        )

        selected_attack_size = (
            attack_size
        )

        if _attack_is_visible(
            clean_ranks,
            _rank_map(
                trial_attacked_results
            ),
            target_movie_ids,
        ):
            break

    if any(
        value is None
        for value in (
            attacked_ratings,
            fake_profiles,
            attacked_results,
            selected_attack_size,
        )
    ):
        raise ValueError(
            "Unable to generate an attacked recommendation state."
        )

    # ---------------------------------------------------------
    # DETECTION
    # ---------------------------------------------------------

    detection_results = (
        _combine_detection_results(
            attacked_ratings,
            movie_stats,
            target_movie_ids,
        )
    )

    # ---------------------------------------------------------
    # DEFENCE
    # ---------------------------------------------------------

    defended_ratings = (
        apply_from_detection_results(
            attacked_ratings,
            detection_results,
        )
    )

    defended_results = (
        get_recommendations(
            user_id=user_id,
            top_n=DEMO_MOVIE_COUNT,
            ratings_data=(
                defended_ratings
            ),
            candidate_movie_ids=(
                candidate_movie_ids
            ),
        )
    )

    aliases = _build_alias_map(
        clean_results,
        target_movie_ids,
        candidate_movie_ids,
    )

    clean_rank_map = _rank_map(
        clean_results
    )

    attacked_rank_map = _rank_map(
        attacked_results
    )

    defended_rank_map = _rank_map(
        defended_results
    )

    clean_score_map = _score_map(
        clean_results
    )

    attacked_score_map = (
        _score_map(
            attacked_results
        )
    )

    defended_score_map = (
        _score_map(
            defended_results
        )
    )

    target_movements = []

    for index, movie_id in enumerate(
        target_movie_ids,
        start=1,
    ):
        clean_rank = (
            clean_rank_map.get(
                movie_id
            )
        )

        attacked_rank = (
            attacked_rank_map.get(
                movie_id
            )
        )

        defended_rank = (
            defended_rank_map.get(
                movie_id
            )
        )

        target_movements.append(
            {
                "movie_id": int(
                    movie_id
                ),
                "display_name": (
                    f"Targeted Movie "
                    f"{index}"
                ),
                "clean_rank": (
                    clean_rank
                ),
                "attacked_rank": (
                    attacked_rank
                ),
                "defended_rank": (
                    defended_rank
                ),
                "clean_score": (
                    clean_score_map.get(
                        movie_id
                    )
                ),
                "attacked_score": (
                    attacked_score_map.get(
                        movie_id
                    )
                ),
                "defended_score": (
                    defended_score_map.get(
                        movie_id
                    )
                ),
                "attack_gain": (
                    clean_rank
                    - attacked_rank
                    if (
                        clean_rank
                        is not None
                        and attacked_rank
                        is not None
                    )
                    else None
                ),
                "recovery": (
                    defended_rank
                    - attacked_rank
                    if (
                        defended_rank
                        is not None
                        and attacked_rank
                        is not None
                    )
                    else None
                ),
            }
        )

    suspicious_count = int(
        (
            detection_results[
                "predicted_label"
            ]
            == "suspicious"
        ).sum()
    )

    summary = defence_summary(
        attacked_ratings,
        defended_ratings,
    )

    return {
        "candidate_movie_ids": (
            candidate_movie_ids
        ),
        "target_movie_ids": (
            target_movie_ids
        ),
        "attack": {
            "type": "Average Push",
            "attack_size_percent_per_target": (
                selected_attack_size
            ),
            "filler_size_percent": (
                DEMO_FILLER_SIZE_PERCENT
            ),
            "fake_profiles": int(
                fake_profiles[
                    "user_id"
                ].nunique()
            ),
        },
        "detection": {
            "threshold": (
                DEMO_THRESHOLD
            ),
            "suspicious_profiles_detected": (
                suspicious_count
            ),
        },
        "defence": summary,
        "target_movements": (
            target_movements
        ),
        "clean": (
            _decorate_results(
                clean_results,
                aliases,
            )
        ),
        "without_robustness": (
            _decorate_results(
                attacked_results,
                aliases,
            )
        ),
        "with_robustness": (
            _decorate_results(
                defended_results,
                aliases,
            )
        ),
    }