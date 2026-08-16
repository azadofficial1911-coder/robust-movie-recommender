# Defence and Evaluation Plan — Week 1

## Purpose
Define the defence and evaluation framework comparing Clean, Attacked, and Defended conditions.

## Defence strategies
### Strategy A — Remove suspicious profiles
Use detector output to identify suspicious users and remove their profiles/ratings from the attacked dataset.

### Strategy B — Reduce suspicious-user influence
Assign suspicious users a reduced influence/weight during model training or scoring. Final weighting values remain experimental parameters.

## Evaluation conditions
- **Clean:** original genuine dataset.
- **Attacked:** genuine data with the selected shilling attack.
- **Defended:** attacked data after the selected defence.

Use the same genuine test set across conditions.

## Recommendation metrics
- RMSE
- MAE
- Precision@K
- Recall@K

## Attack-impact metrics
- Target movie predicted score
- Target movie rank
- Target movie hit rate / recommendation frequency

## Detection metrics
- Precision
- Recall
- F1-score
- False Positive Rate
- Confusion Matrix

## Experiment parameters
Each experiment should preserve: experiment ID, condition, attack type, attack size, filler size, target movie, target rating, random seed, detector threshold, defence method, and Top-K.

## Planned figures
1. Clean vs Attacked vs Defended recommendation metrics.
2. Target movie rank comparison.
3. Attack size vs target rank.
4. Random push vs average push.
5. Detection performance.
6. Confusion matrix.

## Planned tables
Recommendation performance, attack impact, and detection performance tables. No results are entered during Week 1.

## Integration
Defence consumes detector output identifying suspicious users. Evaluation consumes recommender predictions/recommendations for Clean, Attacked, and Defended conditions.

## Week 1 scope
Establish design, interfaces, metric definitions, experiment configuration, result structure, and documentation. Full experiments and final results are later-stage work.
