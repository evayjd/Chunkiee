from fastapi import APIRouter
from typing import List

from app.models.response_models import DocumentResponse

from app.db.database import SessionLocal
from app.db.models import Document


router = APIRouter()


@router.get(
    "/documents",
    response_model=List[DocumentResponse]
)
def list_documents():

    db = SessionLocal()

    try:

        docs = db.query(Document).all()

        return [
            DocumentResponse(
                id=str(d.id),
                title=d.title,
                source_type=d.source_type,
                created_at=d.created_at
            )
            for d in docs
        ]

    finally:

        db.close()


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):

    db = SessionLocal()

    try:

        db.query(Document).filter(
            Document.id == doc_id
        ).delete()

        db.commit()

    finally:

        db.close()

    return {"status": "deleted"}