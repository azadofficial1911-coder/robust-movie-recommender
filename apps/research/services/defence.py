"""Defence integration boundary for the RMRS research module.

The Django presentation layer must remain independent from the final
defence algorithm. The real defence implementation can be connected
through this service when it is available.
"""


def apply_defence(*, ratings=None, detection_results=None):
    """
    Apply the real RMRS defence method.

    Parameters will ultimately be supplied by the attack and detection
    stages of the research pipeline.

    This function intentionally does not generate placeholder results.
    """

    raise NotImplementedError(
        "The final defence implementation has not been connected yet."
    )