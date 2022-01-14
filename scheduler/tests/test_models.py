from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Location, EventType, Schedule


class LocationTest(TestCase):
    def test_unique_google_meet_is_enforced(self):
        Location.objects.create(
            location_type=Location.LocationType.GOOGLE_MEET,
        )
        with self.assertRaises(ValidationError):
            Location.objects.create(
                location_type=Location.LocationType.GOOGLE_MEET,
            )

    def test_phone_number_required_if_phone_call(self):
        with self.assertRaises(ValidationError):
            Location.objects.create(
                location_type=Location.LocationType.PHONE_CALL,
            )

    def test_unique_phone_number_enforced_if_phone_call(self):
        Location.objects.create(
            location_type=Location.LocationType.PHONE_CALL,
            phone_number="+18002223333",
        )
        with self.assertRaises(ValidationError):
            Location.objects.create(
                location_type=Location.LocationType.PHONE_CALL,
                phone_number="+18002223333",
            )


class EventTypeTest(TestCase):
    def test_slug_is_auto_generated(self):
        location = Location.objects.create(
            location_type=Location.LocationType.PHONE_CALL,
            phone_number="+18002223333",
        )
        schedule = Schedule.objects.create(
            schedule_name="Regular schedule",
            sun_start="9:00:00",
            sun_end="17:00:00",
            mon_start="9:00:00",
            mon_end="17:00:00",
            tue_start="9:00:00",
            tue_end="17:00:00",
            wed_start="9:00:00",
            wed_end="17:00:00",
            thu_start="9:00:00",
            thu_end="17:00:00",
            fri_start="9:00:00",
            fri_end="17:00:00",
            sat_start="9:00:00",
            sat_end="17:00:00",
        )
        event_type = EventType.objects.create(
            name="15 min with recruiter",
            duration=EventType.Duration.MIN_15,
            horizon=EventType.Horizon.DAYS_30,
            location=location,
            schedule=schedule,
        )
        self.assertEqual(event_type.slug, "15-min-with-recruiter")
