FROM node:22-alpine AS builder

WORKDIR /app

# Install native C++ build tools
RUN apk add --no-cache python3 make g++ gcc libc6-compat

# Enable Corepack
RUN corepack enable

# Copy package management files
COPY frontend/nuxt4/package.json frontend/nuxt4/pnpm-lock.yaml ./

# Install dependencies (ignoring postinstall script for now)
RUN pnpm install --ignore-scripts

# Copy full application source code
COPY frontend/nuxt4/ .

# Regenerate .nuxt types against the REAL source code and nuxt.config.ts
RUN pnpm exec nuxt prepare

# Build Nuxt production bundle
RUN pnpm build


# ---- Production Stage ----
FROM node:22-alpine AS production

WORKDIR /app

COPY --from=builder /app/.output ./

EXPOSE 3000

ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["node", "server/index.mjs"]
