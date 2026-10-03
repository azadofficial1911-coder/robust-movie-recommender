# RMRS Interactive Robustness Frontend

**Project:** Robust Movie Recommender System (RMRS)  
**Unit:** HIT401 Capstone Project  
**Group:** Group 15 · 2026  
**Responsibility:** Frontend / Responsive Robustness Experience  
**Student:** Veasna Kuoy  
**Branch:** `feature/robustness-final-integration`

---

## 1. Responsibility

This work focuses on the **Frontend / Responsive Robustness Experience** for RMRS.

The goal is to make the robustness behaviour easy to understand and demonstrate through the Django website.

The frontend consumes the backend clean, attacked and defended recommendation states and presents them clearly to staff/admin users.

---

## 2. Work Completed This Week

### Staff-Only Robustness Control

Implemented a staff/admin-only floating **Robustness ON/OFF** control.

- Staff can switch between protected mode and attack demonstration mode.
- Normal users do not see the robustness switch.
- Desktop uses a floating control.
- Mobile uses a compact responsive control / bottom-sheet interaction.
- The current state is always visible.

### Robustness ON

When robustness is ON:

- Detection and defence are active.
- Protected recommendation results are displayed.
- The interface shows **Protected mode**.
- Protected target ranks are highlighted.

### Robustness OFF

When robustness is OFF:

- Detection and defence are bypassed for the demonstration.
- Attacked recommendation results are displayed.
- The interface shows **Attack demo mode**.
- Attacked target ranks are highlighted.

---

## 3. Home Page Robustness Impact

Added a new staff-only **Robustness Impact** section to the Home page.

The section shows the movement of each targeted movie through:

```text
Clean → Attacked → Protected
```

Example:

```text
Clean #8 → Attacked #5 → Protected #8
```

For each targeted movie, the interface displays:

- clean rank
- attacked rank
- protected rank
- attack gain
- recovery positions

The rank values come from backend results and are not calculated or hard-coded in JavaScript.

---

## 4. Visible ON/OFF Recommendation Changes

The Home page recommendations visibly change when the staff robustness state changes.

### Example — Robustness ON

Observed protected recommendation examples:

- angels and insects — 4.27
- antonias line — 4.24
- taxi driver — 3.97
- usual suspects the — 3.70

### Example — Robustness OFF

Observed attacked recommendation examples:

- angels and insects — 4.27
- antonias line — 4.24
- taxi driver — 4.21
- braveheart — 3.83

This confirms that the website is displaying different backend recommendation states, not only changing labels.

---

## 5. Staff Protection Summary

The Recommendations page includes an expandable staff protection summary.

It displays:

- protection status
- suspicious profiles detected
- profiles removed
- number of targeted movies protected
- attack type
- attack size
- fake profiles generated

The summary supports both ON and OFF demonstration states.

---

## 6. Recommendation Interface

The Recommendations page displays:

- ranked recommendation list
- predicted scores
- targeted movie highlighting
- clean / attacked / protected movement
- robustness state banner
- staff protection summary

### Robustness ON

The page clearly indicates that detection and defence are active.

### Robustness OFF

The page clearly indicates that the attacked dataset is being demonstrated without protection.

---

## 7. Responsive Behaviour

The new robustness experience was reviewed across desktop and mobile layouts.

Checked areas include:

- navigation
- Home page
- Robustness Impact section
- floating robustness control
- mobile bottom sheet
- recommendation list
- staff protection summary
- targeted movie cards

The existing RMRS responsive layout and navigation were preserved.

---

## 8. Existing Functionality Preserved

The new frontend integration preserves the existing project functionality, including:

- Login
- Signup
- Profile
- Browse
- Movie Details
- Rating
- My Ratings
- My List
- Recommendations
- Robustness Lab
- Attack
- Detection
- Defence
- Evaluation
- Robustness Comparison

The new work extends the existing project rather than rebuilding the recommender or research algorithms.

---

## 9. Main Files Changed

Main files used in this frontend integration include:

```text
apps/core/views.py
templates/core/home.html
templates/recommendations/index.html
templates/partials/robustness_control.html
static/css/home-robustness.css
static/css/robustness-control.css
static/js/robustness-control.js
```

Other existing templates and styles were preserved where possible.

---

## 10. Testing

### Django System Check

Command:

```bash
python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

### Core Tests

Command:

```bash
python manage.py test apps.core.tests
```

Result:

```text
Ran 4 tests
OK
```

### Full Test Suite

Command:

```bash
python manage.py test
```

Latest result:

```text
Found 16 test(s)
15 passed
1 failed
```

Remaining failure:

```text
apps.movies.tests.MovieExplorerTests.test_explorer_loads
```

The failing assertion expects:

```text
Inception
```

in the Movie Explorer response.

This failure is outside the Home robustness frontend changes.

---

## 11. Manual Verification

The following were manually verified:

- staff user can see the robustness control
- normal user does not receive the staff control
- ON shows Protected mode
- OFF shows Attack demo mode
- Home recommendations change between ON and OFF
- targeted movie ranks show Clean → Attacked → Protected
- protected rank is highlighted when ON
- attacked rank is highlighted when OFF
- Home page remains responsive
- recommendation page remains usable
- existing catalogue sections remain visible
- floating robustness control reflects the current state

---

## 12. Key Commits

Final integration commits include:

```text
662814e  Complete home robustness impact integration
2d2c679  Connect home page to robustness state
```

Branch:

```text
feature/robustness-final-integration
```

---

## 13. Status

**Frontend / Responsive Robustness Experience: Ready for Team Review**

This weekly frontend work now demonstrates the robustness workflow directly on the website:

```text
Same recommender
      ↓
Same attack
      ↓
Robustness OFF → attacked recommendation state
Robustness ON  → detection + defence → protected recommendation state
```

The frontend clearly shows the recommendation impact and recovery while preserving the existing RMRS user and research functionality.
