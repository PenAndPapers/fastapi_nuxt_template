---
alwaysApply: false
description: Best practices for FastAPI, SQLAlchemy, and PostgreSQL modular backend architecture.
globs:
  - "backend/fastapi/**/*.py"
---

# Backend Rules (FastAPI + PostgreSQL)

## Layered Architecture & Separation of Concerns
- **Routes (`backend/fastapi/api/modules/*/router.py`)**: Lean HTTP endpoints. Handle request parsing, call services/dependencies, and return response models. Never write database queries or core business logic in routes.
- **Dependencies (`backend/fastapi/api/modules/*/dependency.py`)**: Use FastAPI `Depends` with `yield` to inject scoped database sessions (`AsyncSession`), wire `Repository` into `Service`, and inject `Service` into route handlers.
- **Services (`backend/fastapi/api/modules/*/service.py`)**: Encapsulate all core business logic and multi-step transaction orchestrations. Call repositories for data operations.
- **Repositories (`backend/fastapi/api/modules/*/repository.py`)**: Encapsulate all database access methods using **SQLAlchemy 2.0** or **SQLModel**. Keep operations purely focused on query execution without business decisions.
- **Schemas (`backend/fastapi/api/modules/*/schemas.py`)**: Strict **Pydantic v2** DTOs for request validation (`CreateUserRequest`) and response serialization (`UserResponse`). Never expose database ORM models directly in API responses.
- **Models (`backend/fastapi/api/modules/*/models.py`)**: Pure **SQLAlchemy 2.0** or **SQLModel** ORM entity declarations. Defines database tables and relationships. Do not write raw SQL or database query handlers inside model classes.

## Asynchronous Database Operations
- Enforce fully async I/O using SQLAlchemy 2.0 (`async_sessionmaker`, `select()`, `await session.execute()`).
- Keep transaction boundaries explicit: commit transactions at the service or request level, avoiding auto-commits inside low-level helper queries.
- Prevent blocking the asyncio event loop by avoiding synchronous database drivers or `time.sleep()` calls inside `async def` routes.

## Testing & Quality Control
- Follow Test-Driven Development (TDD) practices: write unit and integration test cases in `tests/` alongside feature additions.
- Use `pytest-asyncio` and an isolated test database (or transaction rollback fixtures) for API endpoint tests.