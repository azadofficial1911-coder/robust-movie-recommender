from django.apps import AppConfig


class MoviesConfig(AppConfig):
    """Movie catalogue, browsing, metadata, and future TMDB integration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.movies"
