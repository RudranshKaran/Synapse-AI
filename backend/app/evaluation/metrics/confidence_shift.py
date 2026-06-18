"""Confidence Shift metric — measures change in confidence between opinion and revision.

For each participant, compares the confidence score of the original opinion
with the confidence score of the final revision. The shift is simply
revision_confidence - original_confidence.
"""


def compute_confidence_shift(
    original_confidence: float | None, revised_confidence: float | None
) -> float:
    """Compute the Confidence Shift for a single participant.

    Args:
        original_confidence: Confidence score from the initial opinion.
        revised_confidence: Confidence score from the final revision.

    Returns:
        Shift value (positive = more confident, negative = less confident).
        If either confidence is None, returns 0.0.
    """
    if original_confidence is None or revised_confidence is None:
        return 0.0
    return round(revised_confidence - original_confidence, 1)
