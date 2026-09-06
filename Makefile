SHELL := /bin/bash

# --------------------------------------------------------------------
# Color helpers
# --------------------------------------------------------------------
_RESET  := \033[0m
_BOLD   := \033[1m
_INFO   := \033[36m$(_BOLD)
_OK     := \033[32m$(_BOLD)
_WARN   := \033[33m$(_BOLD)
_ERR    := \033[31m$(_BOLD)

# --------------------------------------------------------------------
# Project paths
# --------------------------------------------------------------------
FRONTEND_DIR := frontend/nuxt4
BACKEND_DIR  := backend/fastapi

# --------------------------------------------------------------------
# Enforced tool versions (keep in sync with README.md prerequisites)
# --------------------------------------------------------------------
NODE_MAJOR_REQUIRED := 22

# --------------------------------------------------------------------
# Default target
# --------------------------------------------------------------------
.DEFAULT_GOAL := help

.PHONY: help \
        frontend-check frontend-install frontend-prepare frontend-dev \
        frontend-build frontend-preview frontend-generate \
        frontend-typecheck frontend-lint frontend-lint-fix \
        frontend-format frontend-format-check frontend-clean \
        backend-check backend-dev backend-update-deps \
        backend-lint-fix backend-test backend-test-watch \
        backend-migrate-create backend-migrate-up backend-migrate-down \
        setup-frontend setup-backend setup-project \
        docker-up docker-down docker-rebuild docker-logs docker-ps \
        docker-migrate-up docker-migrate-down docker-health \
        docker-build docker-test docker-shell-backend docker-shell-frontend docker-clean \
        dev-up clean-project

# ========================================================
# Help
# ========================================================
help: ## Show this help message
	@echo -e ""
	@echo -e "$(_INFO)FastAPI Nuxt Template — available Make targets$(_RESET)"
	@echo -e ""
	@echo -e "$(_BOLD)Frontend targets:$(_RESET)"
	@grep -E '^[a-zA-Z_-]+.*:.*##' $(MAKEFILE_LIST) \
		| grep '^frontend-' \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  $(_OK)%-22s$(_RESET) %s\n", $$1, $$2}'
	@echo -e ""
	@echo -e "$(_BOLD)Backend targets:$(_RESET)"
	@grep -E '^[a-zA-Z_-]+.*:.*##' $(MAKEFILE_LIST) \
		| grep -v '^frontend-' \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  $(_OK)%-22s$(_RESET) %s\n", $$1, $$2}'
	@echo -e ""

# ========================================================
# Frontend commands (delegated to frontend/nuxt4/Makefile)
# ========================================================
frontend-check: ## Verify Node 22.x LTS + pnpm are installed (fail-fast)
	@if [ ! -f $(FRONTEND_DIR)/Makefile ]; then \
		echo "$(_ERR)❌ $(FRONTEND_DIR)/Makefile not found$(_RESET)"; \
		exit 1; \
	fi
	@cd $(FRONTEND_DIR) && make dev-check

frontend-install: frontend-check ## Install frontend deps (skips if lockfile unchanged)
	@cd $(FRONTEND_DIR) && make dev-install

frontend-prepare: frontend-install ## Run `nuxt prepare` (generates .nuxt + types)
	@cd $(FRONTEND_DIR) && make dev-prepare

frontend-dev: frontend-prepare ## Start Nuxt 4 dev server (http://localhost:3000)
	@cd $(FRONTEND_DIR) && make dev

frontend-build: frontend-prepare ## Build the frontend for production (.output/)
	@cd $(FRONTEND_DIR) && make build

frontend-preview: frontend-build ## Preview production build on http://localhost:3000
	@cd $(FRONTEND_DIR) && make preview

frontend-generate: frontend-prepare ## Generate static site (SSG output)
	@cd $(FRONTEND_DIR) && make generate

frontend-typecheck: frontend-prepare ## Run Nuxt type checking (vue-tsc)
	@cd $(FRONTEND_DIR) && make typecheck

frontend-lint: frontend-install ## Run ESLint (writes no-fix output, non-zero on lint errors)
	@cd $(FRONTEND_DIR) && make lint

frontend-lint-fix: frontend-install ## Run ESLint with --fix (auto-fixable issues only)
	@cd $(FRONTEND_DIR) && make lint-fix

frontend-format: frontend-install ## Run Prettier (rewrite files in place)
	@cd $(FRONTEND_DIR) && make format

frontend-format-check: frontend-install ## Run Prettier in check-only mode (CI, returns non-zero on unformatted files)
	@cd $(FRONTEND_DIR) && make format-check

frontend-clean: ## Remove generated Nuxt artifacts + node_modules
	@echo -e "$(_WARN)▶ Cleaning frontend artifacts…$(_RESET)"
	@cd $(FRONTEND_DIR) && make clean

# ========================================================
# Backend commands (delegated to backend/fastapi/Makefile)
# ========================================================

backend-clean:
	@cd $(BACKEND_DIR) && make clean

# ========================================================
# Project setup
# ========================================================

setup-frontend: frontend-prepare ## Full first-run frontend setup: check → install → prepare
	@echo -e "$(_OK)✅ Frontend setup complete. Run 'make frontend-dev' to start the dev server.$(_RESET)"

setup-backend: backend-check ## Full first-run backend setup: install → env → dev → test
	@echo -e "$(_OK)✅ Backend setup complete. Run 'make backend-dev' to start the dev server.$(_RESET)"

setup-project: setup-frontend setup-backend ## Full first-run project setup: check → install → prepare → dev → test
	@echo -e "$(_OK)✅ Project setup complete. Run 'make frontend-dev' to start the dev server.$(_RESET)"

clean: frontend-clean backend-clean ## Remove all project artifacts (includes Docker images)
	@echo -e "$(_WARN)▶ Cleaning project artifacts…$(_RESET)"
	@docker compose down -v
	@echo -e "$(_OK)✅ All project artifacts cleaned."

# --------------------------------------------------------------------
# Docker targets (orchestrated via docker-compose)
# --------------------------------------------------------------------
docker-build: ## Build all Docker images
	@echo -e "$(_INFO)▶ Building Docker images…$(_RESET)"
	@cd $(BACKEND_DIR) && make docker-build
	@cd $(FRONTEND_DIR) && make docker-build
	@echo -e "$(_OK)✅ All Docker images built."

docker-test: ## Run all tests in Docker environment
	@echo -e "$(_INFO)▶ Running backend tests in Docker…$(_RESET)"
	@cd $(BACKEND_DIR) && make docker-test
	@echo -e "$(_INFO)▶ Running frontend tests in Docker…$(_RESET)"
	@cd $(FRONTEND_DIR) && make docker-test
	@echo -e "$(_OK)✅ All Docker tests completed."

docker-shell-backend: ## Open shell in backend container
	@cd $(BACKEND_DIR) && make docker-shell

docker-shell-frontend: ## Open shell in frontend container
	@cd $(FRONTEND_DIR) && make docker-shell

# ========================================================
# Docker commands
# ========================================================
docker-up: ## Build and start all Docker services (detached)
	@echo -e "$(_INFO)▶ Building and starting Docker services…$(_RESET)"
	@if [ ! -f .env ]; then \
		echo -e "$(_WARN)⚠ .env not found, copying from .env.example$(_RESET)" && \
		cp .env.example .env; \
	fi
	@docker compose up -d --build
	@echo -e "$(_OK)✅ All services started. Frontend: http://localhost:3000  Backend: http://localhost:8000  Nginx: http://localhost:8080$(_RESET)"

docker-up-logs: ## Build and start all Docker services with logs (foreground)
	@echo -e "$(_INFO)▶ Building and starting Docker services with logs…$(_RESET)"
	@if [ ! -f .env ]; then \
		echo -e "$(_WARN)⚠ .env not found, copying from .env.example$(_RESET)" && \
		cp .env.example .env; \
	fi
	@docker compose up --build

docker-down: ## Stop and remove all Docker services (preserves volumes)
	@echo -e "$(_INFO)▶ Stopping Docker services…$(_RESET)"
	@docker compose down
	@echo -e "$(_OK)✅ Services stopped.$(_RESET)"

docker-down-volumes: ## Stop services and remove volumes (DESTRUCTIVE — drops DB data)
	@echo -e "$(_WARN)▶ Stopping services and removing volumes…$(_RESET)"
	@docker compose down -v
	@echo -e "$(_OK)✅ Services and volumes removed.$(_RESET)"

docker-rebuild: ## Force rebuild and restart all services
	@echo -e "$(_INFO)▶ Rebuilding all Docker services…$(_RESET)"
	@docker compose build --no-cache
	@docker compose up -d
	@echo -e "$(_OK)✅ All services rebuilt and restarted.$(_RESET)"

docker-restart: ## Restart all running services
	@echo -e "$(_INFO)▶ Restarting Docker services…$(_RESET)"
	@docker compose restart
	@echo -e "$(_OK)✅ Services restarted.$(_RESET)"

docker-logs: ## Tail logs for all services
	@docker compose logs -f --tail=100

docker-logs-backend: ## Tail backend logs only
	@docker compose logs -f --tail=100 backend

docker-logs-frontend: ## Tail frontend logs only
	@docker compose logs -f --tail=100 frontend

docker-ps: ## List running Docker services
	@docker compose ps

docker-health: ## Check health status of all services
	@echo -e "$(_INFO)▶ Service health:$(_RESET)"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

docker-migrate-up: ## Run Alembic migrations inside the backend container
	@echo -e "$(_INFO)▶ Running database migrations…$(_RESET)"
	@docker compose exec backend alembic upgrade head
	@echo -e "$(_OK)✅ Migrations applied.$(_RESET)"

docker-migrate-down: ## Rollback last Alembic migration inside the backend container
	@echo -e "$(_WARN)▶ Rolling back last migration…$(_RESET)"
	@docker compose exec backend alembic downgrade -1
	@echo -e "$(_OK)✅ Migration rolled back.$(_RESET)"

docker-clean: docker-down docker-down-volumes ## Stop services and remove all data + images
	@echo -e "$(_INFO)▶ Removing Docker images…$(_RESET)"
	@docker compose down --rmi all --volumes --remove-orphans
	@echo -e "$(_OK)✅ All Docker artifacts cleaned.$(_RESET)"