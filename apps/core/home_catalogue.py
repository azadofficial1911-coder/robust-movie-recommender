"""Home-page catalogue helpers backed by the real processed MovieLens data."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MOVIE_STATS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "movie_statistics.csv"
)

TOP_SHELF_SIZE = 24
MIN_TOP_RATED_COUNT = 50


def _display_title(value: object) -> str:
    """Return a readable title without changing the underlying movie ID."""

    title = str(value).strip()
    if not title:
        return "Untitled Movie"

    # The processed MovieLens titles are stored in lower case.
    # Title-casing here is presentation only.
    return title.title()


def load_home_movies() -> list[dict]:
    """Load every movie available in the processed MovieLens statistics file."""

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
        movie_stats["movie_id"],
        errors="raise",
    ).astype(int)
    movie_stats["rating_count"] = pd.to_numeric(
        movie_stats["rating_count"],
        errors="coerce",
    ).fillna(0).astype(int)
    movie_stats["mean_rating"] = pd.to_numeric(
        movie_stats["mean_rating"],
        errors="coerce",
    ).fillna(0.0).astype(float)

    movies = []
    for row in movie_stats.sort_values(
        ["title", "movie_id"],
        kind="stable",
    ).itertuples(index=False):
        movies.append(
            {
                "id": int(row.movie_id),
                "title": _display_title(row.title),
                "rating": round(float(row.mean_rating), 2),
                "rating_count": int(row.rating_count),
            }
        )

    return movies


def build_home_catalogue() -> dict:
    """Build Netflix-style shelves while ensuring every movie is represented."""

    movies = load_home_movies()

    most_rated = sorted(
        movies,
        key=lambda movie: (
            movie["rating_count"],
            movie["rating"],
            movie["title"],
        ),
        reverse=True,
    )[:TOP_SHELF_SIZE]

    eligible_top_rated = [
        movie
        for movie in movies
        if movie["rating_count"] >= MIN_TOP_RATED_COUNT
    ]

    top_rated = sorted(
        eligible_top_rated,
        key=lambda movie: (
            movie["rating"],
            movie["rating_count"],
        ),
        reverse=True,
    )[:TOP_SHELF_SIZE]

    grouped: dict[str, list[dict]] = defaultdict(list)
    for movie in movies:
        first = movie["title"][:1].upper()
        key = first if first.isalpha() else "#"
        grouped[key].append(movie)

    alphabetical_rows = []
    for key in sorted(
        grouped,
        key=lambda value: (value == "#", value),
    ):
        alphabetical_rows.append(
            {
                "key": key,
                "title": f"Movies {key}" if key != "#" else "Movies #",
                "movies": grouped[key],
            }
        )

    featured = (
        top_rated[0]
        if top_rated
        else (most_rated[0] if most_rated else None)
    )

    return {
        "all_movies": movies,
        "movie_count": len(movies),
        "featured": featured,
        "most_rated": most_rated,
        "top_rated": top_rated,
        "alphabetical_rows": alphabetical_rows,
    }
