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
        frontend-up frontend-down frontend-shell \
        backend-install backend-update-deps backend-lint backend-lint-fix \
        backend-test backend-test-unit backend-test-integration backend-test-e2e \
        backend-migrate-create backend-migrate-upgrade backend-migrate-downgrade \
        backend-migrate-history backend-migrate-current backend-migrate-pending \
        backend-clean backend-rotate-signing-key backend-generate-signing-key \
        setup-frontend setup-backend setup-project \
        docker-up docker-up-logs docker-down docker-down-volumes docker-rebuild docker-restart docker-logs docker-ps \
        docker-health docker-clean \
        fullstack-test fullstack-shell \
        dev-up clean-project

# --------------------------------------------------------------------
# Help
# --------------------------------------------------------------------
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

# --------------------------------------------------------------------
# Frontend commands (delegated to frontend/nuxt4/Makefile)
# --------------------------------------------------------------------
frontend-check: ## Verify Node 22.x LTS + pnpm are installed (fail-fast)
	@if [ ! -f $(FRONTEND_DIR)/Makefile ]; then \
		echo "$(_ERR)❌ $(FRONTEND_DIR)/Makefile not found$(_RESET)"; \
		exit 1; \
	fi
	@cd $(FRONTEND_DIR) && make check-prerequisites

frontend-install: frontend-check ## Install frontend deps (skips if lockfile unchanged)
	@cd $(FRONTEND_DIR) && make install

frontend-prepare: frontend-install ## Run `nuxt prepare` (generates .nuxt + types)
	@cd $(FRONTEND_DIR) && make prepare

frontend-dev: frontend-prepare ## Start Nuxt 4 dev server (http://localhost:3000)
	@cd $(FRONTEND_DIR) && make dev

frontend-generate: frontend-prepare ## Generate static site (SSG output)
	@cd $(FRONTEND_DIR) && make generate

frontend-typecheck: frontend-prepare ## Run Nuxt type checking (vue-tsc)
	@cd $(FRONTEND_DIR) && make typecheck

frontend-lint: frontend-install ## Run ESLint (writes no-fix output, non-zero on lint errors)
	@cd $(FRONTEND_DIR) && make lint

frontend-lint-fix: frontend-prepare ## Run ESLint with --fix (auto-fixable issues only)
	@cd $(FRONTEND_DIR) && make lint-fix

frontend-format: frontend-prepare ## Run Prettier (rewrite files in place)
	@cd $(FRONTEND_DIR) && make format

frontend-format-check: frontend-prepare ## Run Prettier in check-only mode (CI, returns non-zero on unformatted files)
	@cd $(FRONTEND_DIR) && make format-check

frontend-clean: ## Remove generated Nuxt artifacts + node_modules
	@echo -e "$(_WARN)▶⚠️  Cleaning frontend artifacts…$(_RESET)"
	@cd $(FRONTEND_DIR) && make down

frontend-build: frontend-prepare ## Build the frontend for production (.output/)
	@cd $(FRONTEND_DIR) && make build

frontend-up: ## Start frontend container
	@echo "▶ Starting frontend container..."
	@cd $(FRONTEND_DIR) && make up

frontend-down: ## Stop and remove frontend container
	@echo -e "$(_WARN)▶⚠️  Stopping and removing frontend container…$(_RESET)"
	@cd $(FRONTEND_DIR) && make down

frontend-preview: frontend-build ## Preview production build on http://localhost:3000
	@cd $(FRONTEND_DIR) && make preview

frontend-shell: ## Open shell in frontend container
	@cd $(FRONTEND_DIR) && make shell

# --------------------------------------------------------------------
# Backend commands (delegated to backend/fastapi/Makefile)
# --------------------------------------------------------------------
backend-install:
	@cd $(BACKEND_DIR) && make install
	@echo -e "$(_OK)✅ Backend deps installed."

backend-update-deps:
	@cd $(BACKEND_DIR) && make update-deps
	@echo -e "$(_OK)✅ Backend deps updated."

backend-lint:
	@cd $(BACKEND_DIR) && make lint
	@echo -e "$(_OK)✅ Backend lint completed."

backend-migrate-create:
	@cd $(BACKEND_DIR) && make migrate-create
	@echo -e "$(_OK)✅ Backend migration created."

backend-migrate-upgrade:
	@cd $(BACKEND_DIR) && make migrate-upgrade
	@echo -e "$(_OK)✅ Backend migrations applied."

backend-migrate-downgrade:
	@cd $(BACKEND_DIR) && make migrate-downgrade
	@echo -e "$(_OK)✅ Backend migrations rolled back."

backend-migrate-history:
	@cd $(BACKEND_DIR) && make migrate-history
	@echo -e "$(_OK)✅ Backend migrations history completed."

backend-migrate-current:
	@cd $(BACKEND_DIR) && make migrate-current
	@echo -e "$(_OK)✅ Backend current migration completed."

backend-migrate-pending:
	@cd $(BACKEND_DIR) && make migrate-pending
	@echo -e "$(_OK)✅ Backend pending migrations completed."

backend-test:
	@cd $(BACKEND_DIR) && make test
	@echo -e "$(_OK)✅ Backend tests completed."

backend-test-unit:
	@cd $(BACKEND_DIR) && make test-unit
	@echo -e "$(_OK)✅ Backend unit tests completed."

backend-test-integration:
	@cd $(BACKEND_DIR) && make test-integration
	@echo -e "$(_OK)✅ Backend integration tests completed."

backend-test-e2e:
	@cd $(BACKEND_DIR) && make test-e2e
	@echo -e "$(_OK)✅ Backend end-to-end tests completed."

backend-clean:
	@cd $(BACKEND_DIR) && make clean
	@echo -e "$(_OK)✅ Backend artifacts cleaned."

backend-generate-signing-key:
	@cd $(BACKEND_DIR) && make generate-signing-key
	@echo -e "$(_OK)✅ Backend signing key generated."

# --------------------------------------------------------------------
# Docker targets (orchestrated via docker-compose)
# --------------------------------------------------------------------

fullstack-test: ## Run all tests in Docker environment
	@echo -e "$(_INFO)▶ℹ️ Running backend tests in Docker…$(_RESET)"
	@cd $(BACKEND_DIR) && make test
	@echo -e "$(_INFO)▶ℹ️ Running frontend tests in Docker…$(_RESET)"
	@cd $(FRONTEND_DIR) && make test
	@echo -e "$(_OK)✅ All Docker tests completed."

fullstack-shell: ## Open shell in backend and frontend container
	@echo -e "$(_INFO)▶ℹ️ Opening shell in backend container…$(_RESET)"
	@cd $(BACKEND_DIR) && make shell
	@echo -e "$(_INFO)▶ℹ️ Opening shell in frontend container…$(_RESET)"
	@cd $(FRONTEND_DIR) && make shell

fullstack-clean: ## Remove generated Nuxt artifacts + node_modules
	@echo -e "$(_WARN)▶⚠️  Cleaning frontend artifacts…$(_RESET)"
	@cd $(FRONTEND_DIR) && make clean
	@echo -e "$(_WARN)▶⚠️  Cleaning backend artifacts…$(_RESET)"
	@cd $(BACKEND_DIR) && make clean
	@echo -e "$(_OK)✅ All Docker artifacts cleaned successfully"

# --------------------------------------------------------------------
# Docker commands
# --------------------------------------------------------------------
docker-up: ## Build and start all Docker services (detached) fullstack mode
	@echo -e "$(_INFO)▶ℹ️ Building and starting Docker services…$(_RESET)"
	@if [ ! -f .env ]; then \
		echo -e "$(_WARN)⚠️ .env not found, copying from .env.example$(_RESET)" && \
		cp .env.example .env; \
	fi
	# check if backend .venv exists, if not, build it
	@if [ ! -d ./backend/fastapi/.venv ]; then \
		echo -e "$(_WARN)⚠️ Backend .venv not found, building…$(_RESET)" && \
		make backend-install; \
	fi
	@docker compose up -d --build
	@echo -e "$(_OK)✅ All services started. Frontend: http://localhost:3000  Backend: http://localhost:8000  Nginx: http://localhost:8080$(_RESET)"

docker-up-logs: ## Build and start all Docker services with logs (foreground)
	@echo -e "$(_INFO)▶ℹ️ Building and starting Docker services with logs…$(_RESET)"
	@if [ ! -f .env ]; then \
		echo -e "$(_WARN)⚠️ .env not found, copying from .env.example$(_RESET)" && \
		cp .env.example .env; \
	fi
	@docker compose up --build

docker-down: ## Stop and remove all Docker services (preserves volumes)
	@echo -e "$(_INFO)▶ℹ️ Stopping Docker services…$(_RESET)"
	@docker compose down
	@echo -e "$(_OK)✅ Services stopped.$(_RESET)"

docker-down-volumes: ## Stop services and remove volumes (DESTRUCTIVE — drops DB data)
	@echo -e "$(_WARN)▶⚠️ Stopping services and removing volumes…$(_RESET)"
	@docker compose down -v
	@echo -e "$(_OK)✅ Services and volumes removed.$(_RESET)"

docker-rebuild: ## Force rebuild and restart all services
	@echo -e "$(_INFO)▶ℹ️ Rebuilding all Docker services…$(_RESET)"
	@docker compose build --no-cache
	@docker compose up -d
	@echo -e "$(_OK)✅ All services rebuilt and restarted.$(_RESET)"

docker-restart: ## Restart all running services
	@echo -e "$(_INFO)▶ℹ️ Restarting Docker services…$(_RESET)"
	@docker compose restart
	@echo -e "$(_OK)✅ Services restarted.$(_RESET)"

docker-logs: ## Tail logs for all services
	@docker compose logs -f --tail=100

docker-ps: ## List running Docker services
	@docker compose ps

docker-health: ## Check health status of all services
	@echo -e "$(_INFO)▶ℹ️ Service health:$(_RESET)"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

docker-clean: docker-down docker-down-volumes ## Stop services and remove all data + images
	@echo -e "$(_INFO)▶ℹ️ Removing Docker images…$(_RESET)"
	@docker compose down --rmi all --volumes --remove-orphans
	@echo -e "$(_OK)✅ All Docker artifacts cleaned.$(_RESET)"