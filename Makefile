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
        setup-frontend \
        docker-up docker-down docker-rebuild docker-logs docker-ps \
        docker-migrate-up docker-migrate-down docker-health

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
	@echo -e "$(_BOLD)Project targets:$(_RESET)"
	@grep -E '^[a-zA-Z_-]+.*:.*##' $(MAKEFILE_LIST) \
		| grep -v '^frontend-' \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  $(_OK)%-22s$(_RESET) %s\n", $$1, $$2}'
	@echo -e ""

# ========================================================
# Frontend commands
# ========================================================

frontend-check: ## Verify Node 22.x LTS + pnpm are installed (fail-fast)
	@echo -e "$(_INFO)▶ Checking frontend tooling…$(_RESET)"
	@if ! command -v node >/dev/null 2>&1; then \
		echo -e "$(_ERR)❌ Node.js is not installed.$(_RESET) Install Node 22.x LTS from https://nodejs.org/"; \
		exit 1; \
	fi
	@NODE_MAJOR=$$(node -p "parseInt(process.versions.node.split('.')[0], 10)"); \
	if [ "$$NODE_MAJOR" -ne $(NODE_MAJOR_REQUIRED) ]; then \
		echo -e "$(_ERR)❌ Node.js $$(node -v) detected — major version $(NODE_MAJOR_REQUIRED).x LTS is required.$(_RESET)"; \
		echo "  Install Node 22.x LTS from https://nodejs.org/"; \
		exit 1; \
	fi
	@echo -e "$(_OK)✅ Node $$(node -v)$(_RESET)"
	@if ! command -v pnpm >/dev/null 2>&1; then \
		echo -e "$(_ERR)❌ pnpm is not installed.$(_RESET) Install with: npm install -g pnpm"; \
		exit 1; \
	fi
	@echo -e "$(_OK)✅ pnpm $$(pnpm -v)$(_RESET)"
	@echo -e "$(_OK)All frontend prerequisites met.$(_RESET)"

frontend-install: frontend-check ## Install frontend deps (skips if lockfile unchanged)
	@echo -e "$(_INFO)▶ Installing frontend dependencies…$(_RESET)"
	@(cd $(FRONTEND_DIR) && pnpm install --frozen-lockfile) 2>/dev/null \
		|| ( \
			echo -e "$(_WARN)⚠ Lockfile mismatch, re-locking…$(_RESET)" && \
			cd $(FRONTEND_DIR) && pnpm install \
		)
	@echo -e "$(_OK)✅ Frontend dependencies installed.$(_RESET)"

frontend-prepare: frontend-install ## Run `nuxt prepare` (generates .nuxt + types)
	@echo -e "$(_INFO)▶ Preparing Nuxt environment…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run postinstall
	@echo -e "$(_OK)✅ Nuxt environment ready.$(_RESET)"

frontend-dev: frontend-prepare ## Start Nuxt 4 dev server (http://localhost:3000)
	@echo -e "$(_INFO)▶ Starting Nuxt dev server on http://localhost:3000$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm dev

frontend-build: frontend-prepare ## Build the frontend for production (.output/)
	@echo -e "$(_INFO)▶ Building frontend for production…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm build
	@echo -e "$(_OK)✅ Frontend build complete → $(FRONTEND_DIR)/.output/$(_RESET)"

frontend-preview: frontend-build ## Preview the production build on http://localhost:3000
	@echo -e "$(_INFO)▶ Previewing production build on http://localhost:3000$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm preview --port 3000 --host

frontend-generate: frontend-prepare ## Generate static site (SSG output)
	@echo -e "$(_INFO)▶ Generating static site…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm generate
	@echo -e "$(_OK)✅ Static site generated → $(FRONTEND_DIR)/.output/public/$(_RESET)"

frontend-typecheck: frontend-prepare ## Run Nuxt type checking (vue-tsc)
	@echo -e "$(_INFO)▶ Running type checks…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run typecheck

frontend-lint: frontend-install ## Run ESLint (writes no-fix output, non-zero on lint errors)
	@echo -e "$(_INFO)▶ Running ESLint…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run lint

frontend-lint-fix: frontend-install ## Run ESLint with --fix (auto-fixable issues only)
	@echo -e "$(_INFO)▶ Running ESLint (auto-fix)…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run lint:fix

frontend-format: frontend-install ## Run Prettier (rewrite files in place)
	@echo -e "$(_INFO)▶ Running Prettier…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run format

frontend-format-check: frontend-install ## Run Prettier in check-only mode (CI, returns non-zero on unformatted files)
	@echo -e "$(_INFO)▶ Checking Prettier formatting…$(_RESET)"
	@cd $(FRONTEND_DIR) && pnpm run format:check

frontend-clean: ## Remove generated Nuxt artifacts + node_modules
	@echo -e "$(_WARN)▶ Cleaning frontend artifacts…$(_RESET)"
	@rm -rf $(FRONTEND_DIR)/node_modules \
		$(FRONTEND_DIR)/.nuxt \
		$(FRONTEND_DIR)/.output \
		$(FRONTEND_DIR)/.nitro \
		$(FRONTEND_DIR)/.data \
		$(FRONTEND_DIR)/dist \
	@echo -e "$(_OK)✅ Frontend artifacts cleaned.$(_RESET)"


# ========================================================
# Backend commands
# ========================================================

backend-check: # Verify that docker is installed and uv is available (fail-fast)
	@echo -e "$(_INFO)▶ Checking backend tooling…$(_RESET)"
	@if ! command -v docker >/dev/null 2>&1; then \
		echo -e "$(_ERR)❌ Docker is not installed.$(_RESET) Install from https://www.docker.com/"; \
		exit 1; \
	fi
	@if ! command -v uv >/dev/null 2>&1; then \
		echo -e "$(_ERR)❌ uv is not installed.$(_RESET) Install with: brew install uv"; \
		exit 1; \
	fi
	@echo -e "$(_OK)✅ Docker $$(docker -v)$(_RESET)"
	@echo -e "$(_OK)✅ uv $$(uv --version)$(_RESET)"
	@echo -e "$(_OK)All backend prerequisites met.$(_RESET)"

backend-prepare: backend-check ## Refer to backend/fastapi/Makefile commands for installation instructions
	@cd $(BACKEND_DIR) && make setup
	@echo -e "$(_OK)✅ Backend dependencies installed.$(_RESET)"

backend-dev: backend-check ## Refer to backend/fastapi/Makefile commands for dev server
	@cd $(BACKEND_DIR) && make dev
	@echo -e "$(_OK)✅ Backend dev server started successfully.$(_RESET)"

backend-update-deps: backend-check ## Refer to backend/fastapi/Makefile commands for updating dependencies
	@cd $(BACKEND_DIR) && make update-deps
	@echo -e "$(_OK)✅ Backend dependencies updated successfully.$(_RESET)"

backend-lint-fix: backend-check ## Refer to backend/fastapi/Makefile commands for linting
	@cd $(BACKEND_DIR) && make lint-fix
	@echo -e "$(_OK)✅ Backend lint fixed successfully.$(_RESET)"

backend-test: backend-check ## Refer to backend/fastapi/Makefile commands for testing
	@cd $(BACKEND_DIR) && make test
	@echo -e "$(_OK)✅ Backend tests passed successfully.$(_RESET)"

backend-test-watch: backend-check ## Refer to backend/fastapi/Makefile commands for testing with watch
	@cd $(BACKEND_DIR) && make test-watch
	@echo -e "$(_OK)✅ Backend tests passed successfully with watch mode.$(_RESET)"

backend-migrate-create: backend-check ## Refer to backend/fastapi/Makefile commands for creating migrations
	@cd $(BACKEND_DIR) && make migrate-create
	@echo -e "$(_OK)✅ Backend migrations created successfully.$(_RESET)"

backend-migrate-up: backend-check ## Refer to backend/fastapi/Makefile commands for applying migrations
	@cd $(BACKEND_DIR) && make migrate-up
	@echo -e "$(_OK)✅ Backend migrations applied successfully.$(_RESET)"

backend-migrate-down: backend-check ## Refer to backend/fastapi/Makefile commands for rolling back migrations
	@cd $(BACKEND_DIR) && make migrate-down
	@echo -e "$(_OK)✅ Backend migrations rolled back successfully.$(_RESET)"

backend-clean:
	@cd $(BACKEND_DIR) && make clean
	@echo -e "$(_OK)✅ Backend artifacts cleaned.$(_RESET)"


# ========================================================
# Project setup
# ========================================================

setup-frontend: frontend-prepare ## Full first-run frontend setup: check → install → prepare
	@echo -e "$(_OK)✅ Frontend setup complete. Run 'make frontend-dev' to start the dev server.$(_RESET)"

setup-backend: backend-prepare ## Full first-run backend setup: install → env → dev → test
	@echo -e "$(_OK)✅ Backend setup complete. Run 'make dev' to start the dev server.$(_RESET)"

setup-project: setup-frontend setup-backend ## Full first-run project setup: check → install → prepare → dev → test
	@echo -e "$(_OK)✅ Project setup complete. Run 'make frontend-dev' to start the dev server.$(_RESET)"

dev-up: backend-dev frontend-dev ## Update frontend and backend dependencies
	@echo -e "$(_OK)✅ Frontend and backend dependencies updated successfully.$(_RESET)"

clean-project: frontend-clean backend-clean ## Clean project artifacts
	@echo -e "$(_OK)✅ Project artifacts cleaned.$(_RESET)"


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

docker-shell-backend: ## Open a shell in the backend container
	@docker compose exec backend /bin/bash

docker-shell-frontend: ## Open a shell in the frontend container
	@docker compose exec frontend /bin/sh

docker-shell-db: ## Open psql shell in the postgres container
	@docker compose exec postgres psql -U $${POSTGRES_USER:-appuser} -d $${POSTGRES_DB:-appdb}

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
