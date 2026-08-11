# Contributing to RMRS

## Before coding

1. Pull the latest main branch.
2. Create a feature branch.
3. Keep one branch focused on one responsibility.
4. Run `python manage.py check` and `python manage.py test` before opening a pull request.

## Branch examples

- `feature/movie-explorer`
- `feature/collaborative-filtering`
- `feature/push-attacks`
- `feature/attack-detection`
- `feature/defence-evaluation`

## Team integration rule

The web layer should call service functions/classes. ML or research code should not directly manipulate templates, and templates should not contain algorithm logic. This boundary makes it easier to test and replace algorithms later.
