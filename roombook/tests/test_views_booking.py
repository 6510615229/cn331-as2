# roombook/tests/test_views_booking.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from roombook.models import Classrooms, Booking
from django.apps import apps
import datetime as dt

class BookingOutOfHoursViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")
        self.room = self.Classrooms.objects.create(
            name="CPE103",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="tester", password="1234")
        self.client.login(username="tester", password="1234")
        self.booking_url = reverse("roombook:index")

    def test_post_out_of_hours_should_not_create_booking(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": "2025-01-01",
            "start_time": "07:00",
            "end_time": "08:00",
        })

        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302), "คาดว่า view จะตอบกลับ 200 หรือ 302")
        self.assertEqual(after, before, "ไม่ควรสร้าง Booking ใหม่เมื่อนอกเวลาเปิด-ปิด")

class BookingOverlapViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")

        self.room = self.Classrooms.objects.create(
            name="CPE104",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )

        self.user = User.objects.create_user(username="u1", password="1234")
        self.client.login(username="u1", password="1234")
        self.booking_url = reverse("roombook:index")
        self.booking_date = dt.date(2025, 1, 1)
        self.Booking.objects.create(
            classroom=self.room,
            user=self.user,
            date=self.booking_date,
            start_time=dt.time(9, 0),
            end_time=dt.time(10, 0),
            canceled=False,
        )

    def test_post_overlapping_should_not_create_another(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": self.booking_date.isoformat(),
            "start_time": "09:30",
            "end_time": "10:30",
        })
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(after, before, "ไม่ควรสร้าง Booking เพิ่มเมื่อเวลาชนกัน")

class BookingBackToBackIsAllowedViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")

        self.room = self.Classrooms.objects.create(
            name="CPE105",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )

        self.user = User.objects.create_user(username="u2", password="1234")
        self.client.login(username="u2", password="1234")
        self.booking_url = reverse("roombook:index")
        self.booking_date = dt.date(2025, 1, 2)
        self.Booking.objects.create(
            classroom=self.room,
            user=self.user,
            date=self.booking_date,
            start_time=dt.time(9, 0),
            end_time=dt.time(10, 0),
            canceled=False,
        )

    def test_back_to_back_should_not_create(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": self.booking_date.isoformat(),
            "start_time": "10:00",
            "end_time": "11:00",
        })
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(after, before, "ระบบนี้ถือว่าช่วงชิดขอบก็ชน จึงไม่ควรสร้างเพิ่ม")

class BookingUnavailableRoomViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")
        self.room = self.Classrooms.objects.create(
            name="CPE106",
            is_available=False,            # ❗ ปิดห้อง
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )

        self.user = User.objects.create_user(username="u3", password="1234")
        self.client.login(username="u3", password="1234")
        self.booking_url = reverse("roombook:index")
        self.booking_date = dt.date(2025, 1, 3)

    def test_unavailable_room_should_not_create(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": self.booking_date.isoformat(),
            "start_time": "09:00",
            "end_time": "10:00",
        })
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(after, before, "ห้องปิดการใช้งานไม่ควรสร้าง Booking")

class BookingDurationMustBeOneHourViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")
        self.room = self.Classrooms.objects.create(
            name="CPE107",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="u4", password="1234")
        self.client.login(username="u4", password="1234")
        self.booking_url = reverse("roombook:index")
        self.booking_date = dt.date(2025, 1, 4)

    def test_shorter_than_one_hour_should_not_create(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": self.booking_date.isoformat(),
            "start_time": "09:00",
            "end_time": "09:30",
        })
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(after, before, "สั้นกว่า 1 ชั่วโมง ไม่ควรสร้าง Booking")

    def test_longer_than_one_hour_should_not_create(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, {
            "classroom": self.room.id,
            "date": self.booking_date.isoformat(),
            "start_time": "09:00",
            "end_time": "11:00",
        })
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(after, before, "ยาวกว่า 1 ชั่วโมง ไม่ควรสร้าง Booking")

class BookingIntegrationHappyPathTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")

        self.room = self.Classrooms.objects.create(
            name="CPE108",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="e2e", password="1234")
        self.client.login(username="e2e", password="1234")
        self.date = dt.date(2025, 1, 5)
        self.booking_url = reverse("roombook:book", args=[self.room.id])
        self.payload = {
            "date": self.date.isoformat(),
            "start_time": "10:00",
        }

    def test_full_flow_create_booking(self):
        before = self.Booking.objects.count()
        resp = self.client.post(self.booking_url, self.payload)
        after = self.Booking.objects.count()
        self.assertIn(resp.status_code, (302, 200))
        self.assertEqual(after, before + 1, "ควรสร้าง Booking ใหม่ในเคสดี (happy path)")

class CancelBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")
        self.room = self.Classrooms.objects.create(
            name="CPE109",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="bob", password="1234")
        self.other = User.objects.create_user(username="alice", password="1234")
        self.client.login(username="bob", password="1234")
        self.booking = self.Booking.objects.create(
            classroom=self.room,
            user=self.user,
            date=dt.date(2025, 1, 6),
            start_time=dt.time(10, 0),
            end_time=dt.time(11, 0),
            canceled=False,
        )
        self.url = reverse("roombook:cancel_booking", args=[self.booking.id])

    def test_user_can_cancel_own_booking(self):
        before = self.Booking.objects.filter(canceled=False).count()
        resp = self.client.post(self.url)
        after = self.Booking.objects.filter(canceled=False).count()
        self.assertEqual(before - after, 1)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.canceled)
        self.assertIn(resp.status_code, (200, 302))

    def test_other_user_cannot_cancel(self):
        self.client.logout()
        self.client.login(username="alice", password="1234")
        resp = self.client.post(self.url)
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.canceled)
        self.assertIn(resp.status_code, (200, 302))

class CancelBookingEdgeCaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="u1", password="p")
        self.user2 = User.objects.create_user(username="u2", password="p")
        self.room = Classrooms.objects.create(code="C101", name="Test", open_time=dt.time(8), close_time=dt.time(10))
        self.booking = Booking.objects.create(
            classroom=self.room, user=self.user1,
            date=dt.date.today(), start_time=dt.time(8), end_time=dt.time(9)
        )

    def test_cancel_by_other_user_should_forbid(self):
        self.client.login(username="u2", password="p")
        resp = self.client.post(f"/classrooms/bookings/{self.booking.id}/cancel/")
        self.assertRedirects(resp, "/classrooms/me/bookings/")

    def test_cancel_with_get_should_show_error(self):
        self.client.login(username="u1", password="p")
        resp = self.client.get(f"/classrooms/bookings/{self.booking.id}/cancel/")
        self.assertRedirects(resp, "/classrooms/me/bookings/")

class CancelBookingExtraTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="p")
        self.staff = User.objects.create_user(username="staff", password="p", is_staff=True)
        self.room = Classrooms.objects.create(
            code="CX01", name="Cancel X",
            open_time=dt.time(8), close_time=dt.time(10), is_available=True
        )
        self.booking = Booking.objects.create(
            classroom=self.room, user=self.owner,
            date=dt.date.today(), start_time=dt.time(8), end_time=dt.time(9)
        )

    def test_cancel_twice_should_show_info(self):
        self.client.login(username="owner", password="p")
        r1 = self.client.post(f"/classrooms/bookings/{self.booking.id}/cancel/")
        self.assertEqual(r1.status_code, 302)
        r2 = self.client.post(f"/classrooms/bookings/{self.booking.id}/cancel/")
        self.assertEqual(r2.status_code, 302)

    def test_staff_can_cancel_others_booking(self):
        self.client.login(username="staff", password="p")
        r = self.client.post(f"/classrooms/bookings/{self.booking.id}/cancel/")
        self.assertEqual(r.status_code, 302)

class AdminOverviewPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="1234")
        self.admin = User.objects.create_user(username="admin", password="1234", is_staff=True)

    def test_non_admin_redirected(self):
        self.client.login(username="user", password="1234")
        resp = self.client.get(reverse("roombook:admin_overview"))
        self.assertEqual(resp.status_code, 302)

    def test_admin_can_access(self):
        self.client.login(username="admin", password="1234")
        resp = self.client.get(reverse("roombook:admin_overview"))
        self.assertEqual(resp.status_code, 200)

class BookViewEdgeCasesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("booker", password="1234")
        self.client.login(username="booker", password="1234")
        self.room = Classrooms.objects.create(code="E201", name="Edge 201",
                                              open_time=dt.time(8,0), close_time=dt.time(18,0),
                                              is_available=True)

    def test_book_get_redirects(self):
        url = reverse("roombook:book", args=[self.room.id])
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 302)

    def test_book_post_missing_data_redirects(self):
        url = reverse("roombook:book", args=[self.room.id])
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 302)

    def test_book_post_room_closed_redirects(self):
        self.room.is_available = False
        self.room.save()
        url = reverse("roombook:book", args=[self.room.id])
        resp = self.client.post(url, {
            "date": dt.date.today().isoformat(),
            "start_time": "10:00",
        })
        self.assertEqual(resp.status_code, 302)

    def test_book_post_duplicate_same_day_redirects(self):
        Booking.objects.create(classroom=self.room, user=self.user,
                               date=dt.date.today(), start_time=dt.time(9,0), end_time=dt.time(10,0))
        url = reverse("roombook:book", args=[self.room.id])
        resp = self.client.post(url, {
            "date": dt.date.today().isoformat(),
            "start_time": "10:00",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Booking.objects.count(), 1)
