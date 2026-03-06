from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    """
    RAG 查询请求
    """

    query: str
    doc_id: Optional[str] = None


class UploadRequest(BaseModel):
    """
    预留：如果未来支持 URL / 文本上传
    """

    title: Optional[str] = None
    source_uri: Optional[str] = None