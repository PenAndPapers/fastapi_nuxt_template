---
name: infra
description: Procedure for managing Docker containers, docker-compose services, and local dev environments. Trigger when updating Dockerfiles or environment configs.
---

# Infrastructure & DevOps Procedure

## Step 1: Environment & Config Validation
1. Verify required environment variables are listed in `.env.example`.
2. Ensure secrets are never hardcoded.

## Step 2: Container Updates
1. Edit target `Dockerfile` or `docker-compose.yml`.
2. Run validation check: `docker compose config`.

## Step 3: Local Environment Test
1. Rebuild and start container services: `docker compose up --build -d`.
2. Inspect logs to confirm services are healthy: `docker compose logs -f`.