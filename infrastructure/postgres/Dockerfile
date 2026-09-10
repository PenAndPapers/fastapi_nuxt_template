FROM postgres:18-alpine

# Set secure defaults for PostgreSQL
ENV POSTGRES_INITDB_ARGS="-c max_connections=200 -c shared_buffers=256MB"

# Copy custom config if needed
# COPY infrastructure/postgress/postgresql.conf /etc/postgresql/postgresql.conf

EXPOSE 5432

# Switch explicitly to the built-in non-root postgres user
USER postgres

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD pg_isready -U postgres || exit 1
