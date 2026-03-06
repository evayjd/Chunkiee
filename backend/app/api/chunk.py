from fastapi import APIRouter
from typing import List

from app.models.response_models import ChunkResponse

from app.services.retrieval.vector_store import VectorStore


router = APIRouter()

vector_store = VectorStore()


@router.get(
    "/documents/{doc_id}/chunks",
    response_model=List[ChunkResponse]
)
def get_chunks(doc_id: str):

    chunks = vector_store.get_chunks_by_doc_id(doc_id)

    return [
        ChunkResponse(
            id=c["id"],
            doc_id=c["doc_id"],
            chunk_index=c["chunk_index"],
            text=c["text"],
            meta=c["meta"]
        )
        for c in chunks
    ]