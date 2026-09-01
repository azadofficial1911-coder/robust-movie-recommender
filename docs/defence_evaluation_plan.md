# Defence & Evaluation Plan

## 1. Purpose
Define the defence and Clean vs Attacked vs Defended evaluation framework.

## 2. Clean condition
Original genuine training data -> recommender -> clean results. Use the fixed genuine test set.

## 3. Attacked condition
Genuine training data + synthetic attack profiles -> recommender -> attacked results.

## 4. Defended condition
Attacked data -> detection results -> defence -> defended data -> recommender -> defended results. Reuse the same genuine test set.

## 5. Defence strategy A
Remove complete profiles whose detector `predicted_label == suspicious`. Do not use `true_label` for the defence decision. Keep the original attacked data unchanged and record removed user/rating counts.

## 6. Optional defence strategy B
Reduce suspicious-user influence using a lower weight. Final weights must be justified experimentally and this method must not delay the primary removal defence.

## 7. Recommendation metrics
RMSE, MAE, Precision@K, Recall@K.

## 8. Attack-impact metrics
Target rank, target predicted score/prediction shift, hit rate.

## 9. Detection metrics
TP, FP, TN, FN, Precision, Recall, F1, False Positive Rate, Confusion Matrix. False positives matter because genuine profiles may be removed.

## 10. Experiment result structure
Preserve experiment ID, attack type, attack size, filler size, target movie, target rating, random seed, detector threshold, defence method and Top-K.

## 11. Graph plan
1. Clean vs Attacked vs Defended
2. Target Movie Rank
3. Attack Size vs Target Rank
4. Random vs Average
5. Detection Performance
6. Confusion Matrix

## 12. Table plan
Recommendation: RMSE, MAE, Precision@K, Recall@K.
Attack: target rank, target score, hit rate.
Detection: Precision, Recall, F1, False Positive Rate.
No results are entered during Week 1.

## 13. Website integration
Future Defence Centre: suspicious profiles, defence method, profiles affected, target rank before/after, RMSE before/after.
Future Evaluation Dashboard: Clean/Attacked/Defended, RMSE, MAE, Precision@10, Recall@10, target rank, hit rate and graphs.

## 14. Report integration
Methodology explains defence/metrics/conditions; Results presents real numbers/tables/graphs; Discussion explains attack impact, defence effectiveness, trade-offs, false positives and limitations.

## 15. Limitations
Detector errors may remove genuine users. Defence may reduce attack impact without returning exactly to the clean baseline. Final conclusions require real controlled experiments.
