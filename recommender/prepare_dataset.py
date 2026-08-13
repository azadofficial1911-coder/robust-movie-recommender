from pathlib import Path
import pandas as pd

from data_loader import load_movies


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "movies_clean.csv"


def validate_movies(movies):
    print("DATASET VALIDATION")
    print("-" * 40)

    print("Total rows:", len(movies))
    print("Unique movie IDs:", movies["movie_id"].nunique())
    print("Duplicate rows:", movies.duplicated().sum())
    print("Duplicate movie IDs:", movies["movie_id"].duplicated().sum())

    print("\nMissing values:")
    print(movies.isnull().sum())

    print("\nYear statistics:")
    print("Minimum year:", movies["year"].min())
    print("Maximum year:", movies["year"].max())


def clean_movies(movies):
    movies_clean = movies.copy()

    # Standardise text fields
    movies_clean["title"] = movies_clean["title"].astype(str).str.strip()

    # Replace missing metadata with clear placeholder values
    movies_clean["directors"] = movies_clean["directors"].fillna("Unknown")
    movies_clean["actors"] = movies_clean["actors"].fillna("Unknown")
    movies_clean["genres"] = movies_clean["genres"].fillna("Unknown")

    # Remove exact duplicate rows if any exist
    movies_clean = movies_clean.drop_duplicates()

    # Sort by movie ID for consistency
    movies_clean = movies_clean.sort_values("movie_id").reset_index(drop=True)

    return movies_clean


def save_clean_movies(movies_clean):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    movies_clean.to_csv(OUTPUT_FILE, index=False)

    print("\nClean movie dataset saved successfully.")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    movies = load_movies()

    validate_movies(movies)

    movies_clean = clean_movies(movies)

    save_clean_movies(movies_clean)

    print("\nFirst 5 cleaned rows:")
    print(movies_clean.head())