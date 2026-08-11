"""Views for recommendation presentation."""
from django.shortcuts import render
from .services.demo import get_demo_recommendations


def index(request):
    """Render a frontend-only recommendation workflow for Week 1."""
    selected_user = request.GET.get("user", "196")
    try:
        limit = max(1, min(int(request.GET.get("limit", "10")), 20))
    except ValueError:
        limit = 10

    context = {
        "selected_user": selected_user,
        "selected_limit": limit,
        "demo_results": get_demo_recommendations(limit=limit),
    }
    return render(request, "recommendations/index.html", context)
