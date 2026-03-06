from typing import Dict, List


class ContextBuilder:
    def __init__(
        self,
        max_chars: int = 6000
    ):
        self.max_chars = max_chars

    def build(
        self,
        chunks: List[Dict]
    ) -> Dict:
        
        # 先做 packing，避免上下文超长
        packed_chunks = self._pack_chunks(chunks)

        context_parts: List[str] = []
        citations: List[Dict] = []

        current_length = 0

        for i, chunk in enumerate(packed_chunks, start=1):

            chunk_text = chunk.get("text", "").strip()
            meta = chunk.get("meta", {}) or {}
            doc_id = chunk.get("doc_id")
            chunk_index = chunk.get("chunk_index")

            if not chunk_text:
                continue

            # 提取 metadata
            page_start = meta.get("page_start")
            page_end = meta.get("page_end")
            section = meta.get("section")

            # 构造 citation 标题
            header = self._build_chunk_header(
                citation_id=i,
                doc_id=doc_id,
                chunk_index=chunk_index,
                page_start=page_start,
                page_end=page_end,
                section=section
            )

            block = f"{header}\n{chunk_text}\n"

            # 二次保护，避免 header 加进去后超长
            if current_length + len(block) > self.max_chars:
                break

            context_parts.append(block)
            current_length += len(block)

            citations.append({
                "citation_id": i,
                "doc_id": doc_id,
                "chunk_index": chunk_index,
                "page_start": page_start,
                "page_end": page_end,
                "section": section
            })

        context = "\n".join(context_parts).strip()

        return {
            "context": context,
            "citations": citations
        }

    def _pack_chunks(
        self,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        做 context packing

        逻辑：
        1. 优先保留排序靠前的 chunk
        2. 尽量在 max_chars 内塞入更多信息
        3. 如果存在 final_score，则优先按 final_score 排序
        """
        if not chunks:
            return []

        # 如果已有 rerank / final_score，则按分数排序
        # 否则保留原顺序
        if any("final_score" in c for c in chunks):
            sorted_chunks = sorted(
                chunks,
                key=lambda x: x.get("final_score", 0),
                reverse=True
            )
        elif any("rerank_score" in c for c in chunks):
            sorted_chunks = sorted(
                chunks,
                key=lambda x: x.get("rerank_score", 0),
                reverse=True
            )
        else:
            sorted_chunks = chunks

        packed: List[Dict] = []
        total_length = 0

        for chunk in sorted_chunks:

            chunk_text = chunk.get("text", "").strip()

            if not chunk_text:
                continue

            # 这里预留一点 header 空间
            estimated_length = len(chunk_text) + 120

            if total_length + estimated_length > self.max_chars:
                continue

            packed.append(chunk)
            total_length += estimated_length

        return packed

    def _build_chunk_header(
        self,
        citation_id: int,
        doc_id: str,
        chunk_index: int,
        page_start=None,
        page_end=None,
        section=None
    ) -> str:
        """
        构造每个 chunk 的头部信息
        """

        parts = [f"[{citation_id}]"]

        if doc_id is not None:
            parts.append(f"doc_id={doc_id}")

        if chunk_index is not None:
            parts.append(f"chunk={chunk_index}")

        if page_start is not None and page_end is not None:
            if page_start == page_end:
                parts.append(f"page={page_start}")
            else:
                parts.append(f"pages={page_start}-{page_end}")
        elif page_start is not None:
            parts.append(f"page={page_start}")

        if section:
            parts.append(f"section={section}")

        return " | ".join(parts)


# singleton
_context_builder = ContextBuilder()


def build_context(chunks: List[Dict]) -> Dict:
    """
    对外接口
    """
    return _context_builder.build(chunks)