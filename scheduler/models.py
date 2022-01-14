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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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
    # Do not link the EventType as a FK. Instead, copy the values of
    # `location_type`, `phone_number`, and `description` from the
    # EventType. This is to prevent inadvertant changes to the Event
    # in case the admin decides to modify the EventType after the
    # Event is confirmed and booked.
    location_type = models.IntegerField(
        null=True,
        editable=False,
        help_text="1=Phone call, 2=Google Meet",
    )
    phone_number = PhoneNumberField(
        blank=True,
        editable=False,
    )
    description = models.TextField(
        blank=True,
        editable=False,
    )
    start_time = models.DateTimeField(
        null=True,
        editable=False,
    )
    # auto-calculate from EventType's duration
    end_time = models.DateTimeField(
        null=True,
        editable=False,
    )
    booker_name = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
    )
    booker_email = models.EmailField(
        blank=True,
        editable=False,
    )

    def __str__(self):
        return f"{self.booker_name} {self.start_time} - {self.end_time}"


class Schedule(models.Model):
    LOW_BOUND = "Must be a low bounded value"
    HIGH_BOUND = "Must be a high bounded value"
    IS_REQUIRED = "This field is required"

    schedule_name = models.CharField(
        max_length=64,
    )
    sun_off = models.BooleanField(
        default=True,
    )
    sun_start = models.TimeField(
        null=True,
        blank=True,
    )
    sun_end = models.TimeField(
        null=True,
        blank=True,
    )
    mon_off = models.BooleanField(
        default=False,
    )
    mon_start = models.TimeField(
        null=True,
        blank=True,
    )
    mon_end = models.TimeField(
        null=True,
        blank=True,
    )
    tue_off = models.BooleanField(
        default=False,
    )
    tue_start = models.TimeField(
        null=True,
        blank=True,
    )
    tue_end = models.TimeField(
        null=True,
        blank=True,
    )
    wed_off = models.BooleanField(
        default=False,
    )
    wed_start = models.TimeField(
        null=True,
        blank=True,
    )
    wed_end = models.TimeField(
        null=True,
        blank=True,
    )
    thu_off = models.BooleanField(
        default=False,
    )
    thu_start = models.TimeField(
        null=True,
        blank=True,
    )
    thu_end = models.TimeField(
        null=True,
        blank=True,
    )
    fri_off = models.BooleanField(
        default=False,
    )
    fri_start = models.TimeField(
        null=True,
        blank=True,
    )
    fri_end = models.TimeField(
        null=True,
        blank=True,
    )
    sat_off = models.BooleanField(
        default=True,
    )
    sat_start = models.TimeField(
        null=True,
        blank=True,
    )
    sat_end = models.TimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.schedule_name

    class Meta:
        verbose_name = "availability schedule"

    def clean(self):
        # ensure time ranges respect min and max
        if self.sun_start and self.sun_end and self.sun_start > self.sun_end:
            raise ValidationError(
                {
                    "sun_start": self.LOW_BOUND,
                    "sun_end": self.HIGH_BOUND,
                }
            )
        if self.mon_start and self.mon_end and self.mon_start > self.mon_end:
            raise ValidationError(
                {
                    "mon_start": self.LOW_BOUND,
                    "mon_end": self.HIGH_BOUND,
                }
            )
        if self.tue_start and self.tue_end and self.tue_start > self.tue_end:
            raise ValidationError(
                {
                    "tue_start": self.LOW_BOUND,
                    "tue_end": self.HIGH_BOUND,
                }
            )
        if self.wed_start and self.wed_end and self.wed_start > self.wed_end:
            raise ValidationError(
                {
                    "wed_start": self.LOW_BOUND,
                    "wed_end": self.HIGH_BOUND,
                }
            )
        if self.thu_start and self.thu_end and self.thu_start > self.thu_end:
            raise ValidationError(
                {
                    "thu_start": self.LOW_BOUND,
                    "thu_end": self.HIGH_BOUND,
                }
            )
        if self.fri_start and self.fri_end and self.fri_start > self.fri_end:
            raise ValidationError(
                {
                    "fri_start": self.LOW_BOUND,
                    "fri_end": self.HIGH_BOUND,
                }
            )
        if self.sat_start and self.sat_end and self.sat_start > self.sat_end:
            raise ValidationError(
                {
                    "sat_start": self.LOW_BOUND,
                    "sat_end": self.HIGH_BOUND,
                }
            )

        # ensure times are filled if days are on
        if not self.sun_off:
            if not self.sun_start:
                raise ValidationError(
                    {"sun_start": self.IS_REQUIRED},
                )
            if not self.sun_end:
                raise ValidationError(
                    {"sun_end": self.IS_REQUIRED},
                )
        if not self.mon_off:
            if not self.mon_start:
                raise ValidationError(
                    {"mon_start": self.IS_REQUIRED},
                )
            if not self.mon_end:
                raise ValidationError(
                    {"mon_end": self.IS_REQUIRED},
                )
        if not self.tue_off:
            if not self.tue_start:
                raise ValidationError(
                    {"tue_start": self.IS_REQUIRED},
                )
            if not self.tue_end:
                raise ValidationError(
                    {"tue_end": self.IS_REQUIRED},
                )
        if not self.wed_off:
            if not self.wed_start:
                raise ValidationError(
                    {"wed_start": self.IS_REQUIRED},
                )
            if not self.wed_end:
                raise ValidationError(
                    {"wed_end": self.IS_REQUIRED},
                )
        if not self.wed_off:
            if not self.wed_start:
                raise ValidationError(
                    {"wed_start": self.IS_REQUIRED},
                )
            if not self.wed_end:
                raise ValidationError(
                    {"wed_end": self.IS_REQUIRED},
                )
        if not self.thu_off:
            if not self.thu_start:
                raise ValidationError(
                    {"thu_start": self.IS_REQUIRED},
                )
            if not self.fri_end:
                raise ValidationError(
                    {"fri_end": self.IS_REQUIRED},
                )
        if not self.sat_off:
            if not self.sat_start:
                raise ValidationError(
                    {"sat_start": self.IS_REQUIRED},
                )
            if not self.sat_end:
                raise ValidationError(
                    {"sat_end": self.IS_REQUIRED},
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
