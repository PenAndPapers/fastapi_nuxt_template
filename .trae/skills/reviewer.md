---
name: reviewer
description: Procedure for conducting code reviews, static security checks, and code quality audits. Trigger before finalizing a feature or PR.
---

# Code Review Procedure

## Step 1: Type & Syntax Checks
1. Run backend type checking: `mypy backend/`.
2. Run frontend type checking: `pnpm --filter frontend run typecheck`.

## Step 2: Code Audit Checklist
- [ ] No hardcoded API keys or secrets.
- [ ] All database queries are async and paginated where necessary.
- [ ] Pydantic DTO types match Frontend TypeScript interfaces.
- [ ] Error handlers provide standard HTTP status codes.

## Step 3: Output Feedback
Format audit findings cleanly:
- 🔴 **Critical:** Issues that break build, security, or data integrity.
- 🟡 **Warning:** Code smells or potential performance bottlenecks.
- 🟢 **Suggestion:** Refactoring or readability improvements.