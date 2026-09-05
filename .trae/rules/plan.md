---
alwaysApply: false
description: Technical planning, feature specifications, architecture design, and requirement breakdowns.
globs:
  - "docs/plans/**/*.md"
  - "docs/specs/**/*.md"
---

# Technical Planner Rules

## Task Decomposition
- Break incoming feature requests into atomic, verifiable implementation steps.
- Define explicit input/output contracts between Backend, Frontend, and Infrastructure layers.

## Deliverables
- Output clear, lightweight spec documents in `docs/plans/` or direct markdown briefs before code generation.
- Detail data schemas, endpoints, component hierarchies, and environment requirements upfront.
- Identify potential breaking changes or migration risks early.