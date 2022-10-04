import calendar
import json
from datetime import datetime, time, timedelta
from itertools import product

import pytz
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.text import slugify

from .lib.planner import EventPlanner
from .models import Event, Schedule

WEEKDAY_MAP = {
    "0": {
        "previous": ["sat_off", "sat_start", "sat_end"],
        "now": ["sun_off", "sun_start", "sun_end"],
        "next": ["mon_off", "mon_start", "mon_end"],
    },
    "1": {
        "previous": ["sun_off", "sun_start", "sun_end"],
        "now": ["mon_off", "mon_start", "mon_end"],
        "next": ["tue_off", "tue_start", "tue_end"],
    },
    "2": {
        "previous": ["mon_off", "mon_start", "mon_end"],
        "now": ["tue_off", "tue_start", "tue_end"],
        "next": ["wed_off", "wed_start", "wed_end"],
    },
    "3": {
        "previous": ["tue_off", "tue_start", "tue_end"],
        "now": ["wed_off", "wed_start", "wed_end"],
        "next": ["thu_off", "thu_start", "thu_end"],
    },
    "4": {
        "previous": ["wed_off", "wed_start", "wed_end"],
        "now": ["thu_off", "thu_start", "thu_end"],
        "next": ["fri_off", "fri_start", "fri_end"],
    },
    "5": {
        "previous": ["thu_off", "thu_start", "thu_end"],
        "now": ["fri_off", "fri_start", "fri_end"],
        "next": ["sat_off", "sat_start", "sat_end"],
    },
    "6": {
        "previous": ["fri_off", "fri_start", "fri_end"],
        "now": ["sat_off", "sat_start", "sat_end"],
        "next": ["sun_off", "sun_start", "sun_end"],
    },
}


def join_slugs(iterable):
    return "-".join(iterable)


def add_availability_to_week(week, availability):
    return zip(week, availability)


def parse_event(event):
    split_string = event.split("-")
    event_type = "phone" if split_string[0] == "phone" else "gmeet"
    duration = int(split_string[-2])
    return event_type, duration


def build_dt_to_iso(date, time):
    return pytz.utc.localize(datetime.combine(date, time)).isoformat()


def build_artificial_events(selected_date, prev_day, next_day):
    DAY_MAP = {
        "previous": prev_day,
        "now": selected_date,
        "next": next_day,
    }

    # get the weekday of the date as number
    # 0=Sun, 1=Mon, ..., 5=Fri, 6=Sat
    weekday = selected_date.strftime("%w")

    # use a buffer of a day from the selected date due to timezone differences
    artificial_events = []
    schedule = Schedule.objects.first()
    for day in ["previous", "now", "next"]:
        if getattr(schedule, WEEKDAY_MAP[weekday][day][0]):
            artificial_events.append(
                {
                    "start": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(), time(0, 0, 0)
                        )
                    },
                    "end": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(), time(23, 59, 59)
                        )
                    },
                }
            )
        else:
            artificial_events.append(
                {
                    "start": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(), time(0, 0, 0)
                        )
                    },
                    "end": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(),
                            getattr(schedule, WEEKDAY_MAP[weekday][day][1]),
                        )
                    },
                }
            )
            artificial_events.append(
                {
                    "start": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(),
                            getattr(schedule, WEEKDAY_MAP[weekday][day][2]),
                        )
                    },
                    "end": {
                        "dateTime": build_dt_to_iso(
                            DAY_MAP[day].date(), time(23, 59, 59)
                        )
                    },
                }
            )

    return artificial_events


def build_available_times(start, end, duration, events):
    available_times = []
    now = timezone.now()
    current_start = start
    current_end = current_start + timedelta(minutes=duration)
    while current_end <= end:
        skip = False

        if current_start > now:
            # iterate through events
            for event in events:
                event_start = datetime.fromisoformat(
                    event["start"]["dateTime"]
                )
                event_end = datetime.fromisoformat(event["end"]["dateTime"])
                # break out of loop due to time conflicts with event
                if (
                    current_start >= event_start and current_start < event_end
                ) or (current_end > event_start and current_end <= event_end):
                    skip = True
                    break

            # only add to available times if `skip=False`
            if not skip:
                available_times.append(current_start)

        # add duration to `current_start` and `current_end`
        current_start = current_start + timedelta(minutes=duration)
        current_end = current_start + timedelta(minutes=duration)
    return available_times


def index(request):
    return render(request, "scheduler/index.html")


def set_user_tz(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        request.session["user_tz"] = payload["timezone"]
        return HttpResponse("Timezone set for session")
    return HttpResponseNotAllowed(["GET"])


def day_picker(request, event):
    # get timezone optional param, if passed into url
    # this param is passed via htmx
    tz_param = request.GET.get("timezone", None)
    # if param was passed, update session variable
    if tz_param:
        request.session["user_tz"] = tz_param

    user_tz = pytz.timezone(request.session.get("user_tz", "UTC"))

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

    # determine current date in user's timezone and make date naive
    # making the date naive will force django to resolve the date as-is
    # without converting to UTC when rendering in the template
    today = timezone.now().astimezone(user_tz).replace(tzinfo=None)

    # get the date with the month to display, if available
    # if not available, default to today's date
    # this will be the proxy for displaying the month on the calendar
    calendar_day = datetime.strptime(
        request.GET.get("day", today.strftime("%Y%m%d")), "%Y%m%d"
    )

    # build calendar of available days for current month
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    weeks = cal.monthdatescalendar(calendar_day.year, calendar_day.month)

    return render(
        request,
        template,
        {
            "event": event,
            "calendar": weeks,
            "month_proxy": calendar_day,
            "previous": weeks[0][0] + timedelta(days=-1),
            "next": weeks[-1][-1] + timedelta(days=1),
            "current_date": today,
            "horizon_date": today + timedelta(days=60),
            "weekdays": ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
            "user_tz": user_tz.zone,
            "timezones": pytz.common_timezones,
        },
    )


def time_picker(request, event, date):
    # get timezone optional param, if passed into url
    # this param is passed via htmx
    tz_param = request.GET.get("timezone", None)
    # if param was passed, update session variable
    if tz_param:
        request.session["user_tz"] = tz_param

    template = "scheduler/partials/time_picker.html"

    planner = EventPlanner()
    selected_date = datetime.strptime(date, "%Y%m%d")
    prev_day = selected_date + timedelta(days=-1)
    next_day = selected_date + timedelta(days=1)
    user_tz = pytz.timezone(request.session.get("user_tz", "UTC"))
    time_min = user_tz.localize(selected_date)
    time_max = time_min + timedelta(days=1)

    # artificially build unavailable time slots based on schedule
    unavailable = build_artificial_events(selected_date, prev_day, next_day)

    # get the calendar events for that day
    calendar_events = planner.get_events(
        time_min.isoformat(), time_max.isoformat()
    )

    # build available time slots
    _, event_duration = parse_event(event)
    available_times = build_available_times(
        time_min, time_max, event_duration, unavailable + calendar_events
    )

    return render(
        request,
        template,
        {
            "event": event,
            "selected_date": selected_date.date(),
            "previous": prev_day.date(),
            "next": next_day.date(),
            "available_times": available_times,
            "user_tz": user_tz.zone,
            "timezones": pytz.common_timezones,
        },
    )
