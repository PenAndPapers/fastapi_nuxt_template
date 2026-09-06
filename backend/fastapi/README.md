# Backend — FastAPI

## Folder Structure

```
backend/fastapi/
├── api/                    # API route handlers
│   ├── modules/             # Feature modules (auth, user, etc.)
│   │   ├── auth/            # Authentication logic
│   │   │   ├── router.py    # Auth endpoints
│   │   │   ├── dependency.py # FastAPI dependencies
│   │   │   ├── service.py   # Business logic for the module
│   │   │   ├── repository.py # Database access layer logic for the module
│   │   │   ├── model.py     # Auth SQLAlchemy models
│   │   │   ├── schema.py    # Pydantic schemas, DTOs
│   │   │   └── exception.py # Custom HTTP exceptions for the module
│   │   └── user/            # User endpoints
│   └── health.py            # Health check endpoint
│
├── core/                   # Core application setup
│   ├── config.py            # Pydantic settings (env vars)
│   ├── base_model.py        # Base model for ORM entities
│   ├── database.py          # SQLAlchemy engine & session
│   └── exception.py         # Custom HTTP exceptions for the module
│
├── migrations/             # Alembic database migrations
│   ├── versions/           # Versioned migration scripts
│   ├── env.py              # Migration environment config
│   └── script.py.mako      # Migration template
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── e2e/                # End-to-end tests
│   └── conftest.py         # pytest fixtures
│
├── utils/                  # Shared helper utilities
├── main.py                 # FastAPI application entry point
├── pyproject.toml          # Python dependencies (uv)
├── alembic.ini             # Alembic configuration
└── Makefile               # Dev convenience commands
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app factory — includes routers, middleware |
| `core/config.py` | Centralized settings via `pydantic-settings` |
| `core/database.py` | SQLAlchemy engine, `Base`, `SessionLocal`, `get_db` |
| `api/modules/{module}/router.py` | Route definitions per feature |
| `api/modules/{module}/dependency.py` | FastAPI `Depends()` dependencies |
| `api/modules/{module}/service.py` | Business logic for the module |
| `api/modules/{module}/repository.py` | Database access layer logic for the module |
| `api/modules/{module}/schema.py` | Request/response validation schemas, DTOs |
| `api/modules/{module}/model.py` | SQLAlchemy ORM models |
| `api/modules/{module}/exception.py` | Custom HTTP exceptions for the module |
| `migrations/versions/*.py` | Alembic migration scripts |
| `pyproject.toml` | Project metadata & dependencies |

---

## Module Pattern

Each feature module follows a consistent structure:

- **`router.py`** — FastAPI route handlers (`@router.post()`, `@router.get()`, etc.)
- **`dependency.py`** — FastAPI `Depends()` dependencies (auth, DB session)
- **`service.py`** — Business logic for the module
- **`repository.py`** — Database access layer logic for the module
- **`schema.py`** — Pydantic `BaseModel` classes for request/response validation, DTOs
- **`model.py`** — SQLAlchemy ORM model classes
- **`exception.py`** — Custom HTTP exceptions for the module
