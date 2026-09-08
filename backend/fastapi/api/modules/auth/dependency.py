from typing import Annotated

from fastapi import Depends

from core.database import DatabaseDep

from .jwt.service import JwtService
from .repo import AuthRepository
from .service import AuthService


# 1. Repositories (depends on DB session)
def get_auth_repository(db: DatabaseDep) -> AuthRepository:
  return AuthRepository(db)


AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]


# 2. Domain Services (depends on repository)
def get_auth_service(repository: AuthRepositoryDep) -> AuthService:
  return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# 3. Stateless Services (no state or DB dependencies needed)
JwtServiceDep = Annotated[JwtService, Depends(JwtService)]
