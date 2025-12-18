#!/usr/bin/env python3
"""
main.py - 使用範例 Usage Example

Event logging and safety monitoring demonstration for autonomous systems.
"""

import time
from observability.event_logger import EventLogger, SafetyMonitor, EventCategory


def main() -> None:
    """Main demonstration function"""
    # 創建事件日誌記錄器 Create event logger
    logger = EventLogger(100)

    # 創建安全監控器 Create safety monitor
    monitor = SafetyMonitor(logger)

    # 記錄系統啟動事件 Log system startup event
    logger.log_event(
        EventCategory.AUDIT,
        "flight_controller",
        "INFO",
        "System started",
        None,
    )

    # 模擬感測器錯誤 Simulate sensor error
    logger.log_event(
        EventCategory.SENSOR_ERROR,
        "sensor_fusion",
        "WARN",
        "IMU calibration drift detected",
        {
            "drift_value": 0.05,
            "threshold": 0.03,
        },
    )

    # 檢查高度限制 Check altitude limit
    monitor.check_altitude_limit(150.0, 100.0)

    # 檢查速度限制 Check velocity limit
    monitor.check_velocity_limit(25.0, 30.0)

    # 等待事件處理 Wait for event processing
    time.sleep(0.1)

    # 生成安全報告 Generate safety report
    report = monitor.generate_safety_report()
    print(report)

    # 導出 JSON 日誌 Export JSON log
    json_log = logger.export_json()
    print("\n日誌 JSON 導出：")
    print(json_log)


if __name__ == "__main__":
    main()
