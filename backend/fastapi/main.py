from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api import api_router
from core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.allow_origins,
  allow_credentials=settings.allow_credentials,
  allow_methods=settings.allow_methods,
  allow_headers=settings.allow_headers,
)

app.add_middleware(
  TrustedHostMiddleware,
  allowed_hosts=settings.trusted_hosts,
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
  return {"message": settings.app_name}
