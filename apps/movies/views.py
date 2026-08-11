"""HTTP views for the movie browsing experience."""
from django.shortcuts import render
from .services.catalog import get_all_movies


def explorer(request):
    """Render the Week 1 Movie Explorer.

    The controls are intentionally present before real dataset filtering is wired
    in. Keeping the UI contract stable lets the data/recommender work connect later.
    """
    context = {
        "movies": get_all_movies(),
        "genres": ["Action", "Drama", "Sci-Fi", "Thriller"],
        "selected": {
            "query": request.GET.get("q", ""),
            "genre": request.GET.get("genre", ""),
            "rating": request.GET.get("rating", ""),
            "sort": request.GET.get("sort", "highest"),
            "year_from": request.GET.get("year_from", ""),
            "year_to": request.GET.get("year_to", ""),
        },
    }
    return render(request, "movies/explorer.html", context)
