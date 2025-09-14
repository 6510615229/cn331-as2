from django.db import models
from datetime import datetime, timedelta, time as dtime, date as ddate
from django.conf import settings
from django.db.models import Q
# Create your models here.

class Classrooms(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=64)
    capacity = models.PositiveIntegerField(default=1)          # จองพร้อมกันได้กี่คนต่อ 1 ช่วงเวลา
    is_available = models.BooleanField(default=True)           # เปิด/ปิดการจองทั้งห้อง
    open_time = models.TimeField(default=dtime(8, 0))          # 08:00
    close_time = models.TimeField(default=dtime(18, 0))        # 18:00

    def __str__(self):
        return f"{self.name} ({self.code})"

    def hours_range(self):
        slots = []
        if self.open_time and self.close_time and self.open_time < self.close_time:
            cur = datetime.combine(ddate.today(), self.open_time)
            end = datetime.combine(ddate.today(), self.close_time)
            while cur + timedelta(hours=1) <= end:
                slots.append(cur.time())
                cur += timedelta(hours=1)
        return slots
    
    def is_slot_available(self, the_date: ddate, start_time: dtime) -> bool:
        if not self.is_available:
            return False
        active_bookings_count = Booking.objects.filter(
            classroom=self,
            date=the_date,
            start_time=start_time,
            canceled=False
        ).count()

        return active_bookings_count < self.capacity

class Booking(models.Model):
    classroom   = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="bookings")
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    date        = models.DateField()
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    canceled    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "classroom", "date"],
                condition=Q(canceled=False),
                name="one_hour_per_room_per_day",
            ),
        ]
        ordering = ["-date", "start_time"]

    def __str__(self):
        return f"{self.classroom.name} {self.date} {self.start_time}-{self.end_time} by {self.user}"
