from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import RMRSAuthenticationForm

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=RMRSAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
]
