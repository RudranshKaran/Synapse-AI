"""Agreement Score metric — measures semantic similarity between revised positions.

Computes pairwise cosine similarities between embeddings of all
participants' final revised positions and returns the average.
"""

import numpy as np

from app.evaluation.embedding import compute_embeddings, cosine_similarity


def compute_agreement_score(revised_positions: list[str]) -> float:
    """Compute the Agreement Score across all revised positions.

    Generates embeddings for each position, calculates pairwise cosine
    similarities, and averages them to produce an overall score.

    Args:
        revised_positions: List of final revised position texts, one per participant.

    Returns:
        Agreement score as a float between 0.0 and 100.0.

    Raises:
        ValueError: If fewer than 2 positions are provided.
    """
    if len(revised_positions) < 2:
        raise ValueError("At least 2 positions are required for agreement scoring.")

    embeddings = compute_embeddings(revised_positions)
    n = len(embeddings)
    total_sim = 0.0
    pair_count = 0

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            total_sim += sim
            pair_count += 1

    average_similarity = total_sim / pair_count if pair_count > 0 else 0.0
    return round(average_similarity * 100.0, 1)
