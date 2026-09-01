# RMRS Capstone — Week 6 Member 3 Handover
## Attack & Detection

> **Member 3 scope:** Synthetic shilling attack generation, attack-effect validation, suspicious-user detection, and handover outputs for defence/evaluation and website integration.

---

## 1. Status

**Week 6 Attack & Detection pipeline: Complete for pilot execution**

Implemented:

- Reproducible **Random Push** attack generation
- Reproducible **Average Push** attack generation
- Synthetic fake-user profile generation
- Attacked training datasets
- Ground-truth genuine/suspicious labels
- Clean vs attacked recommender comparison
- Initial explainable suspicious-user detector
- Detection result export
- Detection metric summary
- Automated attack and detection tests

---

## 2. Pilot Configuration

| Parameter | Value |
|---|---:|
| Target movie ID | **758** |
| Attack objective | **Push** |
| Attack size | **5%** |
| Genuine users | **943** |
| Synthetic users | **47** |
| Filler size | **5%** |
| Filler movies per attacker | **84** |
| Ratings per fake profile | **85** |
| Target rating | **5** |
| Random seed | **42** |
| Detection threshold | **0.5** |

### Configuration files

```text
experiments/configs/attack_config.json
experiments/configs/detection_config.json
```

---

## 3. Attack Outputs

### Random Push

```text
data/attacked/fake_profiles/random_pilot.csv
data/attacked/attacked_datasets/random_pilot.csv
data/attacked/labels/random_pilot_labels.csv
```

### Average Push

```text
data/attacked/fake_profiles/average_pilot.csv
data/attacked/attacked_datasets/average_pilot.csv
data/attacked/labels/average_pilot_labels.csv
```

### Schemas

**Fake profiles**
```text
user_id,movie_id,rating,attack_type,target_movie_id
```

**Attacked dataset**
```text
user_id,movie_id,rating,timestamp
```

**Ground-truth labels**
```text
user_id,true_label
```

Ground-truth distribution for each scenario:

| Label | Users |
|---|---:|
| genuine | **943** |
| suspicious | **47** |
| **Total** | **990** |

---

## 4. Dataset Integrity

| Check | Result |
|---|---|
| Genuine training rows | **80,029** |
| Synthetic ratings added | **3,995** |
| Total attacked rows | **84,024** |
| Maximum genuine user ID | **943** |
| First synthetic user ID | **944** |
| Final synthetic user ID | **990** |
| Duplicate fake user/movie rows | **0** |
| Rating range | **1–5** |
| Genuine test data modified | **No** |

Synthetic ratings use one deterministic timestamp:

```text
maximum genuine training timestamp + 1
```

---

## 5. Attack-Effect Evaluation

The pilot target was evaluated using genuine users who had Movie **758** held out in the fixed test set and did not have it in their training history.

Evaluation users:

```text
49, 117, 246, 366, 374, 417, 457
```

### Summary

| Condition | Mean Target Score | Mean Target Rank | Median Target Rank | Hit@10 |
|---|---:|---:|---:|---:|
| Clean | **1.9722** | **1127.43** | **1120** | **0.0** |
| Random Push | **3.1083** | **778.86** | **733** | **0.0** |
| Average Push | **3.6731** | **407.57** | **257** | **0.0** |

> **Interpretation:** Lower rank is better. Both attacks increased the target movie's predicted recommendation score and improved its ranking. Average Push produced the stronger pilot effect.

### Result files

```text
results/tables/attack_effect_pilot_per_user.csv
results/tables/attack_effect_pilot_summary.csv
```

---

## 6. Suspicious-User Detector

The initial detector uses explainable behavioural features.

| Feature | Pilot Weight |
|---|---:|
| Rating-deviation behaviour | **20%** |
| Profile-size pattern | **20%** |
| Extreme-rating ratio | **15%** |
| Target-item behaviour | **45%** |

The detector produces:

```text
user_id,suspicion_score,predicted_label,true_label
```

Ground truth is **not** used to calculate the suspicion score. It is attached only after prediction for evaluation.

### Detection outputs

```text
results/tables/random_detection_results.csv
results/tables/average_detection_results.csv
results/tables/detection_metrics_pilot.csv
```

### Pilot detection metrics

| Scenario | TP | FP | TN | FN | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Random Push | **47** | **0** | **943** | **0** | **1.0** | **1.0** | **1.0** | **0.0** |
| Average Push | **47** | **0** | **943** | **0** | **1.0** | **1.0** | **1.0** | **0.0** |

> These values represent **perfect separation in the controlled Week 6 pilot**. They should not be interpreted as universal real-world detection accuracy.

---

# Handover to Member 4 — Achintha

Use the following files for defence and final evaluation.

### Attacked datasets

```text
data/attacked/attacked_datasets/random_pilot.csv
data/attacked/attacked_datasets/average_pilot.csv
```

### Ground-truth labels

```text
data/attacked/labels/random_pilot_labels.csv
data/attacked/labels/average_pilot_labels.csv
```

### Detection outputs

```text
results/tables/random_detection_results.csv
results/tables/average_detection_results.csv
```

### Detection summary

```text
results/tables/detection_metrics_pilot.csv
```

### Attack-effect results

```text
results/tables/attack_effect_pilot_per_user.csv
results/tables/attack_effect_pilot_summary.csv
```

### Recommended Member 4 flow

```text
Attacked dataset
      ↓
Detection output
      ↓
Defence method
      ↓
Defended dataset
      ↓
Clean vs Attacked vs Defended evaluation
```

---

# Handover to Member 1 — Veasna

## Attack Lab display values

### Random Push

| Field | Value |
|---|---|
| Attack type | Random Push |
| Target movie ID | 758 |
| Attack size | 5% |
| Filler size | 5% |
| Fake users generated | 47 |
| Fake ratings generated | 3,995 |
| Status | Completed |

### Average Push

| Field | Value |
|---|---|
| Attack type | Average Push |
| Target movie ID | 758 |
| Attack size | 5% |
| Filler size | 5% |
| Fake users generated | 47 |
| Fake ratings generated | 3,995 |
| Status | Completed |

## Detection display values

| Field | Value |
|---|---:|
| Users analysed | **990** |
| Suspicious users detected | **47** |
| Detection threshold | **0.5** |

Detailed user-level values are available from:

```text
results/tables/random_detection_results.csv
results/tables/average_detection_results.csv
```

Useful columns:

```text
user_id
suspicion_score
predicted_label
true_label
```

---

## 7. Reproducibility

Generate attacked datasets:

```powershell
python experiments/generate_attacked_data.py
```

Run attack-effect evaluation:

```powershell
python experiments/evaluate_attack_effect.py
```

Run suspicious-user detection:

```powershell
python experiments/run_detection.py
```

Run Django validation:

```powershell
python manage.py check
python manage.py test
```

Run Member 3 standalone tests:

```powershell
python -m unittest discover -s tests -v
```

Current Member 3 standalone test result:

```text
17 tests passed
```

---

## 8. Important Integration Rules

1. Synthetic attackers are **research-data users only**.
2. Fake user IDs must **not** become Django authentication accounts.
3. Synthetic profiles must be injected only into the **training condition**.
4. The fixed genuine **test set must remain unchanged**.
5. Ground-truth labels must not be used to calculate suspicion scores.
6. The clean MovieLens files must never be overwritten.

---

## 9. Week 6 Member 3 Completion Summary

```text
Pilot configuration                    ✅
Random Push generator                  ✅
Average Push generator                 ✅
Synthetic fake profiles                ✅
Attacked datasets                      ✅
Ground-truth labels                    ✅
Attack validation                      ✅
Automated attack tests                 ✅
Clean vs attacked recommender test     ✅
Detection feature extraction           ✅
Suspicion scoring                      ✅
Detection classification               ✅
Detection output export                ✅
Detection metrics                      ✅
Member 1 / Member 4 handover           ✅
```

**Next repository action:** final QA, pull-request review, and merge of `feature/week6-attack-detection` into `main`.
