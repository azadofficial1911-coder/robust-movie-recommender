"""Movie catalogue boundary for the Django presentation layer.

The first six entries preserve the Week 1 catalogue. Additional sample entries
make the first-time 10+ rating experience possible until the team's real movie
catalogue mapping is connected.
"""

_MOVIES = [
    {"id": 1, "title": "The Dark Knight", "year": 2008, "genres": "Action · Drama", "rating": 4.8, "poster": "images/posters/dark-knight.svg"},
    {"id": 2, "title": "Interstellar", "year": 2014, "genres": "Drama · Sci-Fi", "rating": 4.7, "poster": "images/posters/interstellar.svg"},
    {"id": 3, "title": "Inception", "year": 2010, "genres": "Action · Sci-Fi", "rating": 4.6, "poster": "images/posters/inception.svg"},
    {"id": 4, "title": "The Matrix", "year": 1999, "genres": "Action · Sci-Fi", "rating": 4.5, "poster": "images/posters/matrix.svg"},
    {"id": 5, "title": "Arrival", "year": 2016, "genres": "Drama · Sci-Fi", "rating": 4.3, "poster": "images/posters/arrival.svg"},
    {"id": 6, "title": "Blade Runner 2049", "year": 2017, "genres": "Drama · Sci-Fi", "rating": 4.2, "poster": "images/posters/blade-runner.svg"},
    {"id": 7, "title": "Toy Story", "year": 1995, "genres": "Animation · Comedy", "rating": 4.3, "poster": ""},
    {"id": 8, "title": "Star Wars", "year": 1977, "genres": "Action · Sci-Fi", "rating": 4.6, "poster": ""},
    {"id": 9, "title": "Titanic", "year": 1997, "genres": "Drama · Romance", "rating": 4.1, "poster": ""},
    {"id": 10, "title": "Alien", "year": 1979, "genres": "Horror · Sci-Fi", "rating": 4.4, "poster": ""},
    {"id": 11, "title": "Gladiator", "year": 2000, "genres": "Action · Drama", "rating": 4.5, "poster": ""},
    {"id": 12, "title": "The Truman Show", "year": 1998, "genres": "Comedy · Drama", "rating": 4.2, "poster": ""},
]


def get_all_movies() -> list[dict]:
    return [movie.copy() for movie in _MOVIES]


def get_movie_by_id(movie_id: int) -> dict | None:
    for movie in _MOVIES:
        if movie["id"] == movie_id:
            return movie.copy()
    return None


def get_featured_movies(limit: int = 4) -> list[dict]:
    movies = sorted(_MOVIES, key=lambda movie: movie["rating"], reverse=True)
    return [movie.copy() for movie in movies[:limit]]
