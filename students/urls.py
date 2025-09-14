from django.urls import path
from . import views
app_name = 'students'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path("admin-login/", views.admin_login_view, name="admin_login"),
]