---
name: backend-engineer
description: Standards for FastAPI, SQLAlchemy, Pydantic, async patterns, database migrations, API design, authentication, and testing. Load when building APIs, services, or data-layer logic.
---

# Backend Skill Rules

## Architecture & Patterns
- Use **FastAPI** with modular routers (`api/modules/{domain}/router.py`).
- Follow **Clean Architecture**: `api/` (handlers) → `core/` (config/db) → `models/` (SQLAlchemy) → `schemas/` (Pydantic).
- Prefer **dependency injection** for DB sessions, settings, and services.
- Keep business logic in **service layers**, not in route handlers.

## Database (SQLAlchemy + Alembic)
- Use `asyncpg` driver with `postgresql+asyncpg://` URLs.
- Define models inheriting from `Base` in `core/database.py`.
- Run migrations via `alembic upgrade head` in CI/CD.
- Use `pool_pre_ping=True` for resilience.

## API Design
- Version APIs under `/api/v1/` prefix (configurable via `settings.api_prefix`).
- Return consistent error shapes: `{ "detail": "...", "code": "ERROR_CODE" }`.
- Use Pydantic `BaseModel` for request/response validation.
- Document with OpenAPI tags per module.

## Authentication & Authorization
- JWT tokens via `python-jose` / `passlib`.
- Store password hashes with `bcrypt`.
- Protect routes with `Depends(get_current_user)`.
- Implement RBAC via scopes/roles in token payload.

## Async & Performance
- Use `async def` for I/O-bound endpoints.
- Leverage `asyncpg` connection pooling.
- Avoid blocking calls in async functions.
- Use `background_tasks` for fire-and-forget work.

## Configuration
- Centralize settings in `core/config.py` using `pydantic-settings`.
- Load from `.env` + environment variables.
- Never hardcode secrets.

## Testing
- Unit tests in `tests/unit/`, integration in `tests/integration/`.
- Use `pytest-asyncio` for async tests.
- Mock external services; use testcontainers for Postgres/Redis.

## Code Quality
- Lint with `ruff` (line-length 100, target py312).
- Type-check with `mypy --strict`.
- Format with `ruff format`.