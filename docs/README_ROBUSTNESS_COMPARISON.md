# RMRS Robustness Comparison – Frontend / Django Integration

## Project

**Robust Movie Recommender System (RMRS)**  
HIT401 Capstone Project · Group 15 · 2026

## Responsibility

**Team Member:** Veasna  
**Primary Responsibility:** Frontend / Django Integration

## Purpose

This document summarises the implementation of the **Robustness Comparison** interface for RMRS.

The purpose of the page is to provide a staff-only comparison of recommender performance under the same attack scenario with robustness disabled and enabled.

The page compares:

- Clean Baseline
- Without Robustness — attacked recommender
- With Robustness — detection and defence applied

The interface supports both:

- Random Push
- Average Push

## Main Deliverable

The main output completed in this work is a functioning:

**Robustness Comparison Page**

Route:

```text
/research/comparison/
```

The page is available only to authorised staff users.

## Implemented Features

### 1. Robustness Comparison Route

A new Django route was added for the comparison interface.

```text
/research/comparison/
```

The route is registered in:

```text
apps/research/urls.py
```

### 2. Staff-Only Access

The comparison page uses the existing RMRS staff-access protection.

Normal users cannot access the page.

Verified behaviour:

```text
Staff / Admin User
→ Can access Robustness Lab
→ Can access Robustness Comparison

Normal User
→ Cannot access Robustness Lab
→ Cannot access Robustness Comparison
→ Receives 403 Forbidden when accessing the comparison URL directly
```

### 3. Attack Scenario Selection

The page provides a scenario selector for:

```text
Random Push
Average Push
```

The selected scenario is submitted through the Django view and the corresponding experiment results are displayed.

### 4. Clean Reference

The page displays the clean baseline as the reference condition.

Displayed metrics include:

- Target Rank
- Target Score
- RMSE
- MAE

### 5. Without Robustness

The interface displays the attacked recommender condition with defence disabled.

Displayed metrics include:

- Target Rank
- Target Score
- RMSE
- MAE
- Hit Rate @10
- Defence status

### 6. With Robustness

The interface displays the defended recommender condition after suspicious-user detection and profile removal.

Displayed metrics include:

- Target Rank
- Target Score
- RMSE
- MAE
- Hit Rate @10
- Defence status
- Detected Users
- Removed Users
- Ratings Removed

### 7. Robustness Impact Flow

A visual comparison flow was added:

```text
Clean → Attacked → Defended
```

This helps show the attack effect and the recovery after defence.

### 8. Target Rank Movement

The page also includes a target-rank comparison section showing:

```text
Clean
Attacked
Defended
```

This provides a clear visual summary of attack damage and defence recovery.

### 9. Robustness Lab Navigation

A new full-width **Robustness Comparison** card was added to the Robustness Lab.

Navigation flow:

```text
Robustness Lab
    ↓
Robustness Comparison
    ↓
Random Push / Average Push
    ↓
Clean vs Without Robustness vs With Robustness
```

A **Back to Robustness Lab** button is also provided on the comparison page.

## Data Source

The Django presentation layer does not invent experiment results.

The comparison page uses the existing RMRS result-loading service to read experiment outputs and defence-summary data.

The page displays real stored experiment values for:

- Clean
- Random Push attacked
- Random Push defended
- Average Push attacked
- Average Push defended

## Verified Results

### Random Push

**Clean Baseline**

- Target Rank: 1127.4
- Target Score: 1.97
- RMSE: 0.9298
- MAE: 0.7253

**Without Robustness**

- Target Rank: 778.9
- Target Score: 3.11
- RMSE: 0.9304
- MAE: 0.7261
- Hit Rate @10: 0.00

**With Robustness**

- Target Rank: 1127.4
- Target Score: 1.97
- RMSE: 0.9298
- MAE: 0.7253
- Hit Rate @10: 0.00
- Detected Users: 47
- Removed Users: 47
- Ratings Removed: 3995

### Average Push

**Clean Baseline**

- Target Rank: 1127.4
- Target Score: 1.97
- RMSE: 0.9298
- MAE: 0.7253

**Without Robustness**

- Target Rank: 407.6
- Target Score: 3.67
- RMSE: 0.9309
- MAE: 0.7262
- Hit Rate @10: 0.00

**With Robustness**

- Target Rank: 1127.4
- Target Score: 1.97
- RMSE: 0.9298
- MAE: 0.7253
- Hit Rate @10: 0.00
- Detected Users: 47
- Removed Users: 47
- Ratings Removed: 3995

## Files Changed

The implementation changed the following files:

```text
apps/research/urls.py
apps/research/views.py
static/css/week6.css
templates/research/index.html
templates/research/robustness_comparison.html
```

### File Responsibilities

#### `apps/research/urls.py`

Adds the new Robustness Comparison route.

#### `apps/research/views.py`

Adds the staff-only comparison view and handles Random Push / Average Push selection.

#### `templates/research/index.html`

Adds the Robustness Comparison card to the Robustness Lab.

#### `templates/research/robustness_comparison.html`

Implements the complete lecturer-facing comparison interface.

#### `static/css/week6.css`

Adds responsive styling for the comparison page, metric cards, status labels, robustness flow and target-rank movement.

## Validation

The implementation was tested successfully.

### Django System Check

```bash
python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

### Django Tests

```bash
python manage.py test
```

Result:

```text
Found 14 test(s).
Ran 14 tests.
OK
```

### Manual Tests

The following manual tests were completed successfully:

- Random Push scenario
- Average Push scenario
- Clean baseline display
- Without Robustness display
- With Robustness display
- Target rank recovery display
- Detected users display
- Removed users display
- Ratings removed display
- Robustness Lab navigation
- Back to Robustness Lab navigation
- Staff user access
- Normal user access restriction
- 403 Forbidden response for non-staff direct access

## Git Information

Development branch:

```text
feature/robustness-ui
```

Main implementation commit:

```text
a3dab77
```

Commit message:

```text
Add robustness comparison frontend and Django integration
```

The branch was pushed to GitHub and a Pull Request was created for integration into `main`.

## How to Test the Feature

Activate the project environment:

```bash
cd ~/Desktop/HIT401_Capstone/robust-movie-recommender
source ../rmrs_env/bin/activate
```

Run migrations if required:

```bash
python manage.py migrate
```

Run the project:

```bash
python manage.py runserver
```

Log in with a staff account.

Open:

```text
http://127.0.0.1:8000/research/
```

Select:

```text
Robustness Comparison
```

Then test both:

```text
Random Push
Average Push
```

## Notes for Team Members

- The comparison interface is presentation/integration work.
- It does not replace the recommender, attack, detection or defence algorithms.
- Experiment values are loaded from existing RMRS result files.
- Final comparison logic can later be moved behind a dedicated comparison service without redesigning the frontend.
- Do not hard-code new experiment numbers directly into the template.

## Current Status

**Completed and validated.**

The required weekly frontend / Django integration deliverable — **Working Robustness Comparison page** — is implemented and ready for team review.
