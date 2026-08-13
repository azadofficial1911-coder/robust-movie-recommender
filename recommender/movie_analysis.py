from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_movies


BASE_DIR = Path(__file__).resolve().parent.parent
FIGURE_DIR = BASE_DIR / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def analyse_movies():
    movies = load_movies()

    print("\nMOVIE DATASET SUMMARY")
    print("-" * 40)

    print("Total movies:", len(movies))
    print("Unique movie IDs:", movies["movie_id"].nunique())
    print("Minimum year:", movies["year"].min())
    print("Maximum year:", movies["year"].max())

    print("\nMissing values:")
    print(movies.isnull().sum())

    print("\nDuplicate rows:", movies.duplicated().sum())
    print("Duplicate movie IDs:", movies["movie_id"].duplicated().sum())

    # -------------------------
    # Movies by year
    # -------------------------

    year_counts = movies["year"].value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    year_counts.plot(kind="bar")

    plt.title("Number of Movies by Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Movies")
    plt.tight_layout()

    year_file = FIGURE_DIR / "movies_by_year.png"
    plt.savefig(year_file)
    plt.close()

    print("\nSaved:", year_file)

    # -------------------------
    # Genre analysis
    # -------------------------

    genres = (
        movies["genres"]
        .dropna()
        .str.split()
        .explode()
        .value_counts()
        .head(15)
    )

    plt.figure(figsize=(10, 6))
    genres.plot(kind="bar")

    plt.title("Top Movie Genres")
    plt.xlabel("Genre")
    plt.ylabel("Number of Movies")
    plt.tight_layout()

    genre_file = FIGURE_DIR / "genre_distribution.png"
    plt.savefig(genre_file)
    plt.close()

    print("Saved:", genre_file)

    # -------------------------
    # Missing metadata graph
    # -------------------------

    missing = movies.isnull().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        plt.figure(figsize=(8, 5))
        missing.plot(kind="bar")

        plt.title("Missing Movie Metadata")
        plt.xlabel("Column")
        plt.ylabel("Missing Values")
        plt.tight_layout()

        missing_file = FIGURE_DIR / "missing_metadata.png"
        plt.savefig(missing_file)
        plt.close()

        print("Saved:", missing_file)


if __name__ == "__main__":
    analyse_movies()