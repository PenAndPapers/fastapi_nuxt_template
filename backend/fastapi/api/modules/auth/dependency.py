from typing import Annotated

from fastapi import Depends

from api.modules.user.repository import UserRepository, UserRoleRepository
from core.database import DatabaseDep

from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository
from .service import AuthService


# 1. Repositories (depends on DB session)
def get_auth_repository(db: DatabaseDep) -> AuthRepository:
  return AuthRepository(db)


def get_user_repository(db: DatabaseDep) -> UserRepository:
  return UserRepository(db)


def get_user_role_repository(db: DatabaseDep) -> UserRoleRepository:
  return UserRoleRepository(db)


AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends(get_user_role_repository)]


# 2. Stateless Services (no state or DB dependencies needed)
JwtServiceDep = Annotated[JwtService, Depends(JwtService)]
PasswordServiceDep = Annotated[PasswordService, Depends(PasswordService)]


# 3. Domain Services (depends on repository)
def get_auth_service(
  repository: AuthRepositoryDep,
  user_repository: UserRepositoryDep,
  user_role_repository: UserRoleRepositoryDep,
  jwt_service: JwtServiceDep,
  password_service: PasswordServiceDep,
) -> AuthService:
  return AuthService(
    repository, user_repository, user_role_repository, jwt_service, password_service
  )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
