import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


class Location(models.Model):
    class LocationType(models.IntegerChoices):
        PHONE_CALL = 1, "Phone call"
        GOOGLE_MEET = 2, "Google Meet"

    location_type = models.IntegerField(
        choices=LocationType.choices,
        default=LocationType.PHONE_CALL,
        help_text="1=Phone call, 2=Google Meet",
    )
    phone_number = PhoneNumberField(
        blank=True,
        help_text="Only applies to phone call type",
    )

    def __str__(self):
        if self.location_type == self.LocationType.PHONE_CALL:
            return f"{self.get_location_type_display()} {self.phone_number}"
        return self.get_location_type_display()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "location_type",
                ],
                condition=models.Q(location_type=2),
                name="one_google_meet_type",
            ),
            models.UniqueConstraint(
                fields=[
                    "phone_number",
                ],
                condition=models.Q(location_type=1),
                name="unique_number_for_phone_call",
            ),
        ]

    def clean(self):
        if self.location_type == self.LocationType.GOOGLE_MEET:
            # ensure there's only one Google Meet type
            obj_count = Location.objects.filter(
                location_type=self.LocationType.GOOGLE_MEET
            ).count()
            if obj_count > 0:
                raise ValidationError(
                    {"location_type": "Only one Google Meet type allowed"},
                )

        if self.location_type == self.LocationType.PHONE_CALL:
            # ensure phone number is populated
            if not self.phone_number:
                raise ValidationError(
                    {"phone_number": "Missing phone number"},
                )

            # ensure only unique phone number
            obj_count = Location.objects.filter(
                location_type=self.LocationType.PHONE_CALL,
                phone_number=self.phone_number,
            ).count()
            if obj_count > 0:
                raise ValidationError(
                    {"phone_number": "Must be unique"},
                )


class EventType(models.Model):
    class Duration(models.IntegerChoices):
        MIN_15 = 1, "15 min"
        MIN_30 = 2, "30 min"
        MIN_45 = 3, "45 min"
        MIN_60 = 4, "60 min"

    class Horizon(models.IntegerChoices):
        DAYS_30 = 1, "30 days"
        DAYS_60 = 2, "60 days"
        DAYS_90 = 3, "90 days"

    name = models.CharField(
        max_length=64,
        unique=True,
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        editable=False,
    )
    duration = models.IntegerField(
        choices=Duration.choices,
        default=Duration.MIN_15,
        help_text="Duration of event in minutes",
    )
    horizon = models.IntegerField(
        choices=Horizon.choices,
        default=Horizon.DAYS_30,
        help_text="How far out can this event type be scheduled in days?",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        blank=True,
    )
    schedule = models.ForeignKey(
        "Schedule",
        on_delete=models.CASCADE,
        help_text="Schedule to use for availability hours",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    start_time = models.DateTimeField(
        editable=False,
    )
    end_time = models.DateTimeField(
        editable=False,
    )
    booker_name = models.CharField(
        max_length=64,
        editable=False,
    )
    booker_email = models.CharField(
        max_length=64,
        editable=False,
    )

    def __str__(self):
        return f"{self.booker_name} {self.start_time} - {self.end_time}"


class Schedule(models.Model):
    schedule_name = models.CharField(
        max_length=64,
    )
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

    def __str__(self):
        return self.schedule_name

    class Meta:
        verbose_name = "availability schedule"
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
