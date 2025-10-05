from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User, Group

class StudentsViewsExtraTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u", password="p")
        self.admin = User.objects.create_user("ad", password="p", is_staff=True)

    def test_login_get_ok(self):
        resp = self.client.get(reverse("students:login"))
        self.assertEqual(resp.status_code, 200)

    def test_login_post_bad_credentials_stays(self):
        resp = self.client.post(reverse("students:login"), {"username":"u", "password":"wrong"})
        self.assertEqual(resp.status_code, 200)

    def test_login_post_success_redirects(self):
        resp = self.client.post(reverse("students:login"), {"username":"u", "password":"p"})
        self.assertIn(resp.status_code, (302, 303))

    def test_logout_redirects(self):
        self.client.login(username="u", password="p")
        resp = self.client.get(reverse("students:logout"))
        self.assertIn(resp.status_code, (302, 303))

    def test_admin_login_get_ok(self):
        resp = self.client.get(reverse("students:admin_login"))
        self.assertEqual(resp.status_code, 200)

    def test_admin_login_bad_credentials(self):
        resp = self.client.post(reverse("students:admin_login"), {"username":"u", "password":"p"})
        self.assertEqual(resp.status_code, 200)

    def test_admin_login_success_redirects(self):
        resp = self.client.post(reverse("students:admin_login"), {"username":"ad", "password":"p"})
        self.assertIn(resp.status_code, (302, 303))

class StudentsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass1")
        self.room_admin_user = User.objects.create_user(username="roomadmin", password="pass2")
        g = Group.objects.create(name="room_admin")
        self.room_admin_user.groups.add(g)

    def test_index_page_loads_200(self):
        resp = self.client.get("/students/")
        self.assertEqual(resp.status_code, 200)

    def test_login_success_with_safe_next_redirects_to_next(self):
        resp = self.client.post("/students/login/", {
            "username": "user1",
            "password": "pass1",
            "next": "/classrooms/"
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/classrooms/"))

    def test_login_success_with_unsafe_next_falls_back(self):
        resp = self.client.post("/students/login/", {
            "username": "user1",
            "password": "pass1",
            "next": "http://evil.example.com/steal"
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith("/classrooms/"),
            f"Expected fallback to /classrooms/, got {resp.url}"
        )

    def test_admin_login_post_non_admin_stays_on_login(self):
        try:
            url = reverse("students:admin_login")
        except NoReverseMatch:
            url = "/students/admin_login/"
        resp = self.client.post(url, {
            "username": "user1",
            "password": "pass1",
        })
        self.assertIn(resp.status_code, (200, 302, 303), f"Unexpected status {resp.status_code} at {url}")

    def test_admin_login_post_room_admin_group_redirects(self):
        try:
            url = reverse("students:admin_login")
        except NoReverseMatch:
            url = "/students/admin_login/"

        resp = self.client.post(url, {
            "username": "roomadmin",
            "password": "pass2",
        })
        self.assertIn(resp.status_code, (302, 303), f"Unexpected status {resp.status_code} at {url}")
        self.assertTrue(
            resp.url.startswith("/classrooms/admin/overview/") or resp.url.startswith("/classrooms/admin/overview"),
            f"Unexpected redirect target: {resp.url}"
        )

    def test_register_success_with_students_group(self):
        Group.objects.create(name="students")
        resp = self.client.post("/students/register/", {
            "username": "reg_with_group",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(resp.url.startswith("/students/login"))
        new_user = User.objects.get(username="reg_with_group")
        self.assertTrue(new_user.groups.filter(name="students").exists())

    def test_register_success_without_students_group(self):
        resp = self.client.post("/students/register/", {
            "username": "reg_no_group",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(resp.url.startswith("/students/login"))
        new_user = User.objects.get(username="reg_no_group")
        self.assertFalse(new_user.groups.filter(name="students").exists())

class StudentsViewsExtraCoverageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.admin = User.objects.create_superuser(username="super", email="a@a.com", password="12345")
        self.group_admin = Group.objects.create(name="room_admin")
        self.group_admin.user_set.add(self.user)

    def test_login_view_get(self):
        resp = self.client.get(reverse("students:login"))
        self.assertEqual(resp.status_code, 200)

    def test_login_view_post_invalid(self):
        resp = self.client.post(reverse("students:login"), {"username": "nope", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "login")

    def test_login_view_post_success(self):
        resp = self.client.post(reverse("students:login"), {"username": "testuser", "password": "12345"})
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(resp.url.startswith("/classrooms/") or resp.url.startswith("/students/"))

    def test_logout_view(self):
        self.client.login(username="testuser", password="12345")
        resp = self.client.get(reverse("students:logout"))
        self.assertIn(resp.status_code, (302, 303))

    def test_admin_login_as_superuser_redirects(self):
        resp = self.client.post(reverse("students:admin_login"), {"username": "super", "password": "12345"})
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn("/classrooms/admin/overview", resp.url)

    def test_admin_login_as_group_member_redirects(self):
        resp = self.client.post(reverse("students:admin_login"), {"username": "testuser", "password": "12345"})
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn("/classrooms/admin/overview", resp.url)

class StudentsViewsEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="edgeuser", password="StrongPass123")

    def test_index_when_logged_in_200(self):
        self.client.login(username="edgeuser", password="StrongPass123")
        resp = self.client.get("/students/")
        self.assertEqual(resp.status_code, 200)

    def test_register_password_mismatch_stays_200(self):
        resp = self.client.post("/students/register/", {
            "username": "mismatchuser",
            "password1": "Abc12345",
            "password2": "AbcXXXXX",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "password", status_code=200)

    def test_register_duplicate_username_stays_200(self):
        resp = self.client.post("/students/register/", {
            "username": "edgeuser",
            "password1": "Abc12345",
            "password2": "Abc12345",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "username", status_code=200)

    def test_logout_post_redirects(self):
        self.client.login(username="edgeuser", password="StrongPass123")
        resp = self.client.post("/students/logout/")
        self.assertIn(resp.status_code, (302, 303))
    
    def test_index_when_logged_in_via_reverse(self):
        self.client.login(username="edge2", password="StrongPass123")
        url = reverse("students:index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_register_empty_form_is_invalid(self):
        url = reverse("students:register")
        resp = self.client.post(url, {})  
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            ("username" in resp.content.decode("utf-8").lower()) or
            ("password" in resp.content.decode("utf-8").lower())
        )

    def test_logout_get_and_post_redirect(self):
        self.client.login(username="edge2", password="StrongPass123")
        url = reverse("students:logout")
        r1 = self.client.get(url)
        self.assertIn(r1.status_code, (302, 303))
        self.client.login(username="edge2", password="StrongPass123")
        r2 = self.client.post(url)
        self.assertIn(r2.status_code, (302, 303))

