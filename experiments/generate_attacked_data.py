"""Generate reproducible Week 6 attacked datasets and ground-truth labels."""

import json
import sys
from pathlib import Path

import pandas as pd


# Allow this script to import project modules when executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from apps.research.services.attacks import (  # noqa: E402
    generate_average_push,
    generate_random_push,
)


TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train_ratings.csv"
MOVIE_STATS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "movie_statistics.csv"
)
CONFIG_PATH = PROJECT_ROOT / "experiments" / "configs" / "attack_config.json"

FAKE_PROFILE_DIR = PROJECT_ROOT / "data" / "attacked" / "fake_profiles"
ATTACKED_DATASET_DIR = (
    PROJECT_ROOT / "data" / "attacked" / "attacked_datasets"
)
LABEL_DIR = PROJECT_ROOT / "data" / "attacked" / "labels"


def load_config(path: Path) -> dict:
    """Load the pilot attack configuration."""

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_attacked_dataset(
    genuine_train: pd.DataFrame,
    fake_profiles: pd.DataFrame,
) -> pd.DataFrame:
    """Combine genuine training ratings with synthetic attack profiles.

    Synthetic ratings receive one deterministic timestamp immediately
    after the maximum genuine training timestamp.
    """

    genuine_copy = genuine_train[
        ["user_id", "movie_id", "rating", "timestamp"]
    ].copy(deep=True)

    synthetic_timestamp = int(genuine_copy["timestamp"].max()) + 1

    fake_ratings = fake_profiles[
        ["user_id", "movie_id", "rating"]
    ].copy()

    fake_ratings["timestamp"] = synthetic_timestamp

    fake_ratings = fake_ratings[
        ["user_id", "movie_id", "rating", "timestamp"]
    ]

    attacked = pd.concat(
        [genuine_copy, fake_ratings],
        ignore_index=True,
    )

    return attacked


def build_ground_truth_labels(
    genuine_train: pd.DataFrame,
    fake_profiles: pd.DataFrame,
) -> pd.DataFrame:
    """Create genuine/suspicious labels for all users in one scenario."""

    genuine_user_ids = sorted(
        int(user_id)
        for user_id in genuine_train["user_id"].unique()
    )

    fake_user_ids = sorted(
        int(user_id)
        for user_id in fake_profiles["user_id"].unique()
    )

    genuine_labels = pd.DataFrame(
        {
            "user_id": genuine_user_ids,
            "true_label": "genuine",
        }
    )

    fake_labels = pd.DataFrame(
        {
            "user_id": fake_user_ids,
            "true_label": "suspicious",
        }
    )

    return pd.concat(
        [genuine_labels, fake_labels],
        ignore_index=True,
    )


def save_scenario(
    attack_name: str,
    genuine_train: pd.DataFrame,
    fake_profiles: pd.DataFrame,
) -> None:
    """Save fake profiles, attacked dataset, and labels."""

    attacked_dataset = build_attacked_dataset(
        genuine_train,
        fake_profiles,
    )

    labels = build_ground_truth_labels(
        genuine_train,
        fake_profiles,
    )

    fake_profile_path = (
        FAKE_PROFILE_DIR / f"{attack_name}_pilot.csv"
    )

    attacked_dataset_path = (
        ATTACKED_DATASET_DIR / f"{attack_name}_pilot.csv"
    )

    labels_path = (
        LABEL_DIR / f"{attack_name}_pilot_labels.csv"
    )

    fake_profiles.to_csv(
        fake_profile_path,
        index=False,
    )

    attacked_dataset.to_csv(
        attacked_dataset_path,
        index=False,
    )

    labels.to_csv(
        labels_path,
        index=False,
    )

    print(f"\n{attack_name.title()} Push")
    print(f"  Fake users: {fake_profiles['user_id'].nunique()}")
    print(f"  Fake ratings: {len(fake_profiles)}")
    print(f"  Attacked rows: {len(attacked_dataset)}")
    print(f"  Label rows: {len(labels)}")
    print(f"  Fake profiles: {fake_profile_path}")
    print(f"  Attacked dataset: {attacked_dataset_path}")
    print(f"  Labels: {labels_path}")


def main() -> None:
    """Generate Random Push and Average Push Week 6 pilot outputs."""

    config = load_config(CONFIG_PATH)

    genuine_train = pd.read_csv(TRAIN_PATH)
    movie_statistics = pd.read_csv(MOVIE_STATS_PATH)

    required_train_columns = {
        "user_id",
        "movie_id",
        "rating",
        "timestamp",
    }

    missing_train_columns = required_train_columns.difference(
        genuine_train.columns
    )

    if missing_train_columns:
        raise ValueError(
            "train_ratings.csv is missing required columns: "
            + ", ".join(sorted(missing_train_columns))
        )

    original_train = genuine_train.copy(deep=True)

    target_movie_id = int(config["target_movie_id"])
    attack_size_percent = float(config["attack_size_percent"])
    filler_size_percent = float(config["filler_size_percent"])
    target_rating = int(config["target_rating"])
    random_seed = int(config["random_seed"])
    rating_min = int(config["rating_min"])
    rating_max = int(config["rating_max"])

    global_average_rating = float(
        genuine_train["rating"].mean()
    )

    random_profiles = generate_random_push(
        ratings=genuine_train,
        target_movie_id=target_movie_id,
        attack_size_percent=attack_size_percent,
        filler_size_percent=filler_size_percent,
        global_average_rating=global_average_rating,
        random_seed=random_seed,
        target_rating=target_rating,
        rating_min=rating_min,
        rating_max=rating_max,
    )

    average_profiles = generate_average_push(
        ratings=genuine_train,
        movie_statistics=movie_statistics,
        target_movie_id=target_movie_id,
        attack_size_percent=attack_size_percent,
        filler_size_percent=filler_size_percent,
        random_seed=random_seed,
        target_rating=target_rating,
        rating_min=rating_min,
        rating_max=rating_max,
    )

    if not genuine_train.equals(original_train):
        raise RuntimeError(
            "Attack generation modified the genuine training dataset."
        )

    FAKE_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    ATTACKED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Week 6 attack generation")
    print("------------------------")
    print(f"Target movie: {target_movie_id}")
    print(f"Attack size: {attack_size_percent}%")
    print(f"Filler size: {filler_size_percent}%")
    print(f"Target rating: {target_rating}")
    print(f"Random seed: {random_seed}")
    print(f"Training global mean: {global_average_rating:.6f}")

    save_scenario(
        "random",
        genuine_train,
        random_profiles,
    )

    save_scenario(
        "average",
        genuine_train,
        average_profiles,
    )

    print("\nGeneration completed successfully.")


if __name__ == "__main__":
    main()