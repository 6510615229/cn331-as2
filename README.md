# cn331-as2

## Members

1. พลกฤต กันยายน — 6510615229  
2. พลอยพรรณ เต็งประยูร — 6510615245

---

# Classrooms Project

เว็บแอป **ระบบจองห้องเรียน** พัฒนาด้วย **Django** แบ่งเป็น 2 แอป:

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

## โครงสร้างโฟลเดอร์ Roombook Test

    roombook/
    └── tests/
        ├── init.py
        ├── test_admin_smoke.py
        ├── test_models.py
        ├── test_urls.py
        ├── test_views_admin.py
        ├── test_views_booking.py
        └── test_views.py

### รายละเอียดการทดสอบแต่ละไฟล์

#### 1. `test_admin_smoke.py`

- ตรวจสอบการลงทะเบียนคลาส `ModelAdmin` ภายในไฟล์ `admin.py`
- ตรวจสอบว่าโมเดลหลัก (`Classrooms`, `Booking`) สามารถใช้งานใน Django Admin ได้อย่างถูกต้อง

#### 2. `test_models.py`

- ตรวจสอบการมีอยู่ของโมเดล `Classrooms` และ `Booking`
- ตรวจสอบการสร้างข้อมูลจริงในฐานข้อมูล
- ตรวจสอบตรรกะเวลาการจอง (จองได้เฉพาะ 1 ชั่วโมงต่อครั้ง)
- ตรวจสอบฟังก์ชัน `hours_range()` และ `is_slot_available()`
- ตรวจสอบการคืนค่า `__str__()` ของโมเดล

#### 3. `test_urls.py`

- ตรวจสอบชื่อและการแม็ปของ URL เช่น  
  `roombook:index`, `roombook:classroom`, `roombook:book`, `roombook:admin_overview`
- ตรวจสอบว่าการ `reverse()` และ `resolve()` ของ Django ทำงานได้ถูกต้อง

#### 4. `test_views.py`

- ตรวจสอบหน้า `index` โหลดได้เมื่อผู้ใช้ล็อกอิน
- ตรวจสอบ redirect ไปหน้า Login เมื่อล็อกอินไม่สำเร็จ
- ตรวจสอบการแสดงข้อมูลใน context ของหน้า `classroom_detail`

#### 5. `test_views_admin.py`

- ตรวจสอบสิทธิ์ของผู้ใช้ทั่วไปที่เข้าหน้า `/admin/overview/`
- ตรวจสอบว่าเฉพาะผู้ใช้ที่เป็นแอดมินเท่านั้นที่เข้าถึงได้
- ตรวจสอบพารามิเตอร์วันที่ไม่ถูกต้องให้ fallback เป็นวันปัจจุบัน
- ตรวจสอบข้อมูลสรุปการจอง (จำนวนห้อง, การจอง) ถูกต้องในหน้าแอดมิน

#### 6. `test_views_booking.py`

- ตรวจสอบกระบวนการจองห้องเรียนในทุกกรณี:
  - จองภายในเวลาที่อนุญาต (Happy Path)
  - จองนอกเวลาทำการ
  - จองซ้ำหรือเวลาชนกัน
  - ห้องไม่พร้อมใช้งาน
  - การจองเกิน 1 ชั่วโมง
- ตรวจสอบการยกเลิกการจองทั้งของผู้ใช้เองและของผู้อื่น
- ตรวจสอบข้อความแจ้งเตือน (`messages`) และการ redirect หลังการดำเนินการ

---

### การรันเทสต์

รันเฉพาะแอป Roombook

```bash
python manage.py test roombook -v 2
```

รันเฉพาะบางไฟล์

```bash
# ตัวอย่าง: รันเฉพาะ test_views_booking.py
python manage.py test roombook.tests.test_views_booking -v 2
```

รันการทดสอบพร้อมเก็บข้อมูล coverage

```bash
coverage run --source='roombook' manage.py test roombook -v 2
coverage report -m
```

## โครงสร้างโฟลเดอร์ Students Test

    students/
    └── tests/
        ├── init.py
        ├── test_auth.py
        └── test_views_students.py

### รายละเอียดการทดสอบแต่ละไฟล์

#### 1. `test_auth.py`

- ตรวจสอบหน้า **Login** โหลดได้ (`GET /students/login/`)
- ตรวจสอบการเข้าสู่ระบบด้วยข้อมูลถูกต้อง (Redirect ไปหน้าแรก)
- ตรวจสอบการเข้าสู่ระบบด้วยข้อมูลผิดพลาด (อยู่หน้าเดิม)
- ตรวจสอบการออกจากระบบ (`Logout`) แล้ว redirect กลับไปหน้า login
- ตรวจสอบการทำงานของ **Admin Login** ทั้งกรณีผู้ใช้ทั่วไปและผู้ดูแลระบบ

#### 2. `test_views_students.py`

- ตรวจสอบหน้า **Index** ของนักเรียน:
  - ผู้ใช้ทั่วไปเข้าสู่ระบบแล้วต้องเปิดหน้าได้ (HTTP 200)
  - ผู้ใช้ที่ยังไม่ล็อกอินจะถูก redirect ไปหน้า Login
- ตรวจสอบหน้า **Register**:
  - สมัครด้วยข้อมูลถูกต้อง → redirect ไปหน้า login
  - สมัครด้วยรหัสผ่านไม่ตรงกัน → แสดง error
  - สมัครด้วย username ซ้ำ → อยู่หน้าเดิม
  - สมัครโดยไม่มี group `students` → ตรวจสอบไม่ถูกเพิ่มเข้ากลุ่ม
  - สมัครโดยมี group `students` → ตรวจสอบถูกเพิ่มเข้ากลุ่ม
- ตรวจสอบหน้า **Admin Login**:
  - ผู้ใช้ทั่วไปล็อกอินผ่าน admin_login → อยู่หน้าเดิม
  - สมาชิกกลุ่ม `room_admin` → redirect ไปหน้า `/classrooms/admin/overview/`
  - ผู้ใช้ superuser → redirect ไปหน้า `/classrooms/admin/overview/`
- ตรวจสอบหน้า **Logout**:
  - ทั้ง `GET` และ `POST` ต้อง redirect ไปหน้าล็อกอิน
- ตรวจสอบกรณี edge case:
  - การส่งฟอร์มว่างหรือไม่ถูกต้อง (status 200, อยู่หน้าเดิม)
  - ตรวจสอบการเข้าถึง index ผ่าน `reverse('students:index')` เมื่อผู้ใช้ล็อกอินแล้ว

---

### การรันเทสต์

รันเฉพาะแอป Students

```bash
python manage.py test students -v 2
```

รันเฉพาะบางไฟล์

```bash
# ตัวอย่าง: รันเฉพาะ test_auth.py
python manage.py test students.tests.test_auth -v 2

# ตัวอย่าง: รันเฉพาะ test_views_students.py
python manage.py test students.tests.test_views_students -v 2

```

รันการทดสอบพร้อมเก็บข้อมูล coverage

```bash
coverage run --source='students' manage.py test students -v 2
coverage report -m
```

ต้องการรวมผลการทดสอบสองแอปเข้าด้วยกัน

```bash
coverage run --source='roombook' manage.py test roombook -v 2
coverage run -a --source='students' manage.py test students -v 2
coverage report -m
```

---

## Continuous Integration (CI)

มีการตั้งค่า GitHub Actions สำหรับรัน Unit Tests อัตโนมัติเมื่อมีการ push หรือ pull request ไปยัง branch `testing`.

Workflow: `.github/workflows/ci.yml`  
การทดสอบประกอบด้วย:

- `roombook` app
- `students` app  

โดยใช้ `coverage` ในการวัด code coverage อัตโนมัติ
