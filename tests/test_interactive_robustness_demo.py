from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.research.services.user_robustness_demo import (
    _attack_is_visible,
    _build_alias_map,
    _choose_targets,
)


class InteractiveRobustnessHelperTests(TestCase):
    def test_choose_targets_returns_three_lower_ranked_movies(self):
        results = [
            {"movie_id": movie_id, "predicted_rating": 5.0 - movie_id / 100}
            for movie_id in range(1, 21)
        ]

        targets = _choose_targets(results)

        self.assertEqual(len(targets), 3)
        self.assertTrue(all(target not in range(1, 8) for target in targets))

    def test_attack_visibility_requires_real_rank_improvement(self):
        clean = {101: 18, 102: 23, 103: 29}
        attacked = {101: 2, 102: 4, 103: 6}

        self.assertTrue(
            _attack_is_visible(clean, attacked, [101, 102, 103])
        )

    def test_aliases_create_good_target_and_random_roles(self):
        clean_results = [
            {"movie_id": movie_id, "predicted_rating": 5.0 - movie_id / 100}
            for movie_id in range(1, 15)
        ]
        aliases = _build_alias_map(
            clean_results,
            [8, 10, 12],
            list(range(1, 15)),
        )

        self.assertEqual(aliases[8]["display_name"], "Targeted Movie 1")
        self.assertEqual(aliases[8]["role"], "target")
        self.assertEqual(aliases[1]["display_name"], "Good Movie 1")
        self.assertEqual(aliases[1]["role"], "good")
        self.assertTrue(
            any(value["role"] == "random" for value in aliases.values())
        )


class RobustnessTogglePermissionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.normal_user = user_model.objects.create_user(
            username="normal-user",
            password="test-password-123",
        )
        self.staff_user = user_model.objects.create_user(
            username="staff-user",
            password="test-password-123",
            is_staff=True,
        )
        self.url = reverse("recommendations:toggle_robustness")

    def test_normal_user_cannot_disable_robustness(self):
        self.client.force_login(self.normal_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_staff_can_turn_robustness_off_and_back_on(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["robustness_enabled"])
        self.assertTrue(self.client.session["robustness_disabled"])

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["robustness_enabled"])
        self.assertFalse(self.client.session["robustness_disabled"])
