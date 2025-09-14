from django.urls import path
from . import views

app_name = "roombook"

urlpatterns = [
    path("", views.index, name="index"),
    path("me/bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("<int:classroom_id>/", views.classroom_detail, name="classroom"),
    path("<int:classroom_id>/book", views.book, name="book"),
    path("admin/overview/", views.admin_overview, name="admin_overview"),
]
