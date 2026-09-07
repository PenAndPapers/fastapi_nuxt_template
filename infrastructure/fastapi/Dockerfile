FROM python:3.12-slim AS builder

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary directly from official image (faster & avoids pip overhead)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation & copy-mode for performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency definition files first for optimal layer caching
COPY backend/fastapi/pyproject.toml backend/fastapi/uv.lock ./

# Install dependencies into system site-packages at /install
RUN uv pip install --system --target=/install -r pyproject.toml
RUN uv pip install --system --target=/install --group dev

# Copy remaining source code and install project itself
COPY backend/fastapi/ ./
RUN uv pip install --system --target=/install --no-deps .


# ---- Production stage ----
FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python site-packages from builder
COPY --from=builder /install /usr/local/lib/python3.12/site-packages
COPY --from=builder /install/bin /usr/local/bin

WORKDIR /app

# Copy application source code
COPY backend/fastapi/ ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
