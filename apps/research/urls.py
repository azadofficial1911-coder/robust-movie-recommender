from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.lab, name="lab"),
    # Keep the original Week 1 paths/names so teammate links are less likely to break.
    path("attack/", views.attack_lab, name="attack_lab"),
    path("detection/", views.detection, name="detection"),
    path("defence/", views.defence, name="defence"),
    path("evaluation/", views.evaluation, name="evaluation"),
]
