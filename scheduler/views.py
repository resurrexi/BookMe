from django.shortcuts import render, redirect
from .models import Event


def index(request):
    return render(request, "scheduler/index.html")

def time_picker(request, event):
    EVENT_CHOICES = [
        "phone-call-15-min",
        "phone-call-30-min",
        "phone-call-45-min",
        "phone-call-60-min",
        "google-meet-15-min",
        "google-meet-30-min",
        "google-meet-45-min",
        "google-meet-60-min",
    ]

    if event not in EVENT_CHOICES:
        return redirect("scheduler:index")

    if request.htmx:
        template = "scheduler/partials/time_picker_form.html"
    else:
        template = "scheduler/time_picker.html"

    return render(request, template)
