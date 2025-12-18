# Causal Diagrams / 因果圖

## 模型建議

- **Structural Causal Models (SCM)**：描述部署、觀測、治理之間的因果邊。
- **Do-Calculus**：評估干預（deploy / rollback）對 SLO 的影響。

## 範例
<<<<<<< HEAD
<<<<<<< HEAD

- $Deploy \rightarrow ErrorRate \rightarrow Rollback$ vs
  $Deploy \rightarrow Observability \rightarrow AutoFix$。
=======
- $Deploy \rightarrow ErrorRate \rightarrow Rollback$ vs $Deploy \rightarrow Observability \rightarrow AutoFix$。
>>>>>>> origin/alert-autofix-37
=======

- $Deploy \rightarrow ErrorRate \rightarrow Rollback$ vs $Deploy \rightarrow Observability \rightarrow AutoFix$。
>>>>>>> origin/copilot/sub-pr-402
- 事件圖應儲存在 docs/knowledge-graph.yaml 的因果層。

## 工具

- dowhy, causalnex, graphviz。
