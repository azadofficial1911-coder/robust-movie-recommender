from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Max
from django.shortcuts import render

from apps.movies.models import WebsiteRating
from apps.recommendations.services.recommender import get_recommendations
from apps.research.services.user_robustness_demo import (
    build_user_robustness_demo,
)

from .home_catalogue import build_home_catalogue


@login_required
def home(request):
    """
    Authenticated Netflix-style RMRS home page.

    The normal movie catalogue comes from the processed MovieLens data.

    Personalised recommendations can also reflect the staff robustness
    demonstration:

    - Robustness ON  -> defended/protected recommendations
    - Robustness OFF -> attacked recommendations

    Normal users remain protected.
    """

    catalogue = build_home_catalogue()

    # ---------------------------------------------------------
    # User rating state
    # ---------------------------------------------------------
    user_ratings = WebsiteRating.objects.filter(
        user=request.user
    )

    rating_count = user_ratings.count()

    latest_timestamp = user_ratings.aggregate(
        latest=Max("timestamp")
    )["latest"]

    # ---------------------------------------------------------
    # Robustness mode
    #
    # Normal users are always protected.
    # Staff may toggle the demonstration mode.
    # ---------------------------------------------------------
    robustness_enabled = True

    if request.user.is_staff:
        robustness_enabled = not bool(
            request.session.get(
                "robustness_disabled",
                False,
            )
        )

    robustness_demo = None
    demo_error = None
    active_mode = "clean"

    # ---------------------------------------------------------
    # Build/reuse the same robustness demonstration used by
    # the Recommendations page.
    # ---------------------------------------------------------
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

        robustness_demo = cache.get(cache_key)

        if robustness_demo is None:
            try:
                robustness_demo = build_user_robustness_demo(
                    request.user.id
                )

                cache.set(
                    cache_key,
                    robustness_demo,
                    timeout=900,
                )

            except Exception as exc:
                if request.user.is_staff:
                    demo_error = str(exc)

    # ---------------------------------------------------------
    # Select the active recommendation state.
    # ---------------------------------------------------------
    if robustness_demo:

        if request.user.is_staff and not robustness_enabled:
            recommended = (
                robustness_demo["without_robustness"][:12]
            )
            active_mode = "attacked"

        else:
            recommended = (
                robustness_demo["with_robustness"][:12]
            )
            active_mode = "protected"

    else:
        # Normal recommender fallback when the robustness
        # demonstration cannot yet be generated.
        recommended = get_recommendations(
            request.user.id,
            top_n=12,
        )

    context = {
        **catalogue,
        "recommended": recommended,
        "rating_count": rating_count,
        "robustness_enabled": robustness_enabled,
        "robustness_demo": robustness_demo,
        "active_mode": active_mode,
        "demo_error": demo_error,
    }

    return render(
        request,
        "core/home.html",
        context,
    )