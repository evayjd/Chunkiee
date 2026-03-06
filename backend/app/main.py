from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.api.upload import router as upload_router
from app.api.doc import router as doc_router
from app.api.chunk import router as chunk_router
from app.api.query import router as query_router

from app.db.database import engine
from app.db.models import Base

import app.db.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup + shutdown lifecycle
    """

    # ---- startup ----
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    yield

    # ---- shutdown ----
    # 可以在这里关闭资源


def create_app() -> FastAPI:

    app = FastAPI(
        title="RAG Document Search API",
        description="RAG-based document retrieval and QA system",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload_router, prefix="/api", tags=["upload"])
    app.include_router(doc_router, prefix="/api", tags=["documents"])
    app.include_router(chunk_router, prefix="/api", tags=["chunks"])
    app.include_router(query_router, prefix="/api", tags=["query"])

    return app


app = create_app()


@app.get("/")
def root():
    return {"message": "RAG API is running"}