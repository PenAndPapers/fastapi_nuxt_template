# Backend — FastAPI

## Folder Structure

```
backend/fastapi/
├── api/                    # API route handlers
│   ├── modules/             # Feature modules (auth, user, etc.)
│   │   ├── auth/            # Authentication logic
│   │   │   ├── router.py    # Auth endpoints
│   │   │   ├── model.py     # Auth SQLAlchemy models
│   │   │   ├── schema.py    # Pydantic schemas
│   │   │   ├── dependency.py # FastAPI dependencies
│   │   │   └── exception.py # Auth-specific exceptions
│   │   └── user/            # User endpoints
│   └── health.py            # Health check endpoint
│
├── core/                   # Core application setup
│   ├── config.py            # Pydantic settings (env vars)
│   └── database.py          # SQLAlchemy engine & session
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
├── helpers/                # Shared helper utilities
├── utils/                  # Shared pure utilities
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
| `api/modules/{module}/schema.py` | Request/response validation schemas |
| `api/modules/{module}/model.py` | SQLAlchemy ORM models |
| `migrations/versions/*.py` | Alembic migration scripts |
| `pyproject.toml` | Project metadata & dependencies |

---

## Module Pattern

Each feature module follows a consistent structure:

- **`router.py`** — FastAPI route handlers (`@router.post()`, `@router.get()`, etc.)
- **`schema.py`** — Pydantic `BaseModel` classes for request/response validation
- **`model.py`** — SQLAlchemy ORM model classes
- **`dependency.py`** — FastAPI `Depends()` dependencies (auth, DB session)
- **`exception.py`** — Custom HTTP exceptions for the module
