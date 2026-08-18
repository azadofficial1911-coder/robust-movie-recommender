"""Suspicious-user detection interfaces for the RMRS research module.

Week 1 defines candidate behavioural features, suspicion-score handling,
classification rules, and the standard detection-result structure.

The final detector will be implemented after feature selection,
attack generation, and supervisor confirmation.
"""

from dataclasses import dataclass


CANDIDATE_FEATURES = (
    "rating_deviation",
    "profile_size",
    "extreme_rating_ratio",
    "profile_similarity",
    "target_item_behaviour",
    "filler_pattern_behaviour",
)


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


def detect_suspicious_users(
    ratings,
    threshold: float = 0.5,
):
    """Analyse user-rating behaviour and detect suspicious profiles.

    Planned implementation:
    1. Group ratings by user.
    2. Calculate approved behavioural features.
    3. Normalise feature values.
    4. Calculate a suspicion score for each user.
    5. Apply the selected classification threshold.
    6. Return structured DetectionResult records.

    The final detection method will be implemented after the candidate
    features have been evaluated and approved.
    """

    raise NotImplementedError(
        "Final suspicious-user detection requires approved behavioural features."
    )
