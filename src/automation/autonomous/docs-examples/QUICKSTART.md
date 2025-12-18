# 無人機自治系統 - Quickstart 指南

## 📋 前置需求

- Ubuntu 20.04 或更高版本
- ROS 2 Humble / Iron / Jazzy
- Python 3.8+
- C++17 編譯器
- Go 1.20+

## 🚀 快速開始

### 1. 克隆倉庫

```bash
git clone https://github.com/we-can-fix/synergymesh.git
cd synergymesh/autonomous-system
```

### 2. 安裝依賴

#### ROS 2 依賴

```bash
# 安裝 ROS 2 (以 Humble 為例)
sudo apt update
sudo apt install ros-humble-desktop

# 安裝專案依賴
cd architecture-stability
rosdep install --from-paths . --ignore-src -r -y
```

#### Python 依賴

```bash
# 安裝 API 治理模組依賴
cd ../api-governance
pip install -r requirements.txt

# 安裝測試模組依賴
cd ../testing-compatibility
pip install -r requirements.txt
```

#### Go 依賴

```bash
cd ../security-observability
go mod download
```

### 3. 構建項目

#### 構建 C++ 核心控制層

```bash
cd ../architecture-stability

# 使用 colcon 構建
colcon build --symlink-install

# 或使用 CMake
mkdir build && cd build
cmake ..
make -j$(nproc)
```

#### 構建 Go 微服務

```bash
cd ../../security-observability
go build -o event_logger
```

### 4. 運行模擬

#### 啟動飛行控制器

```bash
cd ../architecture-stability
source install/setup.bash
ros2 run autonomy_core flight_controller
```

#### 啟動安全監控服務

```bash
cd ../security-observability
./event_logger
```

### 5. 運行測試

#### Python 測試

```bash
cd ../testing-compatibility
python test_compatibility.py
```

#### API 治理驗證

```bash
cd ../api-governance
python api_contract.py
```

### 6. 監控系統狀態

```bash
# 查看 ROS 2 節點
ros2 node list

# 查看主題
ros2 topic list

# 查看服務
ros2 service list

# 查看事件日誌
tail -f /var/log/autonomy/events.log
```

## 📊 系統架構

```
┌─────────────────────────────────────────────────────────┐
│              無人機自治系統架構                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │ Sensor Fusion    │──────│ Flight           │       │
│  │ (C++)            │      │ Controller (C++) │       │
│  │ ROS 2 Node       │      │ ROS 2 Node       │       │
│  └──────────────────┘      └──────────────────┘       │
│         △                           │                   │
│         │                           ▼                   │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │ Safety Monitor   │      │ Navigation       │       │
│  │ (Python)         │      │ (Python)         │       │
│  │ API Gateway      │      │ Path Planner     │       │
│  └──────────────────┘      └──────────────────┘       │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │ Observability & Security Monitoring (Go)       │    │
│  │ - Event Logging                                │    │
│  │ - Distributed Tracing                          │    │
│  │ - Safety Violation Detection                   │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │ API Governance Layer (Python)                  │    │
│  │ - Contract Validation                          │    │
│  │ - Dependency Management                        │    │
│  │ - Error Classification                         │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🔧 配置說明

### 環境變量

```bash
# ROS 2 配置
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=1

# 日誌配置
export LOG_LEVEL=INFO
export LOG_PATH=/var/log/autonomy

# 安全配置
export ENABLE_AUTHENTICATION=true
export ENABLE_ENCRYPTION=true
```

### 配置文件

主要配置文件位於 `docs-examples/governance_matrix.yaml`。

## 📈 監控與可觀測性

### 事件日誌

事件日誌保存在：

- 本地：`/var/log/autonomy/events.log`
- JSON 格式：通過 API 導出

### 安全報告

```bash
# 生成安全報告
curl http://localhost:8080/api/v1/safety/report
```

### 性能監控

```bash
# 查看系統性能
ros2 topic hz /cmd_vel
ros2 topic bw /imu/data
```

## 🧪 測試與驗證

### 單元測試

```bash
cd testing-compatibility
python -m unittest discover
```

### 整合測試

```bash
# 啟動所有服務後執行
./scripts/run_integration_tests.sh
```

### 兼容性測試

```bash
# 測試跨版本兼容性
python test_compatibility.py --matrix
```

## 🔒 安全最佳實踐

1. **身份驗證**：啟用 OAuth2 身份驗證
2. **加密**：使用 TLS 1.3 加密通信
3. **審計日誌**：啟用完整審計日誌
4. **定期掃描**：每季度進行滲透測試

## 📚 更多資源

- [架構穩定性骨架文檔](../architecture-stability/README.md)
- [API 治理文檔](../api-governance/README.md)
- [測試框架文檔](../testing-compatibility/README.md)
- [安全監控文檔](../security-observability/README.md)
- [治理矩陣](governance_matrix.yaml)

## 🆘 故障排除

### 常見問題

1. **ROS 2 節點無法通信**
   - 檢查 `ROS_DOMAIN_ID` 設置
   - 確認網絡配置

2. **編譯錯誤**
   - 檢查依賴是否完整安裝
   - 確認 C++ 標準為 C++17

3. **Python 測試失敗**
   - 確認 Python 版本 >= 3.8
   - 檢查所有依賴已安裝

### 獲取幫助

- 提交 Issue：[GitHub Issues](https://github.com/we-can-fix/synergymesh/issues)
- 郵件聯繫：<team@synergymesh.com>

## 📄 授權

MIT License - 詳見 [LICENSE](../../LICENSE) 文件
