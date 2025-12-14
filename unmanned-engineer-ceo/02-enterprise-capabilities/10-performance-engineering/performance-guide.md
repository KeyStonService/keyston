# Performance Engineering Guide

## Dimensions
- **CPU**：profilers、vectorization、affinity。
- **Memory**：pooling、arena allocators、GC tuning。
- **I/O**：async pipelines、batch writes、zero-copy。
- **DB**：index設計、partitioning、query plan。
- **Cache**：TTL 策略、cache stampede 防護。
- **Concurrency**：lock hierarchy、actor model、backpressure。

## Workflow
1. Baseline → Profiling → Hypothesis → Fix → Verification。
2. 所有數據記錄於 profiling-recipes.md 與 metrics-and-roi.md。
