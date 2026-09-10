FROM redis:7-alpine

# Redis runs as non-root user by default
# Persistence configuration is handled at runtime in docker-compose

EXPOSE 6379

# Switch explicitly to the built-in non-root redis user
USER redis

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD redis-cli ping || exit 1
