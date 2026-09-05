from fastapi import APIRouter

router = APIRouter()


@router.post("/register", summary="Register a new user")
def register() -> dict[str, str]:
    return {"message": "register endpoint"}


@router.post("/login", summary="Login user")
def login() -> dict[str, str]:
    return {"message": "login endpoint"}
