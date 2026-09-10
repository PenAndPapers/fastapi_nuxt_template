FROM nginx:1.31-alpine

# Create non-root user nginx if not already present
RUN addgroup -g 1000 nginx-user || true && adduser -u 1000 -G nginx-user -s /bin/sh -D nginx-user || true

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config with proper permissions
COPY infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf

# Adjust permissions for non-root user
RUN chown -R nginx-user:nginx-user /var/cache/nginx /var/run /var/log/nginx
RUN chmod -R 755 /var/cache/nginx /var/run /var/log/nginx

USER nginx-user

EXPOSE 80

# Healthcheck uses wget (built-in busybox) instead of curl to avoid CVE-2026-11856, CVE-2026-10536
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1
