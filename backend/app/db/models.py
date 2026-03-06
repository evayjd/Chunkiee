import uuid

from sqlalchemy import Column, Integer, Text, ForeignKey, text as sql_text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector


Base = declarative_base()


class Document(Base):
    """
    documents 表的 ORM 映射
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source_type = Column(Text, nullable=False)
    source_uri = Column(Text, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("now()")
    )


class Chunk(Base):
    """
    chunks 表的 ORM 映射
    """
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doc_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = Column(Integer, nullable=False)

    text = Column(Text, nullable=False)

    meta = Column(JSONB, nullable=True)

    embedding = Column(Vector(1024), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("now()")
    )