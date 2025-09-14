from datetime import date as ddate, datetime, time as dtime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.db import IntegrityError
from django.middleware.csrf import get_token
from .models import Classrooms, Booking

@login_required(login_url="students:login")
def index(request):
    rooms = Classrooms.objects.all().order_by("code")
    return render(request, "roombook/index.html", {"rooms": rooms})

@login_required(login_url="students:login")
def classroom_detail(request, classroom_id: int):
    room = get_object_or_404(Classrooms, pk=classroom_id)
    # Resolve date from query string
    qdate = request.GET.get("date")
    try:
        the_date = ddate.fromisoformat(qdate) if qdate else ddate.today()
    except Exception:
        the_date = ddate.today()

    # Build hourly slots within the room's open-close window
    slots = room.hours_range()
    slot_info = []
    for t in slots:
        start = t
        end = (datetime.combine(the_date, start) + timedelta(hours=1)).time()
        available = room.is_slot_available(the_date, start)
        slot_info.append({"start": start, "end": end, "can_book": available})

    my_booking = (
        Booking.objects
        .filter(user=request.user, classroom=room, date=the_date, canceled=False)
        .order_by("start_time")
        .first()
    )

    my_booking_exists = bool(my_booking)
    my_booking_start  = my_booking.start_time.strftime("%H:%M") if my_booking else ""
    
    slot_json = [
        {"start": s["start"].strftime("%H:%M"), "end": s["end"].strftime("%H:%M"), "can_book": bool(s["can_book"])}
        for s in slot_info
    ]
    bookings_today = (
        Booking.objects.filter(classroom=room, date=the_date, canceled=False)
        .select_related("user").order_by("start_time")
    )
    bookings_json = [{"start": b.start_time.strftime("%H:%M"), "end": b.end_time.strftime("%H:%M"), "user": b.user.username}
                     for b in bookings_today]
    
    context = {
        "room": room,
        "the_date": the_date,
        "slot_json": slot_json,
        "bookings_json": bookings_json,
        "room_status": "เปิด" if room.is_available else "ปิด",
        "room_open": 1 if room.is_available else 0,
        "my_booking_exists": my_booking_exists,
        "my_booking_start":  my_booking_start,
    }

    return render(request, "roombook/classrooms.html", context)

@login_required(login_url="students:login")
def book(request, classroom_id: int):
    if request.method != "POST":
        return redirect("roombook:classroom", classroom_id=classroom_id)

    room = get_object_or_404(Classrooms, pk=classroom_id)

    the_date_str = request.POST.get("date")
    start_str    = request.POST.get("start_time")
    if not the_date_str or not start_str:
        messages.error(request, "ข้อมูลไม่ครบ")
        return redirect("roombook:classroom", classroom_id=room.id)

    the_date = ddate.fromisoformat(the_date_str)
    start    = datetime.strptime(start_str, "%H:%M").time()
    end      = (datetime.combine(the_date, start) + timedelta(hours=1)).time()

    if Booking.objects.filter(user=request.user, classroom=room, date=the_date, canceled=False).exists():
        messages.error(request, "คุณจองห้องนี้วันนี้ไว้แล้ว (อนุญาต 1 ชั่วโมงต่อห้องต่อวัน). หากต้องการเปลี่ยนเวลา โปรดยกเลิกการจองเดิมก่อน")
        return redirect("roombook:classroom", classroom_id=room.id)

    try:
        Booking.objects.create(
            classroom=room, user=request.user,
            date=the_date, start_time=start, end_time=end
        )
        messages.success(request, "จองสำเร็จ")
    except IntegrityError:
        messages.error(request, "ช่วงเวลานี้ถูกจองไปแล้ว")
    return redirect("roombook:classroom", classroom_id=room.id)

@login_required(login_url="students:login")
def my_bookings(request):
    bookings = (Booking.objects
                .filter(user=request.user)
                .select_related("classroom")
                .order_by("-date", "start_time"))
    return render(request, "roombook/my_bookings.html", {"bookings": bookings})

@login_required(login_url="students:login")
def cancel_booking(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์ยกเลิกการจองนี้")
        return redirect("roombook:my_bookings")
    if request.method == "POST":
        if booking.canceled:
            messages.info(request, "การจองนี้ถูกยกเลิกไว้แล้ว")
        else:
            booking.canceled = True
            booking.save(update_fields=["canceled"])
            messages.success(request, "ยกเลิกการจองเรียบร้อย")
        return redirect("roombook:my_bookings")
    messages.error(request, "วิธียกเลิกไม่ถูกต้อง")
    return redirect("roombook:my_bookings")

def _is_room_admin(user):
    return (
        user.is_authenticated and
        (user.is_staff or user.is_superuser or user.groups.filter(name="room_admin").exists())
    )

@login_required(login_url="students:login")
def admin_overview(request):
    # อนุญาตเฉพาะแอดมิน
    if not _is_room_admin(request.user):
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return redirect("students:admin_login")
    # วันที่ (default = วันนี้)
    qdate = request.GET.get("date")
    try:
        the_date = ddate.fromisoformat(qdate) if qdate else ddate.today()
    except Exception:
        the_date = ddate.today()
    # ดึง "การจองที่ยังไม่ถูกยกเลิก" ของวันนั้น พร้อมข้อมูลห้องและผู้ใช้
    qs = (
        Booking.objects
        .filter(date=the_date, canceled=False)
        .select_related("classroom", "user")
        .order_by("classroom__code", "start_time")
    )

    kpi_rooms_total = Classrooms.objects.count()         # จำนวนห้องทั้งหมด
    kpi_bookings_total = qs.count()                      # จำนวนการจองในวันนั้น

    # รวมรายการแสดงผลห้องที่มีการจอง
    room_map = {}
    for b in qs:
        rid = b.classroom_id
        if rid not in room_map:
            room_map[rid] = {
                "id": b.classroom.id,
                "code": b.classroom.code,
                "name": b.classroom.name,
                "bookings": [], 
            }
        room_map[rid]["bookings"].append({
            "start": b.start_time.strftime("%H:%M"),
            "end": b.end_time.strftime("%H:%M"),
            "user": b.user.username,
        })

    rows = list(room_map.values())  

    context = {
        "the_date": the_date,
        "kpi_rooms_total": kpi_rooms_total,
        "kpi_bookings_total": kpi_bookings_total,
        "rows_json": rows, 
    }
    return render(request, "roombook/admin_overview.html", context)