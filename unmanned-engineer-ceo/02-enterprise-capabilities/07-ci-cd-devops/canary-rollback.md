# Canary & Rollback Strategy

## Canary Levels
- **L0 Smoke**：dev stack (`npm run dev:stack`).
- **L1 Canary**：10% traffic via service mesh。
- **L2 Regional**：單一地理區（config/topology-mind-matrix.yaml）。

## Rollback Playbook
1. 觸發器：SLO breach、error budget > 5%、security alert。
2. 操作：使用 `scripts/start-synergymesh-dev.sh --rollback <version>`。
3. 驗證：觀測 dashboards/ 與 docs/KNOWLEDGE_HEALTH.md。
4. 記錄：incident-game-days + metrics-and-roi。

## Tooling
- GitHub Actions workflow `ci-error-handler`。
- Auto-Fix Bot 監聽 pipeline 事件。
