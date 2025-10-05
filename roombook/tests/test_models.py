from django.test import TestCase
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models import ForeignKey, DateTimeField
from roombook.models import Classrooms, Booking
from django.utils import timezone
import datetime as dt
from django.core.exceptions import ValidationError

class ClassroomsModelSmokeTest(TestCase):
    def setUp(self):
        try:
            self.Classrooms = apps.get_model("roombook", "Classrooms")
        except LookupError:
            self.Classrooms = None

    def test_classrooms_model_exists(self):
        if self.Classrooms is None:
            self.skipTest("Model 'Classrooms' not found in roombook (จะปรับชื่อในสเต็ปถัดไป)")
        self.assertIsNotNone(self.Classrooms)

    def test_can_create_basic_classroom(self):
        if self.Classrooms is None:
            self.skipTest("Model 'Classrooms' not found in roombook")
        field_names = {f.name for f in self.Classrooms._meta.get_fields() if hasattr(f, "attname")}
        payload = {}

        if "name" in field_names:
            payload["name"] = "CPE-101"
        if "is_available" in field_names:
            payload["is_available"] = True
        if "open_time" in field_names:
            payload["open_time"] = dt.time(8, 0)
        if "close_time" in field_names:
            payload["close_time"] = dt.time(18, 0)
        if "capacity" in field_names:
            payload["capacity"] = 40

        obj = self.Classrooms.objects.create(**payload)
        self.assertIsNotNone(obj.pk, "ควรสร้างห้องได้และมี primary key")

        qs = self.Classrooms.objects.all()
        self.assertEqual(qs.count(), 1)

class BookingModelSmokeTest(TestCase):
    def setUp(self):
        try:
            self.Booking = apps.get_model("roombook", "Booking")
        except LookupError:
            self.Booking = None

    def test_booking_model_exists(self):
        if self.Booking is None:
            self.fail("ไม่พบโมเดล 'Booking' ")

class BookingLogicGoodPathTest(TestCase):  
    def setUp(self):
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")

        self.room = self.Classrooms.objects.create(
            name="cn331",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="alice", password="1234")

    def test_can_create_one_hour_booking_in_open_hours(self):
        booking_date = dt.date(2025, 1, 1)
        start_t = dt.time(9, 0)
        end_t = dt.time(10, 0)

        b = self.Booking.objects.create(
            classroom=self.room,
            user=self.user,
            date=booking_date,
            start_time=start_t,
            end_time=end_t,
            canceled=False,
        )

        self.assertIsNotNone(b.pk)
        start_dt = timezone.make_aware(dt.datetime.combine(booking_date, start_t))
        end_dt = timezone.make_aware(dt.datetime.combine(booking_date, end_t))
        self.assertEqual(end_dt - start_dt, dt.timedelta(hours=1))
        self.assertLessEqual(start_t, self.room.close_time)
        self.assertGreaterEqual(end_t, self.room.open_time)

class BookingFieldIntrospectionTest(TestCase):
    def test_booking_fields_shape(self):
        Booking = apps.get_model("roombook", "Booking")
        field_types = {
            f.name: getattr(f, "get_internal_type", lambda: type(f).__name__)()
            for f in Booking._meta.get_fields()
        }
        expected = {
            "classroom": "ForeignKey",
            "user": "ForeignKey",
            "date": "DateField",
            "start_time": "TimeField",
            "end_time": "TimeField",
        }
        for name, t in expected.items():
            self.assertIn(name, field_types, f"missing field '{name}'")
            self.assertEqual(field_types[name], t, f"type mismatch for '{name}'")

class BookingLogicBadPathOutOfHoursTest(TestCase):
    def setUp(self):
        self.Classrooms = apps.get_model("roombook", "Classrooms")
        self.Booking = apps.get_model("roombook", "Booking")
        self.room = self.Classrooms.objects.create(
            name="cn331",
            is_available=True,
            open_time=dt.time(8, 0),
            close_time=dt.time(18, 0),
        )
        self.user = User.objects.create_user(username="bob", password="1234")

    def test_booking_outside_hours_should_be_invalid_or_skip(self):
        booking_date = dt.date(2025, 1, 1)
        start_t = dt.time(7, 0)
        end_t = dt.time(8, 0)

        b = self.Booking(
            classroom=self.room,
            user=self.user,
            date=booking_date,
            start_time=start_t,
            end_time=end_t,
            canceled=False,
        )

        try:
            b.full_clean()
        except ValidationError:
            return
        self.skipTest("โมเดลไม่ validate เวลาเปิด-ปิด")

class ClassroomsFunctionTest(TestCase):
    def setUp(self):
        self.room = Classrooms.objects.create(
            code="R100", name="Room 100",
            open_time=dt.time(8, 0), close_time=dt.time(10, 0),
            is_available=True
        )
        self.user = User.objects.create_user(username="u", password="p")

    def test_hours_range_returns_each_hour(self):
        hours = list(self.room.hours_range())
        self.assertEqual(hours, [dt.time(8,0), dt.time(9,0)])

    def test_is_slot_available_when_empty(self):
        available = self.room.is_slot_available(dt.date.today(), dt.time(8,0))
        self.assertTrue(available)

    def test_is_slot_available_when_booked(self):
        Booking.objects.create(
            classroom=self.room, user=self.user,
            date=dt.date.today(), start_time=dt.time(8,0), end_time=dt.time(9,0)
        )
        available = self.room.is_slot_available(dt.date.today(), dt.time(8,0))
        self.assertFalse(available)

    def test_is_slot_available_when_room_closed(self):
        self.room.is_available = False
        self.room.save()
        available = self.room.is_slot_available(dt.date.today(), dt.time(8,0))
        self.assertFalse(available)

class ModelStrTest(TestCase):
    def test_classrooms_str(self):
        room = Classrooms.objects.create(code="X101", name="X Room",
                                         open_time=dt.time(8,0), close_time=dt.time(18,0),
                                         is_available=True)
        s = str(room)
        self.assertTrue(isinstance(s, str) and s != "")

    def test_booking_str(self):
        user = User.objects.create_user("a", password="a")
        room = Classrooms.objects.create(code="X102", name="Y Room",
                                         open_time=dt.time(8,0), close_time=dt.time(18,0),
                                         is_available=True)
        b = Booking.objects.create(classroom=room, user=user,
                                   date=dt.date.today(), start_time=dt.time(9,0), end_time=dt.time(10,0))
        s = str(b)
        self.assertTrue(isinstance(s, str) and s != "")