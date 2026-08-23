from django.urls import path

from . import views

app_name = "movies"

urlpatterns = [
    path("", views.explorer, name="explorer"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("ratings/", views.my_ratings, name="my_ratings"),
    path("my-list/", views.my_list, name="my_list"),
    path("<int:movie_id>/", views.detail, name="detail"),
    path("<int:movie_id>/rate/", views.rate_movie, name="rate"),
    path("<int:movie_id>/list/", views.toggle_list, name="toggle_list"),
]
