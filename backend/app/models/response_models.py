from pydantic import BaseModel
from typing import List, Optional


class Citation(BaseModel):

    citation_id: int
    doc_id: Optional[str]
    chunk_index: Optional[int]
    page_start: Optional[int]
    page_end: Optional[int]
    section: Optional[str]


class QueryResponse(BaseModel):

    answer: str
    citations: List[Citation]


class UploadResponse(BaseModel):

    doc_id: str
    filename: str


class DocumentResponse(BaseModel):

    id: str
    title: str
    source_type: str
    created_at: Optional[str]


class ChunkResponse(BaseModel):

    id: str
    doc_id: str
    chunk_index: int
    text: str
    meta: dict