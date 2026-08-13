# RMRS — Robust Movie Recommender System

Week 1 website foundation for the **Robust Movie Recommender System (RMRS)** capstone project.

The goal of this version is deliberately limited: create a clean, responsive, working Django website shell that the team can later connect to MovieLens processing, collaborative filtering, attacks, detection, defence, evaluation, and optional TMDB integration.

## Week 1 status

Implemented:

- Django project structure with modular apps.
- Reusable `base.html`, navbar, footer, and movie-card component.
- Home page.
- Movie Explorer page with visible search/filter controls.
- Recommendations page with clearly labelled sample results.
- Attack Lab, Detection, Defence, and Evaluation placeholder pages.
- Bootstrap 5.3.8 via official CDN plus custom responsive CSS.
- Local placeholder movie posters so Week 1 does not depend on TMDB.
- Named URL routes for all pages.
- Smoke tests for the main pages.
- GitHub CI workflow for `django check` and automated tests.
- Architecture and integration documentation.

Not implemented in Week 1:

- MovieLens ingestion or preprocessing.
- Collaborative-filtering model.
- Real personalised recommendations.
- Push-attack algorithms.
- Suspicious-user detection.
- Defence algorithms.
- RMSE/MAE experiment pipeline.
- Clean/attacked/defended experiment execution.
- TMDB API integration.
- Authentication.

## Requirements

- Python **3.12, 3.13, or 3.14**.
- Django 6.0.8 (pinned in `requirements.txt`).
- Internet access when viewing the site if you want Bootstrap loaded from its CDN. The site content itself uses local placeholder images.

## Quick start — macOS / Linux

```bash
cd robust-movie-recommender
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Quick start — Windows PowerShell

```powershell
cd robust-movie-recommender
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Verify the project

```bash
python manage.py check
python manage.py test
```

Expected main routes:

| Page | URL |
|---|---|
| Home | `/` |
| Movie Explorer | `/movies/` |
| Recommendations | `/recommendations/` |
| Attack Lab | `/attack/` |
| Detection | `/detection/` |
| Defence | `/defence/` |
| Evaluation | `/evaluation/` |

## Project organisation

The project uses small Django apps so each future subsystem has a clear home:

- `apps/core` — shared/public website pages such as Home.
- `apps/movies` — movie catalogue/explorer and later TMDB/movie metadata integration.
- `apps/recommendations` — recommender UI and later collaborative-filtering integration.
- `apps/research` — attack, detection, defence, and evaluation interfaces.
- `templates` — global templates and reusable UI components.
- `static` — CSS, JavaScript, and local images.
- `docs` — architecture, integration guidance, and Week 1 checklist.

See `docs/ARCHITECTURE.md` and `docs/INTEGRATION_GUIDE.md` before adding major features.

## Coding conventions

1. Keep views thin: views should coordinate requests and responses, not contain ML algorithms.
2. Put algorithms/data processing into `services/` modules.
3. Keep external APIs in `integrations/` modules.
4. Reuse templates/components instead of copying HTML.
5. Use named Django URLs (`{% url 'movies:explorer' %}`) instead of hard-coded paths.
6. Add tests when a route, service, or integration changes.
7. Never commit API keys, passwords, real secrets, `.env`, large datasets, or the SQLite development database.

## Suggested Git workflow

```bash
git checkout -b feature/week1-website-foundation
# make a focused change
git add .
git commit -m "Add Home page layout"
git push -u origin feature/week1-website-foundation
```

Good commit examples:

- `Set up Django website project`
- `Add base template and navigation`
- `Add Home and Movie Explorer layouts`
- `Add Recommendations demo interface`
- `Add research placeholder pages`
- `Improve responsive website styling`

Avoid vague commits such as `update`, `stuff`, `final`, or `final2`.

## Future deployment

Development settings are intentionally convenient. Production settings live in `config/settings/production.py` and require a real secret key plus explicit hosts. Do not deploy using the development settings.
