from apps.movies.models import WatchlistItem, WebsiteRating


def attach_user_state(movies, user):
    """Attach the current user's rating and My List state to movie dictionaries."""
    movies = [movie.copy() for movie in movies]
    movie_ids = [movie["id"] for movie in movies]

    ratings = {
        item.movie_id: item.rating
        for item in WebsiteRating.objects.filter(user=user, movie_id__in=movie_ids)
    }
    listed_ids = set(
        WatchlistItem.objects.filter(user=user, movie_id__in=movie_ids)
        .values_list("movie_id", flat=True)
    )

    for movie in movies:
        movie["user_rating"] = ratings.get(movie["id"])
        movie["in_list"] = movie["id"] in listed_ids

    return movies
