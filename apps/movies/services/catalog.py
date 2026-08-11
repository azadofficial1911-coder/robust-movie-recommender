"""Movie catalogue service boundary.

Replace the in-memory Week 1 data behind these functions later without forcing
views/templates to know whether records came from MovieLens, a database, or TMDB.
"""

_DUMMY_MOVIES = [
    {
        "id": 1,
        "title": "The Dark Knight",
        "year": 2008,
        "genres": "Action · Drama",
        "rating": 4.8,
        "poster": "images/posters/dark-knight.svg",
    },
    {
        "id": 2,
        "title": "Interstellar",
        "year": 2014,
        "genres": "Drama · Sci-Fi",
        "rating": 4.7,
        "poster": "images/posters/interstellar.svg",
    },
    {
        "id": 3,
        "title": "Inception",
        "year": 2010,
        "genres": "Action · Sci-Fi",
        "rating": 4.6,
        "poster": "images/posters/inception.svg",
    },
    {
        "id": 4,
        "title": "The Matrix",
        "year": 1999,
        "genres": "Action · Sci-Fi",
        "rating": 4.5,
        "poster": "images/posters/matrix.svg",
    },
    {
        "id": 5,
        "title": "Arrival",
        "year": 2016,
        "genres": "Drama · Sci-Fi",
        "rating": 4.3,
        "poster": "images/posters/arrival.svg",
    },
    {
        "id": 6,
        "title": "Blade Runner 2049",
        "year": 2017,
        "genres": "Drama · Sci-Fi",
        "rating": 4.2,
        "poster": "images/posters/blade-runner.svg",
    },
]


def get_all_movies() -> list[dict]:
    """Return a copy so callers cannot mutate the shared demo catalogue."""
    return [movie.copy() for movie in _DUMMY_MOVIES]


def get_featured_movies(limit: int = 4) -> list[dict]:
    """Return the highest-rated demo movies for the Home page."""
    movies = sorted(_DUMMY_MOVIES, key=lambda movie: movie["rating"], reverse=True)
    return [movie.copy() for movie in movies[:limit]]
