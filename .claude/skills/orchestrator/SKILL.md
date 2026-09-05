---
name: orchestrator
description: Standards for task decomposition, agent coordination, workflow routing, and multi-step execution. Load when planning complex features, breaking down large tasks, or executing multi-role workflows.
---

# Orchestrator Skill Rules

## Workflow Routing
- Map incoming user intent to the appropriate skill domain (`frontend`, `backend`, `devops`, `qa-testing`).
- Use domain skills on demand; do not mix domain-specific code implementation into orchestration planning.
- When sub-agents or specialized sub-tasks are needed, provide clear, isolated context boundaries.

## Task Decomposition
- Break large requests into atomic, verifiable, sequential phases (e.g., Plan → Backend → Frontend → QA).
- Clearly define inputs, outputs, and completion criteria for each phase.
- Keep execution steps focused to prevent context clutter.

## Agent & Task Coordination
- Structure sub-tasks with detailed, self-contained prompts.
- Explicitly pass required file paths, technical constraints, expected outputs, and test/verification commands.
- Synthesize findings from sub-tasks into a concise final summary for the user.

## State & Progress Management
- Maintain execution plans directly in Markdown documents (e.g., `docs/plans/` or issue tracking) when handling complex tasks.
- Avoid relying on global persistent state; state context explicitly within project documentation or task briefs.

## Error Handling & Recovery
- If a step or sub-agent execution fails, analyze error outputs, adjust parameters or code, and attempt a fix.
- Escalate to the user if a step fails repeatedly after targeted fix attempts, providing a clear summary of the blockage.
- Never silently swallow build, test, or lint errors.

## Execution Quality Gates
- Before marking a feature phase complete, trigger the relevant validation:
  - **Planning Phase:** Request user confirmation before proceeding to heavy implementation.
  - **Backend:** Run configured linters, type checkers, and backend test suites (e.g., `pytest`).
  - **Frontend:** Run UI linters, type checks, and component build tests.
  - **DevOps:** Validate container and infrastructure configs (e.g., `docker compose config`).
  - **QA / Testing:** Execute automated test suites (e.g., unit, integration, or end-to-end tests).