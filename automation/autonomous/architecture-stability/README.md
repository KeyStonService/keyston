# 架構穩定性骨架 (Architecture Stability Skeleton)

## 概述

**Layer 0 (OS/Hardware)** 優化實現 - 多語言系統級控制層：
- **C++17**: 高性能即時飛行控制器（ROS 2）
- **Rust**: 記憶體安全的低階運行時
- **C**: 硬體抽象層（HAL）與系統介面

## 功能特性

### C++ Flight Controller（優化版）
- ✅ **即時控制**：100Hz 控制迴圈，多執行緒執行器
- ✅ **PID 控制器**：完整實現（比例、積分、微分 + 抗飽和）
- ✅ **感測器融合**：IMU 資料處理與四元數運算
- ✅ **效能優化**：快取對齊記憶體、無鎖原子操作
- ✅ **ROS 2 整合**：使用 ROS 2 Humble/Iron/Jazzy

### Rust Runtime Library
- ✅ **記憶體安全**：零成本抽象、無垃圾回收
- ✅ **即時統計**：延遲監控、截止時間追蹤
- ✅ **鎖無感測器緩衝**：高效能並發資料存取
- ✅ **PID 控制器**：Rust 實現版本

### C Hardware Abstraction Layer
- ✅ **高精度計時**：微秒/奈秒級延遲
- ✅ **快取管理**：DMA 一致性支援
- ✅ **記憶體操作**：對齊記憶體分配
- ✅ **跨平台**：x86/ARM 架構支援

## 系統需求

### 基本需求
- Ubuntu 20.04 或更高版本
- CMake >= 3.8
- GCC 11+ 或 Clang 14+ (C++17 支援)
- GCC (C11 支援)

### ROS 2 需求（C++ 飛行控制器）
- ROS 2 (Humble, Iron, 或 Jazzy)
- rclcpp, geometry_msgs, sensor_msgs

### Rust 需求（Rust 運行時）
- Rust 1.75+
- Cargo

## 構建說明

### 完整構建（All Components）
```bash
# 1. 構建 Rust 運行時
cd rust-layer0
cargo build --release
cargo test

# 2. 構建 C++ 飛行控制器與 C HAL
cd ..
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DENABLE_OPTIMIZATION=ON \
      -DENABLE_LTO=ON \
      ..
make -j$(nproc)

# 3. 執行測試
./test_system_hal
```

### ROS 2 構建（僅飛行控制器）
```bash
# 安裝 ROS 2 依賴
rosdep install --from-paths . --ignore-src -r -y

# 使用 colcon 構建
colcon build --symlink-install \
  --cmake-args \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_OPTIMIZATION=ON
```

### 快速構建（開發模式）
```bash
# Debug 模式（無優化）
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)
```

## 運行示例

### C HAL 測試
```bash
cd build
./test_system_hal
```

**預期輸出：**
```
Running Layer 0 HAL tests...

  ✓ test_timestamp
  ✓ test_aligned_malloc
  ✓ test_cycle_counter
  ✓ test_interrupt_control
  ✓ test_memory_barriers

All tests passed! ✓
```

### Rust 運行時測試
```bash
cd rust-layer0
cargo test --release

# 執行效能測試
cargo test --release -- --nocapture test_pid_controller
```

### C++ 飛行控制器
```bash
# 啟動飛行控制器（需要 ROS 2 環境）
source /opt/ros/humble/setup.bash
ros2 run autonomy_core flight_controller
```

**預期輸出：**
```
[INFO] [flight_controller]: Flight Controller initialized - Layer 0 optimized
[INFO] [flight_controller]: Control frequency: 100Hz, PID tuning: altitude(0.5,0.1,0.2), yaw(0.8,0.05,0.15)
[INFO] [flight_controller]: Starting Flight Controller with multi-threaded executor
```

### IMU 測試資料發布
```bash
# 在另一個終端發送測試資料
ros2 topic pub /imu/data sensor_msgs/msg/Imu "{
  orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0},
  angular_velocity: {x: 0.1, y: 0.0, z: 0.05}
}"

# 觀察控制輸出
ros2 topic echo /cmd_vel
```

## 架構說明

```
┌─────────────────────────────────────┐
│     Flight Controller Node          │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ IMU          │  │ Control     │ │
│  │ Subscriber   │──│ Loop (100Hz)│ │
│  └──────────────┘  └─────────────┘ │
│         │                  │        │
│         ▼                  ▼        │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Sensor       │  │ Cmd Vel     │ │
│  │ Fusion       │  │ Publisher   │ │
│  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────┘
```

## 整合點

此模組整合至 SynergyMesh 平台，提供：

1. **即時控制能力**：為自治系統提供底層控制
2. **感測器融合**：整合多種感測器數據
3. **標準化介面**：通過 ROS 2 主題和服務與其他模組通信

## 參考資料

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [Colcon Build System](https://colcon.readthedocs.io/)
- [Gazebo Simulator](https://gazebosim.org/)
