#!/bin/bash
set -e

echo "🚀 SynergyMesh 開發環境啟動器 (容器內)"

ROOT_DIR="/workspaces/unmanned-island"
cd "$ROOT_DIR"

export NPM_CONFIG_CACHE="/tmp/npm-cache"

echo "[1/3] 啟動基礎服務 (Postgres/Redis/Prometheus/Grafana)..."
if command -v docker-compose >/dev/null 2>&1; then
	docker-compose -f config/dev/docker-compose.yml up -d postgres redis prometheus grafana
elif command -v docker >/dev/null 2>&1; then
	docker compose -f config/dev/docker-compose.yml up -d postgres redis prometheus grafana
else
	echo "⚠️  系統中找不到 docker/docker-compose，略過基礎服務啟動；請在支援 Docker 的開發容器中啟動這些服務。"
fi

echo "⏳ 等待基礎服務啟動..."
sleep 5

echo "[2/3] 啟動 contracts-l1 核心服務..."
cd "$ROOT_DIR/src/core/contract_service/contracts-L1/contracts"
npm install --prefer-offline --no-audit >/dev/null 2>&1 || true
npm run build --if-present >/dev/null 2>&1 || true
nohup npm run dev >/tmp/contracts-l1-dev.log 2>&1 &
CONTRACTS_PID=$!
echo "   ✅ contracts-l1 已啟動 (PID=$CONTRACTS_PID)"

echo "[3/3] 啟動 mcp-servers..."
cd "$ROOT_DIR/src/mcp-servers"
npm install --prefer-offline --no-audit >/dev/null 2>&1 || true
nohup npm start >/tmp/mcp-servers.log 2>&1 &
MCP_PID=$!
echo "   ✅ mcp-servers 已啟動 (PID=$MCP_PID)"

echo ""
echo "✅ 所有主要服務已依優先級啟動完成："
echo "   1) 基礎服務：Postgres / Redis / Prometheus / Grafana (Docker)"
echo "   2) contracts-l1：主合約與 SLSA API (npm run dev)"
echo "   3) mcp-servers：MCP 伺服器集合 (npm start)"
echo ""
echo "🔍 檢查日誌："
echo "   tail -f /tmp/contracts-l1-dev.log"
echo "   tail -f /tmp/mcp-servers.log"
