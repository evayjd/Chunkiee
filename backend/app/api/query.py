from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.app.services.embedding.embedding_model import embed_query
from app.services.retrieval import retrieve_chunks
from app.services.rag import generate_answer


router = APIRouter(prefix="/query", tags=["query"])



class QueryRequest(BaseModel):
    question: str
    top_k: int = 5



class SourceChunk(BaseModel):
    chunk_id: str
    doc_id: str
    content: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]


#Route
@router.post("/", response_model=QueryResponse)
def query(request: QueryRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    # embedding
    query_vector = embed_query(request.question)

    # retrieval
    chunks = retrieve_chunks(query_vector, top_k=request.top_k)

    # RAG generation
    answer = generate_answer(request.question, chunks)

    return QueryResponse(
        answer=answer,
        sources=chunks
    )