import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://chunkie:dyjdyj123@127.0.0.1:5433/ragdb"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    """
    FastAPI dependency
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()