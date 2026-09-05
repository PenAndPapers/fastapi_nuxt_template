---
alwaysApply: false
description: Rules for code audits, performance analysis, security checks, and code quality compliance.
globs:
  - "**/*.py"
  - "**/*.vue"
  - "**/*.ts"
  - "**/*.js"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.json"
  - "**/*.md"
---

# Code Reviewer Rules

## Quality & Security Audit
- Verify type safety (`mypy` for Python, `vue-tsc` / TypeScript for Vue).
- Check for security issues: unhandled input sanitization, exposed secrets, SQL injection risks, or broken authorization checks.
- Enforce strict adherence to project code style, modularity, and naming conventions.

## Feedback Format
- Categorize issues by severity: **Critical**, **Warning**, or **Suggestion**.
- Provide actionable code snippets for suggested corrections.