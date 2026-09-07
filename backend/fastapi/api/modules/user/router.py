from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="List users")
def list_users() -> dict[str, str]:
  return {"message": "list users endpoint"}


@router.get("/{user_id}", summary="Get user by ID")
def get_user(user_id: int) -> dict[str, int]:
  return {"user_id": user_id}
