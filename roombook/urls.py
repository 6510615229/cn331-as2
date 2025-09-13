from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:classroom_id>', views.classroom, name="classroom"),
    path('<int:classroom_id>/book', views.book, name="book"),
]
