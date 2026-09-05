---
name: backend
description: Step-by-step procedure for implementing FastAPI routes, SQLAlchemy models, and Alembic migrations. Trigger when adding or updating backend code.
---

# Backend Implementation Procedure

## Step 1: Database Migration (if applicable)
1. Define/update models in `backend/app/models/`.
2. Generate migration script: `alembic revision --autogenerate -m "description"`.
3. Apply migration: `alembic upgrade head`.

## Step 2: Schemas & Services
1. Create Pydantic v2 schemas in `backend/app/schemas/`.
2. Add business logic inside `backend/app/services/`.

## Step 3: Route Handlers
1. Define route in `backend/app/api/v1/endpoints/`.
2. Wire dependencies (e.g., DB session, authentication).
3. Verify endpoint using `pytest backend/tests/`.