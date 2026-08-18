"""Primary defence: remove profiles identified as suspicious."""
from __future__ import annotations
from typing import Iterable
import pandas as pd

def get_suspicious_user_ids(detection_results: pd.DataFrame, label_column="predicted_label",
                            suspicious_label="suspicious", user_id_column="user_id") -> set:
    required = {user_id_column, label_column}
    missing = required.difference(detection_results.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    return set(detection_results.loc[detection_results[label_column] == suspicious_label, user_id_column])

def remove_suspicious_profiles(ratings: pd.DataFrame, suspicious_user_ids: Iterable,
                               user_id_column="user_id") -> pd.DataFrame:
    if user_id_column not in ratings.columns: raise ValueError(f"Missing required column: {user_id_column}")
    return ratings.loc[~ratings[user_id_column].isin(set(suspicious_user_ids))].copy()

def defence_summary(ratings_before: pd.DataFrame, ratings_after: pd.DataFrame,
                    user_id_column="user_id") -> dict:
    before_users = ratings_before[user_id_column].nunique()
    after_users = ratings_after[user_id_column].nunique()
    return {"users_before": int(before_users), "users_after": int(after_users),
            "users_removed": int(before_users-after_users),
            "ratings_before": int(len(ratings_before)),
            "ratings_after": int(len(ratings_after)),
            "ratings_removed": int(len(ratings_before)-len(ratings_after))}
