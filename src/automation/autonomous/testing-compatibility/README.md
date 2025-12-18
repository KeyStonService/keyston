# 測試與兼容性骨架 (Testing & Compatibility Skeleton)

## 概述

Python + YAML 自動化測試框架，支援 CI/CD 自動化測試、版本兼容性檢查。

## 功能特性

- ✅ **跨版本兼容性檢查**：支援多個 Python、ROS 2、OS 版本
- ✅ **自動化測試執行**：使用 unittest 框架
- ✅ **測試報告生成**：詳細的測試結果和覆蓋率報告
- ✅ **YAML 配置**：靈活的測試配置管理
- ✅ **CI/CD 整合**：易於整合到 GitHub Actions

## 系統需求

- Python >= 3.8
- PyYAML >= 6.0

## 安裝

```bash
pip install -r requirements.txt
```

## 使用範例

### 運行測試

```bash
# 運行所有測試
python test_compatibility.py

# 運行特定測試
python -m unittest test_compatibility.CompatibilityTestSuite.test_altitude_control

# 詳細輸出
python -m unittest test_compatibility -v
```

### 預期輸出

```
test_altitude_control (__main__.CompatibilityTestSuite) ... ok
test_emergency_landing (__main__.CompatibilityTestSuite) ... ok
test_imu_data_fusion (__main__.CompatibilityTestSuite) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK

╔════════════════════════════════════════╗
║         測試報告 - 2025-11-26 01:57:00        ║
╚════════════════════════════════════════╝

總測試數：3
✓ 通過：3
✗ 失敗：0
⊘ 跳過：0

通過率：100.0%

詳細結果：
✓ test_imu_data_fusion (100.50ms)
✓ test_altitude_control (100.50ms)
✓ test_emergency_landing (100.50ms)
```

## 測試套件說明

### sensor_fusion_tests

- **test_imu_data_fusion**: 驗證 IMU 資料融合邏輯
- **test_gps_integration**: 驗證 GPS 整合功能

### flight_control_tests

- **test_altitude_control**: 驗證高度控制算法
- **test_emergency_landing**: 驗證緊急著陸程序

## 兼容性矩陣

| 組件 | 支援版本 |
|------|---------|
| Python | 3.8, 3.9, 3.10, 3.11, 3.12 |
| ROS 2 | Humble, Iron, Jazzy |
| OS | Ubuntu 20.04, 22.04, 24.04 |
| C++ | C++17, C++20 |

## 測試覆蓋率要求

- 單元測試覆蓋率：>= 80%
- 整合測試覆蓋率：>= 70%
- 安全關鍵覆蓋率：>= 95%

## CI/CD 整合

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python test_compatibility.py
```

## 整合至 SynergyMesh

此模組與 SynergyMesh 測試基礎設施整合：

1. **自動化測試**：提供測試套件和報告生成
2. **兼容性檢查**：確保跨版本兼容性
3. **CI/CD 管道**：與 GitHub Actions 整合

## 參考資料

- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [PyYAML Documentation](https://pyyaml.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
