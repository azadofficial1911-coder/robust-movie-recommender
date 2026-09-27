from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from apps.movies.models import WebsiteRating


class Command(BaseCommand):
    help = "Verify website movie IDs against MovieLens movie IDs."

    def handle(self, *args, **options):

        project_root = Path(__file__).resolve().parents[4]

        train_file = (
            project_root
            / "data"
            / "processed"
            / "train_ratings.csv"
        )

        movie_stats_file = (
            project_root
            / "data"
            / "processed"
            / "movie_statistics.csv"
        )

        target_movie_id = 758

        print("=" * 60)
        print("RMRS MOVIE ID VERIFICATION")
        print("=" * 60)

        # --------------------------------------------------
        # Load MovieLens data
        # --------------------------------------------------

        if not train_file.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Training file not found: {train_file}"
                )
            )
            return

        if not movie_stats_file.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Movie statistics file not found: "
                    f"{movie_stats_file}"
                )
            )
            return

        train_ratings = pd.read_csv(train_file)
        movie_stats = pd.read_csv(movie_stats_file)

        train_movie_ids = set(
            train_ratings["movie_id"]
            .dropna()
            .astype(int)
            .unique()
        )

        stats_movie_ids = set(
            movie_stats["movie_id"]
            .dropna()
            .astype(int)
            .unique()
        )

        # --------------------------------------------------
        # Website ratings
        # --------------------------------------------------

        website_ratings = WebsiteRating.objects.all()

        website_movie_ids = set(
            website_ratings.values_list(
                "movie_id",
                flat=True,
            )
        )

        website_movie_ids = {
            int(movie_id)
            for movie_id in website_movie_ids
        }

        print()
        print("DATASET INFORMATION")
        print("-------------------")

        print(
            f"Training ratings: "
            f"{len(train_ratings):,}"
        )

        print(
            f"MovieLens movies in training: "
            f"{len(train_movie_ids):,}"
        )

        print(
            f"Movie statistics IDs: "
            f"{len(stats_movie_ids):,}"
        )

        print(
            f"Website rating records: "
            f"{website_ratings.count():,}"
        )

        print(
            f"Unique website movie IDs: "
            f"{len(website_movie_ids):,}"
        )

        # --------------------------------------------------
        # Website -> MovieLens mapping
        # --------------------------------------------------

        missing_from_train = sorted(
            website_movie_ids - train_movie_ids
        )

        missing_from_stats = sorted(
            website_movie_ids - stats_movie_ids
        )

        print()
        print("WEBSITE MOVIE ID CHECK")
        print("----------------------")

        if not missing_from_train:
            self.stdout.write(
                self.style.SUCCESS(
                    "PASS - All website movie IDs exist "
                    "in MovieLens training data."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "FAIL - Website movie IDs missing "
                    "from training data:"
                )
            )

            print(missing_from_train)

        if not missing_from_stats:
            self.stdout.write(
                self.style.SUCCESS(
                    "PASS - All website movie IDs exist "
                    "in movie_statistics.csv."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "FAIL - Website movie IDs missing "
                    "from movie_statistics.csv:"
                )
            )

            print(missing_from_stats)

        # --------------------------------------------------
        # Target movie
        # --------------------------------------------------

        print()
        print("TARGET MOVIE CHECK")
        print("------------------")

        print(
            f"Target movie ID: {target_movie_id}"
        )

        target_in_train = (
            target_movie_id in train_movie_ids
        )

        target_in_stats = (
            target_movie_id in stats_movie_ids
        )

        print(
            f"Exists in training data: "
            f"{target_in_train}"
        )

        print(
            f"Exists in movie statistics: "
            f"{target_in_stats}"
        )

        if target_in_stats:

            target_row = movie_stats[
                movie_stats["movie_id"]
                == target_movie_id
            ]

            if not target_row.empty:

                row = target_row.iloc[0]

                if "title" in movie_stats.columns:
                    print(
                        f"Target title: "
                        f"{row['title']}"
                    )

                if "rating_count" in movie_stats.columns:
                    print(
                        f"Rating count: "
                        f"{row['rating_count']}"
                    )

                if "mean_rating" in movie_stats.columns:
                    print(
                        f"Mean rating: "
                        f"{row['mean_rating']}"
                    )

        # --------------------------------------------------
        # Sample mappings
        # --------------------------------------------------

        print()
        print("SAMPLE WEBSITE -> MOVIELENS")
        print("---------------------------")

        sample_ids = sorted(
            website_movie_ids
        )[:10]

        if not sample_ids:
            print(
                "No WebsiteRating records currently exist."
            )

        for movie_id in sample_ids:

            movie_row = movie_stats[
                movie_stats["movie_id"] == movie_id
            ]

            if movie_row.empty:
                title = "NOT FOUND"
            else:
                title = str(
                    movie_row.iloc[0]["title"]
                )

            print(
                f"Website movie_id={movie_id} "
                f"-> MovieLens movie_id={movie_id} "
                f"-> {title}"
            )

        # --------------------------------------------------
        # Final result
        # --------------------------------------------------

        mapping_pass = (
            not missing_from_train
            and not missing_from_stats
            and target_in_train
            and target_in_stats
        )

        print()
        print("=" * 60)

        if mapping_pass:

            self.stdout.write(
                self.style.SUCCESS(
                    "FINAL RESULT: PASS"
                )
            )

            print(
                "Website movie IDs correctly use "
                "the MovieLens movie_id namespace."
            )

        else:

            self.stdout.write(
                self.style.ERROR(
                    "FINAL RESULT: FAIL"
                )
            )

            print(
                "One or more movie ID mapping "
                "problems need investigation."
            )

        print("=" * 60)