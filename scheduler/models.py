from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Location(models.Model):
    PHONE_CALL = 1
    GOOGLE_MEET = 2
    LOCATION_TYPE_CHOICES = [
        (PHONE_CALL, "Phone call"),
        (GOOGLE_MEET, "Google Meet"),
    ]
    location_type = models.IntegerField(
        choices=LOCATION_TYPE_CHOICES,
        default=PHONE_CALL,
        help_text="1=Phone call, 2=Google Meet",
    )
    phone_number = PhoneNumberField(
        blank=True,
        help_text="Only applies to phone call type",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields="location_type",
                condition=models.Q(location_type=2),
                name="one_google_meet_type",
            )
        ]


class EventType(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )
    slug = models.CharField(
        max_length=256,
        unique=True,
        editable=False,
    )
    duration = models.PositiveIntegerField(
        help_text="Duration of event in minutes"
    )
    horizon = models.PositiveIntegerField(
        help_text="How far out can this event type be scheduled in days?"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        blank=True,
    )


class Event(models.Model):
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(
        editable=False,
    )
    booker_email = models.CharField(
        max_length=64,
    )


class Schedule(models.Model):
    schedule_name = models.CharField()
    sun_start = models.TimeField()
    sun_end = models.TimeField()
    mon_start = models.TimeField()
    mon_end = models.TimeField()
    tue_start = models.TimeField()
    tue_end = models.TimeField()
    wed_start = models.TimeField()
    wed_end = models.TimeField()
    thu_start = models.TimeField()
    thu_end = models.TimeField()
    fri_start = models.TimeField()
    fri_end = models.TimeField()
    sat_start = models.TimeField()
    sat_end = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(sun_start__lt=models.F("sun_end")),
                name="sun_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(mon_start__lt=models.F("mon_end")),
                name="mon_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(tue_start__lt=models.F("tue_end")),
                name="tue_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(wed_start__lt=models.F("wed_end")),
                name="wed_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(thu_start__lt=models.F("thu_end")),
                name="thu_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(fri_start__lt=models.F("fri_end")),
                name="fri_time_range",
            ),
            models.CheckConstraint(
                check=models.Q(sat_start__lt=models.F("sat_end")),
                name="sat_time_range",
            ),
        ]
