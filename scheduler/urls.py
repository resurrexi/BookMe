from django.urls import path, register_converter
from . import views


class DateConverter:
    regex = "[0-9]{8}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{value}"


register_converter(DateConverter, "yyyymmdd")

app_name = "scheduler"
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "<slug:event>/<yyyymmdd:date>", views.time_picker, name="time_picker"
    ),
    path("<slug:event>/", views.day_picker, name="calendar"),
]
