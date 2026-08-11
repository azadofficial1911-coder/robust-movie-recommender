"""Interface for the future real recommender engine."""
from typing import Protocol


class RecommenderEngine(Protocol):
    """Contract the web layer can depend on regardless of algorithm choice."""

    def recommend(self, user_id: int, limit: int = 10) -> list[dict]:
        """Return ranked recommendations for a user."""
        ...
