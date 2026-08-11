from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Shared public pages and site-level UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
