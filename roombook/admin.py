from django.contrib import admin
from .models import *

class ClassroomsAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "capacity", "is_available", "open_time", "close_time")
    list_filter = ("is_available",)
    search_fields = ("code", "name")
    ordering = ("code",)
    list_editable = ("capacity", "is_available")
    fieldsets = (
        ("Classroom Info", {"fields": ("code", "name", "capacity", "is_available")}),
        ("Booking Window (per day)", {"fields": ("open_time", "close_time")}),
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = ("classroom", "user", "date", "start_time", "end_time", "canceled", "created_at")
    list_filter = ("classroom", "date", "canceled")
    search_fields = ("user__username", "classroom__name", "classroom__code")
    ordering = ("-date", "start_time")
    date_hierarchy = "date"
    list_per_page = 50
    autocomplete_fields = ["classroom", "user"]
    readonly_fields = ("end_time", "created_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("classroom", "user")

    # Actions
    def mark_canceled(self, request, queryset):
        updated = queryset.update(canceled=True)
        self.message_user(request, f"Canceled {updated} booking(s).")
    mark_canceled.short_description = "Cancel selected bookings"

    def mark_active(self, request, queryset):
        updated = queryset.update(canceled=False)
        self.message_user(request, f"Restored {updated} booking(s) (set as active).")
    mark_active.short_description = "Restore selected bookings (set as active)"

    actions = ["mark_canceled", "mark_active"]

admin.site.register(Classrooms, ClassroomsAdmin)
admin.site.register(Booking, BookingAdmin)
