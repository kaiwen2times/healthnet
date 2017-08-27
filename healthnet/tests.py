import unittest

from django.test import TestCase

from healthnet.models import Hospital
from healthnet.models import Location
from healthnet.models import Profile


class AppointmentMethodTests(TestCase):
    if __name__ == '__main__':
        unittest.main()

    def setUp(self):
        Location.objects.create(city='Rochester', zip="14623", state='NY,country = USA',
                                address="5353 Jefferon Rd")
        Location.objects.create(city='Buffalo', zip="14623", state='NY,country = USA',
                                address="5353 Jefferon Rd")


    def test_compare_locations(self):
        first_loc = Location.objects.get(city="Rochester")
        second_loc = Location.objects.get(city="Buffalo")
        self.assertEqual(first_loc == second_loc, False)


class HospitalTestCase(TestCase):
    def setUp(self):
        Location.objects.create(city="Brooklyn", zip="11210", state="New York", country="USA",
                                address="1000 Thousand Ave")
        Hospital.objects.create(name="NY Methodist Hospital", phone="347-743-1347",
                                location=Location.objects.get(city="Brooklyn"))

    def test_hospitals_can_get_location(self):
        methodistHospitalLocation = Location.objects.get(city="Brooklyn")
        methodistHospital = Hospital.objects.get(name="NY Methodist Hospital")
        self.assertEqual(methodistHospital.location, methodistHospitalLocation)

class ProfileTestCase(TestCase):
    def setUp(self):
        Profile.objects.create(firstname = "Kazusa", lastname = "Kitahara", insurance = "Excellus",)
        Profile.objects.create(firstname = "Kasumi", lastname = "Kitahara", insurance = "Excellus",)

    def test_profile(self):
        profile1 = Profile.objects.get(firstname = "Kazusa")
        profile2 = Profile.objects.get(firstname = "Kasumi")
        self.assertEqual(profile1 == profile2,False)