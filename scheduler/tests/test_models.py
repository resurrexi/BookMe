from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from ..models import PhoneNumber, Schedule, Event


class ScheduleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Schedule.objects.create(
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
        )

    def setUp(self):
        self.schedule = Schedule.objects.first()

    def test_only_one_instance_is_allowed(self):
        with self.assertRaisesRegex(
            ValidationError, r"Only one instance allowed"
        ):
            Schedule.objects.create(
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
            )

    def test_deleting_instance_is_not_allowed(self):
        with self.assertRaises(PermissionDenied):
            self.schedule.delete()

    def test_monday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"mon_start(.*?)low bounded"
        ):
            self.schedule.mon_start = "18:00:00"
            self.schedule.save()

    def test_tuesday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"tue_start(.*?)low bounded"
        ):
            self.schedule.tue_start = "18:00:00"
            self.schedule.save()

    def test_wednesday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"wed_start(.*?)low bounded"
        ):
            self.schedule.wed_start = "18:00:00"
            self.schedule.save()

    def test_thursday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"thu_end(.*?)high bounded"
        ):
            self.schedule.thu_start = "18:00:00"
            self.schedule.save()

    def test_friday_time_range_is_respected(self):
        with self.assertRaisesRegex(
            ValidationError, r"fri_end(.*?)high bounded"
        ):
            self.schedule.fri_start = "18:00:00"
            self.schedule.save()

    def test_sunday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.schedule.sun_start)
        self.assertIsNone(self.schedule.sun_end)

        with self.assertRaisesRegex(
            ValidationError, r"sun_start(.*?)required"
        ):
            self.schedule.sun_off = False
            self.schedule.save()

    def test_saturday_time_range_required_if_day_is_on(self):
        self.assertIsNone(self.schedule.sat_start)
        self.assertIsNone(self.schedule.sat_end)

        with self.assertRaisesRegex(ValidationError, r"sat_end(.*?)required"):
            self.schedule.sat_off = False
            self.schedule.sat_start = "9:00:00"
            self.schedule.save()
