## 8. Ratings Dataset and Current Limitation

The MovieLens 100K ratings dataset has now been added to the project.

The ratings data contains:

- 100,000 ratings
- 943 unique users
- 1,682 unique movie IDs
- Rating values from 1 to 5
- 0 missing values
- 0 duplicate rows

The global average rating is 3.5299.

The ratings dataset contains the following fields:

- `user_id`
- `movie_id`
- `rating`
- `timestamp`

The cleaned ratings dataset is stored at:

`data/processed/ratings_clean.csv`

One dataset mismatch was identified during validation. The ratings dataset contains 1,682 unique movie IDs, while the current movie metadata file contains 1,681 movie IDs.

Movie ID `267` is present in the ratings dataset but is missing from the current movie metadata file. This limitation has been documented and should be considered when joining rating information with movie metadata.

## 9. Ratings Analysis

A reproducible ratings analysis script was created at:

`recommender/rating_analysis.py`

The analysis produced the following results:

- Total ratings: 100,000
- Unique users: 943
- Unique rated movies: 1,682
- Minimum rating: 1
- Maximum rating: 5
- Global average rating: 3.5299
- Minimum ratings per user: 20
- Maximum ratings per user: 737
- Mean ratings per user: 106.04
- Median ratings per user: 65

The user-movie interaction matrix has a size of:

`943 × 1682`

The calculated dataset density is:

`6.3047%`

The calculated dataset sparsity is:

`93.6953%`

The following additional outputs are generated:

`data/processed/movie_statistics.csv`

`results/figures/rating_distribution.png`

`results/figures/ratings_per_user.png`

`results/figures/ratings_per_movie.png`

These results provide the baseline dataset statistics required before developing and evaluating the recommendation algorithms.

## 10. Planned Recommendation and Evaluation Approach

The planned baseline recommendation method is user-based collaborative filtering.

The recommendation pipeline will use the prepared rating interactions to:

1. Construct the user-movie matrix.
2. Calculate similarity between users.
3. Identify similar neighbours for a target user.
4. Predict ratings for unseen movies.
5. Rank predicted ratings.
6. Generate Top-N movie recommendations.

A train/test strategy will also be implemented for recommendation evaluation.

The same genuine test data should later be preserved when comparing clean, attacked, and defended recommendation conditions. This will allow the robustness experiments to be compared fairly.

## 11. Week 1 Outputs Completed

The following Week 1 dataset preparation and analysis outputs have now been completed:

- Raw movie metadata stored under `data/raw/`
- MovieLens user-rating data added
- Reusable movie and ratings dataset loaders
- Movie dataset validation
- Movie preprocessing procedure
- Clean movie dataset: `movies_clean.csv`
- Clean ratings dataset: `ratings_clean.csv`
- Movie metadata exploratory analysis
- Ratings exploratory analysis
- Movie statistics: `movie_statistics.csv`
- Movies-by-year figure
- Genre-distribution figure
- Missing-metadata figure
- Rating-distribution figure
- Ratings-per-user figure
- Ratings-per-movie figure
- User-movie matrix statistics
- Dataset density calculation
- Dataset sparsity calculation
- Dataset documentation

The dataset preparation stage is now ready to support the next stage of baseline recommender development.