from django.db import models

# Create your models here.
class Classrooms(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=64)
    hours_Available = models.IntegerField()
    capacity = models.PositiveIntegerField(default=2)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.id}: {self.name} ({self.code})"
    
    def is_seat_available(self):
        return self.students.count() < self.capacity
    
    def is_hour_available(self):
        return self.students.count() < self.hours_Available
    
    def can_add_student(self):
        return self.is_available and self.is_seat_available() and self.is_hour_available()

class Students(models.Model):
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    rooms = models.ManyToManyField(Classrooms, blank=True, related_name="students")

    def __str__(self):
        return f"{self.first} {self.last}"
    
