"""Views for the recommendation presentation layer."""

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.movies.models import WebsiteRating
from apps.research.services.user_robustness_demo import (
    build_user_robustness_demo,
)

from .services.recommender import get_recommendations


@login_required
def index(request):
    """
    Display personalised recommendation results for the logged-in user.

    Normal users are always protected. Staff can switch between the attacked
    and defended states through the global robustness control.
    """

    try:
        top_n = int(request.GET.get("top_n", 10))
    except ValueError:
        top_n = 10

    top_n = min(max(top_n, 1), 50)

    user_ratings = WebsiteRating.objects.filter(
        user=request.user
    )
    rating_count = user_ratings.count()
    latest_timestamp = user_ratings.aggregate(
        latest=Max("timestamp")
    )["latest"]

    robustness_enabled = True

    if request.user.is_staff:
        robustness_enabled = not bool(
            request.session.get(
                "robustness_disabled",
                False,
            )
        )

    demo = None
    demo_error = None

    if rating_count >= 3:
        timestamp_key = (
            latest_timestamp.isoformat()
            if latest_timestamp is not None
            else "none"
        )
        cache_key = (
            f"robustness-demo:user:{request.user.id}:"
            f"ratings:{rating_count}:{timestamp_key}"
        )
        demo = cache.get(cache_key)

        if demo is None:
            try:
                demo = build_user_robustness_demo(
                    request.user.id
                )
                cache.set(
                    cache_key,
                    demo,
                    timeout=900,
                )
            except Exception as exc:
                if request.user.is_staff:
                    demo_error = str(exc)

    if demo:
        if request.user.is_staff and not robustness_enabled:
            source_results = demo["without_robustness"]
            active_mode = "attacked"
        else:
            source_results = demo["with_robustness"]
            active_mode = "protected"

        results = source_results[:top_n]
    else:
        results = get_recommendations(
            request.user.id,
            top_n=top_n,
        )
        active_mode = "clean"

    context = {
        "results": results,
        "rating_count": rating_count,
        "top_n": top_n,
        "robustness_enabled": robustness_enabled,
        "active_mode": active_mode,
        "robustness_demo": demo,
        "demo_error": demo_error,
    }

    return render(
        request,
        "recommendations/index.html",
        context,
    )


@require_POST
@login_required
def toggle_robustness(request):
    """Allow staff only to switch the demonstration protection state."""

    if not request.user.is_staff:
        return JsonResponse(
            {"error": "Staff access required."},
            status=403,
        )

    disabled = bool(
        request.session.get(
            "robustness_disabled",
            False,
        )
    )

    request.session["robustness_disabled"] = not disabled
    request.session.modified = True

    enabled = disabled

    return JsonResponse(
        {
            "robustness_enabled": enabled,
            "mode": "protected" if enabled else "attacked",
        }
    )
