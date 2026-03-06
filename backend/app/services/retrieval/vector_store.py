from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import SessionLocal
from app.db.models import Chunk


class VectorStore:

    def __init__(self):
        pass

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        批量写入 chunks
        """
        db: Session = SessionLocal()

        try:

            db_objects = []

            for item in chunks:

                chunk = Chunk(
                    id=item["id"],
                    doc_id=item["doc_id"],
                    chunk_index=item["chunk_index"],
                    text=item["text"],
                    meta=item.get("meta", {}),
                    embedding=item["embedding"]
                )

                db_objects.append(chunk)

            # 使用 bulk insert 提升性能
            db.bulk_save_objects(db_objects)

            db.commit()

        except Exception:

            db.rollback()
            raise

        finally:

            db.close()

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        基于 query embedding 检索最相似的 chunks
        """
        db: Session = SessionLocal()

        try:

            embedding_str = self._format_vector(query_embedding)

            if doc_id is not None:

                sql = text("""
                    SELECT
                        id,
                        doc_id,
                        chunk_index,
                        text,
                        meta,
                        embedding,
                        embedding <=> CAST(:query_embedding AS vector) AS distance
                    FROM chunks
                    WHERE doc_id = :doc_id
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :top_k
                """)

                rows = db.execute(
                    sql,
                    {
                        "query_embedding": embedding_str,
                        "doc_id": doc_id,
                        "top_k": top_k
                    }
                ).mappings().all()

            else:

                sql = text("""
                    SELECT
                        id,
                        doc_id,
                        chunk_index,
                        text,
                        meta,
                        embedding,
                        embedding <=> CAST(:query_embedding AS vector) AS distance
                    FROM chunks
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :top_k
                """)

                rows = db.execute(
                    sql,
                    {
                        "query_embedding": embedding_str,
                        "top_k": top_k
                    }
                ).mappings().all()

            results = []

            for row in rows:

                distance = float(row["distance"])
                similarity = 1 - distance

                results.append(
                    {
                        "id": str(row["id"]),
                        "doc_id": str(row["doc_id"]),
                        "chunk_index": row["chunk_index"],
                        "text": row["text"],
                        "meta": row["meta"],
                        "embedding": row["embedding"],
                        "distance": distance,
                        "similarity": similarity
                    }
                )

            return results

        finally:

            db.close()

    def get_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()

        try:

            rows = (
                db.query(Chunk)
                .filter(Chunk.doc_id == doc_id)
                .order_by(Chunk.chunk_index.asc())
                .all()
            )

            results = []

            for row in rows:

                results.append(
                    {
                        "id": str(row.id),
                        "doc_id": str(row.doc_id),
                        "chunk_index": row.chunk_index,
                        "text": row.text,
                        "meta": row.meta
                    }
                )

            return results

        finally:

            db.close()

    def delete_by_doc_id(self, doc_id: str) -> None:
        """
        删除某个文档对应的全部 chunks
        """

        db: Session = SessionLocal()

        try:

            db.query(Chunk).filter(
                Chunk.doc_id == doc_id
            ).delete()

            db.commit()

        except Exception:

            db.rollback()
            raise

        finally:

            db.close()

    @staticmethod
    def _format_vector(vector: List[float]) -> str:
        """
        把 Python 的 list 向量转换为 pgvector 可识别的字符串格式
        """

        return "[" + ",".join(f"{x:.6f}" for x in vector) + "]"