---
alwaysApply: false
description: Rules for Docker, container orchestration, environment setups, and deployment configs.
globs:
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/.env*"
  - "**/Makefile*"
---

# Infrastructure Rules (Docker + DevOps)

## Containerization
- Build minimal production images using **multi-stage Dockerfiles**.
- Maintain local development setups in `docker-compose.yml` with support for volume mounts and live-reloading across services (FastAPI, Nuxt, PostgreSQL).

## Security & Environment
- Never hardcode credentials, API keys, or database URIs in source files.
- Inject all configurations strictly via `.env` files and runtime environment variables.