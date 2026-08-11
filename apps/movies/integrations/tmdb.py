"""Future TMDB integration boundary.

Do not add API keys to source code. When TMDB is introduced, read credentials
from environment variables and keep HTTP/API-specific logic in this module.
"""


def fetch_movie_metadata(*args, **kwargs):
    """Placeholder for a future TMDB adapter."""
    raise NotImplementedError("TMDB integration is outside the Week 1 scope.")
