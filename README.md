# FastAPI Nuxt Template

## Description

This project is a production-ready, Dockerized full-stack template combining **FastAPI** (Python backend) with **Nuxt 4** (Vue 3 frontend) and **PostgreSQL** as the primary data store. It includes a modular monolith architecture with isolated feature modules (e.g., `auth`, `user`), state management via **Pinia**, database migrations via **Alembic**, and a complete CI/CD-ready tooling layer (Ruff, ESLint, Prettier, pytest).

---

# Local System Prerequisites

Install these applications globally on your host machine before initializing the project.

| Application | Version / Spec | Purpose | Link |
| --- | --- | --- | --- |
| **Docker Desktop** / **Engine** | 24.0+ | Container runtime & local service orchestration (`docker compose`) | [Docs](https://docs.docker.com/get-docker/) |
| **Git** | 2.30+ | Source control | [Docs](https://git-scm.com/) |
| **Python** | 3.12+ | Runtime for backend | [Docs](https://www.python.org/) |
|| **uv** | Latest | Python package, virtualenv, and Python version manager | [Docs](https://docs.astral.sh/uv/) |
| **Node.js** | 22.x (LTS) | Tooling runtime for frontend build system | [Docs](https://nodejs.org/) |
| **pnpm** | 9.x+ | Package manager for frontend dependencies | [Docs](https://pnpm.io/) |
| **Database GUI** *(Optional)* | Latest | DB inspection (DBeaver, TablePlus, or pgAdmin) | [DBeaver](https://dbeaver.io/) |

> **Note on Python:** You do not need to manage global Python installations or `pip`. `uv` automatically downloads and uses the correct Python version defined in `pyproject.toml`.

---

# Stack Overview by Domain

### Backend Stack (`backend/fastapi/`)

Managed via `uv` in a project-local virtual environment (`.venv`).

* **Runtime:** Python 3.11+
* **Framework:** FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy 2.0 (Async), Alembic (Migrations)
* **Caching & Sessions:** Redis
* **Quality & Testing:** Ruff (Linter/Formatter), pytest

### Frontend Stack (`frontend/nuxt4/`)

Managed via `pnpm` inside the `frontend/nuxt4/` directory.

* **Framework:** Nuxt 4 (Vue 3 Composition API)
* **Language:** TypeScript
* **State Management:** Pinia
* **UI & Styling:** PrimeVue, Tailwind CSS
* **Data Fetching:** Nuxt `$fetch` / `useFetch` (Native)
* **Quality & Formatting:** ESLint, Prettier

### Infrastructure & DevOps

* **Local Orchestration:** Docker Compose (FastAPI, Postgres, Redis, Nuxt)
* **CI/CD:** GitHub Actions (Linting, Testing, Container Builds)
* **Production Runtime:** Containerized deployment (Kubernetes / AWS ECS compatible)

---

# Related Documentation

- [`Backend Documentation`](./docs/backend/fastapi/README.md)
- [`Frontend Documentation`](./docs/frontend/nuxt4/README.md)
- [`Infrastructure Documentation`](./docs/infrastructure/README.md)