from django.test import TestCase
from django.contrib import admin
from roombook.models import Classrooms, Booking
from roombook.admin import ClassroomsAdmin, BookingAdmin

class AdminSmokeTest(TestCase):
    def test_admin_register(self):
        self.assertIn(Classrooms, admin.site._registry)
        self.assertIn(Booking, admin.site._registry)

    def test_admin_class_defined(self):
        self.assertTrue(issubclass(ClassroomsAdmin, admin.ModelAdmin))
        self.assertTrue(issubclass(BookingAdmin, admin.ModelAdmin))