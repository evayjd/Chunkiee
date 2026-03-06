from typing import Dict, List

from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        device: str = "mps"
    ):

        self.model = CrossEncoder(
            model_name,
            device=device
        )

    def rerank(
        self,
        query: str,
        chunks: List[Dict]
    ) -> List[Dict]:

        if not chunks:
            return []

        pairs = [(query, c["text"]) for c in chunks]

        scores = self.model.predict(pairs)

        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)

        chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return chunks


_reranker = Reranker()


def rerank_chunks(
    query: str,
    chunks: List[Dict]
) -> List[Dict]:

    return _reranker.rerank(query, chunks)