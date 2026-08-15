from pathlib import Path
import pandas as pd


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Dataset file locations
MOVIES_FILE = BASE_DIR / "data" / "raw" / "ml-100k" / "movielens_100k.csv"
RATINGS_FILE = BASE_DIR / "data" / "raw" / "ml-100k" / "u.data"


def load_movies():
    """
    Load the raw movie dataset.
    """

    if not MOVIES_FILE.exists():
        raise FileNotFoundError(
            f"Movie dataset was not found at: {MOVIES_FILE}"
        )

    movies = pd.read_csv(MOVIES_FILE)

    return movies


def load_ratings():
    """
    Load the MovieLens 100K ratings dataset.
    """

    if not RATINGS_FILE.exists():
        raise FileNotFoundError(
            f"Ratings dataset was not found at: {RATINGS_FILE}"
        )

    ratings = pd.read_csv(
        RATINGS_FILE,
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"]
    )

    return ratings


if __name__ == "__main__":

    # Test movie dataset
    movies = load_movies()

    print("Movie dataset loaded successfully!")
    print("Number of movies:", len(movies))
    print("Movie columns:", movies.columns.tolist())

    print()

    # Test ratings dataset
    ratings = load_ratings()

    print("Ratings dataset loaded successfully!")
    print("Number of ratings:", len(ratings))
    print("Ratings columns:", ratings.columns.tolist())

    print()
    print("First 5 ratings:")
    print(ratings.head())