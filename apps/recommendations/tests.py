from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RecommendationPageTests(TestCase):
    """Tests for the authenticated RMRS Recommendations page."""

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        # Authenticate the user before accessing protected pages.
        self.client.force_login(self.user)

    def test_recommendation_page_loads(self):
        """Authenticated users should be able to open Recommendations."""

        response = self.client.get(
            reverse("recommendations:index")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommendations")
        self.assertContains(
            response,
            "Recommendation Integration Ready"
        )

    def test_no_ratings_message_is_displayed(self):
        """A new user should be prompted to create a rating profile."""

        response = self.client.get(
            reverse("recommendations:index")
        )

        self.assertContains(
            response,
            "You currently have 0 saved rating(s)"
        )

    def test_anonymous_user_is_redirected_to_login(self):
        """Logged-out users should not access Recommendations."""

        self.client.logout()

        response = self.client.get(
            reverse("recommendations:index")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)