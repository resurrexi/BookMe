import calendar
import json
import pytz
from itertools import product
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.utils import timezone
from .lib.planner import EventPlanner
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

    # determine current date in user's timezone
    today = timezone.now().astimezone(user_tz)

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
            "user_tz": user_tz,
        },
    )


def time_picker(request, event, date):
    template = "scheduler/partials/time_picker.html"
    planner = EventPlanner()
    selected_date = datetime.strptime(date, "%Y%m%d")
    user_tz = pytz.timezone(request.session.get("user_tz", "UTC"))

    # get the weekday of the date as number
    # 0=Sun, 1=Mon, ..., 5=Fri, 6=Sat
    weekday = int(selected_date.strftime("%w"))

    # get the schedule for that weekday
    # add a buffer of a day to account for timezone differences
    schedule = Schedule.objects.first()
    if weekday == 0:
        start = schedule.sat_start or schedule.sun_start
        end = schedule.mon_end or schedule.sun_end
    elif weekday == 1:
        start = schedule.sun_start or schedule.mon_start
        end = schedule.tue_end or schedule.mon_end
    elif weekday == 2:
        start = schedule.mon_start or schedule.tue_start
        end = schedule.wed_end or schedule.tue_end
    elif weekday == 3:
        start = schedule.tue_start or schedule.wed_start
        end = schedule.thu_end or schedule.wed_end
    elif weekday == 4:
        start = schedule.wed_start or schedule.thu_start
        end = schedule.fri_end or schedule.thu_end
    elif weekday == 5:
        start = schedule.thu_start or schedule.fri_start
        end = schedule.sat_end or schedule.fri_end
    else:
        start = schedule.fri_start or schedule.sat_start
        end = schedule.sun_end or schedule.sat_end

    # attach date to schedule times, times saved in DB will be in UTC
    # since UTC times can bleed into prior or next day, take the min/max
    # of the selected date's time boundaries or the scheduled time boundaries
    time_min = user_tz.localize(selected_date)
    time_max = time_min + timedelta(days=1)
    start = max(
        pytz.utc.localize(
            datetime.combine(
                (selected_date + timedelta(days=-1)).date(), start
            )
        ).astimezone(user_tz),
        time_min,
    )
    end = min(
        pytz.utc.localize(
            datetime.combine((selected_date + timedelta(days=1)).date(), end)
        ).astimezone(user_tz),
        time_max,
    )

    # get the calendar events for that day
    calendar_events = planner.get_events(
        time_min.isoformat(), time_max.isoformat()
    )

    # build available time slots
    _, event_duration = parse_event(event)
    available_times = build_available_times(
        start, end, event_duration, calendar_events
    )

    return render(
        request,
        template,
        {
            "event": event,
            "selected_date": selected_date.date(),
            "available_times": available_times,
            "user_tz": user_tz,
        },
    )
