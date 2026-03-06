from fastapi import APIRouter

from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse, Citation

from app.services.retrieval.retrieval import Retriever
from app.services.rag.context_builder import build_context
from app.services.rag.prompt_builder import build_prompt
from app.services.rag.generator import generate_answer


router = APIRouter()

retriever = Retriever()


@router.post(
    "/query",
    response_model=QueryResponse
)
def query_rag(req: QueryRequest):

    # retrieval
    chunks = retriever.retrieve(
        query=req.query,
        doc_id=req.doc_id
    )

    # build context
    context_data = build_context(chunks)

    # build prompt
    prompt = build_prompt(
        question=req.query,
        context_data=context_data
    )

    # generate answer
    result = generate_answer(
        prompt=prompt,
        context_data=context_data
    )

    citations = [
        Citation(**c)
        for c in result["citations"]
    ]

    return QueryResponse(
        answer=result["answer"],
        citations=citations
    )