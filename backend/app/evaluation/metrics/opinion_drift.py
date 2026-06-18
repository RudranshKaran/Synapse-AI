"""Opinion Drift metric — measures semantic change between original and revised positions.

For each participant, computes the embedding-based cosine similarity between
the original opinion and the final revised position. Drift = 1 - similarity,
where higher values indicate larger changes in stance.
"""

from app.evaluation.embedding import compute_embedding, cosine_similarity


def compute_opinion_drift(original_text: str, revised_text: str) -> float:
    """Compute the Opinion Drift for a single participant.

    Measures the semantic distance between the original and revised
    positions. Drift = 1.0 - cosine_similarity(original, revised).

    Args:
        original_text: The participant's initial opinion.
        revised_text: The participant's final revised position.

    Returns:
        Drift score between 0.0 (no change) and 1.0 (complete reversal).
    """
    emb_original = compute_embedding(original_text)
    emb_revised = compute_embedding(revised_text)

    similarity = cosine_similarity(emb_original, emb_revised)
    drift = 1.0 - similarity
    return round(max(0.0, min(drift, 1.0)), 4)
