from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Location, EventType, Schedule


class LocationTest(TestCase):
    def test_unique_google_meet_is_enforced(self):
        Location.objects.create(
            location_type=Location.LocationType.GOOGLE_MEET,
        )
        with self.assertRaisesRegex(ValidationError, r"one Google Meet"):
            Location.objects.create(
                location_type=Location.LocationType.GOOGLE_MEET,
            )

    def test_phone_number_required_if_phone_call(self):
        with self.assertRaisesRegex(ValidationError, r"Missing phone number"):
            Location.objects.create(
                location_type=Location.LocationType.PHONE_CALL,
            )

    def test_unique_phone_number_enforced_if_phone_call(self):
        Location.objects.create(
            location_type=Location.LocationType.PHONE_CALL,
            phone_number="+18002223333",
        )
        with self.assertRaisesRegex(ValidationError, r"Must be unique"):
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


class ScheduleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Schedule.objects.create(
            schedule_name="Regular schedule",
            sun_off=False,
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
            sat_off=False,
            sat_start="9:00:00",
            sat_end="17:00:00",
        )
        Schedule.objects.create(
            schedule_name="Off schedule",
            sun_off=True,
            mon_off=True,
            tue_off=True,
            wed_off=True,
            thu_off=True,
            fri_off=True,
            sat_off=True,
        )

    def setUp(self):
        self.normal_schedule = Schedule.objects.get(
            schedule_name="Regular schedule"
        )
        self.off_schedule = Schedule.objects.get(schedule_name="Off schedule")

    def test_sunday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"sun_start(.*?)low bounded"
        ):
            self.normal_schedule.sun_start = "18:00:00"
            self.normal_schedule.save()

    def test_monday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"mon_start(.*?)low bounded"
        ):
            self.normal_schedule.mon_start = "18:00:00"
            self.normal_schedule.save()

    def test_tuesday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"tue_start(.*?)low bounded"
        ):
            self.normal_schedule.tue_start = "18:00:00"
            self.normal_schedule.save()

    def test_wednesday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"wed_start(.*?)low bounded"
        ):
            self.normal_schedule.wed_start = "18:00:00"
            self.normal_schedule.save()

    def test_thursday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"thu_end(.*?)high bounded"
        ):
            self.normal_schedule.thu_start = "18:00:00"
            self.normal_schedule.save()

    def test_friday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"fri_end(.*?)high bounded"
        ):
            self.normal_schedule.fri_start = "18:00:00"
            self.normal_schedule.save()

    def test_saturday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"sat_end(.*?)high bounded"
        ):
            self.normal_schedule.sat_end = "8:00:00"
            self.normal_schedule.save()

    def test_sunday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.sun_start)
        self.assertIsNone(self.off_schedule.sun_end)

        with self.assertRaisesRegex(
            ValidationError, r"sun_start(.*?)required"
        ):
            self.off_schedule.sun_off = False
            self.off_schedule.save()

    def test_monday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.mon_start)
        self.assertIsNone(self.off_schedule.mon_end)

        with self.assertRaisesRegex(
            ValidationError, r"mon_start(.*?)required"
        ):
            self.off_schedule.mon_off = False
            self.off_schedule.save()

    def test_tuesday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.tue_start)
        self.assertIsNone(self.off_schedule.tue_end)

        with self.assertRaisesRegex(
            ValidationError, r"tue_start(.*?)required"
        ):
            self.off_schedule.tue_off = False
            self.off_schedule.save()

    def test_wednesday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.wed_start)
        self.assertIsNone(self.off_schedule.wed_end)

        with self.assertRaisesRegex(
            ValidationError, r"wed_start(.*?)required"
        ):
            self.off_schedule.wed_off = False
            self.off_schedule.save()

    def test_thursday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.thu_start)
        self.assertIsNone(self.off_schedule.thu_end)

        with self.assertRaisesRegex(ValidationError, r"thu_end(.*?)required"):
            self.off_schedule.thu_off = False
            self.off_schedule.thu_start = "9:00:00"
            self.off_schedule.save()

    def test_friday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.fri_start)
        self.assertIsNone(self.off_schedule.fri_end)

        with self.assertRaisesRegex(ValidationError, r"fri_end(.*?)required"):
            self.off_schedule.fri_off = False
            self.off_schedule.fri_start = "9:00:00"
            self.off_schedule.save()

    def test_saturday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.off_schedule.sat_start)
        self.assertIsNone(self.off_schedule.sat_end)

        with self.assertRaisesRegex(ValidationError, r"sat_end(.*?)required"):
            self.off_schedule.sat_off = False
            self.off_schedule.sat_start = "9:00:00"
            self.off_schedule.save()
