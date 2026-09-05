---
name: tester
description: Standards for unit, integration, and end-to-end testing across backend (pytest) and frontend (vitest, playwright). Load when writing tests, configuring CI, or debugging flaky tests.
---

# Tester Skill Rules

## Test Pyramid
- **Unit (70%)**: Pure functions, services, composables, utilities.
- **Integration (20%)**: API endpoints, DB interactions, store actions.
- **E2E (10%)**: Critical user journeys (login, checkout, onboarding).

## Backend (pytest)
- **Structure**: `tests/unit/`, `tests/integration/`, `tests/e2e/`.
- **Fixtures**: `conftest.py` with `async_client`, `db_session`, `override_settings`.
- **Async**: Use `pytest-asyncio` (`@pytest.mark.asyncio`).
- **DB**: Testcontainers (Postgres) or transaction rollback per test.
- **Mocking**: `pytest-mock` / `unittest.mock` for external HTTP, Redis, email.
- **Coverage**: Target ≥ 80% (`pytest --cov=backend --cov-report=term-missing`).

## Frontend (Vitest + Playwright)
- **Unit (Vitest)**: Components, composables, Pinia stores, utils.
  - Mount with `@vue/test-utils` (`mount()`, `shallowMount()`).
  - Mock `useFetch`/`useAsyncData` via `vi.mock('#imports')`.
- **E2E (Playwright)**:
  - Tests in `tests/e2e/*.spec.ts`.
  - Page Object Models for reusable flows.
  - Run against built preview (`pnpm preview`) or dev server.
  - Trace on failure (`trace: 'on-first-retry'`).
- **Coverage**: `vitest --coverage` (v8 provider).

## Test Data & Factories
- Use **factory functions** (`createUser()`, `createPost()`) over static fixtures.
- Leverage `faker` for realistic random data.
- Isolate tests: no shared mutable state.

## CI Integration
- Run in GitHub Actions: `backend-test`, `frontend-test` jobs.
- Fail fast on lint/type errors before tests.
- Upload coverage artifacts (Codecov / GitHub Code Scanning).
- Flaky test detection: rerun failed tests once (`--reruns 1`).

## Debugging Flaky Tests
- Capture screenshots/videos (Playwright) / HTML (Vitest) on failure.
- Use `TRAE-debugger` skill for runtime inspection.
- Add `console.log` / `icecream` temporarily; remove before commit.

## Contract Testing
- Generate OpenAPI schema from FastAPI (`app.openapi()`).
- Validate frontend calls against schema (`schemathesis` / `zod`).
- Run as integration test in CI.

## Performance & Load
- Locust / k6 scripts in `tests/load/`.
- Run nightly; alert on regression > 10% p95 latency.