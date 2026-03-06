import uuid
from typing import Dict, List

from app.services.parsers.factory import get_parser
from app.services.ingestion.cleaning import clean_text
from app.services.ingestion.chunking import TextChunker

from app.services.embedding.embedding_service import embed_documents
from app.services.retrieval.vector_store import VectorStore


class IngestionPipeline:
    """
    文档入库 pipeline
    parse -> clean -> chunk -> embed -> store
    """

    def __init__(self):

        # 文本切块器
        self.chunker = TextChunker()

        # 向量数据库接口
        self.vector_store = VectorStore()

    def process_document(
        self,
        file_path: str,
        doc_id: str
    ) -> Dict:
        """
        处理一个文档并写入数据库
        """
        # 选择 parser

        parser = get_parser(file_path)

        parsed = parser.parse(file_path)

        raw_text = parsed["text"]


        # 文本清洗

        cleaned_text = clean_text(raw_text)

        # 文本切块
        chunks = self.chunker.chunk(cleaned_text)

        # 提取 chunk 文本
        chunk_texts = [c["text"] for c in chunks]

        # 调用 embedding_service
        embeddings = embed_documents(chunk_texts)


        # 构建数据库对象
        db_chunks: List[Dict] = []

        for i, chunk in enumerate(chunks):

            db_chunks.append({
                "id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "chunk_index": i,
                "text": chunk["text"],
                "meta": chunk.get("meta", {}),
                "embedding": embeddings[i]
            })


        # 写入数据库
        self.vector_store.add_chunks(db_chunks)

        return {
            "doc_id": doc_id,
            "chunks_created": len(db_chunks)
        }