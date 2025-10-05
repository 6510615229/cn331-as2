# roombook/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from roombook.models import Classrooms, Booking
import datetime as dt

class RoomBookIndexViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("roombook:index")
        self.login_url = reverse("students:login")

    def test_index_redirects_to_login_when_anonymous(self):
        resp = self.client.get(self.index_url)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(self.login_url))

    def test_index_status_200_when_logged_in(self):
        User.objects.create_user(username="alice", password="1234")
        logged_in = self.client.login(username="alice", password="1234")
        self.assertTrue(logged_in, "ควรล็อกอินสำเร็จในเทส")
        resp = self.client.get(self.index_url)
        self.assertEqual(resp.status_code, 200)

class ClassroomDetailEdgeCasesTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("u", password="p")
        self.client.login(username="u", password="p")
        self.room = Classrooms.objects.create(
            code="Z101", name="Zed", open_time=dt.time(8,0), close_time=dt.time(10,0), is_available=True
        )

    def test_detail_valid_date_populates_context(self):
        url = reverse("roombook:classroom", args=[self.room.id])
        r = self.client.get(url, {"date": dt.date.today().isoformat()})
        self.assertEqual(r.status_code, 200)
        self.assertIn("slot_json", r.context)
        self.assertIn("bookings_json", r.context)

    def test_detail_invalid_date_falls_back_to_today(self):
        url = reverse("roombook:classroom", args=[self.room.id])
        r = self.client.get(url, {"date": "9999-99-99"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("slot_json", r.context)

    def test_detail_my_booking_exists_true(self):
        Booking.objects.create(
            classroom=self.room, user=self.u, date=dt.date.today(), start_time=dt.time(8,0), end_time=dt.time(9,0)
        )
        url = reverse("roombook:classroom", args=[self.room.id])
        r = self.client.get(url, {"date": dt.date.today().isoformat()})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context.get("my_booking_exists"))