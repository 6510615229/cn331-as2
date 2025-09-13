from django.contrib import admin

from .models import *

class ClassroomsAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "hours_Available", "capacity", "is_available"]

class StudentsAdmin(admin.ModelAdmin):
    filter_horizontal = ["rooms"]


admin.site.register(Classrooms, ClassroomsAdmin)
admin.site.register(Students, StudentsAdmin)
