FROM python:3.14-slim AS builder

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary directly from official image (faster & avoids pip overhead)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation & copy-mode for performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency definition files first for optimal layer caching
COPY backend/fastapi/pyproject.toml backend/fastapi/uv.lock ./

# Install production dependencies only (dev dependencies excluded in production)
RUN uv pip install --system --target=/install -r pyproject.toml
# Install test dependencies for development/testing inside container
RUN uv pip install --system --target=/install pytest pytest-asyncio httpx

# Copy remaining source code
COPY backend/fastapi/ .


# ---- Production stage ----
FROM python:3.14-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first (used in COPY chown)
RUN useradd --create-home --shell /bin/bash --uid 1000 app

WORKDIR /app

# Copy installed python site-packages from builder
COPY --from=builder --chown=app:app /install /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=app:app /install/bin /usr/local/bin

# Copy application source code
COPY --from=builder --chown=app:app /app ./

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
