# RMRS Final Front-End Handover

## Project
**Robust Movie Recommender System (RMRS)**  
HIT401 Capstone Project · Group 15 · 2026

## Purpose
This document explains the final front-end changes completed on the branch:

`veasna-final-frontend`

The work focuses on improving the RMRS user interface and overall look and feel while preserving the existing Django routes, authentication, ratings, watchlist, research logic, staff permissions, and backend integration.

---

## Completed Front-End Improvements

### Account Interfaces
- Login page redesigned
- Signup page redesigned
- Profile page redesigned
- Improved responsive layout
- Consistent RMRS branding
- Password show/hide support retained

### Navigation
- Improved RMRS navbar
- Active-page highlighting
- Improved user dropdown
- Added user avatar initial
- Improved mobile navigation
- Renamed **Research Lab** to **Robustness Lab**
- Staff-only access preserved

### Home Page
- Improved featured movie hero
- Improved personalised recommendation area
- Improved Popular Movies section
- Improved Action Movies section
- Improved Comedy section
- Improved horizontal movie rows

### Movie Cards
- Unified reusable movie-card design
- Consistent card height and spacing
- Improved movie title, year, genre and rating layout
- Improved `Details & Rate` button
- Added professional RMRS poster fallback
- Broken or missing poster images now use the RMRS fallback design

### Movie Details & Rating
- Improved movie details layout
- Consistent poster/fallback design
- Improved movie-information panel
- Improved rating form
- Improved My List controls
- Added clear `Back to Browse` navigation
- Existing rating and watchlist backend functionality preserved

### Footer
- Improved RMRS branding
- Added project description
- Added HIT401 Capstone Project / Group 15 / 2026 information
- Footer remains at the bottom of short pages
- Responsive design added

### Robustness Lab
- Renamed the staff research area to **Robustness Lab**
- Improved main robustness dashboard
- Improved Attack Laboratory interface
- Improved Detection interface
- Improved Defence interface
- Improved Evaluation interface
- Added `Back to Robustness Lab` navigation to research subpages
- Existing research forms, tables, figures, backend variables and staff permissions preserved

---

## Main Files Updated

### CSS
- `static/css/style.css`
- `static/css/week6.css`

### Account Templates
- `templates/accounts/login.html`
- `templates/accounts/signup.html`
- `templates/accounts/profile.html`

### Shared Templates
- `templates/partials/navbar.html`
- `templates/partials/footer.html`
- `templates/components/movie_card.html`

### Home / Movie Templates
- `templates/core/home.html`
- `templates/movies/detail.html`

### Research Templates
- `templates/research/index.html`
- `templates/research/attack_lab.html`
- `templates/research/detection.html`
- `templates/research/defence.html`
- `templates/research/evaluation.html`

---

## Branch and Commit Information

Branch:

```bash
veasna-final-frontend
```

Latest front-end commit:

```text
5004bfd Polish final RMRS frontend and robustness interfaces
```

Other front-end commits in this branch include:

```text
102b4b8 Improve final RMRS profile interface
e054e8e Polish final RMRS login and signup interfaces
fe69443 Improve final RMRS login interface
```

---

## Validation Completed

The following checks were completed successfully:

```bash
python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

Tests:

```bash
python manage.py test
```

Result:

```text
Ran 14 tests
OK
```

---

## How Team Members Can Review the Branch

From the project folder:

```bash
git checkout main
git pull origin main
git fetch origin
git checkout veasna-final-frontend
```

If the branch is not available locally:

```bash
git checkout -b veasna-final-frontend origin/veasna-final-frontend
```

Activate the virtual environment:

```bash
source ../rmrs_env/bin/activate
```

Install requirements if needed:

```bash
python -m pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Run checks:

```bash
python manage.py check
python manage.py test
```

Run the project:

```bash
python manage.py runserver
```

Then open the local Django URL shown in the terminal.

---

## Pages to Review

Please review:

- Login
- Signup
- Profile
- Home
- Browse
- Recommendations
- My Ratings
- My List
- Movie Details & Rating
- Robustness Lab
- Attack Laboratory
- Detection
- Defence
- Evaluation

For the Robustness Lab, use a Django account with `is_staff=True`.

---

## Important Notes

- No database file should be committed as part of this front-end update.
- Existing backend functionality was intentionally preserved.
- Staff-only research access still uses Django `is_staff`.
- No credentials are included in this handover document.
- Browser CSS may be cached. If an older design appears, use a hard refresh:

```text
macOS: Command + Shift + R
Windows: Ctrl + Shift + R
```

---

## Recommended Merge Workflow

1. Review the Pull Request from `veasna-final-frontend` into `main`.
2. Confirm there are no merge conflicts.
3. Run `python manage.py check`.
4. Run `python manage.py test`.
5. Manually check the main user pages and Robustness Lab.
6. Merge only after team approval.

---

## Status

**Front-end implementation: Complete and ready for team review.**

The branch has been committed, tested and pushed to GitHub.
