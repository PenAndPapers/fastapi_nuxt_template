PYTHONDONTWRITEBYTECODE := 1
export PYTHONDONTWRITEBYTECODE

PY := PYTHONDONTWRITEBYTECODE=1 uv run

.PHONY: setup install env-copy dev lint lint-fix test test-watch migrate-create migrate-up migrate-down db-shell clean

setup: install env-copy
	@echo ""
	@echo "✅✅ Backend setup complete ✅✅"
	@echo "   Next steps:"
	@echo "   1. Update .env with your PostgreSQL credentials"
	@echo "   2. Run 'make migrate-up' to apply migrations"
	@echo "   3. Run 'make dev' to start the dev server"

install:
	@echo ""
	@echo "💻 Installing dependencies with uv..."
	@echo ""
	uv sync --all-groups
	@echo ""
	@echo "✅ Dependencies installed successfully"
	@echo ""

env-copy:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Copied .env.example -> .env"; \
	else \
		echo "⚠️ .env already exists, skipping copy"; \
	fi

update-deps:
	@echo "💻 Updating and syncing all dependencies..."
	uv lock --upgrade && uv sync --all-groups
	@echo "✅ Dependencies updated successfully"

dev:
	$(PY) uvicorn main:app --reload --host 0.0.0.0 --port 8000

lint:
	$(PY) ruff check .

lint-fix:
	$(PY) ruff check --fix .
	$(PY) ruff format .

test:
	$(PY) pytest tests -v

test-watch:
	$(PY) pytest tests -v --watch

migrate-create:
	$(PY) alembic revision --autogenerate -m "$(msg)"

migrate-up:
	$(PY) alembic upgrade head

migrate-down:
	$(PY) alembic downgrade -1

db-shell:
	$(PY) python -c "from core.database import SessionLocal; db = SessionLocal(); print('Connected. Use `db` session.')"

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
