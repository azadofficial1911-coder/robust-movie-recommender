from functools import wraps

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .services.attacks import AttackConfig, validate_attack_config
from .services.detection import CANDIDATE_FEATURES, validate_threshold
from .services.evaluation import EXPECTED_METRICS
from .services.live_workflow import (
    MOVIE_STATS_FILE,
    run_attack,
    run_defence,
    run_detection,
    run_evaluation,
    workflow_status,
)
from .services.results_loader import load_result_figures
from .services.robustness_comparison import (
    build_robustness_comparison,
    normalise_scenario,
)


def staff_required(view_func):
    """Require an authenticated staff/research account."""

    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied(
                "Research Lab access is restricted to staff."
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def _session_key(request) -> str:
    """Ensure the staff browser has a stable session key for live experiments."""

    if request.session.session_key is None:
        request.session.create()
    return str(request.session.session_key)


def _research_movie_catalogue() -> list[dict]:
    """Load the real processed MovieLens catalogue used by the experiments."""

    movie_stats = pd.read_csv(MOVIE_STATS_FILE)

    required_columns = {"movie_id", "title"}
    missing = required_columns.difference(movie_stats.columns)
    if missing:
        raise ValueError(
            "movie_statistics.csv is missing required columns: "
            + ", ".join(sorted(missing))
        )

    movies = []

    for row in movie_stats.sort_values("movie_id").itertuples(index=False):
        movies.append(
            {
                "id": int(row.movie_id),
                "title": str(row.title),
                "rating_count": int(getattr(row, "rating_count", 0)),
                "mean_rating": float(getattr(row, "mean_rating", 0.0)),
            }
        )

    return movies


@staff_required
def lab(request):
    status = workflow_status(_session_key(request))
    return render(
        request,
        "research/index.html",
        {"workflow_status": status},
    )


@staff_required
def attack_lab(request):
    """Configure and execute a real Random Push or Average Push attack."""

    movies = _research_movie_catalogue()
    movie_lookup = {
        int(movie["id"]): movie
        for movie in movies
    }

    errors = []
    attack_requested = False
    attack_result = None

    form_data = {
        "attack_type": "random",
        "target_movie_id": "",
        "attack_size_percent": 5,
        "filler_size_percent": 20,
        "random_seed": 42,
    }

    if request.method == "POST":
        attack_requested = True
        form_data = {
            "attack_type": request.POST.get("attack_type", "random"),
            "target_movie_id": request.POST.get("target_movie_id", ""),
            "attack_size_percent": request.POST.get("attack_size_percent", "5"),
            "filler_size_percent": request.POST.get("filler_size_percent", "20"),
            "random_seed": request.POST.get("random_seed", "42"),
        }

        try:
            target_movie_id = int(form_data["target_movie_id"])

            if target_movie_id not in movie_lookup:
                errors.append(
                    "Target movie ID does not exist in the processed MovieLens catalogue."
                )

            config = AttackConfig(
                attack_type=form_data["attack_type"],
                target_movie_id=target_movie_id,
                attack_size_percent=float(form_data["attack_size_percent"]),
                filler_size_percent=float(form_data["filler_size_percent"]),
                random_seed=int(form_data["random_seed"]),
            )
            errors.extend(validate_attack_config(config))

            if not errors:
                attack_result = run_attack(
                    _session_key(request),
                    config,
                )
                attack_result["target_movie_title"] = movie_lookup[
                    target_movie_id
                ]["title"]
        except (TypeError, ValueError) as exc:
            errors.append(
                str(exc)
                or "Please enter valid values for the attack configuration."
            )

    status = workflow_status(_session_key(request))

    return render(
        request,
        "research/attack_lab.html",
        {
            "page_title": "Attack Laboratory",
            "movies": movies,
            "movie_count": len(movies),
            "errors": errors,
            "attack_requested": attack_requested,
            "attack_result": attack_result,
            "form_data": form_data,
            "workflow_status": status,
        },
    )


@staff_required
def detection(request):
    """Run suspicious-user detection on the current session's attacked data."""

    errors = []
    detection_requested = False
    detection_result = None
    threshold = "0.5"
    status = workflow_status(_session_key(request))

    if request.method == "POST":
        detection_requested = True
        threshold = request.POST.get("threshold", "0.5")

        try:
            threshold_value = float(threshold)
            validate_threshold(threshold_value)
            detection_result = run_detection(
                _session_key(request),
                threshold=threshold_value,
            )
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))

        status = workflow_status(_session_key(request))

    if detection_result is None and status.get("has_detection"):
        detection_result = status.get("detection_summary")

    return render(
        request,
        "research/detection.html",
        {
            "page_title": "Suspicious-User Detection",
            "errors": errors,
            "detection_requested": detection_requested,
            "detection_result": detection_result,
            "threshold": threshold,
            "candidate_features": CANDIDATE_FEATURES,
            "workflow_status": status,
        },
    )


@staff_required
def defence(request):
    """Apply the real remove-suspicious-profiles defence to current attacked data."""

    errors = []
    defence_result = None
    status = workflow_status(_session_key(request))

    if request.method == "POST":
        try:
            defence_result = run_defence(
                _session_key(request)
            )
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))
        status = workflow_status(_session_key(request))

    if defence_result is None and status.get("has_defence"):
        defence_result = status.get("defence_summary")

    return render(
        request,
        "research/defence.html",
        {
            "page_title": "Defence Centre",
            "errors": errors,
            "defence_result": defence_result,
            "workflow_status": status,
        },
    )


@staff_required
def evaluation(request):
    """Evaluate live clean, attacked and defended datasets from this session."""

    errors = []
    evaluation_result = None
    status = workflow_status(_session_key(request))

    if request.method == "POST":
        try:
            evaluation_result = run_evaluation(
                _session_key(request)
            )
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))
        status = workflow_status(_session_key(request))

    if evaluation_result is None and status.get("has_evaluation"):
        evaluation_result = status.get("evaluation")

    return render(
        request,
        "research/evaluation.html",
        {
            "page_title": "Evaluation Dashboard",
            "expected_metrics": EXPECTED_METRICS,
            "evaluation_result": evaluation_result,
            "experiment_results": (
                evaluation_result.get("rows")
                if evaluation_result
                else None
            ),
            "result_figures": load_result_figures(),
            "errors": errors,
            "workflow_status": status,
        },
    )


@staff_required
def robustness_comparison(request):
    """Existing reproducible pilot comparison from committed experiment evidence."""

    requested_scenario = request.GET.get("scenario", "random")

    try:
        selected_scenario = normalise_scenario(requested_scenario)
    except ValueError:
        selected_scenario = "random"

    comparison = build_robustness_comparison(selected_scenario)

    return render(
        request,
        "research/robustness_comparison.html",
        {
            "page_title": "Robustness Comparison",
            "selected_scenario": selected_scenario,
            "comparison": comparison,
            "results_available": comparison is not None,
        },
    )
