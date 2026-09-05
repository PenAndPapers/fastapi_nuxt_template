---
name: tester
description: Step-by-step guide for writing and running unit, integration, and API tests. Trigger when writing or running test suites.
---

# QA Testing Procedure

## Step 1: Backend API Tests
1. Add endpoint tests under `backend/tests/api/`.
2. Test both success paths and edge cases (`400`, `401`, `404`, `422`).
3. Execute tests: `pytest -v`.

## Step 2: Frontend Tests
1. Add component/unit tests using Vitest/Playwright under `frontend/tests/`.
2. Execute tests: `pnpm test`.

## Step 3: Test Report
Summarize test execution results including total passed, failed, and unhandled edge cases.