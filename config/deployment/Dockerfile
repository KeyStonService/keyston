# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Dockerfile
#                    Docker 鏡像配置
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Base Stage: Common dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM node:25-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    curl \
    bash \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# ─────────────────────────────────────────────────────────────────────────────
# Dependencies Stage: Install all dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS dependencies

# Install Node.js dependencies
RUN npm ci --only=production

# Copy production dependencies aside
RUN cp -R node_modules prod_node_modules

# Install all dependencies (including dev)
RUN npm ci

# ─────────────────────────────────────────────────────────────────────────────
# Python Stage: Setup Python environment
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS python-deps

# Copy Python requirements
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -e ".[full]" || pip install --no-cache-dir pyyaml pydantic jsonschema

# ─────────────────────────────────────────────────────────────────────────────
# Build Stage: Build TypeScript application
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies AS build

# Copy source code
COPY . .

# Build application
RUN npm run build --if-present

# ─────────────────────────────────────────────────────────────────────────────
# Development Stage: For local development
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS development

# Create non-root user for development
RUN addgroup -g 1001 -S synergymesh \
    && adduser -S synergymesh -u 1001 -G synergymesh \
    && chown -R synergymesh:synergymesh /app

# Copy dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy Python environment
COPY --from=python-deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY . .

# Expose ports
EXPOSE 3000 3001

# Set environment
ENV NODE_ENV=development
ENV SYNERGYMESH_ENV=development

# Start development server
USER synergymesh
CMD ["npm", "run", "dev"]

# ─────────────────────────────────────────────────────────────────────────────
# Test Stage: For running tests
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies AS test

# Create non-root user for test stage
RUN addgroup -g 1001 -S synergymesh \
    && adduser -S synergymesh -u 1001 -G synergymesh \
    && chown -R synergymesh:synergymesh /app

# Copy source code
COPY . .

# Copy Python environment
COPY --from=python-deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Run tests
USER synergymesh
CMD ["npm", "test"]

# ─────────────────────────────────────────────────────────────────────────────
# Production Stage: Optimized production image
# ─────────────────────────────────────────────────────────────────────────────
FROM node:25-alpine AS production

# Install runtime dependencies only
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    tini \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S synergymesh \
    && adduser -S synergymesh -u 1001 -G synergymesh

# Set working directory
WORKDIR /app

# Copy production dependencies
COPY --from=dependencies /app/prod_node_modules ./node_modules

# Copy built application
COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./

# Copy Python environment
COPY --from=python-deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy configuration files
COPY synergymesh.config.yaml ./
COPY config ./config

# Set ownership
RUN chown -R synergymesh:synergymesh /app

# Switch to non-root user
USER synergymesh

# Expose ports
EXPOSE 3000 3001

# Set environment
ENV NODE_ENV=production
ENV SYNERGYMESH_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--"]

# Start application
CMD ["node", "dist/index.js"]

# ─────────────────────────────────────────────────────────────────────────────
# Labels
# ─────────────────────────────────────────────────────────────────────────────
LABEL maintainer="SynergyMesh Team <team@synergymesh.io>"
LABEL org.opencontainers.image.title="SynergyMesh"
LABEL org.opencontainers.image.description="無人化自主協同網格系統"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="SynergyMesh"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/SynergyMesh/SynergyMesh"
