from fastapi import APIRouter

from .depencency import UserServiceDep

router = APIRouter()


@router.get("", summary="List users")
def list_users() -> dict[str, str]:
  return {"message": "list users endpoint"}


@router.get("/{user_id}", summary="Get user by ID")
def get_user(user_id: int) -> dict[str, int]:
  return {"user_id": user_id}


@router.get("/permission/{user_id}", summary="Get user permissions")
def get_user_permissions(user_id: int, user_service: UserServiceDep) -> dict[str, list[str]]:
  return {"permissions": list(user_service.get_user_permissions(user_id))}
