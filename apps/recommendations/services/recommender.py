"""Stable integration boundary between Django and the real recommender."""
from typing import Protocol


class RecommenderEngine(Protocol):
    def recommend(self, user_id: int, limit: int = 10) -> list[dict]:
        ...


def get_recommendations(user_id: int, top_n: int = 10) -> list[dict]:
    """
    Integration contract expected by the Django presentation layer.

    Replace only this implementation/import when the real recommender is ready.
    Expected rows:
        {"movie_id": 123, "title": "Movie", "predicted_rating": 4.72}

    Never hand-type fake predicted scores here.
    """
    return []
