from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.recommendations.services.recommender import get_recommendations

from .home_catalogue import build_home_catalogue


@login_required
def home(request):
    """Authenticated Netflix-style RMRS home page backed by real MovieLens data."""

    catalogue = build_home_catalogue()

    # Personalised recommendations still come from the existing recommender.
    recommended = get_recommendations(
        request.user.id,
        top_n=12,
    )

    return render(
        request,
        "core/home.html",
        {
            **catalogue,
            "recommended": recommended,
        },
    )
