# 安全性與觀測骨架 (Security & Observability Skeleton)

## 概述

Go 微服務治理層，提供分布式追蹤、安全監控、事件日誌功能。

## 功能特性

- ✅ **分布式事件日誌**：支援事件分類和嚴重性分級
- ✅ **追蹤 ID**：用於分布式追蹤和問題排查
- ✅ **安全監控**：實時監控系統安全狀態
- ✅ **違規檢測**：自動檢測安全違規並記錄
- ✅ **報告生成**：生成詳細的安全監控報告
- ✅ **JSON 導出**：支援日誌導出為 JSON 格式

## 系統需求

- Go >= 1.20

## 安裝與構建

```bash
# 初始化 Go 模組
go mod init

# 構建
go build -o event_logger

# 運行
./event_logger
```

## 使用範例

### 基本使用

```go
package main

import (
    "./observability"
)

func main() {
    // 創建事件日誌記錄器
    logger := observability.NewEventLogger(100)
    
    // 記錄事件
    logger.LogEvent(
        observability.EventAudit,
        "flight_controller",
        "INFO",
        "System started",
        nil,
    )
    
    // 創建安全監控器
    monitor := observability.NewSafetyMonitor(logger)
    
    // 檢查高度限制
    if !monitor.CheckAltitudeLimit(150.0, 100.0) {
        // 處理違規
    }
}
```

### 運行示例

```bash
go run main.go
```

### 預期輸出

```
ℹ️ [audit] flight_controller/INFO: System started (TraceID: trace_1732514340000000001)
⚠️ [sensor_error] sensor_fusion/WARN: IMU calibration drift detected (TraceID: trace_1732514341000000002)
🚨 [safety_violation] safety_monitor/CRITICAL: Altitude exceeded: 150.00 > 100.00 (TraceID: trace_1732514342000000003)

╔════════════════════════════════════════╗
║          安全監控報告                    ║
╚════════════════════════════════════════╝

安全違規事件：1
感測器錯誤：1
總事件數：3

最近的安全違規：
  • 13:39:02: Altitude exceeded: 150.00 > 100.00
```

## 事件分類

| 類別 | 描述 | 嚴重性 |
|------|------|--------|
| audit | 審計事件 | INFO |
| sensor_error | 感測器錯誤 | WARN/ERROR |
| control_error | 控制錯誤 | ERROR/CRITICAL |
| safety_violation | 安全違規 | CRITICAL |
| system_error | 系統錯誤 | ERROR/CRITICAL |

## 嚴重性級別

- **INFO**: 資訊性事件
- **WARN**: 警告事件
- **ERROR**: 錯誤事件
- **CRITICAL**: 嚴重事件，需要立即處理

## 安全監控功能

### 高度限制檢查

```go
monitor.CheckAltitudeLimit(currentAltitude, maxAltitude)
```

### 速度限制檢查

```go
monitor.CheckVelocityLimit(currentVelocity, maxVelocity)
```

### 生成安全報告

```go
report := monitor.GenerateSafetyReport()
```

## 整合至 SynergyMesh

此模組與 SynergyMesh 可觀測性基礎設施整合：

1. **事件追蹤**：提供分布式追蹤能力
2. **安全監控**：實時監控系統安全狀態
3. **日誌導出**：支援日誌導出和分析

## 性能特性

- **異步處理**：使用 Go channel 實現非阻塞日誌記錄
- **線程安全**：使用 sync.RWMutex 保證並發安全
- **低延遲**：事件記錄延遲 < 1ms

## 參考資料

- [Go Concurrency Patterns](https://go.dev/blog/pipelines)
- [Distributed Tracing](https://opentelemetry.io/)
- [Structured Logging Best Practices](https://www.honeycomb.io/blog/structured-logging-and-your-team)
