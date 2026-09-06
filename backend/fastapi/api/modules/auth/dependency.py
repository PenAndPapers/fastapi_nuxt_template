from typing import Annotated

from fastapi import Depends

from core.database import DatabaseDep
from .repo import AuthRepository
from .service import AuthService


def get_auth_repository(db: DatabaseDep) -> AuthRepository:
    return AuthRepository(db)


AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]


def get_auth_service(repository: AuthService = Depends(get_auth_repository)) -> AuthService:
    return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
