import uuid
from typing import Dict, List

from app.services.parsers.factory import ParserFactory
from app.services.ingestion.cleaning import TextCleaner
from app.services.ingestion.chunking import TextChunker

from app.services.embedding.embedding_service import embed_documents
from app.services.retrieval.vector_store import VectorStore


class IngestionPipeline:
    """
    Document ingestion pipeline

    Steps:
    parse -> clean -> chunk -> embed -> store
    """

    def __init__(self):

        # text chunker
        self.chunker = TextChunker()

        # vector database interface
        self.vector_store = VectorStore()

    def process_document(
        self,
        file_path: str,
        doc_id: str
    ) -> Dict:
        """
        Process a document and store chunks + embeddings
        """

        # -------- 1. Parse document --------
        parser = ParserFactory.get_parser(file_path)

        parsed = parser.parse(file_path)

        # -------- 2. Clean text --------
        cleaner = TextCleaner()

        cleaned_doc = cleaner.clean_document(parsed)

        # -------- 3. Chunk document --------
        chunks = self.chunker.chunk(cleaned_doc, doc_id)

        if not chunks:
            return {
                "doc_id": doc_id,
                "chunks_created": 0
            }

        # -------- 4. Extract chunk texts --------
        chunk_texts = [c["text"] for c in chunks]

        # -------- 5. Generate embeddings --------
        embeddings = embed_documents(chunk_texts)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding count does not match chunk count"
            )

        # -------- 6. Prepare DB objects --------
        db_chunks: List[Dict] = []

        for i, chunk in enumerate(chunks):

            db_chunks.append({
                # 使用 chunker 生成的 id
                "id": chunk["chunk_id"],

                "doc_id": doc_id,

                "chunk_index": chunk["chunk_index"],

                "text": chunk["text"],

                "meta": {
                    "page": chunk.get("page"),
                    "section": chunk.get("section")
                },

                "embedding": embeddings[i]
            })

        # -------- 7. Store into vector DB --------
        self.vector_store.add_chunks(db_chunks)

        return {
            "doc_id": doc_id,
            "chunks_created": len(db_chunks)
        }