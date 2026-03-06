from typing import List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import text


def insert_chunks(
    db: Session,
    chunks: List[Dict]
):
    """
    插入 chunks
    """

    sql = text("""
    INSERT INTO chunks
    (
        id,
        doc_id,
        chunk_index,
        text,
        meta,
        embedding
    )
    VALUES
    (
        :id,
        :doc_id,
        :chunk_index,
        :text,
        :meta,
        :embedding
    )
    """)

    db.execute(sql, chunks)

    db.commit()


def similarity_search(
    db: Session,
    query_embedding,
    top_k: int,
    doc_id=None
):
    """
    pgvector similarity search
    """

    if doc_id:

        sql = text("""
        SELECT
            id,
            doc_id,
            chunk_index,
            text,
            meta,
            embedding <=> :query_embedding AS distance
        FROM chunks
        WHERE doc_id = :doc_id
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
        """)

        result = db.execute(
            sql,
            {
                "query_embedding": query_embedding,
                "top_k": top_k,
                "doc_id": doc_id
            }
        )

    else:

        sql = text("""
        SELECT
            id,
            doc_id,
            chunk_index,
            text,
            meta,
            embedding <=> :query_embedding AS distance
        FROM chunks
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
        """)

        result = db.execute(
            sql,
            {
                "query_embedding": query_embedding,
                "top_k": top_k
            }
        )

    rows = result.fetchall()

    chunks = []

    for r in rows:

        chunks.append(
            {
                "id": r.id,
                "doc_id": r.doc_id,
                "chunk_index": r.chunk_index,
                "text": r.text,
                "meta": r.meta,
                "distance": r.distance,
                "similarity": 1 - r.distance
            }
        )

    return chunks