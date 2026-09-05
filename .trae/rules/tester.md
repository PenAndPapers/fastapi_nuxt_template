---
alwaysApply: false
description: Guidelines for unit testing, API test suites, and end-to-end testing setups.
globs:
  - "**/tests/**/*.py"
  - "**/*.spec.ts"
  - "**/*.test.ts"
---

# Tester Rules (QA & Automation)

## Test Coverage Standards
- Write automated tests for all core business logic and new API endpoints.
- Test happy paths alongside edge cases (`400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Validation Error`).

## Execution Commands
- **Backend Tests:** `pytest -v`
- **Frontend / Integration Tests:** `pnpm test`
- Ensure mock fixtures accurately reflect production database models and schemas.