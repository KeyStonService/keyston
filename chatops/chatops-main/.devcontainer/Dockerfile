FROM ubuntu:24.04

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates curl git jq make nodejs npm python3 python3-pip golang-go \
  && rm -rf /var/lib/apt/lists/*

RUN npm i -g pnpm@9.15.0

WORKDIR /workspace
