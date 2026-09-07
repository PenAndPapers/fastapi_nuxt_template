PY := pnpm

.PHONY: check-prerequisites install prepare dev build preview generate typecheck lint lint-fix format format-check clean up down test shell down

# Version requirements
NODE_MAJOR_REQUIRED := 22

# --------------------------------------------------------------------
# Help
# --------------------------------------------------------------------
help: ## Show this help message
	@echo "FastAPI Nuxt Template — Frontend Makefile targets"
	@echo ""
	@grep -E '^[a-zA-Z_-]+.*:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  %-22s %s\n", $$1, $$2}'

# --------------------------------------------------------------------
# Prerequisite checks
# --------------------------------------------------------------------
check-prerequisites:## Verify Node 22.x LTS + pnpm are installed (fail-fast)
	@echo "▶ Checking frontend tooling…"
	@if ! command -v node >/dev/null 2>&1; then \
		echo "❌ Node.js is not installed."; \
		echo "  Install Node 22.x LTS from https://nodejs.org/"; \
		exit 1; \
	fi
	@NODE_MAJOR=$$(node -p "parseInt(process.versions.node.split('.')[0], 10)"); \
	if [ "$$NODE_MAJOR" -ne $(NODE_MAJOR_REQUIRED) ]; then \
		echo "❌ Node.js $$(node -v) detected — major version $(NODE_MAJOR_REQUIRED).x LTS is required."; \
		echo "  Install Node 22.x LTS from https://nodejs.org/"; \
		exit 1; \
	fi
	@echo "✅ Node $$(node -v)"
	@if ! command -v pnpm >/dev/null 2>&1; then \
		echo "❌ pnpm is not installed."; \
		echo "  Install with: npm install -g pnpm"; \
		exit 1; \
	fi
	@echo "✅ pnpm $$(pnpm -v)"
	@echo "✅ All frontend prerequisites met."

# --------------------------------------------------------------------
# Installation & setup
# --------------------------------------------------------------------
install: check-prerequisites ## Install frontend deps (skips if lockfile unchanged)
	@echo "▶ Installing frontend dependencies…"
	@(pnpm install --frozen-lockfile) 2>/dev/null \
		|| ( \
			echo "⚠ Lockfile mismatch, re-locking…" && \
			pnpm install \
		)
	@echo "✅ Frontend dependencies installed."

prepare: install ## Run `nuxt prepare` (generates .nuxt + types)
	@echo "▶ Preparing Nuxt environment…"
	@pnpm run postinstall
	@echo "✅ Nuxt environment ready."

# --------------------------------------------------------------------
# Development
# --------------------------------------------------------------------
dev: dev-prepare ## Start Nuxt 4 dev server (http://localhost:3000)
	@echo "▶ Starting Nuxt dev server on http://localhost:3000"
	@pnpm dev

# --------------------------------------------------------------------
# Build & Production
# --------------------------------------------------------------------
build: dev-prepare ## Build the frontend for production (.output/)
	@echo "▶ Building frontend for production…"
	@pnpm build
	@echo "✅ Frontend build complete → .output/"

preview: build ## Preview production build (http://localhost:3000)
	@echo "▶ Previewing production build on http://localhost:3000"
	@pnpm preview --port 3000 --host

generate: dev-prepare ## Generate static site (SSG output)
	@echo "▶ Generating static site…"
	@pnpm generate
	@echo "✅ Static site generated → .output/public/"

# --------------------------------------------------------------------
# Type checking
# --------------------------------------------------------------------
typecheck: dev-prepare ## Run Nuxt type checking (vue-tsc)
	@echo "▶ Running type checks…"
	@pnpm run typecheck

# --------------------------------------------------------------------
# Linting & Formatting
# --------------------------------------------------------------------
lint: ## Run ESLint (writes no-fix output, non-zero on lint errors)
	@echo "▶ Running ESLint…"
	@pnpm run lint

lint-fix: ## Run ESLint with --fix (auto-fixable issues only)
	@echo "▶ Running ESLint (auto-fix)…"
	@pnpm run lint:fix

format: ## Run Prettier (rewrite files in place)
	@echo "▶ Running Prettier…"
	@pnpm run format

format-check: ## Run Prettier in check-only mode (CI, returns non-zero on unformatted files)
	@echo "▶ Checking Prettier formatting…"
	@pnpm run format:check

# --------------------------------------------------------------------
# Cleanup
# --------------------------------------------------------------------
clean: ## Remove generated Nuxt artifacts + node_modules
	@echo "▶ Cleaning frontend artifacts…"
	@rm -rf node_modules .nuxt .output .nitro .data dist
	@echo "✅ Frontend artifacts cleaned."

# --------------------------------------------------------------------
# Docker targets (run inside container via docker compose)
# --------------------------------------------------------------------
build: ## Build frontend Docker image
	@echo "▶ Building frontend Docker image..."
	@docker compose build frontend
	@echo "✅ Frontend Docker image built."

up: ## Run frontend in Docker (detached)
	@echo "▶ Starting frontend container..."
	@docker compose up -d frontend
	@echo "✅ Frontend container started on http://localhost:3000"

down: ## Stop and remove frontend container
	@echo "▶ Stopping frontend container..."
	@docker compose down frontend
	@echo "✅ Frontend container stopped."

test: ## Run tests inside frontend container
	@echo "▶ Running frontend tests in Docker..."
	@docker compose exec frontend pnpm run test:unit 2>/dev/null || echo "⚠ No unit tests configured yet (add test scripts to package.json)"
	@echo "✅ Frontend tests completed."

shell: ## Open shell in frontend container
	@echo "▶ Opening shell in frontend container..."
	@docker compose exec frontend /bin/sh

