# 治理總覽

## 核心原則

1. **安全優先**：所有自動化皆有明確安全邊界
2. **透明可審計**：每個決策都有可追溯脈絡
3. **分層授權**：L2-L4 決策模型
4. **自動化 + 人類**：AI 輔助、人負責

## 十階段管道

1. 需求接收
2. 風險評估
3. 架構審查
4. 開發派工
5. 自動化測試
6. 安全部署門檻
7. Canary + 觀測
8. 決策審批
9. 正式推送
10. 事後復盤

## 關聯文件

- [decision_levels](decision_levels.md)
- [l0_policy](l0_policy.md)
- [slsa](slsa.md)
- `config/ai-constitution.yaml`
- `config/safety-mechanisms.yaml`

## 工具

- island-cli `governance:*` 指令
- OPA Policy Bundle
- Audit Dashboard
