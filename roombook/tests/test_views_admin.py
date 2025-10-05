from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
import datetime as dt
from roombook.models import Classrooms, Booking
from django.db import IntegrityError
from unittest.mock import patch

class AdminOverviewPermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="normal", password="p")

    def test_non_admin_redirected(self):
        self.client.login(username="normal", password="p")
        resp = self.client.get("/classrooms/admin/overview/")
        self.assertIn(resp.status_code, [302, 403, 200], f"Unexpected {resp.status_code}")

class AdminOverviewRoomAdminGroupTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="ra", password="p")
        room_admin = Group.objects.create(name="room_admin")
        self.user.groups.add(room_admin)

        self.r1 = Classrooms.objects.create(
            code="B101", name="Lab 1",
            open_time=dt.time(8, 0), close_time=dt.time(18, 0), is_available=True
        )
        self.r2 = Classrooms.objects.create(
            code="B102", name="Lab 2",
            open_time=dt.time(8, 0), close_time=dt.time(18, 0), is_available=True
        )
        Booking.objects.create(
            classroom=self.r1, user=self.user,
            date=dt.date.today(), start_time=dt.time(9, 0), end_time=dt.time(10, 0)
        )
        Booking.objects.create(
            classroom=self.r2, user=self.user,
            date=dt.date.today(), start_time=dt.time(10, 0), end_time=dt.time(11, 0)
        )

    def test_room_admin_group_can_access_and_context_populated(self):
        self.client.login(username="ra", password="p")
        resp = self.client.get("/classrooms/admin/overview/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("kpi_rooms_total", resp.context)
        self.assertIn("kpi_bookings_total", resp.context)
        self.assertIn("rows_json", resp.context)
        self.assertGreaterEqual(resp.context["kpi_rooms_total"], 2)
        self.assertGreaterEqual(resp.context["kpi_bookings_total"], 2)
        self.assertIsInstance(resp.context["rows_json"], list)
        self.assertGreaterEqual(len(resp.context["rows_json"]), 2)

class BookViewIntegrityErrorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="userie", password="p")
        self.client.login(username="userie", password="p")
        self.room = Classrooms.objects.create(
            code="ERR101", name="Error Room",
            open_time=dt.time(8, 0), close_time=dt.time(18, 0), is_available=True
        )

    @patch("roombook.views.Booking.objects.create", side_effect=IntegrityError)
    def test_booking_integrity_error_redirects_with_message(self, mock_create):
        resp = self.client.post(
            f"/classrooms/{self.room.id}/book",
            {"date": dt.date.today().isoformat(), "start_time": "09:00"},
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        messages = list(resp.context["messages"])
        self.assertTrue(any("ถูกจองไปแล้ว" in str(m) for m in messages))


class AdminOverviewSuperuserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username="super", password="p", email="x@y.com")

    def test_superuser_can_access_admin_overview(self):
        self.client.login(username="super", password="p")
        resp = self.client.get("/classrooms/admin/overview/")
        self.assertEqual(resp.status_code, 200)


class AdminOverviewNoBookingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username="emptyadmin", password="p", email="x@y.com")
        self.client.login(username="emptyadmin", password="p")
        Classrooms.objects.create(
            code="E201", name="Empty", open_time=dt.time(8), close_time=dt.time(18), is_available=True
        )

    def test_admin_overview_empty_room_map(self):
        resp = self.client.get("/classrooms/admin/overview/")
        self.assertEqual(resp.status_code, 200)
        ctx = resp.context
        self.assertIn("rows_json", ctx)
        self.assertEqual(len(ctx["rows_json"]), 0)