from django.shortcuts import render
from .models import EventType


def index(request):
    event_types = EventType.objects.all()
    return render(
        request, "scheduler/index.html", {"event_types": event_types}
    )
