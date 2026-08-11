"""Temporary Week 1 recommendation service.

The view imports this service instead of embedding results directly. The real
collaborative-filtering implementation can later replace this call while keeping
URLs and templates stable.
"""

_DEMO_RESULTS = [
    {"title": "Interstellar", "predicted_score": 4.72},
    {"title": "The Matrix", "predicted_score": 4.51},
    {"title": "Inception", "predicted_score": 4.44},
    {"title": "The Dark Knight", "predicted_score": 4.38},
    {"title": "Arrival", "predicted_score": 4.29},
    {"title": "Blade Runner 2049", "predicted_score": 4.21},
]


def get_demo_recommendations(limit: int = 10) -> list[dict]:
    """Return demo output that is explicitly labelled as non-model data in the UI."""
    return [item.copy() for item in _DEMO_RESULTS[:limit]]
