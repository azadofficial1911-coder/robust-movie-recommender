from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.movies.services.catalog import get_all_movies
from apps.movies.services.user_state import attach_user_state
from apps.recommendations.services.recommender import get_recommendations


@login_required
def home(request):
    """Authenticated streaming-style RMRS home page."""
    movies = attach_user_state(get_all_movies(), request.user)

    featured = movies[0] if movies else None
    popular_movies = sorted(movies, key=lambda movie: movie["rating"], reverse=True)[:6]
    action_movies = [movie for movie in movies if "Action" in movie["genres"]][:6]
    comedy_movies = [movie for movie in movies if "Comedy" in movie["genres"]][:6]

    # Real scores must come from the recommender integration, not the web layer.
    recommended = get_recommendations(request.user.id, top_n=6)

    return render(
        request,
        "core/home.html",
        {
            "featured": featured,
            "popular_movies": popular_movies,
            "action_movies": action_movies,
            "comedy_movies": comedy_movies,
            "recommended": recommended,
        },
    )
