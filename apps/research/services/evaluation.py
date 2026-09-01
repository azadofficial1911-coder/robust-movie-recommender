"""Evaluation integration boundary for the RMRS research module.

Week 6: connects Django to the real evaluation functions in
evaluation/recommender_metrics.py, evaluation/attack_metrics.py and
evaluation/detection_metrics.py (repo root).

Signatures here match those modules exactly as used throughout the
codebase (see experiments/evaluate_defence_effect.py and
experiments/evaluate_recommender_metrics.py) -- in particular,
target_score(predicted_scores, target_movie) takes a
{movie_id: predicted_rating} dict for ONE user, not a list average.
"""

from statistics import mean
from typing import Iterable, Sequence

from evaluation.attack_metrics import hit_rate, target_rank, target_score
from evaluation.detection_metrics import detection_metrics
from evaluation.recommender_metrics import mae, precision_at_k, recall_at_k, rmse

EXPECTED_METRICS = (
    "RMSE",
    "MAE",
    "PRECISION_AT_K",
    "RECALL_AT_K",
    "TARGET_RANK",
    "TARGET_SCORE",
    "HIT_RATE",
    "DETECTION_PRECISION",
    "DETECTION_RECALL",
    "DETECTION_F1",
    "FALSE_POSITIVE_RATE",
)


def evaluate_recommendation_quality(
    *,
    actual: Sequence[float],
    predicted: Sequence[float],
    recommended_lists=None,
    relevant_items=None,
    k: int = 10,
) -> dict:
    """RMSE/MAE for one condition, plus mean Precision@K/Recall@K if
    per-user recommendation lists and relevant-item sets are supplied."""

    metrics = {"rmse": rmse(actual, predicted), "mae": mae(actual, predicted)}

    if recommended_lists is not None and relevant_items is not None:
        recommended_lists = list(recommended_lists)
        relevant_items = list(relevant_items)
        precisions = [precision_at_k(r, rel, k) for r, rel in zip(recommended_lists, relevant_items)]
        recalls = [recall_at_k(r, rel, k) for r, rel in zip(recommended_lists, relevant_items)]
        metrics["precision_at_k"] = mean(precisions) if precisions else 0.0
        metrics["recall_at_k"] = mean(recalls) if recalls else 0.0

    return metrics


def evaluate_attack_impact_for_user(
    *,
    recommended_movie_ids: Sequence,
    predicted_scores: dict,
    target_movie_id,
    k: int = 10,
) -> dict:
    """Target rank, target score and hit@k for ONE user.

    predicted_scores must be a {movie_id: predicted_rating} mapping, as
    produced by recommender.baseline_recommender.recommend_movies().
    """

    rank = target_rank(recommended_movie_ids, target_movie_id)
    score = target_score(predicted_scores, target_movie_id)
    hit = rank is not None and rank <= k

    return {"target_rank": rank, "target_score": score, "hit_at_k": hit}


def summarise_attack_impact(per_user_results: list[dict]) -> dict:
    """Aggregate a list of evaluate_attack_impact_for_user() outputs into
    the mean_target_rank / mean_target_score / hit_rate_at_k form used
    by experiments/evaluate_defence_effect.py."""

    ranks = [r["target_rank"] for r in per_user_results if r["target_rank"] is not None]
    scores = [r["target_score"] for r in per_user_results if r["target_score"] is not None]
    hits = [r["hit_at_k"] for r in per_user_results]

    return {
        "target_rank": mean(ranks) if ranks else None,
        "target_score": mean(scores) if scores else None,
        "hit_rate": hit_rate(hits),
    }


def evaluate_detection(
    *,
    true_labels: Sequence[str],
    predicted_labels: Sequence[str],
    positive_label: str = "suspicious",
) -> dict:
    """Precision/Recall/F1/False Positive Rate for the detector."""

    raw = detection_metrics(true_labels, predicted_labels, positive_label=positive_label)
    return {
        "detection_precision": raw["precision"],
        "detection_recall": raw["recall"],
        "detection_f1": raw["f1"],
        "false_positive_rate": raw["false_positive_rate"],
    }


def evaluate_experiment(
    *,
    clean_results: dict = None,
    attacked_results: dict = None,
    defended_results: dict = None,
) -> dict:
    """
    Evaluate Clean, Attacked and Defended conditions and return one
    combined dict ready for the Evaluation dashboard / experiment_results.csv.

    Each *_results argument is optional. When supplied it may contain:

        "actual": [...], "predicted": [...],              # -> RMSE / MAE
        "recommended_lists": [[...], ...],                  # -> Precision/Recall@K
        "relevant_items": [{...}, ...],                     # -> Precision/Recall@K
        "attack_impact_per_user": [ {...}, ... ],            # each item is the
                                                              # output of
                                                              # evaluate_attack_impact_for_user()
        "true_labels": [...], "predicted_labels": [...],    # -> detection metrics
        "k": 10,

    A condition with no data supplied is omitted from the result.
    """

    conditions = {"clean": clean_results, "attacked": attacked_results, "defended": defended_results}
    evaluated: dict[str, dict] = {}

    for condition, data in conditions.items():
        if not data:
            continue

        result: dict = {}

        if "actual" in data and "predicted" in data:
            result.update(
                evaluate_recommendation_quality(
                    actual=data["actual"],
                    predicted=data["predicted"],
                    recommended_lists=data.get("recommended_lists"),
                    relevant_items=data.get("relevant_items"),
                    k=data.get("k", 10),
                )
            )

        if data.get("attack_impact_per_user"):
            result.update(summarise_attack_impact(data["attack_impact_per_user"]))

        if data.get("true_labels") is not None and data.get("predicted_labels") is not None:
            result.update(
                evaluate_detection(
                    true_labels=data["true_labels"],
                    predicted_labels=data["predicted_labels"],
                )
            )

        if result:
            evaluated[condition] = result

    if not evaluated:
        raise ValueError(
            "evaluate_experiment() requires at least one of clean_results, "
            "attacked_results or defended_results with real, usable data."
        )

    return evaluated
