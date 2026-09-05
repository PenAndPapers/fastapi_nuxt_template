---
name: planner
description: Standards for feature specification, architecture decision records (ADRs), task breakdown, and milestone planning. Load when designing new features or refining requirements.
---

# Planner Skill Rules

## Specification Artifacts
- **`spec.md`**: Single source of truth for a feature.
  - Problem statement, user stories, acceptance criteria.
  - Data models, API contracts, UI sketches (text/mermaid).
  - Non-functional requirements (perf, security, a11y).
- **`checklist.md`**: Verifiable definition of done per story.
- **`tasks.md`**: Ordered, atomic tasks with owners & estimates (optional).

## Architecture Decision Records (ADRs)
- One markdown file per significant decision (`docs/adr/NNN-title.md`).
- Template: Context → Decision → Consequences → Alternatives.
- Link from `spec.md` and `CHANGELOG.md`.

## Planning Process
1. **Discover**: Read existing code, docs, ADRs.
2. **Clarify**: Use `AskUserQuestion` for ambiguities (max 4 Qs).
3. **Design**: Draft `spec.md` + `checklist.md`.
4. **Review**: `NotifyUser` with file paths for approval.
5. **Decompose**: Generate `tasks.md` (backend, frontend, infra, test).
6. **Execute**: Hand off to orchestrator/implementers.

## Estimation & Sizing
- Use **T-shirt sizes** (XS, S, M, L, XL) for tasks.
- Break M+ tasks into smaller subtasks.
- No time estimates; focus on scope & complexity.

## Prioritization
- **MoSCoW**: Must, Should, Could, Won't.
- Tag tasks in `tasks.md` with priority.
- Align with product roadmap / sprint goals.

## Change Management
- Scope changes → new ADR + updated `spec.md`.
- Re-run `NotifyUser` for approval before implementation.
- Track in `CHANGELOG.md` (Keep a Changelog format).

## Documentation Standards
- Write for **future maintainers**, not just current team.
- Diagrams as Mermaid (renderable in GitHub/GitLab).
- Link cross-references: `[spec.md](file:///.../spec.md)`.