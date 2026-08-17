# Suspicious-User Detection Feature Plan

## 1. Purpose

This document records the candidate behavioural features that may be used
to identify suspicious rating profiles in the Robust Movie Recommender
System.

The final detection method has not yet been selected.

The purpose of Week 1 is to define possible features, understand what they
measure, and prepare the structure for later testing.

---

## 2. Detection Concept

The planned detection process is:

User Rating History  
→ Behavioural Feature Calculation  
→ Feature Comparison / Normalisation  
→ Suspicion Score  
→ Classification  
→ Genuine or Suspicious

The detector will analyse user-rating behaviour rather than website
activity.

---

## 3. Candidate Feature 1 — Rating Deviation

### Meaning

Rating deviation measures how much a user's ratings differ from the normal
rating behaviour of the movies they rate.

For example, if a movie normally receives ratings around 3 stars but one
profile consistently rates similar items very differently, this behaviour
may be unusual.

### Why It May Help

Synthetic attack profiles may produce rating patterns that differ from
genuine users because their ratings are generated according to an attack
strategy.

### Status

Candidate feature.

The exact calculation method will be selected later.

---

## 4. Candidate Feature 2 — Profile Size

### Meaning

Profile size represents the number of movies rated by a user.

Conceptually:

Profile Size = Number of ratings submitted by the user

### Why It May Help

Synthetic profiles may have rating counts that differ from normal user
behaviour, particularly when filler size is controlled by the attack
generator.

### Limitation

A genuine user may naturally have a very small or very large profile.

Therefore profile size should not automatically be treated as proof of an
attack.

### Status

Candidate feature.

---

## 5. Candidate Feature 3 — Extreme-Rating Ratio

### Meaning

This feature examines the proportion of ratings at the extreme ends of the
rating scale.

Examples include:

- 1-star ratings
- 5-star ratings

### Why It May Help

Push attacks deliberately assign the target movie a very high rating.

If a profile contains an unusual proportion of extreme ratings, this may
contribute to its suspicion score.

### Limitation

Some genuine users may naturally give many high or low ratings.

### Status

Candidate feature.

---

## 6. Candidate Feature 4 — Profile Similarity

### Meaning

Profile similarity examines whether several users display unusually similar
rating patterns.

### Why It May Help

Synthetic users produced by the same attack generator may:

- rate similar filler items;
- give similar filler ratings;
- promote the same target movie;
- have similar profile sizes.

This may make fake profiles more similar to one another than normal users.

### Limitation

Genuine users with similar movie interests may also have similar profiles.

### Status

Candidate feature.

---

## 7. Candidate Feature 5 — Target-Item Behaviour

### Meaning

This feature examines user behaviour around a selected attack target.

For example, several suspicious profiles may all:

Target Movie → Rating 5

### Why It May Help

Both Random Push and Average Push attacks attempt to promote the same target
movie using the maximum rating.

A concentration of unusual profiles giving the same target movie very high
ratings may provide useful evidence.

### Limitation

A genuinely popular movie may naturally receive many 5-star ratings.

Therefore target-item behaviour should be combined with other behavioural
information.

### Status

Candidate feature.

---

## 8. Candidate Feature 6 — Filler-Pattern Behaviour

### Meaning

This feature examines how a user's non-target filler ratings are
distributed.

### Why It May Help

Random Push and Average Push attacks use specific statistical rules for
generating filler ratings.

Random Push filler ratings are planned around the global rating average.

Average Push filler ratings are planned around individual movie averages.

These generated patterns may differ from genuine human rating behaviour.

### Status

Candidate feature.

---

## 9. Proposed Feature Summary

| Feature | Main Behaviour Examined | Status |
|---|---|---|
| Rating deviation | Difference from normal rating behaviour | Candidate |
| Profile size | Number of ratings submitted | Candidate |
| Extreme-rating ratio | Frequency of 1-star and 5-star ratings | Candidate |
| Profile similarity | Similar behaviour between users | Candidate |
| Target-item behaviour | Behaviour around the attack target | Candidate |
| Filler-pattern behaviour | Distribution of filler ratings | Candidate |

---

## 10. Suspicion Score

The planned detector will eventually combine approved behavioural evidence
into a suspicion score.

The current service interface uses a normalised range:

0.0 to 1.0

Conceptually:

0.0 = very low suspicion  
1.0 = very high suspicion

The exact scoring formula has not yet been selected.

---

## 11. Classification

The current Week 1 interface supports:

- `genuine`
- `suspicious`

A temporary threshold of 0.5 is used in the service code for interface
testing only.

This threshold is not considered the final detection threshold.

The final threshold will be selected during implementation and evaluation.

---

## 12. Ground Truth

The project generates its own synthetic fake users.

This means the experiment can maintain known labels:

- genuine
- fake

The detector produces predictions:

- genuine
- suspicious

These can later be compared to measure detection performance.

---

## 13. Detection Evaluation

The planned evaluation metrics include:

- True Positive
- False Positive
- True Negative
- False Negative
- Precision
- Recall
- F1-score
- False Positive Rate
- Confusion Matrix

These metrics will help determine whether the detector identifies fake users
while avoiding incorrect classification of genuine users.

---

## 14. False Positive Risk

A false positive occurs when:

Genuine User  
→ Detector  
→ Incorrectly Classified as Suspicious

This is important because a later defence system may remove or reduce the
influence of detected suspicious users.

If genuine users are incorrectly detected, recommendation quality may be
negatively affected.

---

## 15. Week 1 Decision

The features listed in this document are candidate features only.

The final feature set will be selected after:

1. inspecting the genuine MovieLens rating behaviour;
2. generating Random Push and Average Push profiles;
3. comparing fake and genuine behaviour;
4. reviewing the project literature;
5. receiving supervisor feedback.

The final detection algorithm will be implemented during a later development
stage.