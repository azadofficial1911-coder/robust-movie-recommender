"""Automated tests for the Week 6 suspicious-user detector."""

import unittest

import pandas as pd

from apps.research.services.detection import (
    calculate_suspicion_scores,
    classify_score,
    detect_suspicious_users,
    extract_detection_features,
    validate_suspicion_score,
    validate_threshold,
)


class DetectionTests(unittest.TestCase):
    """Validate behavioural feature extraction and detection behaviour."""

    def setUp(self):
        """Create a small controlled attacked dataset."""

        genuine_rows = []

        for user_id in range(1, 6):
            genuine_rows.extend(
                [
                    {
                        "user_id": user_id,
                        "movie_id": 1,
                        "rating": 3,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 2,
                        "rating": 4,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 3,
                        "rating": 2,
                    },
                ]
            )

        fake_rows = []

        for user_id in [6, 7]:
            fake_rows.extend(
                [
                    {
                        "user_id": user_id,
                        "movie_id": 1,
                        "rating": 3,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 2,
                        "rating": 4,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 3,
                        "rating": 2,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 4,
                        "rating": 3,
                    },
                    {
                        "user_id": user_id,
                        "movie_id": 5,
                        "rating": 5,
                    },
                ]
            )

        self.ratings = pd.DataFrame(
            genuine_rows + fake_rows
        )

        self.movie_statistics = pd.DataFrame(
            [
                {"movie_id": 1, "mean_rating": 3.0},
                {"movie_id": 2, "mean_rating": 4.0},
                {"movie_id": 3, "mean_rating": 2.0},
                {"movie_id": 4, "mean_rating": 3.0},
                {"movie_id": 5, "mean_rating": 2.0},
            ]
        )

        self.labels = pd.DataFrame(
            [
                {"user_id": 1, "true_label": "genuine"},
                {"user_id": 2, "true_label": "genuine"},
                {"user_id": 3, "true_label": "genuine"},
                {"user_id": 4, "true_label": "genuine"},
                {"user_id": 5, "true_label": "genuine"},
                {"user_id": 6, "true_label": "suspicious"},
                {"user_id": 7, "true_label": "suspicious"},
            ]
        )

    def test_threshold_validation(self):
        """Threshold must stay within zero and one."""

        validate_threshold(0.0)
        validate_threshold(0.5)
        validate_threshold(1.0)

        with self.assertRaises(ValueError):
            validate_threshold(-0.1)

        with self.assertRaises(ValueError):
            validate_threshold(1.1)

    def test_suspicion_score_validation(self):
        """Suspicion scores must stay within zero and one."""

        validate_suspicion_score(0.0)
        validate_suspicion_score(0.5)
        validate_suspicion_score(1.0)

        with self.assertRaises(ValueError):
            validate_suspicion_score(-0.1)

        with self.assertRaises(ValueError):
            validate_suspicion_score(1.1)

    def test_classification_threshold(self):
        """Scores should be classified using the supplied threshold."""

        self.assertEqual(
            classify_score(0.49, threshold=0.5),
            "genuine",
        )

        self.assertEqual(
            classify_score(0.50, threshold=0.5),
            "suspicious",
        )

    def test_feature_extraction_returns_every_user(self):
        """Feature extraction should create one row per analysed user."""

        features = extract_detection_features(
            ratings=self.ratings,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
        )

        self.assertEqual(
            len(features),
            self.ratings["user_id"].nunique(),
        )

        self.assertEqual(
            features["user_id"].nunique(),
            self.ratings["user_id"].nunique(),
        )

    def test_target_behaviour_detects_max_target_rating(self):
        """Maximum target ratings should activate the target signal."""

        features = extract_detection_features(
            ratings=self.ratings,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
        )

        fake_features = features[
            features["user_id"].isin([6, 7])
        ]

        genuine_features = features[
            features["user_id"].isin([1, 2, 3, 4, 5])
        ]

        self.assertTrue(
            (
                fake_features["target_item_behaviour"]
                == 1.0
            ).all()
        )

        self.assertTrue(
            (
                genuine_features["target_item_behaviour"]
                == 0.0
            ).all()
        )

    def test_suspicion_scores_are_bounded(self):
        """All calculated suspicion scores must remain in [0, 1]."""

        features = extract_detection_features(
            ratings=self.ratings,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
        )

        scored = calculate_suspicion_scores(
            features
        )

        self.assertTrue(
            scored["suspicion_score"]
            .between(0.0, 1.0)
            .all()
        )

    def test_detector_returns_structured_results(self):
        """Detection should return one result for every user."""

        results = detect_suspicious_users(
            ratings=self.ratings,
            threshold=0.5,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
            true_labels=self.labels,
        )

        self.assertEqual(
            len(results),
            7,
        )

        result_by_user = {
            result.user_id: result
            for result in results
        }

        self.assertEqual(
            result_by_user[6].true_label,
            "suspicious",
        )

        self.assertEqual(
            result_by_user[1].true_label,
            "genuine",
        )

    def test_ground_truth_does_not_change_scores(self):
        """Ground truth must not influence suspicion-score calculation."""

        without_labels = detect_suspicious_users(
            ratings=self.ratings,
            threshold=0.5,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
        )

        with_labels = detect_suspicious_users(
            ratings=self.ratings,
            threshold=0.5,
            movie_statistics=self.movie_statistics,
            target_movie_id=5,
            true_labels=self.labels,
        )

        scores_without_labels = {
            result.user_id: result.suspicion_score
            for result in without_labels
        }

        scores_with_labels = {
            result.user_id: result.suspicion_score
            for result in with_labels
        }

        self.assertEqual(
            scores_without_labels,
            scores_with_labels,
        )


if __name__ == "__main__":
    unittest.main()