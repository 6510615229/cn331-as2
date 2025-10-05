from django.test import TestCase, Client
from django.contrib.auth.models import User


class StudentsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_login_page_loads(self):
        resp = self.client.get("/students/login/")
        self.assertEqual(resp.status_code, 200)

    def test_login_invalid_password(self):
        resp = self.client.post("/students/login/", {"username": "testuser", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)

    def test_login_success_redirects_to_index(self):
        resp = self.client.post("/students/login/", {"username": "testuser", "password": "12345"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/classrooms/") or resp.url.startswith("/students/"), f"Unexpected redirect target: {resp.url}")

    def test_login_with_bad_credentials_stays_on_login(self):
        resp = self.client.post("/students/login/", {"username": "wrong", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)

    def test_logout_get_redirects(self):
        self.client.login(username="testuser", password="12345")
        resp = self.client.get("/students/logout/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/students/login", resp.url)

    def test_logout_redirects_to_login(self):
        self.client.login(username="testuser", password="12345")
        resp = self.client.post("/students/logout/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/students/login", resp.url)
