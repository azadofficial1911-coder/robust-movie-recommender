# Veasna — Week 1 Definition of Done

## Project Setup

- [x] Django project structure exists.
- [x] Main modular Django apps exist.
- [x] Global `templates/` structure exists.
- [x] `static/css`, `static/js`, and `static/images` directories exist.
- [x] Reusable `base.html` template exists.
- [x] Bootstrap is connected through the official CDN.
- [x] Custom CSS exists.

## Website Structure and Navigation

- [x] Navigation bar works through named Django routes.
- [x] Home page exists.
- [x] Movie Explorer page exists.
- [x] Recommendations page exists.
- [x] Attack Lab interface is prepared for integration.
- [x] Detection interface is prepared for integration.
- [x] Defence interface is prepared for integration.
- [x] Evaluation interface is prepared for integration.

## Movie Explorer Interface

- [x] Search box is available.
- [x] Genre, Year, Rating, and Sort controls are visible.
- [x] Six sample movie cards are available.
- [x] Rate and Details buttons are available in the movie interface.

## Recommendations Interface

- [x] Recommendations page contains clearly labelled sample results.
- [x] Recommendation interface is prepared for future recommender-system integration.

## Design and Responsiveness

- [x] Website styling is consistent across the main pages.
- [x] Responsive layouts are defined for desktop and smaller screens.
- [x] Navigation, movie cards, forms, and page content remain readable on smaller screens.

## Documentation and Team Handover

- [x] README contains installation and run instructions.
- [x] Project structure is organised for future team integration.
- [x] Architecture and integration documentation are available in the `docs/` folder.
- [x] Week 1 progress is documented in this checklist.
- [ ] Code is pushed to the team's GitHub repository and submitted through the agreed branch / Pull Request workflow.

## Week 1 Scope Confirmed

The following features are intentionally not implemented as part of Week 1:

- MovieLens ingestion or preprocessing.
- Collaborative-filtering model.
- Real personalised recommendations.
- Push-attack algorithms.
- Suspicious-user detection algorithms.
- Defence algorithms.
- RMSE/MAE experiment pipeline.
- Clean, attacked, and defended experiment execution.
- TMDB API integration.
- User authentication.

These components will be integrated in later stages by the relevant team members.

## End-of-Week Demonstration Statement

> The Django website foundation is running successfully. All main routes and navigation are operational. The Home, Movie Explorer, and Recommendations pages contain their initial frontend interfaces, while the Attack Lab, Detection, Defence, and Evaluation interfaces are prepared for future integration. The project is organised using a modular and scalable structure so that recommendation, attack, detection, defence, and evaluation services can be integrated without requiring major changes to the existing website foundation.

## Final Week 1 Completion

Week 1 is complete when all items above are checked, including the GitHub push / Pull Request step.
