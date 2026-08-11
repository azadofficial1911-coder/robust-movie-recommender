"""Placeholder research views prepared for later team integration."""
from django.shortcuts import render


def attack_lab(request):
    return render(
        request,
        "research/attack_lab.html",
        {"page_title": "Attack Laboratory", "status_label": "Integration Ready"},
    )


def detection(request):
    return render(
        request,
        "research/detection.html",
        {"page_title": "Suspicious-User Detection", "status_label": "Integration Ready"},
    )


def defence(request):
    return render(
        request,
        "research/defence.html",
        {"page_title": "Defence Centre", "status_label": "Integration Ready"},
    )


def evaluation(request):
    return render(
        request,
        "research/evaluation.html",
        {"page_title": "Evaluation Dashboard", "status_label": "Integration Ready"},
    )
