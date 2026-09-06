PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE

PY := PYTHONDONTWRITEBYTECODE=1 uv run

.PHONY: setup install env-copy dev lint lint-fix test test-watch migrate-create migrate-up migrate-down migrate-logs migrate-check db-shell clean docker-build docker-run docker-test docker-shell docker-clean


install:
	uv sync

update-deps:
	uv lock --upgrade
	uv sync

lint:
	uv run ruff check . --no-cache

lint-fix:
	uv run ruff check . --fix --no-cache
	uv run ruff format .

migrate-create:
	@read -p "Enter migration message: " msg && \
	uv run alembic revision --autogenerate -m "$$msg"

migrate-up:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-logs:
	uv run alembic history --verbose

migrate-check:
	uv run alembic current


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

# --------------------------------------------------------------------
# Docker targets (run inside container via docker compose)
# --------------------------------------------------------------------

docker-build: ## Build backend Docker image
	@echo "▶ Building backend Docker image..."
	@docker compose build backend
	@echo "✅ Backend Docker image built."

docker-run: ## Run backend in Docker (detached)
	@echo "▶ Starting backend container..."
	@docker compose up -d backend
	@echo "✅ Backend container started on http://localhost:8000"

docker-test: ## Run backend tests in Docker
	@echo "▶ Running backend tests in Docker..."
	@docker compose exec backend python -m pytest tests -v
	@echo "✅ Backend tests completed."

docker-shell: ## Open shell in backend container
	@echo "▶ Opening shell in backend container..."
	@docker compose exec backend /bin/bash

docker-clean: ## Stop and remove backend container
	@echo "▶ Stopping backend container..."
	@docker compose down backend
	@echo "✅ Backend container stopped."
