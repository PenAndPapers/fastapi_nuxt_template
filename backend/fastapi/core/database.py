import logging
from collections.abc import Generator
from typing import Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import get_settings
from fastapi import Depends

logger = logging.getLogger(__name__)

settings = get_settings()

Base = declarative_base()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        logger.info("Database session opened")
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        logger.info("Database session closed")
        db.close()


DatabaseDep = Annotated[Session, Depends(get_db)]
