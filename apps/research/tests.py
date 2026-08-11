from django.test import TestCase
from django.urls import reverse


class ResearchPlaceholderTests(TestCase):
    def test_all_research_routes_load(self):
        route_names = [
            "research:attack_lab",
            "research:detection",
            "research:defence",
            "research:evaluation",
        ]
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
