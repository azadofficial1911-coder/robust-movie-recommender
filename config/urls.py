"""Top-level URL configuration for RMRS."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
    path("movies/", include("apps.movies.urls")),
    path("recommendations/", include("apps.recommendations.urls")),
    # Research routes intentionally live at short public paths required by Week 1.
    path("", include("apps.research.urls")),
]
