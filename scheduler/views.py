import calendar
from itertools import product
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.utils import timezone
from .models import Event, Schedule


def join_slugs(iterable):
    return "-".join(iterable)


def add_availability_to_week(week, availability):
    return zip(week, availability)


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

    # determine current date in UTC
    today = timezone.now()

    # build availability flags
    availability_flags = [1, 1, 1, 1, 1, 1, 1]  # 1=day on, 0=day off
    availability = Schedule.objects.first()
    if availability.sun_off:
        availability_flags[0] = 0
    if availability.mon_off:
        availability_flags[1] = 0
    if availability.tue_off:
        availability_flags[2] = 0
    if availability.wed_off:
        availability_flags[3] = 0
    if availability.thu_off:
        availability_flags[4] = 0
    if availability.fri_off:
        availability_flags[5] = 0
    if availability.sat_off:
        availability_flags[6] = 0

    # build calendar of available days for current month
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    weeks = cal.monthdayscalendar(today.year, today.month)
    monthly_cal = [
        add_availability_to_week(week, availability_flags) for week in weeks
    ]

    return render(
        request,
        template,
        {
            "calendar": monthly_cal,
            "current_date": today,
            "weekdays": ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
        },
    )
