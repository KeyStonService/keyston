# Optimization Tips

## 演算法層 Algorithm Level

- **複雜度分析**：提供 $O(n \log n)$ 或更優界，並以 KaTeX 表示關鍵推導。
- **記憶體模式**：Cache-friendly 結構（SoA vs AoS）。
- **批次處理**：將事件堆疊後批次寫入（batch commit）。

## 系統層 System Level

- **Backpressure**：以 reactive streams 控制佇列溢出。
- **調度**：利用優先佇列 + aging 消除饑餓。
- **資料壓縮**：差分儲存 + rolling hash。

## 實務建議

- 在 profiling-recipes.md 中維護語言別工具。
- 每次優化需更新 docs/KNOWLEDGE_HEALTH.md → Performance Panel。
