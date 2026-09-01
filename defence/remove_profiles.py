"""Primary defence: remove profiles predicted as suspicious."""
from pathlib import Path
import pandas as pd

def get_suspicious_user_ids(detection_results, user_id_column="user_id",
                            label_column="predicted_label", suspicious_label="suspicious"):
    missing={user_id_column,label_column}-set(detection_results.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    return set(detection_results.loc[detection_results[label_column]==suspicious_label,user_id_column])

def remove_suspicious_profiles(attacked_dataset, suspicious_user_ids, user_id_column="user_id"):
    if user_id_column not in attacked_dataset.columns: raise ValueError(f"Missing required column: {user_id_column}")
    return attacked_dataset.loc[~attacked_dataset[user_id_column].isin(set(suspicious_user_ids))].copy()

def apply_from_detection_results(attacked_dataset, detection_results, output_path=None):
    suspicious=get_suspicious_user_ids(detection_results)
    defended=remove_suspicious_profiles(attacked_dataset,suspicious)
    if output_path:
        p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True); defended.to_csv(p,index=False)
    return defended

def defence_summary(attacked_dataset, defended_dataset, user_id_column="user_id"):
    bu=attacked_dataset[user_id_column].nunique(); au=defended_dataset[user_id_column].nunique()
    return {"users_before":int(bu),"users_after":int(au),"users_removed":int(bu-au),
            "ratings_before":int(len(attacked_dataset)),"ratings_after":int(len(defended_dataset)),
            "ratings_removed":int(len(attacked_dataset)-len(defended_dataset))}
