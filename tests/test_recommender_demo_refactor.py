from unittest.mock import patch

import pandas as pd
from django.test import SimpleTestCase

from apps.recommendations.services.recommender import (
    MIN_NEIGHBORS,
    TOP_K_NEIGHBORS,
    get_recommendations,
)


class RecommenderDemoRefactorTests(SimpleTestCase):
    """
    Tests for the refactored website recommender.

    These tests verify that:

    1. The same recommender function accepts clean,
       attacked and defended ratings DataFrames.

    2. Candidate movie filtering works.

    3. Display aliases do not change backend movie IDs,
       scores or ranks.

    4. Existing collaborative-filtering settings remain
       unchanged.
    """

    def setUp(self):
        # --------------------------------------------------
        # Logged-in website user's ratings.
        #
        # The user has rated three movies, which satisfies
        # the existing minimum-history requirement.
        # --------------------------------------------------

        self.website_profile = pd.DataFrame(
            [
                {
                    "movie_id": 1,
                    "rating": 5.0,
                },
                {
                    "movie_id": 2,
                    "rating": 4.0,
                },
                {
                    "movie_id": 3,
                    "rating": 1.0,
                },
            ]
        )

        # --------------------------------------------------
        # Clean recommender training data.
        #
        # Three genuine neighbours rate movies 1-6.
        # Movies 4, 5 and 6 are recommendation candidates.
        # --------------------------------------------------

        self.clean_ratings = pd.DataFrame(
            [
                {
                    "user_id": 10,
                    "movie_id": 1,
                    "rating": 5.0,
                },
                {
                    "user_id": 10,
                    "movie_id": 2,
                    "rating": 4.0,
                },
                {
                    "user_id": 10,
                    "movie_id": 3,
                    "rating": 1.0,
                },
                {
                    "user_id": 10,
                    "movie_id": 4,
                    "rating": 5.0,
                },
                {
                    "user_id": 10,
                    "movie_id": 5,
                    "rating": 3.0,
                },
                {
                    "user_id": 10,
                    "movie_id": 6,
                    "rating": 2.0,
                },

                {
                    "user_id": 11,
                    "movie_id": 1,
                    "rating": 4.0,
                },
                {
                    "user_id": 11,
                    "movie_id": 2,
                    "rating": 5.0,
                },
                {
                    "user_id": 11,
                    "movie_id": 3,
                    "rating": 1.0,
                },
                {
                    "user_id": 11,
                    "movie_id": 4,
                    "rating": 4.0,
                },
                {
                    "user_id": 11,
                    "movie_id": 5,
                    "rating": 4.0,
                },
                {
                    "user_id": 11,
                    "movie_id": 6,
                    "rating": 2.0,
                },

                {
                    "user_id": 12,
                    "movie_id": 1,
                    "rating": 5.0,
                },
                {
                    "user_id": 12,
                    "movie_id": 2,
                    "rating": 3.0,
                },
                {
                    "user_id": 12,
                    "movie_id": 3,
                    "rating": 1.0,
                },
                {
                    "user_id": 12,
                    "movie_id": 4,
                    "rating": 5.0,
                },
                {
                    "user_id": 12,
                    "movie_id": 5,
                    "rating": 3.0,
                },
                {
                    "user_id": 12,
                    "movie_id": 6,
                    "rating": 3.0,
                },
            ]
        )

        # --------------------------------------------------
        # Attacked data.
        #
        # Start from the exact clean data and add a
        # synthetic profile.
        #
        # The purpose of this test is not to reproduce the
        # full shilling attack algorithm. It verifies that
        # the SAME recommendation function can accept a
        # modified attacked DataFrame.
        # --------------------------------------------------

        fake_profile = pd.DataFrame(
            [
                {
                    "user_id": 99,
                    "movie_id": 1,
                    "rating": 5.0,
                },
                {
                    "user_id": 99,
                    "movie_id": 2,
                    "rating": 4.0,
                },
                {
                    "user_id": 99,
                    "movie_id": 3,
                    "rating": 1.0,
                },
                {
                    "user_id": 99,
                    "movie_id": 4,
                    "rating": 5.0,
                },
                {
                    "user_id": 99,
                    "movie_id": 5,
                    "rating": 5.0,
                },
                {
                    "user_id": 99,
                    "movie_id": 6,
                    "rating": 1.0,
                },
            ]
        )

        self.attacked_ratings = pd.concat(
            [
                self.clean_ratings,
                fake_profile,
            ],
            ignore_index=True,
        )

        # --------------------------------------------------
        # Defended data.
        #
        # For this controlled unit test, defence removes the
        # synthetic profile and returns to genuine data.
        # --------------------------------------------------

        self.defended_ratings = (
            self.clean_ratings.copy()
        )

        # --------------------------------------------------
        # Metadata used by recommendation output.
        # --------------------------------------------------

        self.movie_stats = pd.DataFrame(
            [
                {
                    "movie_id": 1,
                    "title": "Original Movie 1",
                },
                {
                    "movie_id": 2,
                    "title": "Original Movie 2",
                },
                {
                    "movie_id": 3,
                    "title": "Original Movie 3",
                },
                {
                    "movie_id": 4,
                    "title": "Original Movie 4",
                },
                {
                    "movie_id": 5,
                    "title": "Original Movie 5",
                },
                {
                    "movie_id": 6,
                    "title": "Original Movie 6",
                },
            ]
        )

        self.candidate_ids = {
            4,
            5,
            6,
        }

        self.demo_names = {
            4: "Good Movie 1",
            5: "Targeted Movie 1",
            6: "Random Movie 1",
        }

    def run_recommender(
        self,
        ratings_data,
        display_name_map=None,
    ):
        """
        Run the real refactored recommender while
        replacing only external profile/metadata loading.
        """

        with (
            patch(
                "apps.recommendations.services."
                "recommender._load_website_profile",
                return_value=(
                    self.website_profile.copy()
                ),
            ),
            patch(
                "apps.recommendations.services."
                "recommender._load_movie_stats",
                return_value=(
                    self.movie_stats.copy()
                ),
            ),
        ):
            return get_recommendations(
                user_id=1,
                top_n=3,
                ratings_data=ratings_data,
                candidate_movie_ids=(
                    self.candidate_ids
                ),
                display_name_map=(
                    display_name_map
                ),
            )

    def test_algorithm_settings_remain_unchanged(
        self,
    ):
        """
        The refactor must preserve the project's existing
        collaborative-filtering settings.
        """

        self.assertEqual(
            TOP_K_NEIGHBORS,
            30,
        )

        self.assertEqual(
            MIN_NEIGHBORS,
            3,
        )

    def test_same_function_accepts_clean_data(
        self,
    ):
        results = self.run_recommender(
            self.clean_ratings
        )

        self.assertGreater(
            len(results),
            0,
        )

    def test_same_function_accepts_attacked_data(
        self,
    ):
        results = self.run_recommender(
            self.attacked_ratings
        )

        self.assertGreater(
            len(results),
            0,
        )

    def test_same_function_accepts_defended_data(
        self,
    ):
        results = self.run_recommender(
            self.defended_ratings
        )

        self.assertGreater(
            len(results),
            0,
        )

    def test_candidate_filter_restricts_results(
        self,
    ):
        results = self.run_recommender(
            self.clean_ratings
        )

        returned_ids = {
            item["movie_id"]
            for item in results
        }

        self.assertTrue(
            returned_ids.issubset(
                self.candidate_ids
            )
        )

    def test_ranked_output_contract(
        self,
    ):
        results = self.run_recommender(
            self.clean_ratings,
            display_name_map=(
                self.demo_names
            ),
        )

        self.assertGreater(
            len(results),
            0,
        )

        for expected_rank, item in enumerate(
            results,
            start=1,
        ):
            self.assertIn(
                "movie_id",
                item,
            )

            self.assertIn(
                "display_name",
                item,
            )

            self.assertIn(
                "predicted_score",
                item,
            )

            self.assertIn(
                "rank",
                item,
            )

            self.assertIn(
                "reason",
                item,
            )

            self.assertEqual(
                item["rank"],
                expected_rank,
            )

    def test_aliases_do_not_change_ids_scores_or_ranks(
        self,
    ):
        """
        Presentation aliases must not affect scoring.

        The same ratings and backend IDs should produce
        exactly the same IDs, scores and ranks whether
        aliases are supplied or not.
        """

        without_aliases = self.run_recommender(
            self.clean_ratings,
            display_name_map=None,
        )

        with_aliases = self.run_recommender(
            self.clean_ratings,
            display_name_map=(
                self.demo_names
            ),
        )

        self.assertEqual(
            len(without_aliases),
            len(with_aliases),
        )

        for original, aliased in zip(
            without_aliases,
            with_aliases,
        ):
            self.assertEqual(
                original["movie_id"],
                aliased["movie_id"],
            )

            self.assertEqual(
                original["predicted_score"],
                aliased["predicted_score"],
            )

            self.assertEqual(
                original["rank"],
                aliased["rank"],
            )

    def test_display_names_are_applied_correctly(
        self,
    ):
        results = self.run_recommender(
            self.clean_ratings,
            display_name_map=(
                self.demo_names
            ),
        )

        for item in results:
            movie_id = item["movie_id"]

            self.assertEqual(
                item["display_name"],
                self.demo_names[movie_id],
            )

    def test_legacy_fields_are_preserved(
        self,
    ):
        """
        Existing frontend behaviour should continue
        working while Veasna migrates to the new output
        contract.
        """

        results = self.run_recommender(
            self.clean_ratings
        )

        for item in results:
            self.assertIn(
                "title",
                item,
            )

            self.assertIn(
                "predicted_rating",
                item,
            )

            self.assertEqual(
                item["predicted_rating"],
                item["predicted_score"],
            )

    def test_defended_output_returns_to_clean(
        self,
    ):
        """
        Because defended data in this controlled test is
        identical to clean data, the output should also
        be identical.
        """

        clean_results = self.run_recommender(
            self.clean_ratings
        )

        defended_results = (
            self.run_recommender(
                self.defended_ratings
            )
        )

        self.assertEqual(
            clean_results,
            defended_results,
        )