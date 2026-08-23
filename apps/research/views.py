from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def staff_required(view_func):
    """Require a genuine authenticated staff/research account."""
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Research Lab access is restricted to staff.")
        return view_func(request, *args, **kwargs)

    return wrapped


@staff_required
def lab(request):
    return render(request, "research/index.html")


@staff_required
def attack_lab(request):
    return render(
        request,
        "research/attack_lab.html",
        {"page_title": "Attack Laboratory", "status_label": "Integration Ready"},
    )


@staff_required
def detection(request):
    return render(
        request,
        "research/detection.html",
        {"page_title": "Suspicious-User Detection", "status_label": "Integration Ready"},
    )


@staff_required
def defence(request):
    return render(
        request,
        "research/defence.html",
        {"page_title": "Defence Centre", "status_label": "Integration Ready"},
    )


@staff_required
def evaluation(request):
    return render(
        request,
        "research/evaluation.html",
        {"page_title": "Evaluation Dashboard", "status_label": "Integration Ready"},
    )
