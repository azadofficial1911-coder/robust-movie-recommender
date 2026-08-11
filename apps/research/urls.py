from django.urls import path
from . import views

app_name = "research"

urlpatterns = [
    path("attack/", views.attack_lab, name="attack_lab"),
    path("detection/", views.detection, name="detection"),
    path("defence/", views.defence, name="defence"),
    path("evaluation/", views.evaluation, name="evaluation"),
]
