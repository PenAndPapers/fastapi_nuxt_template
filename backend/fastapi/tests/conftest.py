import uuid
from collections.abc import Generator

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.database import SessionLocal
from main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
  """
  Provides a database session for each test.
  Rolls back the transaction at the end to ensure test isolation.
  """
  session = SessionLocal()
  try:
    yield session
  finally:
    session.rollback()
    session.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
  with TestClient(app) as c:
    yield c


@pytest.fixture()
def faker() -> Faker:
  return Faker()


@pytest.fixture()
def random_string() -> str:
  return str(uuid.uuid4()).replace("-", "")
