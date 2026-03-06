from typing import Dict, List
import numpy as np


def _cosine(a, b):
    """
    计算 cosine similarity
    """
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b) + 1e-10
    )


def mmr_select(
    query_embedding: List[float],
    chunks: List[Dict],
    k: int,
    lambda_param: float = 0.7
) -> List[Dict]:

    if not chunks:
        return []

    embeddings = [
        c.get("embedding")
        for c in chunks
        if c.get("embedding") is not None
    ]

    if not embeddings:
        return chunks[:k]

    selected = []
    candidates = list(range(len(embeddings)))

    while len(selected) < min(k, len(embeddings)):

        best_score = -1e9
        best_idx = None

        for i in candidates:

            relevance = _cosine(
                query_embedding,
                embeddings[i]
            )

            redundancy = 0

            for j in selected:

                redundancy = max(
                    redundancy,
                    _cosine(
                        embeddings[i],
                        embeddings[j]
                    )
                )

            score = (
                lambda_param * relevance
                - (1 - lambda_param) * redundancy
            )

            if score > best_score:
                best_score = score
                best_idx = i

        selected.append(best_idx)
        candidates.remove(best_idx)

    return [chunks[i] for i in selected]