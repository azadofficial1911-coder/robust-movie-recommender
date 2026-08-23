from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import WatchlistItem, WebsiteRating
from .services.catalog import get_all_movies, get_movie_by_id
from .services.user_state import attach_user_state


def _filtered_movies(request):
    """Apply lightweight catalogue filtering while the real dataset is integrated."""
    movies = get_all_movies()

    query = request.GET.get("q", "").strip().lower()
    genre = request.GET.get("genre", "").strip()
    year_from = request.GET.get("year_from", "").strip()
    year_to = request.GET.get("year_to", "").strip()
    minimum_rating = request.GET.get("rating", "").strip()
    sort_by = request.GET.get("sort", "highest").strip()

    if query:
        movies = [movie for movie in movies if query in movie["title"].lower()]
    if genre:
        movies = [movie for movie in movies if genre.lower() in movie["genres"].lower()]
    if year_from.isdigit():
        movies = [movie for movie in movies if movie["year"] >= int(year_from)]
    if year_to.isdigit():
        movies = [movie for movie in movies if movie["year"] <= int(year_to)]
    try:
        if minimum_rating:
            threshold = float(minimum_rating)
            movies = [movie for movie in movies if movie["rating"] >= threshold]
    except ValueError:
        pass

    if sort_by == "newest":
        movies.sort(key=lambda movie: movie["year"], reverse=True)
    elif sort_by == "title":
        movies.sort(key=lambda movie: movie["title"].lower())
    else:
        movies.sort(key=lambda movie: movie["rating"], reverse=True)

    selected = {
        "query": request.GET.get("q", ""),
        "genre": genre,
        "rating": minimum_rating,
        "sort": sort_by,
        "year_from": year_from,
        "year_to": year_to,
    }
    return movies, selected


@login_required
def explorer(request):
    movies, selected = _filtered_movies(request)
    movies = attach_user_state(movies, request.user)

    return render(
        request,
        "movies/explorer.html",
        {
            "movies": movies,
            "genres": ["Action", "Animation", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"],
            "selected": selected,
        },
    )


@login_required
def detail(request, movie_id):
    movie = get_movie_by_id(movie_id)

    if movie is None:
        raise Http404("Movie not found.")

    # Attach existing user-specific state to the movie.
    movie = attach_user_state([movie], request.user)[0]

    # Get the user's current saved rating for this movie.
    saved_rating = WebsiteRating.objects.filter(
        user=request.user,
        movie_id=movie_id,
    ).first()

    # Check whether this movie is currently in the user's list.
    in_list = WatchlistItem.objects.filter(
        user=request.user,
        movie_id=movie_id,
    ).exists()

    return render(
        request,
        "movies/detail.html",
        {
            "movie": movie,
            "saved_rating": saved_rating,
            "in_list": in_list,
        },
    )


@login_required
@require_POST
def rate_movie(request, movie_id):
    movie = get_movie_by_id(movie_id)
    if movie is None:
        raise Http404("Movie not found.")

    try:
        rating = int(request.POST.get("rating", ""))
    except (TypeError, ValueError):
        rating = 0

    if rating not in {1, 2, 3, 4, 5}:
        messages.error(request, "Please select a rating from 1 to 5.")
        return redirect("movies:detail", movie_id=movie_id)

    # One current rating per user/movie: update instead of duplicate.
    WebsiteRating.objects.update_or_create(
        user=request.user,
        movie_id=movie_id,
        defaults={"rating": rating},
    )
    messages.success(request, f"Your rating for {movie['title']} was saved.")
    return redirect("movies:detail", movie_id=movie_id)


@login_required
def my_ratings(request):
    rows = []
    for saved in WebsiteRating.objects.filter(user=request.user):
        movie = get_movie_by_id(saved.movie_id)
        rows.append(
            {
                "movie": movie or {"title": f"Movie {saved.movie_id}", "year": ""},
                "rating": saved.rating,
                "timestamp": saved.timestamp,
            }
        )
    return render(request, "movies/my_ratings.html", {"rows": rows})


@login_required
def onboarding(request):
    movies = attach_user_state(get_all_movies(), request.user)

    if request.method == "POST":
        for movie in movies:
            raw_rating = request.POST.get(f"rating_{movie['id']}")
            if not raw_rating:
                continue
            try:
                rating = int(raw_rating)
            except (TypeError, ValueError):
                continue
            if rating in {1, 2, 3, 4, 5}:
                WebsiteRating.objects.update_or_create(
                    user=request.user,
                    movie_id=movie["id"],
                    defaults={"rating": rating},
                )

        total = WebsiteRating.objects.filter(user=request.user).count()
        if total >= 10:
            messages.success(
                request,
                "Your preferences are saved. RMRS can now request personalised recommendations.",
            )
            return redirect("recommendations:index")

        messages.warning(
            request,
            f"You currently have {total} saved rating(s). Please rate at least 10 movies.",
        )
        movies = attach_user_state(get_all_movies(), request.user)

    rating_count = WebsiteRating.objects.filter(user=request.user).count()
    return render(
        request,
        "movies/onboarding.html",
        {"movies": movies, "rating_count": rating_count},
    )


@login_required
def my_list(request):
    rows = []
    for item in WatchlistItem.objects.filter(user=request.user):
        movie = get_movie_by_id(item.movie_id)
        if movie:
            rows.append({"movie": movie, "added_at": item.added_at})
    return render(request, "movies/my_list.html", {"rows": rows})


@login_required
@require_POST
def toggle_list(request, movie_id):
    movie = get_movie_by_id(movie_id)
    if movie is None:
        raise Http404("Movie not found.")

    item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        movie_id=movie_id,
    )

    if created:
        messages.success(request, f"{movie['title']} was added to My List.")
    else:
        item.delete()
        messages.info(request, f"{movie['title']} was removed from My List.")

    return redirect("movies:detail", movie_id=movie_id)
