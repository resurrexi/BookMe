from django.contrib import admin
from .models import Event, EventType, Schedule, Location

admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(Schedule)
admin.site.register(Location)
