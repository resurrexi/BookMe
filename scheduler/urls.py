from django.urls import path
from . import views

app_name = "scheduler"
urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:event>/", views.time_picker, name="time_picker"),
]
