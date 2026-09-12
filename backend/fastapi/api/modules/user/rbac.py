from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from .depencency import UserServiceDep


def permission_checker(required_permission: str) -> Callable[[], bool]:
  """
  RBAC Permission Checker Dependency.
  Ensures the current user has the required permission to access the endpoint.
  """

  async def _check_permission(
    user_service: UserServiceDep = Depends(),
    # Note: We assume there is a get_current_user dependency that provides the user ID
    # For now, we'll need the user_id. In a real app, this comes from the JWT token.
    # This is a placeholder until get_current_user is fully integrated.
    current_user_id: int = 1,
  ) -> bool:
    permissions = user_service.get_user_permissions(current_user_id)
    if required_permission not in permissions:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Missing required permission: {required_permission}",
      )
    return True

  return _check_permission


# Example usage in routes:
# @router.get("/admin", dependencies=[Depends(PermissionChecker("admin:access"))])
