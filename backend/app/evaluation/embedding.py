"""Embedding utility — wraps Sentence Transformers for semantic similarity.

Uses a lightweight, well-supported model (all-MiniLM-L6-v2) that provides
384-dimensional embeddings suitable for semantic similarity tasks.
The model is ~80MB and runs efficiently on CPU.

Future: support configurable model selection via settings.
"""

import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Load the Sentence Transformer model (cached after first load).

    Args:
        model_name: HuggingFace model identifier.

    Returns:
        Loaded SentenceTransformer instance.
    """
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


def compute_embedding(text: str, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Compute an embedding vector for a single text string.

    Args:
        text: The text to embed.
        model_name: Which model to use.

    Returns:
        Numpy array of float32 embeddings.
    """
    model = _load_model(model_name)
    return model.encode(text, normalize_embeddings=True)


def compute_embeddings(
    texts: list[str], model_name: str = DEFAULT_MODEL
) -> np.ndarray:
    """Compute embedding vectors for multiple texts (batched).

    Args:
        texts: List of text strings to embed.
        model_name: Which model to use.

    Returns:
        2D numpy array of shape (len(texts), embedding_dim).
    """
    model = _load_model(model_name)
    return model.encode(texts, normalize_embeddings=True)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized embedding vectors.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        Similarity score in range [0, 1].
    """
    dot = float(np.dot(vec_a, vec_b))
    return min(max(dot, 0.0), 1.0)
