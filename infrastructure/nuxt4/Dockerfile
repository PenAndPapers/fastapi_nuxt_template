FROM node:26-alpine AS builder

WORKDIR /app

# Install native C++ build tools
RUN apk add --no-cache python3 make g++ gcc

# Install pnpm directly
RUN npm install -g pnpm@latest

# Both files are required for pnpm install to work
COPY frontend/nuxt4/package.json frontend/nuxt4/pnpm-lock.yaml ./

# Strict installation using ONLY exact locked versions from pnpm-lock.yaml
RUN pnpm install --frozen-lockfile --ignore-scripts

# Copy full application source code
COPY frontend/nuxt4/ .

# Regenerate .nuxt types
RUN pnpm exec nuxt prepare

# Build Nuxt production bundle
RUN pnpm build


# ---- Production Stage ----
FROM node:26-alpine AS production

WORKDIR /app

# Copy pre-built output from builder
COPY --from=builder --chown=node:node /app/.output ./

USER node

EXPOSE 3000

ENV HOST=0.0.0.0 \
    PORT=3000 \
    NODE_ENV=production

CMD ["node", "server/index.mjs"]