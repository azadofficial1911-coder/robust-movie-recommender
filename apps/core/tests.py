from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.home_catalogue import build_home_catalogue, load_home_movies


class HomeCatalogueTests(TestCase):
    def test_real_catalogue_loads_multiple_movielens_movies(self):
        movies = load_home_movies()

        self.assertGreater(len(movies), 100)
        self.assertEqual(movies[0]["id"], 1)
        self.assertTrue(any(movie["title"] == "Toy Story" for movie in movies))
        self.assertTrue(all("rating_count" in movie for movie in movies))

    def test_home_catalogue_contains_every_loaded_movie(self):
        catalogue = build_home_catalogue()

        alphabetical_count = sum(
            len(row["movies"])
            for row in catalogue["alphabetical_rows"]
        )

        self.assertEqual(
            alphabetical_count,
            catalogue["movie_count"],
        )
        self.assertEqual(
            catalogue["movie_count"],
            len(catalogue["all_movies"]),
        )


class HomePageTests(TestCase):
    """Tests for the authenticated RMRS home page."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        self.client.force_login(self.user)

    def test_home_page_loads_full_catalogue_sections(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toy Story")
        self.assertContains(response, "Recommended For You")
        self.assertContains(response, "Most Rated")
        self.assertContains(response, "Top Rated")
        self.assertContains(response, "FULL DATASET CATALOGUE")
        self.assertContains(response, "All ")

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
