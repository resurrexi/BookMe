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
    _LOCATIONS = list(map(slugify, Event.LocationType.labels))
    _DURATIONS = list(map(slugify, Event.Duration.labels))
    _PRODUCT_RESULT = list(product(_LOCATIONS, _DURATIONS))
    _EVENT_CHOICES = list(map(join_slugs, _PRODUCT_RESULT))

    if event not in _EVENT_CHOICES:
        return redirect("scheduler:index")

    if request.htmx:
        template = "scheduler/partials/time_picker_form.html"
    else:
        template = "scheduler/time_picker.html"

    return render(request, template)
