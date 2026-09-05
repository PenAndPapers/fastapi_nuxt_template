from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import get_db


def get_auth_db(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    yield db
