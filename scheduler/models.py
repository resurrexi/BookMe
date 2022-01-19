import uuid
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError, PermissionDenied
from phonenumber_field.modelfields import PhoneNumberField


class PhoneNumber(models.Model):
    phone_number = PhoneNumberField(
        blank=True,
    )

    def __str__(self):
        return f"{self.phone_number}"

    class Meta:
        verbose_name = "phone number"
        verbose_name_plural = "phone number"

    def save(self, *args, **kwargs):
        # only 1 instance allowed
        if self._state.adding and PhoneNumber.objects.exists():
            raise ValidationError("Only one instance allowed")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Cannot delete instance")


class Schedule(models.Model):
    LOW_BOUND = "Must be a low bounded value"
    HIGH_BOUND = "Must be a high bounded value"
    IS_REQUIRED = "This field is required"

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

    class Meta:
        verbose_name = "availability schedule"
        verbose_name_plural = "availability schedule"

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
        if not self.thu_off:
            if not self.thu_start:
                raise ValidationError(
                    {"thu_start": self.IS_REQUIRED},
                )
            if not self.thu_end:
                raise ValidationError(
                    {"thu_end": self.IS_REQUIRED},
                )
        if not self.fri_off:
            if not self.fri_start:
                raise ValidationError(
                    {"fri_start": self.IS_REQUIRED},
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
        # only 1 instance allowed
        if self._state.adding and Schedule.objects.exists():
            raise ValidationError("Only one instance allowed")

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Cannot delete instance")


class Event(models.Model):
    class LocationType(models.TextChoices):
        PHONE_CALL = "Phone call"
        GOOGLE_MEET = "Google Meet"

    class Duration(models.IntegerChoices):
        MIN_15 = 15, "15 min"
        MIN_30 = 30, "30 min"
        MIN_45 = 45, "45 min"
        MIN_60 = 60, "60 min"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    location_type = models.CharField(
        max_length=32,
        choices=LocationType.choices,
        default=LocationType.PHONE_CALL,
    )
    phone_number = PhoneNumberField(
        blank=True,
        editable=False,
    )
    duration = models.IntegerField(
        choices=Duration.choices,
        default=Duration.MIN_15,
        help_text="Duration of event in minutes",
    )
    description = models.TextField(
        blank=True,
    )
    start_time = models.DateTimeField(
        null=True,
    )
    # auto-calculate from duration
    end_time = models.DateTimeField(
        null=True,
        editable=False,
    )
    booker_name = models.CharField(
        max_length=64,
        blank=True,
    )
    booker_email = models.EmailField(
        blank=True,
    )

    def __str__(self):
        return f"{self.booker_name} {self.start_time} - {self.end_time}"

    def save(self, *args, **kwargs):
        # auto-calculate end time if `start_time` is given
        if self.start_time:
            self.end_time = self.start_time + timedelta(self.duration)
        super().save(*args, **kwargs)
