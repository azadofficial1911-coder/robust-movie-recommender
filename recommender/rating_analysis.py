from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_ratings, load_movies


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURE_DIR = BASE_DIR / "results" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def analyse_ratings():
    ratings = load_ratings()
    movies = load_movies()

    print("\nRATINGS DATASET SUMMARY")
    print("-" * 40)

    total_ratings = len(ratings)
    unique_users = ratings["user_id"].nunique()
    unique_movies = ratings["movie_id"].nunique()

    min_rating = ratings["rating"].min()
    max_rating = ratings["rating"].max()
    mean_rating = ratings["rating"].mean()

    missing_values = ratings.isnull().sum().sum()
    duplicate_rows = ratings.duplicated().sum()

    print("Total ratings:", total_ratings)
    print("Unique users:", unique_users)
    print("Unique movies:", unique_movies)
    print("Minimum rating:", min_rating)
    print("Maximum rating:", max_rating)
    print("Average rating:", round(mean_rating, 4))
    print("Missing values:", missing_values)
    print("Duplicate rows:", duplicate_rows)

    # Save clean ratings
    ratings_clean = ratings.drop_duplicates().copy()

    ratings_clean_file = PROCESSED_DIR / "ratings_clean.csv"
    ratings_clean.to_csv(ratings_clean_file, index=False)

    print("\nSaved:", ratings_clean_file)

    # Rating distribution
    rating_counts = (
        ratings_clean["rating"]
        .value_counts()
        .sort_index()
    )

    print("\nRating distribution:")
    print(rating_counts)

    plt.figure(figsize=(8, 5))
    rating_counts.plot(kind="bar")
    plt.title("Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Ratings")
    plt.tight_layout()

    rating_distribution_file = FIGURE_DIR / "rating_distribution.png"
    plt.savefig(rating_distribution_file)
    plt.close()

    print("Saved:", rating_distribution_file)

    # Ratings per user
    ratings_per_user = ratings_clean.groupby("user_id").size()

    print("\nRatings per user:")
    print("Minimum:", ratings_per_user.min())
    print("Maximum:", ratings_per_user.max())
    print("Mean:", round(ratings_per_user.mean(), 2))
    print("Median:", ratings_per_user.median())

    plt.figure(figsize=(10, 5))
    ratings_per_user.plot(kind="hist", bins=30)
    plt.title("Ratings per User")
    plt.xlabel("Number of Ratings")
    plt.ylabel("Number of Users")
    plt.tight_layout()

    ratings_per_user_file = FIGURE_DIR / "ratings_per_user.png"
    plt.savefig(ratings_per_user_file)
    plt.close()

    print("Saved:", ratings_per_user_file)

    # Ratings per movie
    movie_stats = (
        ratings_clean.groupby("movie_id")
        .agg(
            rating_count=("rating", "count"),
            mean_rating=("rating", "mean")
        )
        .reset_index()
    )

    movie_stats = movie_stats.merge(
        movies[["movie_id", "title"]],
        on="movie_id",
        how="left"
    )

    movie_stats = movie_stats[
        ["movie_id", "title", "rating_count", "mean_rating"]
    ]

    movie_stats["mean_rating"] = movie_stats["mean_rating"].round(4)

    movie_statistics_file = PROCESSED_DIR / "movie_statistics.csv"
    movie_stats.to_csv(movie_statistics_file, index=False)

    print("\nSaved:", movie_statistics_file)

    plt.figure(figsize=(10, 5))
    movie_stats["rating_count"].plot(kind="hist", bins=30)
    plt.title("Ratings per Movie")
    plt.xlabel("Number of Ratings")
    plt.ylabel("Number of Movies")
    plt.tight_layout()

    ratings_per_movie_file = FIGURE_DIR / "ratings_per_movie.png"
    plt.savefig(ratings_per_movie_file)
    plt.close()

    print("Saved:", ratings_per_movie_file)

    # User-movie matrix
    user_movie_matrix = ratings_clean.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating"
    )

    print("\nUser-movie matrix shape:", user_movie_matrix.shape)

    # Density and sparsity
    possible_ratings = (
        unique_users * unique_movies
    )

    density = total_ratings / possible_ratings
    sparsity = 1 - density

    print("Dataset density:", round(density * 100, 4), "%")
    print("Dataset sparsity:", round(sparsity * 100, 4), "%")

    print("\nGLOBAL AVERAGE RATING")
    print(round(mean_rating, 4))


if __name__ == "__main__":
    analyse_ratings()