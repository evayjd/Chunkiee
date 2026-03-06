from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.models.response_models import UploadResponse

from app.services.ingestion.pipeline import IngestionPipeline

from app.db.database import SessionLocal
from app.db.models import Document


router = APIRouter()

UPLOAD_DIR = "data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):

    doc_id = str(uuid.uuid4())

    filename = file.filename

    path = os.path.join(
        UPLOAD_DIR,
        f"{doc_id}_{filename}"
    )

    with open(path, "wb") as f:
        f.write(await file.read())

    db = SessionLocal()

    try:

        doc = Document(
            id=doc_id,
            title=filename,
            source_type="file",
            source_uri=path
        )

        db.add(doc)
        db.commit()

    finally:

        db.close()

    pipeline = IngestionPipeline()

    pipeline.process_document(
        file_path=path,
        doc_id=doc_id
    )

    return UploadResponse(
        doc_id=doc_id,
        filename=filename
    )