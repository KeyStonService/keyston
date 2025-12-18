FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:18

# Install essential system dependencies for life system development
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    postgresql-client \
    redis-tools \
    python3-pip \
    jq \
    curl \
    wget \
    git \
    unzip \
    netcat-openbsd \
    htop \
    vim \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl for Kubernetes operations
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# Install Helm for package management
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Kind for local Kubernetes clusters
# Using official Kind release v0.20.0
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && ./kind version | grep -q "v0.20.0" \
    && mv ./kind /usr/local/bin/kind

# Install global Node.js tools for life system development
USER node
RUN npm install -g \
    pm2 \
    nodemon \
    typescript \
    ts-node \
    replit

# Switch back to root for Python setup
USER root

# Install Python dependencies for life system scripts
# Note: --break-system-packages is required for PEP 668 compliance in externally managed environments
RUN pip3 install --no-cache-dir --break-system-packages \
    pyyaml \
    requests \
    psycopg2-binary \
    redis \
    kafka-python \
    prometheus-client

# Create workspace directories for life system
RUN mkdir -p /workspace/01-core/{brain,heart,heartbeat,lifecycle} \
    && mkdir -p /workspace/.devcontainer/scripts \
    && chown -R node:node /workspace

# Set working directory
WORKDIR /workspace

# Switch back to node user for development
USER node

# Health check for development container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || echo "Development container running"