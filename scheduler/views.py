import calendar
from itertools import product
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.utils import timezone
from .models import Event, Schedule


def join_slugs(iterable):
    return "-".join(iterable)


def add_availability_to_week(week, availability):
    return zip(week, availability)


def parse_event(event):
    split_string = event.split("-")
    event_type = "phone" if split_string[0] == "phone" else "gmeet"
    duration = int(split_string[-2])
    return event_type, duration


def index(request):
    return render(request, "scheduler/index.html")


def day_picker(request, event):
    # dynamically generate cartesian product of location type and duration
    LOCATIONS = list(map(slugify, Event.LocationType.labels))
    DURATIONS = list(map(slugify, Event.Duration.labels))
    PRODUCT_RESULT = list(product(LOCATIONS, DURATIONS))
    EVENT_CHOICES = list(map(join_slugs, PRODUCT_RESULT))

    if event not in EVENT_CHOICES:
        return redirect("scheduler:index")

    if request.htmx:
        template = "scheduler/partials/calendar.html"
    else:
        template = "scheduler/booking_form.html"

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

    # get the date with the month to display, if available
    # if not available, default to today's date
    # this will be the proxy for displaying the month on the calendar
    calendar_day = datetime.strptime(
        request.GET.get("day", today.strftime("%Y%m%d")), "%Y%m%d"
    )

    # build calendar of available days for current month
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    weeks = cal.monthdatescalendar(calendar_day.year, calendar_day.month)
    monthly_cal = [
        add_availability_to_week(week, availability_flags) for week in weeks
    ]

    return render(
        request,
        template,
        {
            "event": event,
            "calendar": monthly_cal,
            "month_proxy": calendar_day,
            "previous": weeks[0][0] + timedelta(days=-1),
            "next": weeks[-1][-1] + timedelta(days=1),
            "current_date": today,
            "horizon_date": today + timedelta(days=60),
            "weekdays": ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
        },
    )


def time_picker(request, event, date):
    template = "scheduler/partials/time_picker.html"

    # get the weekday of the date as number
    # 0=Sun, 1=Mon, ..., 5=Fri, 6=Sat
    weekday = datetime.strptime(date, "%Y%m%d").strftime("%w")

    # get the schedule for that weekday
    schedule = Schedule.objects.first()
    if weekday == 0:
        start = schedule.sun_start
        end = schedule.sun_end
    elif weekday == 1:
        start = schedule.mon_start
        end = schedule.mon_off
    elif weekday == 2:
        start = schedule.tue_start
        end = schedule.tue_end
    elif weekday == 3:
        start = schedule.wed_start
        end = schedule.wed_end
    elif weekday == 4:
        start = schedule.thu_start
        end = schedule.thu_end
    elif weekday == 5:
        start = schedule.fri_start
        end = schedule.fri_end
    else:
        start = schedule.sat_start
        end = schedule.sat_end

    return render(
        request,
        template,
        {
            "event": event,
            "date": date,
            "availability_start": start,
            "availability_end": end,
        },
    )
