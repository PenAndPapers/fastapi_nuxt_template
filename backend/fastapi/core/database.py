import logging
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

Base = declarative_base()

engine = create_engine(
  settings.database_url,
  pool_size=20,
  max_overflow=50,
  pool_timeout=30,
  pool_recycle=1800,
  pool_pre_ping=True,
  pool_use_lifo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
  db = SessionLocal()
  try:
    logger.info("Database session opened")
    yield db
  except OperationalError as e:
    db.rollback()

    logger.error(f"Database connection error: {e}")
    raise HTTPException(
      status_code=status.HTTP_503_INTERNAL_SERVER_ERROR, detail="Database connection error"
    ) from e
  except SQLAlchemyError as e:
    db.rollback()
    logger.error(f"Database transaction error: {e}")
    raise
  except Exception as e:
    db.rollback()
    logger.error(f"Database session error: {e}")
    raise e
  finally:
    logger.info("Database session closed")
    db.close()


DatabaseDep = Annotated[Session, Depends(get_db)]
