"""Automated tests for Week 6 Random Push and Average Push attacks."""

import unittest

import pandas as pd

from apps.research.services.attacks import (
    AttackConfig,
    calculate_fake_user_count,
    generate_average_push,
    generate_random_push,
    validate_attack_config,
)


class AttackGenerationTests(unittest.TestCase):
    """Validate synthetic shilling attack generation behaviour."""

    def setUp(self):
        """Create a small deterministic genuine ratings dataset."""

        rows = []

        # Ten genuine users and five movies.
        # Movies 1-4 have fixed ratings so their standard deviation is zero.
        # Movie 5 is the target movie.
        for user_id in range(1, 11):
            rows.extend(
                [
                    {
                        "user_id": user_id,
                        "movie_id": 1,
                        "rating": 2,
                        "timestamp": 1000 + user_id,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 2,
                        "rating": 3,
                        "timestamp": 1000 + user_id,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 3,
                        "rating": 4,
                        "timestamp": 1000 + user_id,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 4,
                        "rating": 3,
                        "timestamp": 1000 + user_id,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 5,
                        "rating": 2,
                        "timestamp": 1000 + user_id,
                    },
                ]
            )

        self.ratings = pd.DataFrame(rows)

        self.movie_statistics = pd.DataFrame(
            [
                {"movie_id": 1, "mean_rating": 2.0},
                {"movie_id": 2, "mean_rating": 3.0},
                {"movie_id": 3, "mean_rating": 4.0},
                {"movie_id": 4, "mean_rating": 3.0},
                {"movie_id": 5, "mean_rating": 2.0},
            ]
        )

        self.target_movie_id = 5
        self.attack_size_percent = 20
        self.filler_size_percent = 50
        self.random_seed = 42

    def test_calculate_fake_user_count(self):
        """Attack size should convert correctly into fake-user count."""

        count = calculate_fake_user_count(
            genuine_user_count=10,
            attack_size_percent=20,
        )

        self.assertEqual(count, 2)

    def test_validate_attack_config_rejects_invalid_values(self):
        """Invalid attack configuration should return validation errors."""

        config = AttackConfig(
            attack_type="random",
            target_movie_id=-1,
            attack_size_percent=0,
            filler_size_percent=101,
            target_rating=6,
            random_seed=-1,
        )

        errors = validate_attack_config(config)

        self.assertGreaterEqual(len(errors), 5)

    def test_random_push_generates_expected_profiles(self):
        """Random Push should create valid synthetic profiles."""

        original = self.ratings.copy(deep=True)

        fake = generate_random_push(
            ratings=self.ratings,
            target_movie_id=self.target_movie_id,
            attack_size_percent=self.attack_size_percent,
            filler_size_percent=self.filler_size_percent,
            global_average_rating=float(
                self.ratings["rating"].mean()
            ),
            random_seed=self.random_seed,
        )

        # 20% of 10 genuine users = 2 fake users.
        self.assertEqual(fake["user_id"].nunique(), 2)

        # Maximum genuine ID is 10.
        self.assertEqual(
            sorted(fake["user_id"].unique().tolist()),
            [11, 12],
        )

        # Four eligible filler movies × 50% = 2 filler items.
        # Each fake profile therefore has 2 fillers + 1 target.
        profile_sizes = fake.groupby("user_id").size()
        self.assertTrue((profile_sizes == 3).all())

        target_rows = fake[
            fake["movie_id"] == self.target_movie_id
        ]

        self.assertEqual(len(target_rows), 2)
        self.assertTrue((target_rows["rating"] == 5).all())

        self.assertEqual(
            fake.duplicated(["user_id", "movie_id"]).sum(),
            0,
        )

        self.assertTrue(
            fake["rating"].between(1, 5).all()
        )

        self.assertTrue(
            set(fake["movie_id"]).issubset(
                set(self.ratings["movie_id"])
            )
        )

        pd.testing.assert_frame_equal(
            self.ratings,
            original,
        )

    def test_random_push_is_reproducible(self):
        """The same Random Push seed should produce identical output."""

        global_mean = float(
            self.ratings["rating"].mean()
        )

        first = generate_random_push(
            self.ratings,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            global_mean,
            random_seed=42,
        )

        second = generate_random_push(
            self.ratings,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            global_mean,
            random_seed=42,
        )

        different = generate_random_push(
            self.ratings,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            global_mean,
            random_seed=99,
        )

        pd.testing.assert_frame_equal(first, second)

        self.assertFalse(first.equals(different))

    def test_random_push_centres_on_global_mean(self):
        """Zero-spread Random Push filler ratings should equal the mean."""

        constant_ratings = self.ratings.copy(deep=True)
        constant_ratings["rating"] = 3

        fake = generate_random_push(
            ratings=constant_ratings,
            target_movie_id=self.target_movie_id,
            attack_size_percent=20,
            filler_size_percent=50,
            global_average_rating=3.0,
            random_seed=42,
        )

        fillers = fake[
            fake["movie_id"] != self.target_movie_id
        ]

        self.assertTrue(
            (fillers["rating"] == 3).all()
        )

    def test_average_push_generates_expected_profiles(self):
        """Average Push should create valid synthetic profiles."""

        original = self.ratings.copy(deep=True)

        fake = generate_average_push(
            ratings=self.ratings,
            movie_statistics=self.movie_statistics,
            target_movie_id=self.target_movie_id,
            attack_size_percent=self.attack_size_percent,
            filler_size_percent=self.filler_size_percent,
            random_seed=self.random_seed,
        )

        self.assertEqual(fake["user_id"].nunique(), 2)

        self.assertEqual(
            sorted(fake["user_id"].unique().tolist()),
            [11, 12],
        )

        profile_sizes = fake.groupby("user_id").size()
        self.assertTrue((profile_sizes == 3).all())

        target_rows = fake[
            fake["movie_id"] == self.target_movie_id
        ]

        self.assertEqual(len(target_rows), 2)
        self.assertTrue((target_rows["rating"] == 5).all())

        self.assertEqual(
            fake.duplicated(["user_id", "movie_id"]).sum(),
            0,
        )

        self.assertTrue(
            fake["rating"].between(1, 5).all()
        )

        pd.testing.assert_frame_equal(
            self.ratings,
            original,
        )

    def test_average_push_uses_per_item_means(self):
        """Average Push filler values should follow each item's mean."""

        fake = generate_average_push(
            ratings=self.ratings,
            movie_statistics=self.movie_statistics,
            target_movie_id=self.target_movie_id,
            attack_size_percent=20,
            filler_size_percent=100,
            random_seed=42,
        )

        fillers = fake[
            fake["movie_id"] != self.target_movie_id
        ]

        expected_means = dict(
            zip(
                self.movie_statistics["movie_id"],
                self.movie_statistics["mean_rating"],
            )
        )

        for row in fillers.itertuples():
            self.assertEqual(
                row.rating,
                int(round(expected_means[row.movie_id])),
            )

    def test_average_push_is_reproducible(self):
        """The same Average Push seed should produce identical output."""

        first = generate_average_push(
            self.ratings,
            self.movie_statistics,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            random_seed=42,
        )

        second = generate_average_push(
            self.ratings,
            self.movie_statistics,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            random_seed=42,
        )

        different = generate_average_push(
            self.ratings,
            self.movie_statistics,
            self.target_movie_id,
            self.attack_size_percent,
            self.filler_size_percent,
            random_seed=99,
        )

        pd.testing.assert_frame_equal(first, second)

        self.assertFalse(first.equals(different))

    def test_invalid_target_movie_is_rejected(self):
        """An unknown target movie should not generate an attack."""

        with self.assertRaises(ValueError):
            generate_random_push(
                ratings=self.ratings,
                target_movie_id=999,
                attack_size_percent=20,
                filler_size_percent=50,
                global_average_rating=3.0,
                random_seed=42,
            )


if __name__ == "__main__":
    unittest.main()