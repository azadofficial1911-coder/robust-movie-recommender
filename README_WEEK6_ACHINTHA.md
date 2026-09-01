# Week 6 — Defence & Evaluation, real completed run (Achintha, Member 4)

This isn't a stub or a design doc — every number in here was produced by
actually running the real recommender (Asraful's baseline collaborative
filter) against the real attacked datasets and real detection output
(Azad's pilot handover). See `docs/WEEK6_MEMBER4_HANDOVER.md` for the
full write-up and results tables.

## Where each file goes in your repo

```
apps/research/services/defence.py         -> REPLACES the stub (real implementation)
apps/research/services/evaluation.py      -> REPLACES the stub (real implementation)

experiments/apply_defence.py              -> NEW (applies defence to both pilots)
experiments/evaluate_defence_effect.py    -> NEW (Clean vs Attacked vs Defended, target impact)
experiments/evaluate_recommender_metrics.py -> NEW (Clean vs Attacked vs Defended, RMSE/MAE)
experiments/build_experiment_results.py   -> NEW (builds the master experiment_results.csv)

results/generate_reports.py               -> NEW (final tables + figures from real data)

data/attacked/defended_datasets/random_defended.csv    -> NEW (real output)
data/attacked/defended_datasets/average_defended.csv   -> NEW (real output)

results/tables/defence_summary_pilot.csv               -> NEW (real output)
results/tables/defence_effect_pilot_per_user.csv       -> NEW (real output)
results/tables/defence_effect_pilot_summary.csv        -> NEW (real output)
results/tables/recommender_metrics_pilot.csv           -> NEW (real output)
results/tables/final_recommender_metrics.csv           -> NEW (real output)
results/tables/final_attack_metrics.csv                -> NEW (real output)
results/tables/final_detection_metrics.csv             -> NEW (real output)
results/experiment_results.csv                         -> NEW (the master file)

results/figures/clean_attacked_defended.png            -> NEW (real chart)
results/figures/target_rank_comparison.png             -> NEW (real chart)
results/figures/target_hit_rate.png                    -> NEW (real chart)
results/figures/detection_metrics.png                  -> NEW (real chart)
results/figures/confusion_matrix.png                   -> NEW (real chart)

tests/test_member4_service_boundaries.py  -> NEW (12 tests, does not touch
                                              Azad's existing test_defence_evaluation.py,
                                              test_attack_generation.py, or test_detection.py)

docs/WEEK6_MEMBER4_HANDOVER.md            -> NEW (full write-up, mirrors
                                              Azad's WEEK6_MEMBER3_HANDOVER.md)
```

## The headline result

Because Azad's detector achieved perfect separation on this pilot
(precision = recall = 1.0, zero false positives), the defence fully
recovers Clean baseline performance in both attack scenarios — exactly,
not approximately:

| Condition | RMSE | Target Rank | Target Score |
|---|---:|---:|---:|
| Clean | 0.9298 | 1127.4 | 1.97 |
| Random Push (attacked) | 0.9304 | 778.9 | 3.11 |
| Random Push (defended) | 0.9298 | 1127.4 | 1.97 |
| Average Push (attacked) | 0.9309 | 407.6 | 3.67 |
| Average Push (defended) | 0.9298 | 1127.4 | 1.97 |

Full detail, methodology, and every result table/figure are in
`docs/WEEK6_MEMBER4_HANDOVER.md`.

## Order to run things (if you want to reproduce or extend)

```bash
python experiments/apply_defence.py
python experiments/evaluate_defence_effect.py
python experiments/evaluate_recommender_metrics.py   # ~2-3 minutes
python experiments/build_experiment_results.py
python results/generate_reports.py
python -m pytest tests/ -v                            # 32 tests, all passing
```

## requirements.txt fix included

Your current `requirements.txt` only lists `Django` — but
`recommender/baseline_recommender.py`, `apps/recommendations/services/recommender.py`,
`defence/`, and `evaluation/` all import `pandas`, `numpy`, `matplotlib`
and `scikit-learn`, none of which were listed. This would block anyone
from running `pip install -r requirements.txt` and then any of these
scripts. The `requirements.txt` in this deliverable adds the missing four
packages — replace your existing file with it.
