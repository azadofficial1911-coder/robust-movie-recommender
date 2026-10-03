# Robustness Comparison: Defence and Evaluation Evidence

**RMRS · HIT401 Capstone · Group 15**
**Owner:** Achintha (Member 4, Defence and Evaluation)
**Branch:** `feature/robustness-evaluation`

## What this delivers


This branch adds four things to make that true and checkable:

| Added | What it does |
|---|---|
| `experiments/run_robustness_evaluation.py` | One command that rebuilds all defence and evaluation evidence and then verifies it. |
| `experiments/verify_robustness_evidence.py` | 21 checks that re-derive each claim from the data files, plus `results/evidence_manifest.json` with a SHA-256 hash of every input and output. |
| `experiments/evaluate_target_frequency.py` | Target frequency @10, @50 and @100 over a fixed sample of 100 genuine users, as an extra metric alongside Hit@10 (Hit@10 is 0 for every condition when measured on only 7 users). |
| Extended `results/experiment_results.csv` | Still the single source of truth, now with every field the comparison page needs: defence counts, confusion counts, coverage, evaluation users, recommender parameters and target frequency. |

Other changes:
- `results/generate_reports.py` now copies its figures into `static/images/research/` automatically, so the site can't show stale charts. It also draws `target_frequency.png`.
- `results_loader.py` now returns `None` for blank cells instead of `NaN`, so templates show an empty value rather than the text "nan". It also lists the new figure.
- `tests/test_robustness_evidence.py` has 11 tests. Six of them tamper with the evidence and confirm the verifier fails.

No teammate code was changed: not the recommender, the attack generator, the detector, the comparison view or the templates.

## Results (EXP001_PILOT, target movie 758, 5% attack, 5% filler, seed 42)

| Condition | Target rank ↓ | Target score | Target in Top-10 (100 users) | Target in Top-50 | RMSE | MAE | Users removed |
|---|---|---|---|---|---|---|---|
| Clean | 1127.4 | 1.97 | 0% | 0% | 0.9298 | 0.7253 | n/a |
| Random Push, without robustness | 778.9 | 3.11 | 5% | 12% | 0.9304 | 0.7261 | 0 |
| Random Push, with robustness | 1127.4 | 1.97 | 0% | 0% | 0.9298 | 0.7253 | 47 (3,995 ratings) |
| Average Push, without robustness | 407.6 | 3.67 | 11% | 30% | 0.9309 | 0.7262 | 0 |
| Average Push, with robustness | 1127.4 | 1.97 | 0% | 0% | 0.9298 | 0.7253 | 47 (3,995 ratings) |

Detection in both scenarios: TP = 47, FP = 0, TN = 943, FN = 0, so precision, recall and F1 are all 1.0 and the false-positive rate is 0.0.

**Why "with robustness" equals Clean exactly.** The detector found all 47 fake profiles and flagged no genuine users. Removing exactly those users gives back the original training data row for row, which the verifier confirms. So recovery here is complete, and nothing was faked. If the detector misses a profile, the defended results will sit between Clean and Attacked, and the pipeline reports that automatically.

## Verification: what is proven

Run `python experiments/verify_robustness_evidence.py`. Current status: **21 passed, 0 failed.**

| Plan requirement | Check(s) |
|---|---|
| Defence uses predicted labels, never true labels | `defended_equals_attacked_minus_predicted[*]`, `defence_ignores_true_label[*]`. The second one flips every `true_label` and re-runs the defence; the output is identical. |
| Defended datasets don't overwrite attacked datasets | `attacked_dataset_preserved[*]` |
| Same genuine test data for all conditions | `same_genuine_test_set`: all 5 conditions use the same 19,971 test ratings, with no train/test overlap and no fake users in the test set. |
| Same attack on both sides; only the defence differs | `attacked_is_clean_plus_fakes[*]`, `same_attack_setup_across_scenarios` |
| Same evaluation users | `same_evaluation_users[primary]` (7 users), `same_evaluation_users[target_frequency]` (100 users) |
| Same recommender | `master_results_match_sources` checks that `top_k_neighbours` and `min_neighbours` in the results equal the constants in `recommender/baseline_recommender.py`. All scripts import that one module. |
| Numbers trace back to real outputs | `detection_metrics_recompute[*]`, `defence_summary_recompute[*]`, `target_metrics_recompute_from_per_user`, `target_frequency_recompute_from_per_user`, `attack_and_defence_runs_agree`, `master_results_match_sources` (102 values) |
| Graphs come from real result files | `served_figures_match_generated`: the figures Django serves are byte-identical to the generated ones. |

## Field contract for Veasna and Azad

Read **`results/experiment_results.csv`** only, one row per `condition`: `clean`, `random`, `random_defended`, `average`, `average_defended`. The existing `load_experiment_results()` already returns these rows. Blank cells come back as `None`.

For scenario `s` (`random` or `average`):
- `clean` → the `clean` row
- `without_robustness` → the `s` row
- `with_robustness` → the `s_defended` row

| Column | Meaning | Where it comes from |
|---|---|---|
| `condition`, `scenario`, `attack_type` | Row identity. `scenario` is blank for clean. | build script |
| `defence_applied` | `True` only for `*_defended` rows | build script |
| `attack_size`, `filler_size`, `target_movie`, `random_seed` | Fixed attack setup, identical on both sides | `experiments/configs/attack_config.json` |
| `fake_profiles_injected` | Fake users in the attacked data (47) | attack ground-truth labels, used for reporting only |
| `top_k_neighbours`, `min_neighbours` | Recommender parameters (30, 3) | `recommender/baseline_recommender.py` |
| `training_users`, `training_ratings` | Size of the data fed to the recommender | the condition's training CSV |
| `rmse`, `mae`, `coverage_percent`, `total_test_ratings`, `predictions_produced` | Accuracy on the fixed genuine test set | `recommender_metrics_pilot.csv` |
| `target_rank`, `target_score`, `hit_rate`, `median_target_rank`, `evaluation_users`, `predictable_users` | Target movie metrics on the 7 held-out evaluation users. `target_rank` is the mean rank; lower means more promoted. | `defence_effect_pilot_summary.csv` |
| `target_freq_at_10`, `_at_50`, `_at_100`, `target_freq_mean_rank`, `target_freq_median_rank`, `target_freq_sample_users` | Share (0–1) of 100 fixed genuine users with the target in their Top-K | `target_frequency_summary.csv` |
| `detection_precision`, `detection_recall`, `detection_f1`, `false_positive_rate`, `detection_tp`, `_fp`, `_tn`, `_fn`, `detection_threshold` | Detector performance on the scenario's attacked data. Filled on both the attacked and defended rows; use `defence_applied` to show whether it was used. | `detection_metrics_pilot.csv` (Azad) |
| `suspicious_profiles_detected`, `users_removed`, `ratings_removed` | What the defence removed. `users_removed` and `ratings_removed` are 0 on attacked rows; all three are blank on clean, and `suspicious_profiles_detected` is also blank on attacked rows. | `defence_summary_pilot.csv` |

**Suggested for the comparison page (Veasna):** add a "Users with target in Top-10" metric using `target_freq_at_10`. It is the clearest single number for the attack's effect: 0% → 11% → 0% for Average Push. The current Hit@10 card shows 0.00 in every condition, so it doesn't show any change.

**Suggested for `robustness_comparison.py` (Azad):** build the comparison object from these rows only, e.g. `fake_users = row["fake_profiles_injected"]`, `attack_size = row["attack_size"]`. Then every value on the page has one source.

## How to reproduce

```bash
python experiments/run_robustness_evaluation.py                 # full rebuild, ~15 min
python experiments/run_robustness_evaluation.py --skip-target-frequency   # ~4 min, reuses target frequency
python experiments/run_robustness_evaluation.py --verify-only   # seconds
python -m pytest tests/                                        # 43 tests
python manage.py check && python manage.py test
```

If Azad regenerates the attacks or detection (`generate_attacked_data.py`, `run_detection.py`), run the full command again afterwards. The verifier fails until every downstream file matches the new inputs.

Re-running reproduces the committed numbers exactly. RMSE and MAE can differ around the 15th decimal place between machines because of floating-point summation order; the verifier allows for that tolerance.

## Limitations to state in the report

1. **Only 7 primary evaluation users.** They are the genuine users with the target movie held out in the test set. Hit@10 on them is 0 in every condition. Target frequency over 100 users is added as a supporting metric and doesn't replace them.
2. **Target frequency is a separate fixed sample.** It uses 100 genuine users who never rated the target, drawn with seed 42. The sample is identical across all five conditions, so the rule "keep evaluation users constant" still holds. For 1 of the 100 users, the recommender can't produce a prediction for the target under clean or defended data, so the target can't be ranked; that user counts as a miss. Asraful should confirm he is happy with this addition.
3. **Perfect detection at pilot scale.** 5% attack size and 5% filler with a strong target signal make the fake profiles easy to separate. Larger filler sizes or obfuscated attacks would test the defence more realistically.
4. **RMSE and MAE barely move** (+0.0006 to +0.0011). Push attacks target one movie, so overall accuracy stays nearly unchanged. The attack's effect shows in target rank and target frequency.
