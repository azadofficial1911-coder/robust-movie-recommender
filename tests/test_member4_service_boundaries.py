"""Additional Achintha (Member 4) tests: the Django service boundary
wrappers in apps/research/services/{defence,evaluation}.py, exercised
against small controlled examples so they don't depend on the actual
Week 6 pilot data files being present.
"""

import unittest

import pandas as pd

from apps.research.services.defence import apply_defence
from apps.research.services.evaluation import (
    evaluate_attack_impact_for_user,
    evaluate_experiment,
    summarise_attack_impact,
)


class ApplyDefenceServiceTests(unittest.TestCase):
    def test_apply_defence_end_to_end(self):
        ratings = pd.DataFrame(
            {
                "user_id": [1, 1, 2, 3],
                "movie_id": [10, 11, 10, 12],
                "rating": [4, 5, 3, 2],
            }
        )
        detection_results = pd.DataFrame(
            {
                "user_id": [1, 2, 3],
                "suspicion_score": [0.9, 0.1, 0.7],
                "predicted_label": ["suspicious", "genuine", "suspicious"],
            }
        )
        result = apply_defence(ratings=ratings, detection_results=detection_results)

        self.assertEqual(result["suspicious_user_ids"], [1, 3])
        self.assertEqual(sorted(result["defended_ratings"]["user_id"].unique()), [2])
        self.assertEqual(result["summary"]["users_removed"], 2)
        self.assertEqual(result["summary"]["defence_method"], "remove_suspicious_profiles")
        self.assertEqual(result["summary"]["status"], "applied")

    def test_apply_defence_uses_predicted_label_not_true_label(self):
        ratings = pd.DataFrame({"user_id": [1, 2], "movie_id": [10, 10], "rating": [4, 3]})
        detection_results = pd.DataFrame(
            {
                "user_id": [1, 2],
                "predicted_label": ["suspicious", "genuine"],
                "true_label": ["genuine", "genuine"],  # deliberately disagrees with predicted_label
            }
        )
        result = apply_defence(ratings=ratings, detection_results=detection_results)
        # Must follow predicted_label (user 1 removed) even though true_label says genuine.
        self.assertEqual(result["suspicious_user_ids"], [1])

    def test_apply_defence_requires_inputs(self):
        with self.assertRaises(ValueError):
            apply_defence(ratings=None, detection_results=None)

    def test_original_ratings_unchanged(self):
        ratings = pd.DataFrame({"user_id": [1, 2], "movie_id": [10, 10], "rating": [4, 3]})
        detection_results = pd.DataFrame({"user_id": [1, 2], "predicted_label": ["suspicious", "genuine"]})
        original_len = len(ratings)
        apply_defence(ratings=ratings, detection_results=detection_results)
        self.assertEqual(len(ratings), original_len)


class AttackImpactHelpersTests(unittest.TestCase):
    def test_evaluate_attack_impact_for_user(self):
        result = evaluate_attack_impact_for_user(
            recommended_movie_ids=[10, 20, 758, 40],
            predicted_scores={10: 4.5, 20: 4.2, 758: 3.9, 40: 3.5},
            target_movie_id=758,
            k=10,
        )
        self.assertEqual(result["target_rank"], 3)
        self.assertAlmostEqual(result["target_score"], 3.9)
        self.assertTrue(result["hit_at_k"])

    def test_evaluate_attack_impact_for_user_target_absent(self):
        result = evaluate_attack_impact_for_user(
            recommended_movie_ids=[10, 20, 40],
            predicted_scores={10: 4.5, 20: 4.2, 40: 3.5},
            target_movie_id=758,
            k=10,
        )
        self.assertIsNone(result["target_rank"])
        self.assertIsNone(result["target_score"])
        self.assertFalse(result["hit_at_k"])

    def test_summarise_attack_impact(self):
        per_user = [
            {"target_rank": 3, "target_score": 4.0, "hit_at_k": True},
            {"target_rank": 15, "target_score": 3.0, "hit_at_k": False},
        ]
        summary = summarise_attack_impact(per_user)
        self.assertAlmostEqual(summary["target_rank"], 9.0)
        self.assertAlmostEqual(summary["target_score"], 3.5)
        self.assertAlmostEqual(summary["hit_rate"], 0.5)


class EvaluateExperimentServiceTests(unittest.TestCase):
    def test_evaluate_experiment_combines_conditions(self):
        result = evaluate_experiment(
            clean_results={"actual": [4, 5, 3], "predicted": [4, 4, 3]},
            attacked_results={"actual": [4, 5, 3], "predicted": [2, 2, 3]},
        )
        self.assertIn("clean", result)
        self.assertIn("attacked", result)
        self.assertNotIn("defended", result)
        self.assertLess(result["clean"]["rmse"], result["attacked"]["rmse"])

    def test_evaluate_experiment_requires_data(self):
        with self.assertRaises(ValueError):
            evaluate_experiment()

    def test_evaluate_experiment_attack_impact(self):
        per_user = [
            evaluate_attack_impact_for_user(
                recommended_movie_ids=[1, 2, 99],
                predicted_scores={1: 5.0, 2: 4.5, 99: 4.0},
                target_movie_id=99,
                k=3,
            ),
            evaluate_attack_impact_for_user(
                recommended_movie_ids=[99, 3, 4],
                predicted_scores={99: 5.0, 3: 4.0, 4: 3.5},
                target_movie_id=99,
                k=3,
            ),
        ]
        result = evaluate_experiment(
            attacked_results={
                "actual": [4, 5],
                "predicted": [4, 5],
                "attack_impact_per_user": per_user,
            }
        )
        self.assertAlmostEqual(result["attacked"]["hit_rate"], 1.0)
        self.assertAlmostEqual(result["attacked"]["target_rank"], 2.0)

    def test_evaluate_experiment_detection_metrics(self):
        result = evaluate_experiment(
            defended_results={
                "actual": [4, 5],
                "predicted": [4, 5],
                "true_labels": ["suspicious", "genuine"],
                "predicted_labels": ["suspicious", "genuine"],
            }
        )
        self.assertAlmostEqual(result["defended"]["detection_precision"], 1.0)
        self.assertAlmostEqual(result["defended"]["detection_recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
