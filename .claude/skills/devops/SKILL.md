---
name: devops-engineer
description: Standards for Docker, Docker Compose, GitHub Actions CI/CD, infrastructure as code, monitoring, and deployment. Load when configuring pipelines, containers, or cloud resources.
---

# DevOps Skill Rules

## Containerization (Docker)
- Use **multi-stage builds**: builder → production.
- Pin base image digests (e.g., `python:3.12-slim@sha256:...`).
- Install only runtime deps in final stage (`libpq5`, `curl`).
- Create non-root user (`useradd -m app`).
- Set `HEALTHCHECK` for every service.
- Use `.dockerignore` to exclude `.git`, `__pycache__`, `node_modules`, `.env`.

## Docker Compose
- Define **networks** (e.g., `backend`) for service isolation.
- Use **volumes** for persistent data (`postgres_data`, `redis_data`).
- Wire **healthchecks** with `depends_on: condition: service_healthy`.
- Inject config via **environment variables** (`.env` file).
- Map ports via `${VAR:-default}` for flexibility.

## CI/CD (GitHub Actions)
- Workflow: `lint` → `test` → `build` → `deploy`.
- Cache `uv`/`pip` and `pnpm` dependencies.
- Run `ruff`, `mypy`, `pytest` in `backend` job.
- Run `pnpm lint`, `pnpm typecheck`, `pnpm test` in `frontend` job.
- Build & push Docker images on `main` tag.
- Deploy via `docker compose` on target host (or Kubernetes manifests).

## Infrastructure as Code
- Prefer **Terraform** or **Pulumi** for cloud resources.
- Store state remotely with locking.
- Use modules for VPC, RDS, Redis, LB, DNS.

## Secrets Management
- Never commit secrets. Use GitHub Environments / Vault / AWS Secrets Manager.
- Inject at runtime via `env_file` or orchestrator secrets.

## Observability
- Structured JSON logs (`log_format main` in Nginx).
- Health endpoints: `/health` (liveness), `/ready` (readiness).
- Metrics: Prometheus `/metrics` (FastAPI `prometheus-fastapi-instrumentator`).
- Tracing: OpenTelemetry → Jaeger/Tempo.

## Security
- Scan images with `trivy`/`grype` in CI.
- Run containers read-only rootfs where possible.
- Drop capabilities (`--cap-drop=ALL`).
- Enforce `Content-Security-Policy` via Nginx.

## Rollout Strategy
- Blue/Green or Rolling updates via Compose/Swarm/K8s.
- Automated rollback on healthcheck failure.
- Canary via weighted routing (Nginx/Traefik).