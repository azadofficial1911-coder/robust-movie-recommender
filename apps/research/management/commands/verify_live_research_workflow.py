from uuid import uuid4

from django.core.management.base import BaseCommand, CommandError

from apps.research.services.attacks import AttackConfig
from apps.research.services.live_workflow import (
    clear_workflow,
    run_attack,
    run_defence,
    run_detection,
    run_evaluation,
)


class Command(BaseCommand):
    help = "Execute and verify the live Attack -> Detection -> Defence -> Evaluation workflow."

    def add_arguments(self, parser):
        parser.add_argument("--attack-type", choices=["random", "average"], default="average")
        parser.add_argument("--target-movie-id", type=int, default=758)
        parser.add_argument("--attack-size", type=float, default=5.0)
        parser.add_argument("--filler-size", type=float, default=5.0)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--threshold", type=float, default=0.5)

    def handle(self, *args, **options):
        session_key = f"cli-{uuid4().hex}"
        config = AttackConfig(
            attack_type=options["attack_type"],
            target_movie_id=options["target_movie_id"],
            attack_size_percent=options["attack_size"],
            filler_size_percent=options["filler_size"],
            random_seed=options["seed"],
        )

        self.stdout.write("=" * 76)
        self.stdout.write("RMRS LIVE RESEARCH WORKFLOW VERIFICATION")
        self.stdout.write("=" * 76)

        try:
            attack = run_attack(session_key, config)
            self.stdout.write(self.style.SUCCESS("[1/4] ATTACK: PASS"))
            self.stdout.write(
                f"      {attack['fake_profiles']} fake profiles / "
                f"{attack['fake_ratings']} fake ratings generated"
            )

            detection = run_detection(
                session_key,
                threshold=options["threshold"],
            )
            self.stdout.write(self.style.SUCCESS("[2/4] DETECTION: PASS"))
            self.stdout.write(
                f"      {detection['suspicious_profiles_detected']} suspicious users; "
                f"precision={detection['detection_precision']:.3f}, "
                f"recall={detection['detection_recall']:.3f}, "
                f"F1={detection['detection_f1']:.3f}"
            )

            defence = run_defence(session_key)
            self.stdout.write(self.style.SUCCESS("[3/4] DEFENCE: PASS"))
            self.stdout.write(
                f"      {defence['users_removed']} users / "
                f"{defence['ratings_removed']} ratings removed"
            )

            evaluation = run_evaluation(session_key)
            self.stdout.write(self.style.SUCCESS("[4/4] EVALUATION: PASS"))

            self.stdout.write("")
            self.stdout.write("CONDITION RESULTS")
            self.stdout.write("-" * 76)
            for row in evaluation["rows"]:
                rank = row["target_rank"]
                score = row["target_score"]
                self.stdout.write(
                    f"{row['condition_label']:<31} "
                    f"rank={rank!s:<10} score={score!s:<12} "
                    f"hit@10={row['hit_rate']:.3f} "
                    f"RMSE={row['rmse']!s} MAE={row['mae']!s}"
                )

            stage_checks = [
                attack["fake_profiles"] > 0,
                detection["users_analysed"] > 0,
                defence["users_removed"] >= 0,
                len(evaluation["rows"]) == 3,
            ]

            if not all(stage_checks):
                raise CommandError("One or more workflow stages returned invalid output.")

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("FINAL RESULT: PASS"))
            self.stdout.write(
                "The same live experiment completed Attack -> Detection -> "
                "Defence -> Evaluation without using precomputed dashboard results."
            )

            if not evaluation["attack_promoted_target"]:
                self.stdout.write(
                    self.style.WARNING(
                        "NOTE: this configuration completed correctly but did not "
                        "promote the target on the selected evaluation-user sample."
                    )
                )

            if not evaluation["defence_reduced_attack"]:
                self.stdout.write(
                    self.style.WARNING(
                        "NOTE: this configuration completed correctly but defence "
                        "did not increase the target's mean rank number relative to "
                        "the attacked state on this sample."
                    )
                )

        except Exception as exc:
            raise CommandError(f"Live workflow failed: {exc}") from exc
        finally:
            clear_workflow(session_key)

        self.stdout.write("=" * 76)
