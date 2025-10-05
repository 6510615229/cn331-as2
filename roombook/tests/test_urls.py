# roombook/tests/test_urls.py
from django.test import SimpleTestCase
from django.urls import reverse, resolve

class RoomBookURLsTestCase(SimpleTestCase):
    def test_roombook_index_resolves(self):
        path = reverse("roombook:index")
        resolver = resolve(path)
        self.assertEqual(resolver.view_name, "roombook:index")
