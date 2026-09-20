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
        nuxt4-check nuxt4-install nuxt4-prepare nuxt4-dev \
        nuxt4-build nuxt4-preview nuxt4-generate \
        nuxt4-typecheck nuxt4-lint nuxt4-lint-fix \
        nuxt4-format nuxt4-format-check nuxt4-clean \
        nuxt4-up nuxt4-down nuxt4-shell \
        fastapi-install fastapi-update-deps fastapi-lint fastapi-lint-fix \
        fastapi-test fastapi-test-unit fastapi-test-integration fastapi-test-e2e \
        fastapi-migrate-create fastapi-migrate-upgrade fastapi-migrate-downgrade \
        fastapi-migrate-history fastapi-migrate-current fastapi-migrate-pending \
        fastapi-clean fastapi-rotate-signing-key fastapi-generate-signing-key \
        fullstack-test fullstack-shell fullstack-clean \
        docker-up docker-up-logs docker-down docker-down-volumes docker-rebuild docker-restart docker-logs docker-ps \
        docker-health docker-clean

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
nuxt4-check: ## Verify Node 22.x LTS + pnpm are installed (fail-fast)
	@if [ ! -f $(FRONTEND_DIR)/Makefile ]; then \
		echo "$(_ERR)❌ $(FRONTEND_DIR)/Makefile not found$(_RESET)"; \
		exit 1; \
	fi
	@cd $(FRONTEND_DIR) && make check-prerequisites

nuxt4-install: nuxt4-check ## Install frontend deps (skips if lockfile unchanged)
	@cd $(FRONTEND_DIR) && make install

nuxt4-prepare: nuxt4-install ## Run `nuxt prepare` (generates .nuxt + types)
	@cd $(FRONTEND_DIR) && make prepare

nuxt4-dev: nuxt4-prepare ## Start Nuxt 4 dev server (http://localhost:3000)
	@cd $(FRONTEND_DIR) && make dev

nuxt4-generate: nuxt4-prepare ## Generate static site (SSG output)
	@cd $(FRONTEND_DIR) && make generate

nuxt4-typecheck: nuxt4-prepare ## Run Nuxt type checking (vue-tsc)
	@cd $(FRONTEND_DIR) && make typecheck

nuxt4-lint: nuxt4-install ## Run ESLint (writes no-fix output, non-zero on lint errors)
	@cd $(FRONTEND_DIR) && make lint

nuxt4-lint-fix: nuxt4-prepare ## Run ESLint with --fix (auto-fixable issues only)
	@cd $(FRONTEND_DIR) && make lint-fix

nuxt4-format: nuxt4-prepare ## Run Prettier (rewrite files in place)
	@cd $(FRONTEND_DIR) && make format

nuxt4-format-check: nuxt4-prepare ## Run Prettier in check-only mode (CI, returns non-zero on unformatted files)
	@cd $(FRONTEND_DIR) && make format-check

nuxt4-clean: ## Remove generated Nuxt artifacts + node_modules
	@echo -e "$(_WARN)▶⚠️  Cleaning Nuxt 4 artifacts…$(_RESET)"
	@cd $(FRONTEND_DIR) && make down

nuxt4-build: nuxt4-prepare ## Build the frontend for production (.output/)
	@cd $(FRONTEND_DIR) && make build

nuxt4-up: ## Start frontend container
	@echo "▶ Starting frontend container..."
	@cd $(FRONTEND_DIR) && make up

nuxt4-down: ## Stop and remove frontend container
	@echo -e "$(_WARN)▶⚠️  Stopping and removing Nuxt 4 container…$(_RESET)"
	@cd $(FRONTEND_DIR) && make down

nuxt4-preview: nuxt4-build ## Preview production build on http://localhost:3000
	@cd $(FRONTEND_DIR) && make preview

nuxt4-shell: ## Open shell in frontend container
	@cd $(FRONTEND_DIR) && make shell

# --------------------------------------------------------------------
# Backend commands (delegated to backend/fastapi/Makefile)
# --------------------------------------------------------------------
fastapi-install:
	@cd $(BACKEND_DIR) && make install
	@echo -e "$(_OK)✅ Backend deps installed."

fastapi-update-deps:
	@cd $(BACKEND_DIR) && make update-deps
	@echo -e "$(_OK)✅ Backend deps updated."

fastapi-lint:
	@cd $(BACKEND_DIR) && make lint
	@echo -e "$(_OK)✅ Backend lint completed."

fastapi-lint-fix:
	@cd $(BACKEND_DIR) && make lint-fix
	@echo -e "$(_OK)✅ Backend lint fixed."

fastapi-migrate-create:
	@cd $(BACKEND_DIR) && make migrate-create
	@echo -e "$(_OK)✅ Backend migration created."

fastapi-migrate-upgrade:
	@cd $(BACKEND_DIR) && make migrate-upgrade
	@echo -e "$(_OK)✅ Backend migrations applied."

fastapi-migrate-downgrade:
	@cd $(BACKEND_DIR) && make migrate-downgrade
	@echo -e "$(_OK)✅ Backend migrations rolled back."

fastapi-migrate-history:
	@cd $(BACKEND_DIR) && make migrate-history
	@echo -e "$(_OK)✅ Backend migrations history completed."

fastapi-migrate-current:
	@cd $(BACKEND_DIR) && make migrate-current
	@echo -e "$(_OK)✅ Backend current migration completed."

fastapi-migrate-pending:
	@cd $(BACKEND_DIR) && make migrate-pending
	@echo -e "$(_OK)✅ Backend pending migrations completed."

fastapi-test:
	@cd $(BACKEND_DIR) && make test
	@echo -e "$(_OK)✅ Backend tests completed."

fastapi-test-unit:
	@cd $(BACKEND_DIR) && make test-unit
	@echo -e "$(_OK)✅ Backend unit tests completed."

fastapi-test-integration:
	@cd $(BACKEND_DIR) && make test-integration
	@echo -e "$(_OK)✅ Backend integration tests completed."

fastapi-test-e2e:
	@cd $(BACKEND_DIR) && make test-e2e
	@echo -e "$(_OK)✅ Backend end-to-end tests completed."

fastapi-clean:	
	@cd $(BACKEND_DIR) && make clean
	@echo -e "$(_OK)✅ Backend artifacts cleaned."

fastapi-generate-signing-key:
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