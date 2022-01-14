from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Location


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
