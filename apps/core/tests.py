from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    """Tests for the authenticated RMRS home page."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        # Log in without needing to test the authentication form here.
        self.client.force_login(self.user)

    def test_home_page_loads(self):
        """Authenticated users should be able to open the home page."""

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)

        # Check content from the current streaming-style home page.
        self.assertContains(response, "The Dark Knight")
        self.assertContains(response, "Recommended For You")
        self.assertContains(response, "Popular Movies")

    def test_anonymous_user_is_redirected_to_login(self):
        """Logged-out users should not access the personalised home page."""

        self.client.logout()

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)