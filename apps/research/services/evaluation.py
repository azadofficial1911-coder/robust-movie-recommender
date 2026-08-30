"""Evaluation integration boundary for the RMRS research module.

The final evaluation stage will compare recommendation quality across
clean, attacked and defended conditions using approved metrics such as
RMSE and MAE.

Metric calculations remain outside the Django presentation layer.
"""


EXPECTED_METRICS = (
    "RMSE",
    "MAE",
)


def evaluate_experiment(
    *,
    clean_results=None,
    attacked_results=None,
    defended_results=None,
):
    """
    Evaluate clean, attacked and defended recommendation results.

    The final backend is expected to return real evaluation metrics for
    comparison by the Django presentation layer.

    Placeholder metric values must not be generated here.
    """

    raise NotImplementedError(
        "The final evaluation backend has not been connected yet."
    )