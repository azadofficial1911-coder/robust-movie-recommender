# RMRS Recommender Consistency Verification

## Purpose

This check verifies that the Clean, Attacked and Defended experimental conditions use the same recommender algorithm and evaluation setup.

The purpose is to ensure that differences in results are caused by the attack or defence process rather than by changes to the recommender.

## Recommender Configuration

The recommender uses:

- User-based collaborative filtering
- Mean-centred user ratings
- Cosine similarity
- Positive-similarity neighbours only
- Top-K neighbours: 30
- Minimum neighbours: 3
- Prediction range: 1.0 to 5.0
- Top-N recommendation default: 10

The shared implementation is located in:

`recommender/baseline_recommender.py`

The attack and defence evaluation scripts import the same recommender functions:

- `build_user_item_matrix`
- `build_user_similarity_matrix`
- `calculate_user_means`
- `predict_rating`

This avoids using separate recommendation algorithms for different experiment conditions.

## Fixed Evaluation Data

All evaluated conditions use the same genuine test dataset:

`data/processed/test_ratings.csv`

Test ratings:

- 19,971 genuine ratings

The test dataset is not modified by the attack or defence process.

## Dataset Verification

| Condition | Ratings |
|---|---:|
| Clean | 80,029 |
| Random Push attacked | 84,024 |
| Random Push defended | 80,029 |
| Average Push attacked | 84,024 |
| Average Push defended | 80,029 |

Each attack adds 3,995 synthetic ratings to the clean training dataset.

## Defence Verification

Direct dataset comparisons produced:

- Random defended equals clean: True
- Average defended equals clean: True

For the current controlled pilot, the defence removed the injected malicious profiles without changing the genuine training ratings.

## Recommender Results

| Condition | RMSE | MAE | Target Rank | Target Score |
|---|---:|---:|---:|---:|
| Clean | 0.9298 | 0.7253 | 1127.43 | 1.9722 |
| Random Push | 0.9304 | 0.7261 | 778.86 | 3.1083 |
| Random Defended | 0.9298 | 0.7253 | 1127.43 | 1.9722 |
| Average Push | 0.9309 | 0.7262 | 407.57 | 3.6731 |
| Average Defended | 0.9298 | 0.7253 | 1127.43 | 1.9722 |

## Conclusion

The Clean, Random Push, Average Push and defended experiments use the same collaborative-filtering recommender and the same genuine evaluation dataset.

The experimental difference is the training data:

Clean → genuine training data

Attacked → genuine training data + synthetic attack profiles

Defended → attacked data after suspicious-profile detection and removal

Therefore, changes observed between the conditions can be attributed to the attack and defence pipeline rather than changes to the recommender algorithm.

The exact recovery observed in the defended pilot applies to the tested configuration and should not be interpreted as proof of perfect defence under every possible attack setting.
## Top-N Consistency Verification

A Top-N consistency test was run using the same user-based collaborative filtering configuration across Clean, Random Push, Random Defended, Average Push and Average Defended conditions.

The fixed configuration used:

- Top-K neighbours: 30
- Minimum neighbours: 3
- Top-N recommendations: 10
- Target movie ID: 758
- Genuine test ratings: 19,971
- Evaluation users: 7

Results:

- Random defended Top-N equals Clean: True
- Average defended Top-N equals Clean: True
- Overall consistency result: PASS

The detailed results are stored in:

`results/tables/topn_consistency_results.csv`

## Movie ID Verification

The Django website movie IDs were checked against the MovieLens training data and `movie_statistics.csv`.

Results:

- All website movie IDs exist in MovieLens training data.
- All website movie IDs exist in `movie_statistics.csv`.
- Target movie ID 758 exists in both datasets.
- Website movie IDs use the same MovieLens `movie_id` namespace.
- Final movie ID verification result: PASS.