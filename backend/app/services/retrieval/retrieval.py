from typing import Dict, List, Optional
import ast
import numpy as np

from app.services.embedding.embedding_service import embed_query
from app.services.retrieval.vector_store import VectorStore
from app.services.retrieval.query_rewrite import rewrite_query
from app.services.retrieval.metadata_filter import apply_metadata_filter
from app.services.retrieval.reranker import rerank_chunks
from app.services.retrieval.mmr import mmr_select
from app.config import VECTOR_K, FINAL_K


class Retriever:
    """
    RAG 检索器
    query -> rewrite -> embedding -> vector search -> filter -> rerank -> mmr
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
        # 1. query rewrite
        rewritten_queries = rewrite_query(query)

        all_candidates: List[Dict] = []

        # 2. multi-query retrieval
        for rq in rewritten_queries:
            # query embedding
            query_embedding = embed_query(rq)

            # vector search
            candidates = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=VECTOR_K,
                doc_id=doc_id
            )
            # ===== DEBUG START =====
            print("query:", rq)
            print("retrieved:", len(candidates))

            if candidates:
                print("top similarity:", candidates[0]["similarity"])
                print("top chunk:", candidates[0]["text"][:200])
# ===== DEBUG END =====
            

            # 关键：把数据库返回的 embedding 统一转成 float list
            normalized_candidates = [
                self._normalize_chunk_embedding(c)
                for c in candidates
            ]

            all_candidates.extend(normalized_candidates)

        # 3. deduplicate chunks
        all_candidates = self._dedupe_chunks(all_candidates)

        # 4. metadata filter
        filtered = apply_metadata_filter(
            results=all_candidates,
            doc_id=doc_id
        )

        # 5. rerank
        reranked = rerank_chunks(
            query=query,
            chunks=filtered
        )

        # 6. 用原始 query 做最终 MMR
        query_embedding = embed_query(query)
        query_embedding = self._normalize_embedding(query_embedding)

        final_chunks = mmr_select(
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
        调试模式：
        返回各阶段中间结果，便于排查问题
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

            normalized_candidates = [
                self._normalize_chunk_embedding(c)
                for c in candidates
            ]

            all_candidates.extend(normalized_candidates)

        all_candidates = self._dedupe_chunks(all_candidates)

        filtered = apply_metadata_filter(
            results=all_candidates,
            doc_id=doc_id
        )

        reranked = rerank_chunks(
            query=query,
            chunks=filtered
        )

        debug_query_embedding = self._normalize_embedding(
            embed_query(query)
        )

        final_chunks = mmr_select(
            query_embedding=debug_query_embedding,
            chunks=reranked,
            k=FINAL_K
        )

        return {
            "query": query,
            "rewritten_query": rewritten_queries,
            "candidates": all_candidates,
            "filtered": filtered,
            "reranked": reranked,
            "final_chunks": final_chunks
        }

    def _dedupe_chunks(
        self,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        去重 chunk
        按 (doc_id, chunk_index) 去重，保留第一次出现的结果
        """
        seen = set()
        result = []

        for c in chunks:
            key = (c["doc_id"], c["chunk_index"])

            if key not in seen:
                seen.add(key)
                result.append(c)

        return result

    def _normalize_chunk_embedding(self, chunk: Dict) -> Dict:
        """
        把 chunk 中的 embedding 统一转换为 float list
        防止从数据库读出来是字符串，导致后续 np.dot 报错
        """
        normalized = dict(chunk)
        normalized["embedding"] = self._normalize_embedding(
            chunk.get("embedding")
        )
        return normalized

    def _normalize_embedding(self, embedding) -> List[float]:
        """
        统一把 embedding 转成 List[float]

        支持几种输入：
        1. Python list / tuple / numpy array
        2. pgvector 返回的字符串形式，例如 "[0.1, 0.2, -0.3]"
        3. 其他可迭代数值对象
        """
        if embedding is None:
            return []

        # 情况 1：已经是 numpy array
        if isinstance(embedding, np.ndarray):
            return embedding.astype(float).tolist()

        # 情况 2：是 list / tuple
        if isinstance(embedding, (list, tuple)):
            return [float(x) for x in embedding]

        # 情况 3：是字符串，常见于 raw SQL + pgvector 返回值
        if isinstance(embedding, str):
            text = embedding.strip()

            if not text:
                return []

            try:
                # 例如 "[0.1, 0.2, -0.3]"
                parsed = ast.literal_eval(text)
                if isinstance(parsed, (list, tuple)):
                    return [float(x) for x in parsed]
            except Exception:
                pass

            # 兜底：手工 split
            text = text.strip("[]")
            if not text:
                return []

            return [float(x.strip()) for x in text.split(",") if x.strip()]

        # 情况 4：其他可迭代对象
        try:
            return [float(x) for x in embedding]
        except Exception as e:
            raise ValueError(f"无法解析 embedding：{type(embedding)}") from e