---
alwaysApply: false
description: Best practices for Python, FastAPI, SQLAlchemy, and PostgreSQL backend development.
globs:
  - "backend/fastapi/**/*.py"
---

# Backend Rules (FastAPI + PostgreSQL)

## Architecture & Code Standards
- Use **FastAPI** with strict **Pydantic v2** schemas for request validation and response models.
- Keep route handlers lean; isolate core logic inside service layers.
- Perform database operations asynchronously using **SQLAlchemy 2.0** or **SQLModel**.
- Follow test-driven development (TDD) practices for unit testing.

## Database & API Design
- Follow RESTful conventions for endpoint path structure and status codes.
- Implement explicit pagination (`limit`, `offset`) on all collection endpoints.
- Generate and apply Alembic migrations for any database schema updates.