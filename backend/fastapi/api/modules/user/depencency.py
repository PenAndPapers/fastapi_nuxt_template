from typing import Annotated

from fastapi import Depends

from core.database import DatabaseDep

from .repository import UserRepository
from .service import UserService


def get_user_repository(db: DatabaseDep) -> UserRepository:
  return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_user_service(repository: UserRepositoryDep) -> UserService:
  return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
