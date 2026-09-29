from django.core.management.base import BaseCommand, CommandError

from apps.research.services.user_robustness_demo import (
    build_user_robustness_demo,
)


class Command(BaseCommand):
    help = (
        "Run the interactive robustness pipeline for one website user "
        "and print PASS/FAIL evidence."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            required=True,
            help="Django website user ID to test.",
        )

    def handle(self, *args, **options):
        user_id = int(options["user_id"])

        self.stdout.write("=" * 72)
        self.stdout.write("RMRS INTERACTIVE ROBUSTNESS VERIFICATION")
        self.stdout.write("=" * 72)
        self.stdout.write(f"Website user ID: {user_id}")
        self.stdout.write("")

        try:
            demo = build_user_robustness_demo(user_id)
        except Exception as exc:
            raise CommandError(
                f"Robustness demo could not be built: {exc}"
            ) from exc

        attack = demo["attack"]
        detection = demo["detection"]
        defence = demo["defence"]

        self.stdout.write("ATTACK")
        self.stdout.write("-" * 72)
        self.stdout.write(f"Type: {attack['type']}")
        self.stdout.write(
            "Attack size per target: "
            f"{attack['attack_size_percent_per_target']}%"
        )
        self.stdout.write(
            f"Fake profiles generated: {attack['fake_profiles']}"
        )
        self.stdout.write("")

        self.stdout.write("TARGET RANK MOVEMENT")
        self.stdout.write("-" * 72)

        target_checks = []

        for target in demo["target_movements"]:
            self.stdout.write(
                f"{target['display_name']}: "
                f"clean #{target['clean_rank']} -> "
                f"attacked #{target['attacked_rank']} -> "
                f"defended #{target['defended_rank']}"
            )

            attack_worked = (
                target["clean_rank"] is not None
                and target["attacked_rank"] is not None
                and target["attacked_rank"] < target["clean_rank"]
            )

            defence_helped = (
                target["attacked_rank"] is not None
                and target["defended_rank"] is not None
                and target["defended_rank"] > target["attacked_rank"]
            )

            target_checks.append(attack_worked and defence_helped)

        self.stdout.write("")
        self.stdout.write("DETECTION / DEFENCE")
        self.stdout.write("-" * 72)
        self.stdout.write(
            "Suspicious profiles detected: "
            f"{detection['suspicious_profiles_detected']}"
        )
        self.stdout.write(f"Users removed: {defence['users_removed']}")
        self.stdout.write(f"Ratings removed: {defence['ratings_removed']}")

        fake_profiles_exist = attack["fake_profiles"] > 0
        detection_worked = detection["suspicious_profiles_detected"] > 0
        defence_removed = (
            defence["users_removed"] > 0
            and defence["ratings_removed"] > 0
        )
        target_successes = sum(target_checks)

        final_pass = (
            fake_profiles_exist
            and detection_worked
            and defence_removed
            and target_successes >= 2
        )

        self.stdout.write("")
        self.stdout.write("=" * 72)

        if final_pass:
            self.stdout.write(self.style.SUCCESS("FINAL RESULT: PASS"))
            self.stdout.write(
                "The attack changed recommendation ranks, the detector found "
                "suspicious profiles, and the defence reduced the attack effect."
            )
        else:
            self.stdout.write(self.style.ERROR("FINAL RESULT: FAIL"))
            self.stdout.write(
                "The pipeline ran, but the visual robustness effect was not "
                "strong enough for at least two targets."
            )

        self.stdout.write("=" * 72)
