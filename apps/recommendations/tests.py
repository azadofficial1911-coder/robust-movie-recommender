from django.test import TestCase
from django.urls import reverse


class RecommendationPageTests(TestCase):
    def test_recommendation_page_loads(self):
        response = self.client.get(reverse("recommendations:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personalised Recommendations")
        self.assertContains(response, "Demo results")
