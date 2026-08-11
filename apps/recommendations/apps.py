from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    """Recommendation UI and future recommendation-engine integration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recommendations"
