"""Views for the recommendation presentation layer."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.movies.models import WebsiteRating

from .services.recommender import get_recommendations


@login_required
def index(request):
    """
    Display personalised recommendation results for the logged-in user.

    The Django layer does not calculate recommendations itself.
    Real recommendation results will come from the recommender service.
    """

    try:
        top_n = int(request.GET.get("top_n", 10))
    except ValueError:
        top_n = 10

    # Keep the requested number within a sensible range.
    top_n = min(max(top_n, 1), 50)

    # Ask the recommendation integration service for results.
    results = get_recommendations(
        request.user.id,
        top_n=top_n,
    )

    # Count genuine ratings saved by this Django user.
    rating_count = WebsiteRating.objects.filter(
        user=request.user
    ).count()

    context = {
        "results": results,
        "rating_count": rating_count,
        "top_n": top_n,
    }

    return render(
        request,
        "recommendations/index.html",
        context,
    )