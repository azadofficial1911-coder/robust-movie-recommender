from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .services.catalog import get_all_movies


class MovieExplorerTests(TestCase):
    """Tests for the authenticated RMRS Movie Explorer."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        # Authenticate the test user before accessing protected movie pages.
        self.client.force_login(self.user)

    def test_explorer_loads(self):
        """Authenticated users should be able to open Movie Explorer."""

        response = self.client.get(
            reverse("movies:explorer")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Movie Explorer")
        self.assertContains(response, "Inception")

    def test_catalogue_is_available(self):
        """The local movie catalogue should contain enough movies for testing."""

        self.assertGreaterEqual(
            len(get_all_movies()),
            10,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        """Logged-out users should not access Movie Explorer."""

        self.client.logout()

        response = self.client.get(
            reverse("movies:explorer")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)