from django.urls import path
from . import views

app_name = "recommendations"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "toggle-robustness/",
        views.toggle_robustness,
        name="toggle_robustness",
    ),
]
