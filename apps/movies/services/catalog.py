"""Movie catalogue boundary backed by the processed MovieLens data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MOVIE_STATS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "movie_statistics.csv"
)


def _display_title(value: object) -> str:
    title = str(value).strip()
    return title.title() if title else "Untitled Movie"


def _load_movies() -> list[dict]:
    movie_stats = pd.read_csv(MOVIE_STATS_FILE)

    required_columns = {
        "movie_id",
        "title",
        "rating_count",
        "mean_rating",
    }
    missing = required_columns.difference(movie_stats.columns)
    if missing:
        raise ValueError(
            "movie_statistics.csv is missing required columns: "
            + ", ".join(sorted(missing))
        )

    movie_stats = movie_stats.dropna(
        subset=["movie_id", "title"]
    ).copy()

    movie_stats["movie_id"] = pd.to_numeric(
        movie_stats["movie_id"], errors="raise"
    ).astype(int)
    movie_stats["rating_count"] = pd.to_numeric(
        movie_stats["rating_count"], errors="coerce"
    ).fillna(0).astype(int)
    movie_stats["mean_rating"] = pd.to_numeric(
        movie_stats["mean_rating"], errors="coerce"
    ).fillna(0.0).astype(float)

    movies = []
    for row in movie_stats.sort_values("movie_id").itertuples(index=False):
        movies.append(
            {
                "id": int(row.movie_id),
                "title": _display_title(row.title),
                "year": "",
                "genres": "MovieLens 100K",
                "rating": round(float(row.mean_rating), 2),
                "rating_count": int(row.rating_count),
                "poster": "",
            }
        )

    return movies


def get_all_movies() -> list[dict]:
    return [movie.copy() for movie in _load_movies()]


def get_movie_by_id(movie_id: int) -> dict | None:
    wanted = int(movie_id)
    for movie in _load_movies():
        if movie["id"] == wanted:
            return movie.copy()
    return None


def get_featured_movies(limit: int = 4) -> list[dict]:
    movies = sorted(
        _load_movies(),
        key=lambda movie: (
            movie["rating_count"] >= 50,
            movie["rating"],
            movie["rating_count"],
        ),
        reverse=True,
    )
    return [movie.copy() for movie in movies[:limit]]
