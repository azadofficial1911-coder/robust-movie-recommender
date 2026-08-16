# Attack and Detection Plan

## 1. Purpose

The Attack and Detection component investigates how synthetic malicious
rating profiles can manipulate the collaborative-filtering movie
recommendation system.

The project focuses on two push-type shilling attacks:

- Random Push Attack
- Average Push Attack

The attack module will generate controlled fake-user profiles and inject
them into the recommendation training data. The detection module will later
analyse user-rating behaviour to identify suspicious profiles.

---

## 2. System Boundary

The attack targets the rating data used by the recommender.

It does not attack the Django website or any real commercial system.

The planned process is:

Clean MovieLens Ratings  
→ Synthetic Fake Profiles  
→ Attacked Training Dataset  
→ Collaborative Recommender  
→ Changed Recommendation Results

All experiments will be performed in a controlled offline environment.

---

## 3. Random Push Attack

In a Random Push Attack, synthetic users attempt to promote a selected
target movie.

Each fake profile will:

1. Rate the target movie with the maximum push rating of 5.
2. Select a set of non-target movies as filler items.
3. Generate filler ratings around the global average rating of the genuine
   MovieLens dataset.

The current processed dataset provides the genuine rating information
required for this attack.

### Required Inputs

- `ratings_clean.csv`
- global average rating
- target movie ID
- attack size
- filler size
- target rating
- random seed

### Planned Output

Synthetic fake ratings compatible with the recommender's normal rating
format.

---

## 4. Average Push Attack

In an Average Push Attack, each synthetic user also gives the selected
target movie the maximum rating of 5.

However, filler ratings are generated around the genuine average rating of
each individual filler movie rather than around one global rating mean.

### Required Inputs

- `ratings_clean.csv`
- `movie_statistics.csv`
- target movie ID
- attack size
- filler size
- target rating
- random seed

`movie_statistics.csv` provides rating counts and mean ratings for movies
and will be used when generating Average Push filler ratings.

---

## 5. Attack Parameters

### 5.1 Target Movie

The target movie is the item that the attacker attempts to promote.

The final target-movie selection will be made after considering movie
rating counts, average ratings and supervisor feedback.

The target movie is therefore not hard-coded during Week 1.

### 5.2 Attack Size

Attack size represents the number of synthetic fake users relative to the
number of genuine users.

Attack Size (%) = Fake Users / Genuine Users × 100

The final attack-size values will be confirmed before the main experiments.

### 5.3 Filler Size

Filler size controls how many additional non-target movies each synthetic
profile rates.

The final filler-size values will be confirmed during experiment design.

### 5.4 Target Rating

The planned target rating for push attacks is:

5 stars

This represents the maximum rating in the MovieLens rating scale.

### 5.5 Random Seed

A fixed random seed will be used so that experiments can be reproduced.

The current default value is:

42

Using the same data, attack configuration and random seed should reproduce
the same synthetic attack.

---

## 6. Fake User ID Strategy

Synthetic users must never reuse genuine MovieLens user IDs.

The fake-user ID sequence will begin after the highest genuine user ID.

Conceptually:

maximum genuine user ID + 1  
maximum genuine user ID + 2  
maximum genuine user ID + 3

The final implementation will calculate these IDs automatically.

---

## 7. Fake Profile Format

Synthetic fake ratings will remain compatible with the recommender's normal
rating format.

Planned fields:

- `user_id`
- `movie_id`
- `rating`
- `timestamp`

Generated fake profiles will be stored under:

`data/attacked/fake_profiles/`

The original clean ratings dataset must never be overwritten.

---

## 8. Ground-Truth Labels

Because the project generates the synthetic attackers itself, the real
identity of each fake user is known.

Ground-truth information will be stored separately from the recommender
training data.

Planned fields:

- `user_id`
- `true_label`
- `attack_type`
- `target_movie_id`

Possible true labels:

- `genuine`
- `fake`

Ground-truth labels will later allow the detector's predictions to be
evaluated objectively.

---

## 9. Attacked Dataset

The attacked training dataset will be produced by combining:

Clean Ratings  
+ Synthetic Fake Ratings  
= Attacked Ratings

The recommender-compatible attacked dataset will retain the standard fields:

- `user_id`
- `movie_id`
- `rating`
- `timestamp`

Attacked datasets will be stored under:

`data/attacked/attacked_datasets/`

Experimental labels and metadata will remain separate from recommender
training data where possible.

---

## 10. Detection Plan

The suspicious-user detector will analyse user-rating behaviour.

The planned detection flow is:

User Rating History  
→ Behavioural Features  
→ Suspicion Score  
→ Classification Threshold  
→ Genuine or Suspicious

The current Week 1 implementation defines the interface for this process.

The final detection method will be selected after evaluating candidate
features and receiving supervisor feedback.

---

## 11. Candidate Detection Features

The current candidate feature categories are:

- rating deviation
- profile size
- extreme-rating ratio
- profile similarity
- target-item behaviour
- filler-pattern behaviour

These are candidate features only.

The final detector will use only features that are justified by the project
methodology and supported by later testing.

A more detailed feature plan is maintained in:

`docs/detection_feature_plan.md`

---

## 12. Suspicion Score

The planned detector will produce a normalised suspicion score.

Current interface range:

0.0 to 1.0

Conceptually:

- lower score = lower suspicion
- higher score = higher suspicion

The Week 1 service currently uses a default classification threshold of
0.5 for interface testing only.

This value is not considered the final experimental threshold.

---

## 13. Detection Output

The standard detection result contains:

- `user_id`
- `suspicion_score`
- `predicted_label`
- `true_label`

Possible predicted labels:

- `genuine`
- `suspicious`

Possible ground-truth labels:

- `genuine`
- `fake`

This separation allows predicted behaviour to be compared with known
experimental ground truth.

---

## 14. Detection Evaluation

Because fake-user identities are known, later detection experiments can
calculate:

- True Positives
- False Positives
- True Negatives
- False Negatives
- Precision
- Recall
- F1-score
- False Positive Rate
- Confusion Matrix

A false positive occurs when a genuine user is incorrectly classified as
suspicious.

False positives are important because removing genuine users during defence
could negatively affect recommendation quality.

---

## 15. Inputs From Member 2

The Attack and Detection module receives processed recommendation data from
the Dataset and Recommender component.

Current required inputs include:

- `data/processed/ratings_clean.csv`
- `data/processed/movie_statistics.csv`
- global average rating
- movie rating counts
- movie mean ratings

These inputs are now available in the shared repository.

---

## 16. Outputs for Member 4

The Attack and Detection component will later provide the Defence and
Evaluation component with:

- attacked dataset
- fake-user ground-truth labels
- detection results
- attack configuration
- suspicion scores
- predicted suspicious-user labels

These outputs will support Clean vs Attacked vs Defended experiments.

---

## 17. Website Integration

The attack and detection algorithms remain inside the research service
layer.

Current backend locations:

`apps/research/services/attacks.py`

`apps/research/services/detection.py`

The Django frontend should display results but should not contain the
attack or detection mathematics.

The future Attack Lab interface may provide:

- attack type
- target movie
- attack size
- filler size
- random seed

The future Detection interface may display:

- number of users analysed
- suspicious users detected
- user ID
- suspicion score
- predicted classification

---

## 18. Reproducibility

Attack generation will use explicit configuration values and a fixed random
seed.

Experiment settings are stored under:

`experiments/configs/`

The Week 1 configuration file is:

`experiments/configs/attack_config.json`

The objective is that the same:

- clean dataset
- attack parameters
- random seed

should reproduce the same synthetic attack.

---

## 19. Week 1 Implementation Status

The Week 1 Attack and Detection foundation currently includes:

- attack-data folder structure
- attack configuration structure
- Random Push interface
- Average Push interface
- attack configuration validation
- fake-user count calculation
- suspicious-user detection interface
- suspicion-score validation
- classification interface
- detection-result structure
- candidate detection feature definitions
- integration requirements

Full synthetic attack generation and the final suspicious-user detector
will be implemented during the later implementation and experiment stages.

---

## 20. Attack Validation and Test Plan

Before attack results are used in experiments, the generated synthetic
profiles must pass a set of validation checks.

### 20.1 Random Push Validation

The Random Push implementation must verify that:

- the correct number of fake users is generated;
- every fake user has a unique user ID;
- fake-user IDs do not overlap with genuine MovieLens user IDs;
- every fake profile contains the selected target movie;
- the target movie receives the maximum push rating of 5;
- filler items are valid MovieLens movie IDs;
- the target movie is not accidentally selected as a filler item;
- the number of filler items matches the selected filler-size setting;
- all generated ratings remain within the valid rating range of 1 to 5;
- filler ratings follow the planned global-average rating logic;
- the original clean ratings dataset is never overwritten;
- generated fake profiles are stored separately from clean data;
- the same random seed and configuration reproduce the same attack.

### 20.2 Average Push Validation

The Average Push implementation must satisfy the same structural checks as
Random Push.

In addition, it must verify that:

- each filler rating is generated using the genuine mean rating of the
  selected filler movie;
- the per-movie statistics come from the processed genuine MovieLens data;
- filler generation does not use the global mean where an item-specific
  mean is required.

### 20.3 Ground-Truth Validation

The generated fake-user labels must verify that:

- every synthetic fake user has a ground-truth label;
- every fake-user ID in the attacked dataset appears in the fake-user label
  file;
- genuine users are not incorrectly labelled as fake;
- the attack type is recorded for each synthetic user;
- the target movie ID is recorded for the attack experiment.

### 20.4 Detection Interface Validation

Before the final detector is implemented, the current detection interface
must verify that:

- suspicion scores are restricted to the range 0.0 to 1.0;
- invalid suspicion scores raise an error;
- classification thresholds are restricted to the range 0.0 to 1.0;
- invalid thresholds raise an error;
- scores at or above the threshold are classified as suspicious;
- scores below the threshold are classified as genuine;
- detection results use the agreed standard output structure.

### 20.5 Integration Validation

Before Member 4 uses the attack and detection outputs, the project must
verify that:

- the attacked dataset remains compatible with the recommender;
- fake-user labels remain separate from recommender training fields;
- attack configuration is saved with the experiment;
- detection results include the user ID, suspicion score and predicted
  label;
- the clean dataset remains unchanged and available as the experiment
  baseline.