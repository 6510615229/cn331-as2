# students/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

def user_is_room_admin(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or user.groups.filter(name="room_admin").exists()

def _safe_next(request, fallback):
    nxt = request.GET.get("next") or request.POST.get("next")
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return nxt
    return fallback

def index(request):
    return render(request, "students/index.html")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "เข้าสู่ระบบสำเร็จ")
            return redirect(_safe_next(request, reverse("roombook:index")))
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = AuthenticationForm(request)
    return render(request, "students/login.html", {"form": form})

@login_required(login_url="students:login")
def logout_view(request):
    logout(request)
    messages.info(request, "ออกจากระบบแล้ว")
    return redirect(reverse("students:login"))


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                grp = Group.objects.get(name="students")
                user.groups.add(grp)
            except Group.DoesNotExist:
                pass
            messages.success(request, "สมัครสมาชิกสำเร็จ — กรุณาเข้าสู่ระบบ")
            return redirect(reverse("students:login"))
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง โปรดตรวจสอบแบบฟอร์ม")
    else:
        form = UserCreationForm()
    return render(request, "students/register.html", {"form": form})

def admin_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if not user_is_room_admin(user):
                logout(request)
                messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงส่วนผู้ดูแลระบบ")
                return render(request, "students/admin_login.html", {"form": AuthenticationForm(request)})

            messages.success(request, "เข้าสู่ระบบผู้ดูแลเรียบร้อย")
            return redirect("roombook:admin_overview")

        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = AuthenticationForm(request)

    return render(request, "students/admin_login.html", {"form": form})
