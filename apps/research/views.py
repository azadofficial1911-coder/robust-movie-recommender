from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.movies.services.catalog import get_all_movies

from .services.attacks import AttackConfig, validate_attack_config
from .services.detection import (
    CANDIDATE_FEATURES,
    validate_threshold,
)


def staff_required(view_func):
    """Require a genuine authenticated staff/research account."""
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Research Lab access is restricted to staff.")
        return view_func(request, *args, **kwargs)

    return wrapped


@staff_required
def lab(request):
    return render(request, "research/index.html")


@staff_required
def attack_lab(request):
    """
    Staff-only interface for configuring attack experiments.

    Django handles the form and validates the configuration.
    The actual Random Push and Average Push generation remains
    in the research backend.
    """

    movies = get_all_movies()

    errors = []
    attack_requested = False
    config_valid = False

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
            "attack_type": request.POST.get(
                "attack_type",
                "random",
            ),
            "target_movie_id": request.POST.get(
                "target_movie_id",
                "",
            ),
            "attack_size_percent": request.POST.get(
                "attack_size_percent",
                "5",
            ),
            "filler_size_percent": request.POST.get(
                "filler_size_percent",
                "20",
            ),
            "random_seed": request.POST.get(
                "random_seed",
                "42",
            ),
        }

        try:
            config = AttackConfig(
                attack_type=form_data["attack_type"],
                target_movie_id=int(
                    form_data["target_movie_id"]
                ),
                attack_size_percent=float(
                    form_data["attack_size_percent"]
                ),
                filler_size_percent=float(
                    form_data["filler_size_percent"]
                ),
                random_seed=int(
                    form_data["random_seed"]
                ),
            )

            errors = validate_attack_config(config)

            if not errors:
                config_valid = True

        except (TypeError, ValueError):
            errors.append(
                "Please enter valid values for the attack configuration."
            )

    return render(
        request,
        "research/attack_lab.html",
        {
            "page_title": "Attack Laboratory",
            "movies": movies,
            "errors": errors,
            "attack_requested": attack_requested,
            "config_valid": config_valid,
            "form_data": form_data,
        },
    )

@staff_required
def detection(request):
    """
    Staff-only interface for configuring suspicious-user detection.

    Django validates the detection configuration and prepares the
    presentation layer. The actual detector remains in the research backend.
    """

    errors = []
    detection_requested = False
    config_valid = False

    threshold = "0.5"

    if request.method == "POST":
        detection_requested = True
        threshold = request.POST.get("threshold", "0.5")

        try:
            threshold_value = float(threshold)

            validate_threshold(threshold_value)

            config_valid = True

        except (TypeError, ValueError) as exc:
            errors.append(str(exc))

    return render(
        request,
        "research/detection.html",
        {
            "page_title": "Suspicious-User Detection",
            "errors": errors,
            "detection_requested": detection_requested,
            "config_valid": config_valid,
            "threshold": threshold,
            "candidate_features": CANDIDATE_FEATURES,
        },
    )


@staff_required
def defence(request):
    """
    Staff-only Defence Centre.

    The presentation layer is prepared for the future defence backend.
    No defence calculations are performed inside Django.
    """

    return render(
        request,
        "research/defence.html",
        {
            "page_title": "Defence Centre",
            "integration_ready": True,
        },
    )


@staff_required
def evaluation(request):
    return render(
        request,
        "research/evaluation.html",
        {"page_title": "Evaluation Dashboard", "status_label": "Integration Ready"},
    )
