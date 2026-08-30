from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountFlowTests(TestCase):
    def test_signup_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SafePass12345!",
                "password2": "SafePass12345!",
            },
        )
        self.assertRedirects(response, reverse("movies:onboarding"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_wrong_password_is_rejected(self):
        User.objects.create_user(username="veasna", password="CorrectPass123!")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "veasna", "password": "WrongPassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
