from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.movies.models import WebsiteRating

from .forms import SignUpForm


def signup(request):
    """Register a website user, log them in, then begin preference onboarding."""
    if request.user.is_authenticated:
        return redirect("core:home")

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            "Account created. Rate some movies so RMRS can learn your preferences.",
        )
        return redirect("movies:onboarding")

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile(request):
    """Display a small account summary; RMRS is not a social network."""
    rating_count = WebsiteRating.objects.filter(user=request.user).count()
    return render(
        request,
        "accounts/profile.html",
        {"rating_count": rating_count},
    )
