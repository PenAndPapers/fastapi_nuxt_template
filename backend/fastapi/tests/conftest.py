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
def private_key_fixture() -> str:
  return (
    "-----BEGIN EC PRIVATE KEY-----\n"
    "MHcCAQEEIG2KLeKlBGvqsgYuONt25EYRWeUqnAuEeYaRWI5vMyvUoAoGCCqGSM49\n"
    "AwEHoUQDQgAEIOmFjFCnGcB+thM1BN/sTm/RQpCGOo9Atwmh+1Vl+jsIeBYUnMEQ\n"
    "U9Sg4VTlVQsl+1uwtPR+TQoFQv7j1OVu7Q==\n"
    "-----END EC PRIVATE KEY-----\n"
  )


@pytest.fixture()
def public_key_fixture() -> str:
  return (
    "-----BEGIN PUBLIC KEY-----\n"
    "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIOmFjFCnGcB+thM1BN/sTm/RQpCG\n"
    "Oo9Atwmh+1Vl+jsIeBYUnMEQU9Sg4VTlVQsl+1uwtPR+TQoFQv7j1OVu7Q==\n"
    "-----END PUBLIC KEY-----\n"
  )
