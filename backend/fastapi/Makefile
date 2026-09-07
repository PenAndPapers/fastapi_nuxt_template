PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE

PY := PYTHONDONTWRITEBYTECODE=1 uv run

.PHONY: check-prerequisites require-backend-running install update-deps lint lint-fix test test-unit test-integration test-e2e migrate-create migrate-upgrade migrate-downgrade migrate-history migrate-current migrate-pending build up down shell clean reset-db reset-db-force

# Migration targets depend on docker prerequisites being installed
MIGRATION_PREREQS = check-prerequisites require-backend-running


check-prerequisites: ## Check for required software
	@command -v docker >/dev/null 2>&1 || { echo >&2 "❌ docker is not installed. Please install Docker."; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo >&2 "❌ docker compose is not installed. Please install Docker Compose."; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo >&2 "❌ uv is not installed. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@command -v python >/dev/null 2>&1 || { echo >&2 "❌ python is not installed. Please install Python 3.11+. or higher version."; exit 1; }
	@if [ ! -f .env ] && [ ! -f ../../.env ]; then \
		echo >&2 "❌ .env file not found. Create one at the project root from .env.example:"; \
		echo >&2 "   cp .env.example .env"; \
		exit 1; \
	fi
	@echo ""
	@echo "✅ All backend prerequisites are installed."
	@echo ""


require-backend-running: ## Internal: verify the backend container is up
	@docker compose ps --status running --services 2>/dev/null | grep -q '^backend$$' || { \
		echo "" >&2; \
		echo "❌ Backend container is not running." >&2; \
		echo "   Start the stack first:" >&2; \
		echo "     docker compose up -d postgres redis backend" >&2; \
		echo "" >&2; \
		exit 1; \
	}


install: check-prerequisites
	uv sync

update-deps: check-prerequisites
	uv lock --upgrade
	uv sync

lint:
	uv run ruff check . --no-cache

lint-fix:
	uv run ruff check . --fix --no-cache
	uv run ruff format . --no-cache

# --------------------------------------------------------------------
# Migrations (Docker-first)
# Use these targets to manage Alembic migrations. They run inside the
# backend container so the database host resolves correctly.
# Ensure the stack is up before invoking these:
#   docker compose up -d postgres redis
# --------------------------------------------------------------------

migrate-create: $(MIGRATION_PREREQS) ## Create a new Alembic migration inside the backend service
	@read -p "Enter migration message: " msg && \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"

migrate-upgrade: $(MIGRATION_PREREQS) ## Apply migrations inside the backend service
	@echo "▶ Applying migrations inside the backend service..."
	docker compose exec backend alembic upgrade head

migrate-downgrade: $(MIGRATION_PREREQS) ## Roll back the last migration inside the backend service
	@echo "▶ Rolling back the last migration inside the backend service..."
	docker compose exec backend alembic downgrade -1

migrate-history: $(MIGRATION_PREREQS) ## Show migration history inside the backend service
	@echo "▶ Showing migration history inside the backend service..."
	docker compose exec backend alembic history --verbose

migrate-current: $(MIGRATION_PREREQS) ## Show the current migration inside the backend service
	@echo "▶ Showing the current migration inside the backend service..."
	docker compose exec backend alembic current

migrate-pending: $(MIGRATION_PREREQS) ## Show pending migrations (head vs current) inside the backend service
	@echo "▶ Showing pending migrations (head vs current) inside the backend service..."
	docker compose exec backend alembic heads

generate-signing-key: ## Generate a new ES256 key pair in /app/certs
	@echo "▶ Generating new ES256 signing keys..."
	@docker compose exec -u root backend sh -c '\
		if [ -f /app/certs/private_key.pem ]; then \
			echo "⚠️ Error: /app/certs/private_key.pem already exists! Remove or backup manually to avoid invalidating active sessions."; \
			exit 1; \
		fi; \
		mkdir -p /app/certs && \
		openssl ecparam -name prime256v1 -genkey -noout -out /app/certs/private_key.pem && \
		openssl ec -in /app/certs/private_key.pem -pubout -out /app/certs/public_key.pem && \
		chmod 600 /app/certs/private_key.pem && \
		chmod 644 /app/certs/public_key.pem \
	'
	@echo "✅ New signing keys generated in /app/certs"

# --------------------------------------------------------------------
# Unit Tests
# Test run in Docker container with pytest
# --------------------------------------------------------------------

test: $(MIGRATION_PREREQS) ## Run backend tests in Docker
	@echo "▶ Running backend tests in Docker..."
	docker compose exec backend python -m pytest tests -v
	@echo "✅ Backend tests completed."

test-unit: $(MIGRATION_PREREQS) ## Run backend unit tests in Docker
	@echo "▶ Running backend unit tests in Docker..."
	docker compose exec backend python -m pytest tests/unit -v
	@echo "✅ Backend unit tests completed."

test-integration: $(MIGRATION_PREREQS) ## Run backend integration tests in Docker
	@echo "▶ Running backend integration tests in Docker..."
	docker compose exec backend python -m pytest tests/integration -v
	@echo "✅ Backend integration tests completed."

test-e2e: $(MIGRATION_PREREQS) ## Run backend end-to-end tests in Docker
	@echo "▶ Running backend end-to-end tests in Docker..."
	docker compose exec backend python -m pytest tests/e2e -v
	@echo "✅ Backend end-to-end tests completed."

# --------------------------------------------------------------------
# Docker targets (run inside container via docker compose)
# --------------------------------------------------------------------

build: ## Build backend Docker image
	@echo "▶ Building backend Docker image..."
	@docker compose build backend --no-cache
	@echo "✅ Backend Docker image built."

up: ## Run backend in Docker (detached)
	@echo "▶ Starting backend container..."
	@docker compose up -d backend
	@echo "✅ Backend container started on http://localhost:8000"

down: ## Stop and remove backend container
	@echo "▶ Stopping backend container..."
	@docker compose down backend
	@echo "✅ Backend container stopped."

shell: ## Open shell in backend container
	@echo "▶ Opening shell in backend container..."
	@docker compose exec backend /bin/bash

# --------------------------------------------------------------------
# ⚠️⚠️⚠️ DESTRUCTIVE commands, make sure you know what you're doing!
# Use only for development. Data loss is permanent. Use with caution!
# --------------------------------------------------------------------

clean:
	@echo ""
	@echo "🧹 Cleaning backend artifacts..."
	@echo ""
	find . -name __pycache__ -type d -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -not -path './.venv/*' -delete 2>/dev/null || true
	rm -rf .venv .pytest_cache .ruff_cache .env
	@echo ""
	@echo "✅ Backend artifacts cleaned successfully"
	@echo ""


reset-db: check-prerequisites ## ⚠️  Destroy DB + redis volumes and reinitialize (prompts for confirmation)
	@echo ""
	@echo "⚠️  This will DESTROY all data in the postgres and redis volumes."
	@echo "   Use only for development. Data loss is permanent."
	@echo ""
	@read -p "Are you sure? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "▶ Stopping stack and removing volumes..."; \
		docker compose down -v; \
		echo "▶ Reinitializing postgres and redis..."; \
		docker compose up -d postgres redis; \
		echo ""; \
		echo "✅ Database reset complete."; \
		echo "ℹ️  Next: docker compose up -d backend"; \
		echo ""; \
	else \
		echo "Cancelled."; \
	fi

reset-db-force: check-prerequisites ## ⚠️  Like reset-db but skips the confirmation prompt (CI/scripts)
	@echo "▶ Force-resetting database volumes..."
	@docker compose down -v
	@docker compose up -d postgres redis
	@echo ""
	@echo "✅ Database reset complete."
	@echo "ℹ️  Next: docker compose up -d backend"
	@echo ""
