# Week 6 — wiring real results into the live Defence/Evaluation pages

This connects the real results from the previous deliverable
(`week6-defence-evaluation-REAL-RESULTS.zip`) into the actual running
Django site, so `/research/defence/` and `/research/evaluation/` display
real numbers and charts instead of "Pending" placeholders.

**Verified working**: I ran this through Django's actual test client
(migrations applied, a staff user created, both pages fetched) and
confirmed the real numbers and figure paths appear in the rendered HTML.
`python manage.py test` still passes all 14 existing tests unchanged.

## Where each file goes

```
apps/research/services/results_loader.py   -> NEW
                                                Reads results/experiment_results.csv
                                                and results/tables/defence_summary_pilot.csv.
                                                Never calculates a metric -- only reads
                                                files already produced by the scripts in
                                                the previous deliverable. Returns None
                                                gracefully if those files don't exist yet.

apps/research/views.py                      -> REPLACES the existing file
                                                defence() and evaluation() now call the
                                                loader and pass results into the template
                                                context. Falls back to the original
                                                "pending" behaviour if no results file
                                                exists -- nothing breaks for teammates who
                                                haven't run the pilot scripts yet.

templates/research/defence.html             -> REPLACES the existing file
templates/research/evaluation.html          -> REPLACES the existing file
                                                Both now render real data when available
                                                ({% if results_available %}) and fall back
                                                to the original static "Pending"/"Expected
                                                Integration Flow" content otherwise -- the
                                                Week 1/Week 6 "no fabricated data" wording
                                                and layout is preserved as the fallback.

static/images/research/*.png                -> NEW (5 files)
                                                The same 5 figures from the results
                                                deliverable, copied into Django's static
                                                folder so {% static %} can serve them.
                                                The Evaluation Dashboard now displays all
                                                five inline.
```

## Prerequisite

This assumes you've already copied in the files from
`week6-defence-evaluation-REAL-RESULTS.zip` (specifically
`results/experiment_results.csv` and
`results/tables/defence_summary_pilot.csv`) — `results_loader.py` reads
those paths directly. If those files aren't present yet, both pages
still work exactly as before (fallback "pending" content), so this is
safe to merge even before the results are in place.

## What you'll see once both are merged

- `/research/defence/` — a real table: scenario, defence method,
  suspicious profiles detected, users before/removed/after, ratings
  removed, for both Random Push and Average Push.
- `/research/evaluation/` — a real 5-row comparison table (Clean,
  Random Push Attacked, Random Push Defended, Average Push Attacked,
  Average Push Defended) with RMSE, MAE, Target Rank, Target Score, Hit
  Rate@10, plus all 5 result figures displayed inline.

## Quick way to check it yourself

```bash
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth import get_user_model
get_user_model().objects.create_user(username='staffcheck', password='TestPass123!', is_staff=True)
"
python manage.py runserver
```

Then log in as `staffcheck` / `TestPass123!` and visit `/research/defence/`
and `/research/evaluation/`.
