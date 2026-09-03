# RMRS Capstone — Week 6 Member 1 Handover
## Django User Platform, Research Lab & Integration Layer

> **Member 1 scope — Veasna:** Build and prepare the Django user-facing platform, persistent user-specific movie interactions, staff-only Research Lab access, and stable presentation/integration boundaries for the recommender, Attack, Detection, Defence, and Evaluation modules.

---

## 1. Status

**Week 6 Member 1 scope: Complete**

Implemented, tested, and merged into `main`:

- User authentication flow
- Persistent user-specific movie ratings
- My Ratings
- My List / watchlist
- Movie Detail and rating functionality
- First-time movie-preference onboarding
- Streaming-style home experience
- Staff-only Research Lab access
- Attack integration interface
- Detection integration interface
- Defence integration interface
- Evaluation integration interface
- Recommender integration boundary
- Role-based separation between normal users and research/staff users
- Automated Django validation and tests

The Django presentation layer intentionally does **not** fabricate recommendation, attack, detection, defence, or evaluation results.

---

## 2. Week 6 Responsibility Boundary

Member 1 is responsible for the **Django presentation and integration layer**.

The underlying research algorithms remain the responsibility of the relevant backend/research team members.

```text
Django Website / Member 1
        ↓
Presentation + Integration Layer
        ↓
------------------------------------------------
Recommender  → backend recommender implementation
Attack       → backend attack implementation
Detection    → backend detection implementation
Defence      → backend defence implementation
Evaluation   → backend evaluation implementation
------------------------------------------------
```

Member 1 does not duplicate the backend algorithms.

---

## 3. Authentication

Implemented:

- [x] Signup
- [x] Login
- [x] Logout
- [x] Authentication-aware navigation
- [x] Protected-page access
- [x] Unauthenticated-user redirects
- [x] Separation between normal users and staff users

### Account roles

```text
Normal User
is_staff = False
is_superuser = False
        ↓
Home
Browse
Recommendations
My Ratings
My List
        ↓
No Research Lab
```

```text
Staff / Research User
is_staff = True
is_superuser = False
        ↓
Normal RMRS features
        +
Research Lab
        ↓
Attack
Detection
Defence
Evaluation
```

```text
Superuser / Administrator
is_staff = True
is_superuser = True
        ↓
Normal RMRS features
        +
Research Lab
        +
Django Administration
```

---

## 4. Research Lab Account Access

The Research Lab is intentionally restricted to authorised Django staff users.

### Important rules

- Normal user accounts do not display the Research Lab navigation option.
- Backend/research team members do **not** need to be superusers to develop their algorithms.
- To test backend integration through the Research Lab web interface, a developer needs a local account with:

```text
is_staff = True
```

- A Django superuser can also access the Research Lab because a superuser automatically has:

```text
is_staff = True
is_superuser = True
```

- Full superuser access is only necessary when Django administration access is required.

### Fresh clone / fresh local database

A fresh clone may use a fresh local database, so previous local users may not exist.

To create a local superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts:

```text
Username
Email address
Password
Password again
```

Successful creation:

```text
Superuser created successfully.
```

A local staff/superuser account normally needs to be created only once per local database.

Restarting Django, closing Terminal, or restarting the computer does not normally remove the account.

---

## 5. Persistent Movie Ratings

Implemented:

- [x] Persistent `WebsiteRating` model
- [x] Ratings stored per authenticated user
- [x] Rating from Movie Detail page
- [x] Existing rating update
- [x] No duplicate active rating for the same user/movie
- [x] My Ratings page
- [x] User-specific saved ratings
- [x] First-time 10+ movie preference/onboarding workflow

### Rating behaviour

```text
Open Movie Detail
      ↓
Select rating 1–5
      ↓
Save rating
      ↓
Rating stored for that user
      ↓
View/update from My Ratings / Movie Detail
```

---

## 6. Movie Detail and My List

Implemented:

- [x] Movie Detail page
- [x] Movie information display
- [x] Rating form
- [x] Existing saved-rating display
- [x] Add to My List
- [x] Remove from My List
- [x] My List page
- [x] My Ratings and My List navigation

---

## 7. User Experience

Implemented:

- [x] Streaming-style Home page
- [x] Featured Movie section
- [x] Recommended For You area prepared for real recommender output
- [x] Movie-category rows
- [x] Horizontal scrolling
- [x] Hidden horizontal scrollbar while preserving scrolling
- [x] Movie-poster cache handling
- [x] Removal of outdated visible Week 1 poster wording
- [x] User dropdown
- [x] Desktop layout check

Normal navigation:

```text
Home
Browse
Recommendations
My Ratings
My List
User ▼
```

Staff users additionally receive access to:

```text
Research Lab
```

---

## 8. Research Lab

Implemented:

- [x] Staff-only Research Lab
- [x] Research Lab hidden from normal users
- [x] Direct Research Lab access protected
- [x] Attack interface
- [x] Detection interface
- [x] Defence interface
- [x] Evaluation interface

Research Lab structure:

```text
Research Lab
│
├── Attack Lab
├── Detection
├── Defence
└── Evaluation
```

---

## 9. Attack Integration Interface

Prepared in Django:

- [x] Attack Type
- [x] Target Movie
- [x] Attack Size (%)
- [x] Filler Size (%)
- [x] Random Seed
- [x] Configuration validation
- [x] Backend integration boundary
- [x] No fabricated attack results

### Member 3 handover values

#### Random Push

| Field | Value |
|---|---|
| Attack type | Random Push |
| Target movie ID | 758 |
| Attack size | 5% |
| Filler size | 5% |
| Fake users generated | 47 |
| Fake ratings generated | 3,995 |
| Status | Completed |

#### Average Push

| Field | Value |
|---|---|
| Attack type | Average Push |
| Target movie ID | 758 |
| Attack size | 5% |
| Filler size | 5% |
| Fake users generated | 47 |
| Fake ratings generated | 3,995 |
| Status | Completed |

### Member 3 attack outputs

```text
data/attacked/fake_profiles/random_pilot.csv
data/attacked/fake_profiles/average_pilot.csv

data/attacked/attacked_datasets/random_pilot.csv
data/attacked/attacked_datasets/average_pilot.csv

data/attacked/labels/random_pilot_labels.csv
data/attacked/labels/average_pilot_labels.csv

results/tables/attack_effect_pilot_per_user.csv
results/tables/attack_effect_pilot_summary.csv
```

---

## 10. Detection Integration Interface

Prepared in Django:

- [x] Suspicion Threshold input
- [x] Detection setup validation
- [x] Candidate behavioural-feature presentation
- [x] Backend integration boundary
- [x] No fabricated suspicious-user results

### Candidate behavioural features

```text
Rating_Deviation
Profile_Size
Extreme_Rating_Ratio
Profile_Similarity
Target_Item_Behaviour
Filler_Pattern_Behaviour
```

### Member 3 detection display values

| Field | Value |
|---|---:|
| Users analysed | 990 |
| Suspicious users detected | 47 |
| Detection threshold | 0.5 |

Detailed detection results:

```text
results/tables/random_detection_results.csv
results/tables/average_detection_results.csv
results/tables/detection_metrics_pilot.csv
```

Useful columns:

```text
user_id
suspicion_score
predicted_label
true_label
```

---

## 11. Defence Integration Interface

Prepared in Django:

- [x] Defence workflow/pipeline presentation
- [x] Defence backend integration boundary
- [x] No fabricated defence results

### Member 4 defence handover values

| Field | Value |
|---|---|
| Defence method | Remove Suspicious Profiles |
| Suspicious profiles detected — Random | 47 |
| Suspicious profiles detected — Average | 47 |
| Profiles removed | 47 in each scenario |
| Dataset before | 990 users / 84,024 ratings |
| Dataset after | 943 users / 80,029 ratings |
| Status | Applied |

### Member 4 defence outputs

```text
data/attacked/defended_datasets/random_defended.csv
data/attacked/defended_datasets/average_defended.csv

results/tables/defence_summary_pilot.csv
results/tables/defence_effect_pilot_per_user.csv
results/tables/defence_effect_pilot_summary.csv
```

---

## 12. Evaluation Integration Interface

Prepared in Django:

- [x] Clean / Attacked / Defended comparison structure
- [x] RMSE display location
- [x] MAE display location
- [x] Evaluation backend integration boundary
- [x] No fabricated evaluation metrics

### Member 4 master results file

Use:

```text
results/experiment_results.csv
```

Important dashboard fields include:

```text
condition
rmse
mae
target_rank
target_score
hit_rate
detection_precision
detection_recall
detection_f1
false_positive_rate
```

### Member 4 generated tables

```text
results/tables/final_recommender_metrics.csv
results/tables/final_attack_metrics.csv
results/tables/final_detection_metrics.csv
```

### Member 4 generated figures

```text
results/figures/clean_attacked_defended.png
results/figures/target_rank_comparison.png
results/figures/target_hit_rate.png
results/figures/detection_metrics.png
results/figures/confusion_matrix.png
```

---

## 13. Recommender Integration Boundary

The Django presentation layer includes a stable integration boundary for the real recommender.

Expected recommendation output shape:

```text
movie_id
title
predicted_rating
```

Rules:

- [x] No fake predicted scores are hard-coded.
- [x] Django presentation remains separate from the recommender implementation.
- [x] Real recommender output can be connected through the integration layer.

---

## 14. Important Integration Rules

1. Member 1 owns the Django presentation/integration layer, not the backend research algorithms.
2. Synthetic attackers are research-data users only.
3. Fake attack users must not become Django authentication accounts.
4. Attack, Detection, Defence, and Evaluation backend outputs should be read from the real team-generated files/services.
5. No fabricated research metrics should be displayed.
6. Research Lab access is role-based and requires `is_staff = True`.
7. Normal users must remain separated from staff/research functionality.
8. Django admin/superuser access is not required for ordinary backend algorithm development.
9. A superuser is suitable for local administration and Research Lab integration testing.
10. Clean research datasets must not be overwritten during website integration.

---

## 15. Local Development Environment

Verified local setup:

```text
Python 3.12.10
Django 4.2.30
```

Activate the RMRS environment:

```bash
cd ~/Desktop/HIT401_Capstone/robust-movie-recommender
source ../rmrs_env/bin/activate
```

Confirm versions:

```bash
python --version
python -m django --version
```

Expected:

```text
Python 3.12.10
4.2.30
```

---

## 16. Django Verification

Apply migrations:

```bash
python manage.py migrate
```

Run system check:

```bash
python manage.py check
```

Run automated tests:

```bash
python manage.py test
```

Verified Member 1 result:

```text
Found 14 test(s).
...
Ran 14 tests in ...

OK
```

Week 6 Member 1 verification:

```text
Django system check       ✅
14 automated tests        ✅
Main web pages tested     ✅
Movie rating tested       ✅
My Ratings tested         ✅
My List tested            ✅
Research Lab tested       ✅
Staff access tested       ✅
Normal-user protection    ✅
Attack interface tested   ✅
Detection tested          ✅
Defence tested            ✅
Evaluation tested         ✅
Merged into main          ✅
```

---

## 17. Launch the Website

Start Django:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Recommended manual checks:

```text
Sign Up
Login
Logout
Home
Browse
Movie Detail
Rating
My Ratings
My List
Recommendations
Research Lab — staff/admin only
```

Django admin, if required:

```text
http://127.0.0.1:8000/admin/
```

---

## 18. Fresh Clone / Team Setup Reminder

After a fresh clone:

```bash
cd ~/Desktop/HIT401_Capstone
python3.12 -m venv rmrs_env
source rmrs_env/bin/activate

git clone https://github.com/azadofficial1911-coder/robust-movie-recommender.git
cd robust-movie-recommender

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

If Research Lab testing is required and the fresh local database has no staff account:

```bash
python manage.py createsuperuser
```

---

## 19. Remaining Integration / Verification

The following work should be completed when the corresponding backend branches/results are available in `main`:

- [ ] Connect the real recommender output to the recommendation presentation layer.
- [ ] Connect Member 3 real Attack outputs to the Attack Lab.
- [ ] Connect Member 3 real Detection outputs to the Detection interface.
- [ ] Connect Member 4 real Defence outputs to the Defence interface.
- [ ] Connect Member 4 real Evaluation outputs to the Evaluation dashboard.
- [ ] Embed approved real evaluation figures where appropriate.
- [ ] Run full end-to-end Clean → Attacked → Detected → Defended → Evaluated workflow.
- [ ] Retest Research Lab with a staff/superuser account after backend integration.
- [ ] Confirm Research Lab remains hidden and protected for normal users.
- [ ] Re-run Django and project-level automated tests after integration.
- [ ] Mobile/small-screen layout manually checked if required.

---

## 20. Handover Dependencies

### From Member 3 — Attack & Detection

Member 1 should consume:

```text
Attacked datasets
Ground-truth labels
Attack-effect summaries
Detection results
Detection metric summaries
```

Member 3 backend algorithms remain Member 3 responsibility.

### From Member 4 — Defence & Evaluation

Member 1 should consume:

```text
Defended datasets
Defence summaries
Clean / Attacked / Defended metrics
Master experiment_results.csv
Final tables
Final figures
```

Member 4 backend algorithms remain Member 4 responsibility.

---

## 21. Week 6 Member 1 Completion Summary

```text
Django user platform                          [x]
Signup / Login / Logout                       [x]
Role-based user navigation                    [x]
Persistent movie ratings                      [x]
My Ratings                                    [x]
My List                                       [x]
Movie Detail and rating                       [x]
First-time preference onboarding              [x]
Streaming-style Home                          [x]
Research Lab                                  [x]
Staff-only Research access                    [x]
Attack integration interface                  [x]
Detection integration interface               [x]
Defence integration interface                 [x]
Evaluation integration interface              [x]
Recommender integration boundary              [x]
No fabricated research/recommendation output  [x]
Django system check                           [x]
14 Django automated tests                     [x]
Manual web verification                       [x]
Week 6 changes merged into main               [x]
```

---

## 22. Week 6 Final Status

**Status: Complete**

The Week 6 Django user platform, persistent movie-user functionality, Research Lab access control, and research integration interfaces have been implemented, tested, and merged into `main`.

The Django presentation layer is ready to receive and display the real recommender, Attack, Detection, Defence, and Evaluation outputs produced by the relevant backend/research team members.

Backend/research members can develop their algorithms independently. When testing through the RMRS Research Lab, they must use a Django staff account (`is_staff = True`) or a superuser account.

The next Member 1 activity is integration and end-to-end verification after the relevant backend outputs are available in the shared `main` branch.
