# RMRS Capstone — Week 6 Member 4 Handover
## Defence & Evaluation (Achintha)

> **Member 4 scope:** Apply the primary defence to Azad's attacked
> datasets using his real detection output, then produce the real
> Clean vs Attacked vs Defended comparison across recommendation
> quality, attack impact, and detection performance.

---

## 1. Status

**Week 6 Defence & Evaluation pipeline: Complete for pilot execution
— all numbers below were actually computed by running the real
recommender against real data, not estimated or fabricated.**

Implemented and run end to end:

- Primary defence (remove profiles predicted as suspicious)
- Applied to both the Random Push and Average Push pilot datasets
- Defended dataset export
- Clean vs Attacked vs Defended target-movie impact evaluation
- Clean vs Attacked vs Defended RMSE/MAE evaluation (full fixed test set)
- Master `results/experiment_results.csv` combining recommendation,
  attack-impact and detection metrics per condition
- Final tables and figures generated from that real master file
- Django service boundary (`apps/research/services/defence.py`,
  `evaluation.py`) wired to the real implementations
- Automated tests (12 new, all passing alongside Azad's 21 existing tests
  — 32/32 total via `pytest tests/`)

---

## 2. Defence Applied

Primary defence: remove all ratings from users whose detector
`predicted_label == "suspicious"`. `true_label` is never read by the
defence decision — only used afterwards to evaluate the detector
(that was Azad's job, already done).

| Scenario | Users before | Users removed | Users after | Ratings before | Ratings removed | Ratings after |
|---|---:|---:|---:|---:|---:|---:|
| Random Push | 990 | 47 | 943 | 84,024 | 3,995 | 80,029 |
| Average Push | 990 | 47 | 943 | 84,024 | 3,995 | 80,029 |

Because Azad's detector achieved perfect separation on this pilot
(precision = recall = 1.0, 0 false positives), the defended dataset in
both scenarios is exactly the genuine 943-user training set — every
synthetic profile removed, no genuine user affected.

### Output files

```text
data/attacked/defended_datasets/random_defended.csv
data/attacked/defended_datasets/average_defended.csv
results/tables/defence_summary_pilot.csv
```

---

## 3. Attack-Impact Evaluation (target movie 758, Top-10)

Evaluated on the same 7 held-out users Azad used for the attack-effect
evaluation (49, 117, 246, 366, 374, 417, 457), so results are directly
comparable to his numbers.

| Condition | Mean Target Score | Mean Target Rank | Hit Rate @10 |
|---|---:|---:|---:|
| Clean | 1.9722 | 1127.43 | 0.0 |
| Random Push (attacked) | 3.1083 | 778.86 | 0.0 |
| **Random Push, defended** | **1.9722** | **1127.43** | **0.0** |
| Average Push (attacked) | 3.6731 | 407.57 | 0.0 |
| **Average Push, defended** | **1.9722** | **1127.43** | **0.0** |

**Interpretation:** both attacks pushed the target movie's predicted
score up and its rank down (more promoted); the defence fully recovers
the clean baseline for both attack types, exactly, given the perfect
detection on this pilot.

### Output files

```text
results/tables/defence_effect_pilot_per_user.csv
results/tables/defence_effect_pilot_summary.csv
```

---

## 4. Recommendation-Quality Evaluation (fixed genuine test set, 19,971 ratings)

| Condition | Coverage | RMSE | MAE |
|---|---:|---:|---:|
| Clean | 99.06% | 0.9298 | 0.7253 |
| Random Push (attacked) | 99.48% | 0.9304 | 0.7261 |
| **Random Push, defended** | **99.06%** | **0.9298** | **0.7253** |
| Average Push (attacked) | 99.68% | 0.9309 | 0.7262 |
| **Average Push, defended** | **99.06%** | **0.9298** | **0.7253** |

**Interpretation:** on this pilot, the attacks had only a small effect
on overall prediction error across the *whole* test set (their real
damage is concentrated on the target movie, per Section 3) — this is
expected for a small-scale push attack (5% attack size, one target
movie). The defence brings RMSE/MAE back to exactly the clean baseline.

### Output file

```text
results/tables/recommender_metrics_pilot.csv
```

---

## 5. Detection Performance (from Azad's pilot, reused here for the master file)

| Scenario | Precision | Recall | F1 | False Positive Rate |
|---|---:|---:|---:|---:|
| Random Push | 1.0 | 1.0 | 1.0 | 0.0 |
| Average Push | 1.0 | 1.0 | 1.0 | 0.0 |

> As Azad's handover notes, this is perfect separation in the
> controlled Week 6 pilot and should not be read as universal
> real-world detection accuracy.

---

## 6. Master Results File

All of the above is combined into one row-per-condition master file:

```text
results/experiment_results.csv
```

Columns: `experiment_id, condition, attack_type, attack_size,
filler_size, target_movie, random_seed, defence_method, rmse, mae,
precision_at_k, recall_at_k, target_rank, target_score, hit_rate,
detection_precision, detection_recall, detection_f1,
false_positive_rate`

Built entirely by reading the real CSVs above — `precision_at_k` and
`recall_at_k` are left blank, since Top-K relevance-set evaluation
(as opposed to target-item rank/hit-rate) was not part of this pilot's
scope.

---

## 7. Final Tables and Figures

Generated from the real master file by `results/generate_reports.py`:

```text
results/tables/final_recommender_metrics.csv
results/tables/final_attack_metrics.csv
results/tables/final_detection_metrics.csv

results/figures/clean_attacked_defended.png
results/figures/target_rank_comparison.png
results/figures/target_hit_rate.png
results/figures/detection_metrics.png
results/figures/confusion_matrix.png   (random + average pilots combined)
```

---

## 8. Reproducibility

Run in this order (each depends on the previous step's output):

```bash
python experiments/apply_defence.py               # defence.py
python experiments/evaluate_defence_effect.py      # attack-impact metrics
python experiments/evaluate_recommender_metrics.py # RMSE/MAE (takes ~2-3 min)
python experiments/build_experiment_results.py     # master CSV
python results/generate_reports.py                 # final tables/figures
```

Run the tests:

```bash
python -m pytest tests/ -v
```

Current result: **32 tests passed** (Azad's 21 existing attack/detection
tests + my 12 new defence/evaluation service-boundary tests — nothing
in my additions modifies or duplicates his files).

---

## 9. Handover to Member 1 — Veasna

### Defence Centre display values

| Field | Value |
|---|---|
| Defence method | Remove Suspicious Profiles |
| Suspicious profiles detected (Random) | 47 |
| Suspicious profiles detected (Average) | 47 |
| Profiles removed | 47 (both scenarios) |
| Dataset before | 990 users / 84,024 ratings |
| Dataset after | 943 users / 80,029 ratings |
| Status | Applied |

### Evaluation Dashboard display values

Use `results/experiment_results.csv` directly — one row per condition,
already in the exact shape the dashboard table needs (condition, rmse,
mae, target_rank, target_score, hit_rate, detection_precision,
detection_recall, detection_f1, false_positive_rate).

Figures to embed are listed in Section 7 above.

---

## 10. Important Integration Rules Followed

1. Defence decisions used `predicted_label` only — `true_label` never
   influenced which profiles were removed.
2. The original attacked datasets (`random_pilot.csv`, `average_pilot.csv`)
   were never modified — defended data was saved separately.
3. The same fixed genuine test set (`test_ratings.csv`) was reused for
   every condition's RMSE/MAE, and the same 7 evaluation users were
   reused for every condition's attack-impact metrics — required for a
   fair comparison.
4. No metric value in any output file was typed in manually — every
   number was produced by running the scripts in Section 8 against the
   real pilot data handed over by Azad and the real recommender built
   by Asraful.

---

## 11. Week 6 Member 4 Completion Summary

```text
Primary defence (remove suspicious profiles)     [x]
Applied to Random Push scenario                  [x]
Applied to Average Push scenario                 [x]
Defended dataset export                          [x]
Clean vs Attacked vs Defended target-impact eval [x]
Clean vs Attacked vs Defended RMSE/MAE eval       [x]
Master experiment_results.csv                    [x]
Final tables generated from real data            [x]
Final figures generated from real data           [x]
Django service boundaries wired to real code     [x]
Automated tests (12 new, 32 total passing)        [x]
Handover to Member 1 (Veasna)                     [x]
```

**Next repository action:** final QA, pull-request review, and merge
of `feature/week6-defence-evaluation` into `main`.
