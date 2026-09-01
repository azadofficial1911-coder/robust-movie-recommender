"""Defence integration boundary for the RMRS research module.

Week 6: connects Django to the real primary defence implementation in
`defence/remove_profiles.py` (repo root) -- removal of profiles
predicted as suspicious by Azad's detection module.

Signatures here match the top-level defence/ and evaluation/ modules
exactly (see experiments/apply_defence.py, which this mirrors for the
Django-facing boundary).
"""

import pandas as pd

from defence.remove_profiles import (
    defence_summary,
    get_suspicious_user_ids,
    remove_suspicious_profiles,
)

DEFENCE_METHOD = "remove_suspicious_profiles"


def apply_defence(*, ratings: pd.DataFrame = None, detection_results: pd.DataFrame = None) -> dict:
    """
    Apply the primary Week 6 defence: remove profiles predicted as suspicious.

    Parameters
    ----------
    ratings : pandas.DataFrame
        The attacked rating dataset (columns: user_id, movie_id, rating, ...).
    detection_results : pandas.DataFrame
        Azad's detection output (columns: user_id, suspicion_score,
        predicted_label, true_label).

    Rules
    -----
    - Defence decisions use `predicted_label` only, never `true_label`.
    - `ratings` is never mutated; the defended data is returned separately.

    Returns
    -------
    dict with:
        "defended_ratings"    : pandas.DataFrame -- ratings with suspicious
                                 users removed
        "suspicious_user_ids" : sorted list of removed user IDs
        "summary"             : dict -- users/ratings before & after,
                                 counts removed, defence_method, status
    """

    if ratings is None or detection_results is None:
        raise ValueError(
            "apply_defence() requires both 'ratings' and 'detection_results'. "
            "These come from Azad's attack module output and detection output."
        )

    suspicious_ids = get_suspicious_user_ids(
        detection_results,
        user_id_column="user_id",
        label_column="predicted_label",
        suspicious_label="suspicious",
    )

    defended_ratings = remove_suspicious_profiles(ratings, suspicious_ids)

    summary = defence_summary(ratings, defended_ratings)
    summary["defence_method"] = DEFENCE_METHOD
    summary["suspicious_profiles_detected"] = len(suspicious_ids)
    summary["status"] = "applied"

    return {
        "defended_ratings": defended_ratings,
        "suspicious_user_ids": sorted(suspicious_ids),
        "summary": summary,
    }
