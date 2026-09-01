"""Secondary defence: reduce suspicious-user influence."""
import pandas as pd

def apply_user_weights(ratings, suspicious_user_ids, suspicious_weight=0.5,
                       user_id_column="user_id", weight_column="defence_weight"):
    if not 0.0 <= suspicious_weight <= 1.0: raise ValueError("suspicious_weight must be between 0 and 1.")
    if user_id_column not in ratings.columns: raise ValueError(f"Missing required column: {user_id_column}")
    suspicious=set(suspicious_user_ids); result=ratings.copy()
    result[weight_column]=result[user_id_column].map(lambda uid:suspicious_weight if uid in suspicious else 1.0)
    return result
