# RMRS Architecture

## Why this structure?

Week 1 must produce a real working website without duplicating the recommender, attack, detection, or defence work assigned for later integration. The structure therefore separates **presentation**, **web routing**, and **algorithm/service code**.

```text
Browser
   |
Django URLs
   |
Views (thin request/response coordination)
   |
Services / Integrations
   |
Future MovieLens / Recommender / Attack / Detection / Defence / Evaluation code
   |
Templates render structured results
```

## Apps

### `apps/core`
Home and other site-wide public pages. It may call small read-only services from domain apps when it needs data to present.

### `apps/movies`
Owns the Movie Explorer and movie metadata boundary. Demo movie data currently lives in `services/catalog.py`. Later, replace the data source behind that service instead of rewriting templates.

### `apps/recommendations`
Owns the recommendation UI. `services/recommender.py` defines a small protocol so a collaborative-filtering implementation can be substituted later.

### `apps/research`
Owns the research web pages and integration boundaries for:

- Random/Average Push attacks.
- suspicious-user detection.
- defence/robustness logic.
- evaluation metrics and experiments.

## Templates

- `base.html` — shared HTML document, Bootstrap and custom assets.
- `partials/` — shared navbar/footer.
- `components/` — reusable movie cards.
- app folders — page-specific templates.

## Settings

- `base.py` — settings common to all environments.
- `development.py` — local `runserver` settings.
- `production.py` — safer future deployment defaults.

This avoids a common scaling problem where one `settings.py`, one `views.py`, and one giant template accumulate unrelated responsibilities.
