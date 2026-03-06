from typing import Dict, List, Optional

from app.services.embedding.embedding_service import embed_query
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.query_rewrite import rewrite_query
from app.services.retrieval.metadata_filter import apply_metadata_filter
from app.services.retrieval.reranker import rerank_chunks
from app.services.retrieval.mmr import mmr_select

VECTOR_K = 20  
FINAL_K = 4 


class Retriever:
    """
    RAG 检索器
    query -> rewrite -> embedding -> vector search -> filter -> rerank
    """

    def __init__(self):

        # 向量数据库接口
        self.vector_store = VectorStore()

    def retrieve(
        self,
        query: str,
        doc_id: Optional[str] = None
    ) -> List[Dict]:
        """
        执行完整 retrieval pipeline
        """
        # query rewrite
        rewritten_queries = rewrite_query(query)

        all_candidates: List[Dict] = []

        # multi-query retrieval
        for rq in rewritten_queries:

            # query embedding
            query_embedding = embed_query(rq)

            # vector search
            candidates = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=VECTOR_K,
                doc_id=doc_id
            )

            all_candidates.extend(candidates)

        # deduplicate chunks
        all_candidates = self._dedupe_chunks(all_candidates)

        # metadata filter
        filtered = apply_metadata_filter(
            results=all_candidates,
            doc_id=doc_id
        )

        # rerank
        reranked = rerank_chunks(
            query=query,
            chunks=filtered
        )
        query_embedding = embed_query
        
        final_chunks=mmr_select(
            query_embedding=query_embedding,
            chunks=reranked,
            k=FINAL_K
        )
        return final_chunks

    def retrieve_debug(
        self,
        query: str,
        doc_id: Optional[str] = None
    ) -> Dict:
        """
        调试模式
        """

        rewritten_queries = rewrite_query(query)

        all_candidates: List[Dict] = []

        for rq in rewritten_queries:

            query_embedding = embed_query(rq)

            candidates = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=VECTOR_K,
                doc_id=doc_id
            )

            all_candidates.extend(candidates)

        all_candidates = self._dedupe_chunks(all_candidates)

        filtered = apply_metadata_filter(
            results=all_candidates,
            doc_id=doc_id
        )

        reranked = rerank_chunks(
            query=query,
            chunks=filtered
        )

        return {
            "query": query,
            "rewritten_query": rewritten_queries,
            "candidates": all_candidates,
            "filtered": filtered,
            "reranked": reranked[:FINAL_K]
        }

    def _dedupe_chunks(
        self,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        去重 chunk
        """

        seen = set()
        result = []

        for c in chunks:

            key = (c["doc_id"], c["chunk_index"])

            if key not in seen:
                seen.add(key)
                result.append(c)

        return result