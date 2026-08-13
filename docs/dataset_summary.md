# MovieLens Dataset Summary

## 1. Purpose

This dataset is being prepared for the Robust Movie Recommendation System capstone project. The purpose of the Week 1 dataset work is to establish a clean and reproducible data pipeline that can later support the recommendation, attack, detection, defence, and evaluation components of the project.

## 2. Current Dataset

The current dataset is stored at:

`data/raw/ml-100k/movielens_100k.csv`

The raw dataset is kept separately from processed data so that the original source is not modified during cleaning and analysis.

The dataset currently contains 1,681 movie records.

### Available Columns

The dataset contains the following six columns:

- `movie_id` - unique identifier for each movie
- `title` - movie title
- `year` - movie release year
- `directors` - director information
- `actors` - actor information
- `genres` - movie genre information

## 3. Dataset Validation

Initial validation was performed using Python and pandas.

The following results were observed:

- Total movies: 1,681
- Unique movie IDs: 1,681
- Duplicate rows: 0
- Duplicate movie IDs: 0
- Earliest movie year: 1922
- Latest movie year: 1998

The dataset therefore has a unique `movie_id` for every movie and does not contain duplicate movie records.

## 4. Missing Values

Some movie metadata fields contain missing values.

The initial validation identified missing information in:

- `directors`
- `actors`
- `genres`

During preprocessing, missing values in these metadata fields are replaced with `Unknown`. This allows the records to remain available instead of deleting movies because of incomplete metadata.

## 5. Preprocessing

A reproducible preprocessing script was created at:

`recommender/prepare_dataset.py`

The preprocessing procedure:

1. Loads the original movie dataset.
2. Checks the number of records and unique movie IDs.
3. Checks duplicate rows.
4. Checks missing values.
5. Reviews the movie year range.
6. Removes exact duplicate rows if they exist.
7. Removes unnecessary leading and trailing spaces from movie titles.
8. Replaces missing director, actor, and genre information with `Unknown`.
9. Sorts the dataset by `movie_id`.
10. Saves the cleaned dataset separately from the raw data.

The processed movie dataset is stored at:

`data/processed/movies_clean.csv`

The original raw dataset is not overwritten.

## 6. Reusable Dataset Loader

A reusable Python loader was created at:

`recommender/data_loader.py`

The `load_movies()` function provides a common method for loading the movie dataset.

This approach is intended to keep data loading consistent across later components of the project.

## 7. Exploratory Analysis

A reproducible movie analysis script was created at:

`recommender/movie_analysis.py`

The script analyses:

- number of movies
- unique movie IDs
- movie year range
- missing metadata
- duplicate records
- genre distribution
- number of movies by year

The following figures are generated automatically:

`results/figures/movies_by_year.png`

`results/figures/genre_distribution.png`

`results/figures/missing_metadata.png`

These figures provide an initial understanding of the movie catalogue before the recommendation experiments are developed.

## 8. Current Dataset Limitation

The current `movielens_100k.csv` file contains movie metadata only.

It does not currently contain user-rating interactions such as:

- `user_id`
- `rating`
- `timestamp`

Therefore, rating-based analysis cannot yet be completed from this file alone.

The following tasks require user-rating interaction data and are not calculated from the current metadata file:

- rating distribution
- number of ratings per user
- number of ratings per movie
- global average rating
- average rating per movie
- user-movie interaction matrix
- dataset density and sparsity
- collaborative-filtering similarity
- train/test recommendation evaluation

A compatible ratings dataset will therefore be required before the collaborative-filtering recommender and robustness experiments can be completed.

## 9. Planned Recommendation Approach

The planned baseline recommendation method is user-based collaborative filtering.

Once user-rating data is available, the recommendation pipeline will:

1. Load the clean rating interactions.
2. Construct a user-movie matrix.
3. Calculate similarity between users.
4. Identify the most similar neighbours for a target user.
5. Predict ratings for movies the target user has not rated.
6. Rank predicted ratings.
7. Return Top-N movie recommendations.

The first implementation will focus on a simple and understandable baseline before robustness experiments are introduced.

## 10. Train/Test Strategy

A train/test split will be implemented after user-rating interaction data is available.

The same genuine test data should be preserved when comparing clean, attacked, and defended recommendation conditions. This will support a fair comparison between experimental conditions.

## 11. Week 1 Outputs Completed

The following outputs have currently been prepared:

- Raw movie metadata stored under `data/raw/`
- Reusable movie dataset loader
- Dataset validation procedure
- Movie preprocessing procedure
- `movies_clean.csv`
- Movie metadata exploratory analysis
- Movies-by-year figure
- Genre-distribution figure
- Missing-metadata figure
- Dataset documentation

The rating-dependent parts of the Week 1 plan remain dependent on obtaining user-rating interaction data.