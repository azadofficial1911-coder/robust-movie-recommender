from pathlib import Path
import pandas as pd


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw movie dataset
MOVIES_FILE = BASE_DIR / "data" / "raw" / "ml-100k" / "movielens_100k.csv"


def load_movies():
    """
    Load the raw movie dataset.

    Returns:
        pandas.DataFrame: Movie information containing fields such as
        movie_id, title, year, directors, actors and genres.
    """

    if not MOVIES_FILE.exists():
        raise FileNotFoundError(
            f"Movie dataset was not found at: {MOVIES_FILE}"
        )

    movies = pd.read_csv(MOVIES_FILE)

    return movies


if __name__ == "__main__":
    movies = load_movies()

    print("Movie dataset loaded successfully!")
    print()
    print("First 5 rows:")
    print(movies.head())
    print()
    print("Columns:")
    print(movies.columns.tolist())
    print()
    print("Number of movies:", len(movies))