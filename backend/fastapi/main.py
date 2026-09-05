from fastapi import FastAPI

from api import api_router
from core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": settings.app_name}
