# Future Integration Guide

The Week 1 project is intentionally designed so teammates can connect their work without rebuilding the website shell.

## MovieLens / catalogue integration

Recommended location:

```text
apps/movies/services/
    catalog.py
    movielens.py        # future
```

Keep pandas/data-cleaning code out of templates. If a database is introduced, add models in `apps/movies/models.py` and migrations under `apps/movies/migrations/`.

## Collaborative filtering

Recommended location:

```text
apps/recommendations/services/
    recommender.py      # interface/contract already present
    collaborative.py    # future implementation
```

The view should call a service that returns simple structured results such as:

```python
[{"movie_id": 123, "title": "Example", "predicted_score": 4.62}]
```

## Attacks and detection

Recommended locations:

```text
apps/research/services/attacks.py
apps/research/services/detection.py
```

The algorithms should accept data structures/dataframes and return structured results. They should not import Django templates or request objects.

## Defence and evaluation

Recommended locations:

```text
apps/research/services/defence.py
apps/research/services/evaluation.py
```

Evaluation should eventually return metrics such as RMSE/MAE in a structure the Evaluation view can pass to charts/tables.

## TMDB integration

A placeholder adapter already exists at:

```text
apps/movies/integrations/tmdb.py
```

Keep the API key outside Git. Use environment variables and add caching/rate-limit handling when the integration is implemented.

## Integration checklist

Before merging a feature:

1. The service can run independently of the HTML template.
2. The view remains small and readable.
3. Existing URL names are preserved unless there is a strong reason to change them.
4. Tests cover the new behavior.
5. No dataset, API key, password, or machine-specific path is committed.
