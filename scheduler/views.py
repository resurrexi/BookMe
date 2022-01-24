from itertools import product
from django.shortcuts import render, redirect
from django.utils.text import slugify
from .models import Event


def join_slugs(iterable):
    return "-".join(iterable)


def index(request):
    return render(request, "scheduler/index.html")


def time_picker(request, event):
    # dynamically generate cartesian product of location type and duration
    LOCATIONS = list(map(slugify, Event.LocationType.labels))
    DURATIONS = list(map(slugify, Event.Duration.labels))
    PRODUCT_RESULT = list(product(LOCATIONS, DURATIONS))
    EVENT_CHOICES = list(map(join_slugs, PRODUCT_RESULT))

    if event not in EVENT_CHOICES:
        return redirect("scheduler:index")

    if request.htmx:
        template = "scheduler/partials/time_picker_form.html"
    else:
        template = "scheduler/time_picker.html"

    return render(request, template)
