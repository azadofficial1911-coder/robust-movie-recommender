"""Live staff research workflow for Attack -> Detection -> Defence -> Evaluation.

This service connects the existing RMRS algorithms without replacing them.
The web Research Lab stores one reproducible experiment per staff session in
Django's cache, so every stage operates on the exact attacked dataset created
by the previous stage.
"""

from __future__ import annotations

from statistics import mean
from pathlib import Path

import pandas as pd
from django.core.cache import cache

from apps.research.services.attacks import (
    AttackConfig,
    generate_average_push,
    generate_random_push,
)
from apps.research.services.detection import detect_suspicious_users
from apps.research.services.evaluation import evaluate_detection
from defence.remove_profiles import apply_from_detection_results, defence_summary
from evaluation.attack_metrics import hit_rate, target_rank, target_score
from evaluation.recommender_metrics import mae, rmse
from recommender.baseline_recommender import (
    build_user_item_matrix,
    build_user_similarity_matrix,
    calculate_user_means,
    predict_rating,
    recommend_movies,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAIN_FILE = PROJECT_ROOT / "data" / "processed" / "train_ratings.csv"
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "test_ratings.csv"
MOVIE_STATS_FILE = PROJECT_ROOT / "data" / "processed" / "movie_statistics.csv"

CACHE_TIMEOUT_SECONDS = 60 * 60
EVALUATION_USER_LIMIT = 7
RMSE_SAMPLE_LIMIT = 500
TOP_K = 10


def _cache_key(session_key: str) -> str:
    if not session_key:
        raise ValueError("A valid Django session key is required.")
    return f"rmrs:live-research:{session_key}"


def get_workflow(session_key: str) -> dict | None:
    return cache.get(_cache_key(session_key))


def clear_workflow(session_key: str) -> None:
    cache.delete(_cache_key(session_key))


def _save_workflow(session_key: str, workflow: dict) -> dict:
    cache.set(
        _cache_key(session_key),
        workflow,
        timeout=CACHE_TIMEOUT_SECONDS,
    )
    return workflow


def _load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clean = pd.read_csv(TRAIN_FILE)
    test = pd.read_csv(TEST_FILE)
    movie_stats = pd.read_csv(MOVIE_STATS_FILE)
    return clean, test, movie_stats


def run_attack(session_key: str, config: AttackConfig) -> dict:
    """Generate a real attacked dataset and start a new live workflow."""

    clean, test, movie_stats = _load_sources()

    target_movie_id = int(config.target_movie_id)
    attack_size = float(config.attack_size_percent)
    filler_size = float(config.filler_size_percent)

    if config.attack_type == "random":
        fake_profiles = generate_random_push(
            ratings=clean,
            target_movie_id=target_movie_id,
            attack_size_percent=attack_size,
            filler_size_percent=filler_size,
            global_average_rating=float(clean["rating"].mean()),
            random_seed=int(config.random_seed),
            target_rating=int(config.target_rating),
        )
    elif config.attack_type == "average":
        fake_profiles = generate_average_push(
            ratings=clean,
            movie_statistics=movie_stats,
            target_movie_id=target_movie_id,
            attack_size_percent=attack_size,
            filler_size_percent=filler_size,
            random_seed=int(config.random_seed),
            target_rating=int(config.target_rating),
        )
    else:
        raise ValueError(f"Unsupported attack type: {config.attack_type}")

    attacked = pd.concat(
        [
            clean[["user_id", "movie_id", "rating"]].copy(deep=True),
            fake_profiles[["user_id", "movie_id", "rating"]].copy(deep=True),
        ],
        ignore_index=True,
    )

    fake_user_ids = sorted(
        int(value) for value in fake_profiles["user_id"].unique()
    )

    attack_summary = {
        "attack_type": config.attack_type,
        "target_movie_id": target_movie_id,
        "attack_size_percent": attack_size,
        "filler_size_percent": filler_size,
        "random_seed": int(config.random_seed),
        "target_rating": int(config.target_rating),
        "genuine_users": int(clean["user_id"].nunique()),
        "genuine_ratings": int(len(clean)),
        "fake_profiles": int(fake_profiles["user_id"].nunique()),
        "fake_ratings": int(len(fake_profiles)),
        "attacked_users": int(attacked["user_id"].nunique()),
        "attacked_ratings": int(len(attacked)),
    }

    workflow = {
        "stage": "attack",
        "config": attack_summary,
        "clean": clean,
        "test": test,
        "movie_stats": movie_stats,
        "fake_profiles": fake_profiles,
        "fake_user_ids": fake_user_ids,
        "attacked": attacked,
        "attack_summary": attack_summary,
        "detection_results": None,
        "detection_summary": None,
        "defended": None,
        "defence_summary": None,
        "evaluation": None,
    }

    _save_workflow(session_key, workflow)
    return attack_summary


def run_detection(session_key: str, threshold: float = 0.5) -> dict:
    """Run the real detector against the exact attacked dataset in session."""

    workflow = get_workflow(session_key)
    if not workflow or workflow.get("attacked") is None:
        raise ValueError("Run an attack first. No attacked dataset is available.")

    results = detect_suspicious_users(
        ratings=workflow["attacked"],
        threshold=float(threshold),
        movie_statistics=workflow["movie_stats"],
        target_movie_id=int(workflow["config"]["target_movie_id"]),
    )

    detection_df = pd.DataFrame(
        [
            {
                "user_id": int(result.user_id),
                "suspicion_score": float(result.suspicion_score),
                "predicted_label": result.predicted_label,
            }
            for result in results
        ]
    )

    fake_user_ids = set(workflow["fake_user_ids"])
    detection_df["true_label"] = detection_df["user_id"].apply(
        lambda user_id: "suspicious" if int(user_id) in fake_user_ids else "genuine"
    )

    metrics = evaluate_detection(
        true_labels=detection_df["true_label"].tolist(),
        predicted_labels=detection_df["predicted_label"].tolist(),
    )

    suspicious = detection_df[
        detection_df["predicted_label"] == "suspicious"
    ].sort_values("suspicion_score", ascending=False)

    summary = {
        "threshold": float(threshold),
        "users_analysed": int(len(detection_df)),
        "suspicious_profiles_detected": int(len(suspicious)),
        "genuine_predicted": int(
            (detection_df["predicted_label"] == "genuine").sum()
        ),
        "detection_precision": float(metrics["detection_precision"]),
        "detection_recall": float(metrics["detection_recall"]),
        "detection_f1": float(metrics["detection_f1"]),
        "false_positive_rate": float(metrics["false_positive_rate"]),
        "top_suspicious": suspicious.head(15).to_dict("records"),
    }

    workflow["stage"] = "detection"
    workflow["detection_results"] = detection_df
    workflow["detection_summary"] = summary
    workflow["defended"] = None
    workflow["defence_summary"] = None
    workflow["evaluation"] = None
    _save_workflow(session_key, workflow)
    return summary


def run_defence(session_key: str) -> dict:
    """Remove profiles predicted suspicious from the exact attacked dataset."""

    workflow = get_workflow(session_key)
    if not workflow or workflow.get("attacked") is None:
        raise ValueError("Run an attack first.")
    if workflow.get("detection_results") is None:
        raise ValueError("Run detection before applying defence.")

    defended = apply_from_detection_results(
        workflow["attacked"],
        workflow["detection_results"],
    )

    summary = defence_summary(
        workflow["attacked"],
        defended,
    )
    summary.update(
        {
            "method": "Remove predicted suspicious profiles",
            "suspicious_profiles_detected": int(
                workflow["detection_summary"]["suspicious_profiles_detected"]
            ),
        }
    )

    workflow["stage"] = "defence"
    workflow["defended"] = defended
    workflow["defence_summary"] = summary
    workflow["evaluation"] = None
    _save_workflow(session_key, workflow)
    return summary


def _build_state(ratings: pd.DataFrame):
    matrix = build_user_item_matrix(ratings)
    means = calculate_user_means(matrix)
    similarities = build_user_similarity_matrix(matrix, means)
    return matrix, similarities, means


def _evaluation_users(clean: pd.DataFrame, target_movie_id: int) -> list[int]:
    target_raters = set(
        int(value)
        for value in clean.loc[
            clean["movie_id"] == target_movie_id,
            "user_id",
        ].unique()
    )

    counts = clean.groupby("user_id").size().sort_values(ascending=False)
    candidates = [
        int(user_id)
        for user_id in counts.index
        if int(user_id) not in target_raters
    ]

    if not candidates:
        raise ValueError("No genuine evaluation users are available for this target.")

    return candidates[:EVALUATION_USER_LIMIT]


def _target_metrics_for_condition(
    ratings: pd.DataFrame,
    target_movie_id: int,
    evaluation_users: list[int],
) -> dict:
    matrix, similarities, means = _build_state(ratings)
    total_movies = len(matrix.columns)
    per_user = []

    for user_id in evaluation_users:
        if user_id not in matrix.index:
            per_user.append(
                {
                    "user_id": user_id,
                    "target_rank": None,
                    "target_score": None,
                    "hit_at_10": False,
                }
            )
            continue

        predicted_target = predict_rating(
            user_id=user_id,
            movie_id=target_movie_id,
            user_item_matrix=matrix,
            similarity_matrix=similarities,
            user_means=means,
        )

        recommendations = recommend_movies(
            user_id=user_id,
            user_item_matrix=matrix,
            similarity_matrix=similarities,
            user_means=means,
            top_n=total_movies,
        )

        movie_ids = [int(item["movie_id"]) for item in recommendations]
        scores = {
            int(item["movie_id"]): float(item["predicted_rating"])
            for item in recommendations
        }
        rank = target_rank(movie_ids, target_movie_id)
        score = target_score(scores, target_movie_id)
        if score is None and predicted_target is not None:
            score = float(predicted_target)

        per_user.append(
            {
                "user_id": user_id,
                "target_rank": rank,
                "target_score": score,
                "hit_at_10": rank is not None and rank <= TOP_K,
            }
        )

    ranks = [row["target_rank"] for row in per_user if row["target_rank"] is not None]
    scores = [row["target_score"] for row in per_user if row["target_score"] is not None]

    return {
        "target_rank": mean(ranks) if ranks else None,
        "target_score": mean(scores) if scores else None,
        "hit_rate": hit_rate([row["hit_at_10"] for row in per_user]),
        "per_user": per_user,
        "state": (matrix, similarities, means),
    }


def _quality_metrics_same_rows(
    states: dict[str, tuple],
    test: pd.DataFrame,
) -> dict[str, dict]:
    sample = test[["user_id", "movie_id", "rating"]].head(
        RMSE_SAMPLE_LIMIT
    ).copy()

    predictions: dict[str, dict[int, float]] = {
        condition: {} for condition in states
    }
    actual_by_index: dict[int, float] = {}

    for row in sample.itertuples():
        index = int(row.Index)
        actual_by_index[index] = float(row.rating)

        for condition, (matrix, similarities, means) in states.items():
            prediction = predict_rating(
                user_id=int(row.user_id),
                movie_id=int(row.movie_id),
                user_item_matrix=matrix,
                similarity_matrix=similarities,
                user_means=means,
            )
            if prediction is not None:
                predictions[condition][index] = float(prediction)

    common_indexes = set(actual_by_index)
    for condition_predictions in predictions.values():
        common_indexes &= set(condition_predictions)

    ordered_indexes = sorted(common_indexes)
    if not ordered_indexes:
        return {
            condition: {"rmse": None, "mae": None, "predictions": 0}
            for condition in states
        }

    actual = [actual_by_index[index] for index in ordered_indexes]
    quality = {}

    for condition, condition_predictions in predictions.items():
        predicted = [condition_predictions[index] for index in ordered_indexes]
        quality[condition] = {
            "rmse": float(rmse(actual, predicted)),
            "mae": float(mae(actual, predicted)),
            "predictions": int(len(predicted)),
        }

    return quality


def run_evaluation(session_key: str) -> dict:
    """Evaluate the live clean, attacked and defended datasets now in session."""

    workflow = get_workflow(session_key)
    if not workflow or workflow.get("attacked") is None:
        raise ValueError("Run an attack first.")
    if workflow.get("defended") is None:
        raise ValueError("Run detection and defence before evaluation.")

    target_movie_id = int(workflow["config"]["target_movie_id"])
    evaluation_users = _evaluation_users(workflow["clean"], target_movie_id)

    conditions = {
        "clean": workflow["clean"],
        "attacked": workflow["attacked"],
        "defended": workflow["defended"],
    }

    target_results = {}
    states = {}
    for name, ratings in conditions.items():
        condition = _target_metrics_for_condition(
            ratings,
            target_movie_id,
            evaluation_users,
        )
        states[name] = condition.pop("state")
        target_results[name] = condition

    quality = _quality_metrics_same_rows(states, workflow["test"])

    rows = []
    labels = {
        "clean": "Clean",
        "attacked": "Attacked / Robustness OFF",
        "defended": "Defended / Robustness ON",
    }

    for name in ("clean", "attacked", "defended"):
        rows.append(
            {
                "condition": name,
                "condition_label": labels[name],
                "rmse": quality[name]["rmse"],
                "mae": quality[name]["mae"],
                "predictions": quality[name]["predictions"],
                "target_rank": target_results[name]["target_rank"],
                "target_score": target_results[name]["target_score"],
                "hit_rate": target_results[name]["hit_rate"],
            }
        )

    clean_rank = target_results["clean"]["target_rank"]
    attacked_rank = target_results["attacked"]["target_rank"]
    defended_rank = target_results["defended"]["target_rank"]

    evaluation = {
        "target_movie_id": target_movie_id,
        "evaluation_users": evaluation_users,
        "rows": rows,
        "per_user": {
            name: target_results[name]["per_user"]
            for name in target_results
        },
        "detection": workflow["detection_summary"],
        "defence": workflow["defence_summary"],
        "attack_promoted_target": (
            clean_rank is not None
            and attacked_rank is not None
            and attacked_rank < clean_rank
        ),
        "defence_reduced_attack": (
            attacked_rank is not None
            and defended_rank is not None
            and defended_rank > attacked_rank
        ),
    }

    workflow["stage"] = "evaluation"
    workflow["evaluation"] = evaluation
    _save_workflow(session_key, workflow)
    return evaluation


def workflow_status(session_key: str) -> dict:
    workflow = get_workflow(session_key)
    if not workflow:
        return {
            "has_attack": False,
            "has_detection": False,
            "has_defence": False,
            "has_evaluation": False,
        }

    return {
        "has_attack": workflow.get("attacked") is not None,
        "has_detection": workflow.get("detection_results") is not None,
        "has_defence": workflow.get("defended") is not None,
        "has_evaluation": workflow.get("evaluation") is not None,
        "stage": workflow.get("stage"),
        "attack_summary": workflow.get("attack_summary"),
        "detection_summary": workflow.get("detection_summary"),
        "defence_summary": workflow.get("defence_summary"),
        "evaluation": workflow.get("evaluation"),
    }
