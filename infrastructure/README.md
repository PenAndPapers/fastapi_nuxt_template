# Infrastructure

This directory contains Docker configuration for the FastAPI + Nuxt 4 template.

## Services

The `docker-compose.yml` file orchestrates the following services:

| Service | Description | Default Port |
|---------|-------------|--------------|
| **postgres** | PostgreSQL 17 database | 5432 |
| **redis** | Redis 7 cache (password-protected) | 6379 |
| **mailpit** | Email testing server | 1025 (SMTP), 8025 (UI) |
| **backend** | FastAPI Python application | 8000 |
| **frontend** | Nuxt 4 application (production build) | 3000 |
| **nginx** | Reverse proxy / gateway | 8080 |

## Quick Start

### 1. Copy environment file

```bash
cp .env.example .env
```

Edit `.env` to customize ports, credentials, and other settings.

### 2. Build and start all services

```bash
# Via Makefile
make docker-up

# Or directly
docker compose up -d --build
```

### 3. Apply database migrations

```bash
make docker-migrate-up
# Or
docker compose exec backend alembic upgrade head
```

### 4. Check service health

```bash
make docker-health
# Or
docker compose ps
```

## Access Points

- **Frontend (Nuxt 4)**: http://localhost:3000
- **Backend (FastAPI)**: http://localhost:8000
- **Nginx Gateway**: http://localhost:8080
- **Mailpit UI**: http://localhost:8025
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Common Commands

```bash
# Start services (detached)
make docker-up

# Start services with logs (foreground)
make docker-up-logs

# Stop services (preserves data volumes)
make docker-down

# Stop services and remove all data (DESTRUCTIVE)
make docker-down-volumes

# Force rebuild all services
make docker-rebuild

# Restart services
make docker-restart

# View logs
make docker-logs              # All services
make docker-logs-backend      # Backend only
make docker-logs-frontend     # Frontend only

# Open shells
make docker-shell-backend     # Backend container
make docker-shell-frontend    # Frontend container
make docker-shell-db          # PostgreSQL shell

# Database migrations
make docker-migrate-up        # Apply migrations
make docker-migrate-down      # Rollback last migration

# Clean up
make docker-clean             # Stop and remove everything
```

## Environment Variables

See [`.env.example`](../.env.example) for all available configuration options. The file uses sensible defaults for development.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Nginx     │────▶│   Backend    │────▶│  PostgreSQL  │
│  (8080)     │     │   (8000)     │     │   (5432)     │
└─────────────┘     └──────────────┘     └──────────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │    Redis     │
                    │    (6379)    │
                    └──────────────┘
┌──────────────┐
│   Frontend   │
│   (3000)     │
└──────────────┘
```

Nginx serves as the single entry point, proxying API requests to the backend and serving the static Nuxt build.