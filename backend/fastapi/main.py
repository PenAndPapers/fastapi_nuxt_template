from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api import api_router
from api.modules.user.seed import seed_rbac_data
from core.config import get_settings
from core.database import SessionLocal

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
  # Handle startup
  if settings.seed_data:
    try:
      print("Seeding RBAC data...")
      with SessionLocal() as db:
        seed_rbac_data(db)
      print("RBAC data seeded successfully.")
    except Exception as e:
      print(f"Critical error during RBAC seeding: {e}")
      # We log the error but allow the app to start.
      # If seeding is mandatory for app function, you could raise the error here.

  yield
  # Handle shutdown
  pass


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.origins_list,
  allow_credentials=settings.allow_credentials,
  allow_methods=settings.methods_list,
  allow_headers=settings.headers_list,
)

app.add_middleware(
  TrustedHostMiddleware,
  allowed_hosts=settings.trusted_hosts_list,
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
  return {"message": settings.app_name}
