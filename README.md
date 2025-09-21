# cn331-as2

## Members

1. พลกฤต กันยายน — 6510615229  
2. พลอยพรรณ เต็งประยูร — 6510615245

---

# Classrooms Project

เว็บแอป **ระบบจองห้องเรียน** พัฒนาด้วย **Django** แบ่งเป็น 2 แอป :

- `roombook` — จัดการห้องและการจอง
- `students` — สมัครสมาชิก/เข้าสู่ระบบ/ออกจากระบบ และ admin login

## roombook app

ฟังก์ชันหลัก:

- แสดงรายการห้อง
- หน้าแสดงรายละเอียดและจองห้อง
- หน้าการจองของฉัน
- หน้า **Admin Overview** (สรุปการจองประจำวัน แบบ custom ไม่ใช่ Django admin)

## students app

ฟังก์ชันหลัก:

- สมัครสมาชิก
- เข้าสู่ระบบ
- ออกจากระบบ
- Admin login

---

# คุณสมบัติหลัก

## สำหรับ Users

1. สมัครสมาชิกและเข้าสู่ระบบ
2. ดูรายการห้องทั้งหมด
3. เลือกวันและ **จองเป็นรายชั่วโมง** สำหรับห้องที่เปิดให้จอง
4. ดู **My Bookings** และ **ยกเลิกการจอง** ได้

> กติกา: **1 ผู้ใช้ จองได้ 1 ชั่วโมง/ห้อง/วัน** (ต้องยกเลิกของเดิมก่อนจึงจะเปลี่ยนช่วงเวลาได้)

## สำหรับ Admins (ไม่ใช่ Django Admin)

1. เข้าระบบแอดมิน
2. เข้าหน้า **Admin Overview** เพื่อดูภาพรวมการจองของวันนั้น (จำนวนการจอง/รายการห้องที่ถูกจอง พร้อมเวลา–ผู้จอง)

---

# URL Paths

- `/admin/` — หน้าเข้าระบบ Django Admin  
- `/students/` — หน้าแรกของ students  
- `/students/register/` — สมัครสมาชิก  
- `/students/login/` — เข้าสู่ระบบผู้ใช้ทั่วไป  
- `/students/admin-login/` — เข้าสู่ระบบผู้ดูแล (ต้องมีสิทธิ์ตามที่กำหนด)  
- `/students/logout/` — ออกจากระบบ  

- `/classrooms/` — รายการห้องทั้งหมด  
- `/classrooms/<id>/?date=YYYY-MM-DD` — หน้าดูช่วงเวลา + จอง  
- `/classrooms/<id>/book` — ส่งฟอร์มจอง  
- `/classrooms/me/bookings/` — การจองของฉัน  
- `/classrooms/bookings/<booking_id>/cancel/` — ยกเลิกการจองของตัวเอง
- `/classrooms/admin/overview/?date=YYYY-MM-DD` — หน้าแอดมินสรุปการจอง

> หมายเหตุ: ใน Markdown ให้ห่อ `<id>` และ `<booking_id>` ด้วย backticks เมื่อเขียนในข้อความอื่น ๆ เพื่อไม่ให้ถูกตีความเป็น HTML tag

---

## วิธีติดตั้ง & รัน (Dev)

1. สร้าง virtualenv และติดตั้งแพ็กเกจ

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate

   pip install -r requirements.txt

1. สร้างฐานข้อมูล

    ```bash
    python manage.py makemigrations
    python manage.py migrate

1. สร้างผู้ดูแลระบบ (สำหรับเข้า /admin/ และ/หรือสิทธิ์แอดมินในระบบ)

    ```bash
    python manage.py createsuperuser

1. รันเซิร์ฟเวอร์

    ```bash
    python manage.py runserver

---

## คลิปสอนการใช้งาน
https://youtu.be/OPusKwJ5SSw

---

## การใช้งานผ่าน web app บน cloud
- URL: https://cn331-as2-n86r.onrender.com
- คลิปอธิบายการใช้งาน : 
- สามารถดูรายละเอียด username และ password จากไฟล์ usersinfo.pdf ใน repository นี้ได้
