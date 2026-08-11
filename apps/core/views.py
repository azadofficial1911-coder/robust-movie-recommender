"""Views for shared site pages."""
from django.shortcuts import render
from apps.movies.services.catalog import get_featured_movies


def home(request):
    """Render the Week 1 landing page with local demo movie content."""
    context = {
        "featured_movies": get_featured_movies(limit=4),
        "genres": ["Action", "Drama", "Sci-Fi", "Thriller"],
    }
    return render(request, "core/home.html", context)
