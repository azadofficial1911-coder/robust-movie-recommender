from django.test import TestCase
from django.urls import reverse
from .services.catalog import get_all_movies


class MovieExplorerTests(TestCase):
    def test_explorer_loads(self):
        response = self.client.get(reverse("movies:explorer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Movie Explorer")
        self.assertContains(response, "Inception")

    def test_demo_catalogue_is_available(self):
        self.assertGreaterEqual(len(get_all_movies()), 4)
