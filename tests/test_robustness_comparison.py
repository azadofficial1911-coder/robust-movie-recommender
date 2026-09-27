import unittest

from apps.research.services.robustness_comparison import (
    _verify_same_attack,
    build_robustness_comparison,
    normalise_scenario,
)


class RobustnessComparisonTests(unittest.TestCase):

    def test_normalise_random(self):
        self.assertEqual(
            normalise_scenario("random"),
            "random",
        )

    def test_normalise_average(self):
        self.assertEqual(
            normalise_scenario("average"),
            "average",
        )

    def test_normalise_case_and_spaces(self):
        self.assertEqual(
            normalise_scenario("  Average  "),
            "average",
        )

    def test_invalid_scenario_rejected(self):
        with self.assertRaises(ValueError):
            normalise_scenario("nuke")

    def test_random_comparison_builds(self):
        comparison = build_robustness_comparison(
            "random"
        )

        self.assertIsNotNone(comparison)
        self.assertEqual(
            comparison["scenario"],
            "random",
        )
        self.assertEqual(
            comparison["scenario_label"],
            "Random Push",
        )

    def test_average_comparison_builds(self):
        comparison = build_robustness_comparison(
            "average"
        )

        self.assertIsNotNone(comparison)
        self.assertEqual(
            comparison["scenario"],
            "average",
        )
        self.assertEqual(
            comparison["scenario_label"],
            "Average Push",
        )

    def test_same_attack_verified_random(self):
        comparison = build_robustness_comparison(
            "random"
        )

        self.assertTrue(
            comparison["same_attack_verified"]
        )

    def test_same_attack_verified_average(self):
        comparison = build_robustness_comparison(
            "average"
        )

        self.assertTrue(
            comparison["same_attack_verified"]
        )

    def test_random_uses_shared_attack_source(self):
        comparison = build_robustness_comparison(
            "random"
        )

        self.assertEqual(
            comparison["provenance"][
                "without_robustness_source"
            ],
            comparison["provenance"][
                "with_robustness_attack_source"
            ],
        )

    def test_average_uses_shared_attack_source(self):
        comparison = build_robustness_comparison(
            "average"
        )

        self.assertEqual(
            comparison["provenance"][
                "without_robustness_source"
            ],
            comparison["provenance"][
                "with_robustness_attack_source"
            ],
        )

    def test_attack_fingerprint_exists_random(self):
        comparison = build_robustness_comparison(
            "random"
        )

        fingerprint = comparison[
            "attack_source"
        ]["sha256"]

        self.assertIsNotNone(fingerprint)
        self.assertEqual(
            len(fingerprint),
            64,
        )

    def test_attack_fingerprint_exists_average(self):
        comparison = build_robustness_comparison(
            "average"
        )

        fingerprint = comparison[
            "attack_source"
        ]["sha256"]

        self.assertIsNotNone(fingerprint)
        self.assertEqual(
            len(fingerprint),
            64,
        )

    def test_random_contains_three_conditions(self):
        comparison = build_robustness_comparison(
            "random"
        )

        self.assertIn("clean", comparison)
        self.assertIn(
            "without_robustness",
            comparison,
        )
        self.assertIn(
            "with_robustness",
            comparison,
        )

    def test_attack_mismatch_rejected(self):
        attacked = {
            "attack_type": "average",
            "attack_size": 5,
            "filler_size": 5,
            "target_movie": 758,
            "random_seed": 42,
        }

        defended = {
            "attack_type": "average",
            "attack_size": 10,
            "filler_size": 5,
            "target_movie": 758,
            "random_seed": 42,
        }

        with self.assertRaises(ValueError):
            _verify_same_attack(
                attacked,
                defended,
            )


if __name__ == "__main__":
    unittest.main()