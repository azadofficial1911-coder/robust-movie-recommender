from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ResearchPermissionTests(TestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="normal",
            password="SafePass123!",
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="SafePass123!",
            is_staff=True,
        )

    def test_normal_user_cannot_access_research_lab(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("research:lab"))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_access_research_lab(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("research:lab"))
        self.assertEqual(response.status_code, 200)

    def test_staff_user_can_access_all_research_pages(self):
        self.client.force_login(self.staff_user)
        for route_name in [
            "research:attack_lab",
            "research:detection",
            "research:defence",
            "research:evaluation",
        ]:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
