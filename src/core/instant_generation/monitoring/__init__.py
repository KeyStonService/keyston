"""
Monitoring Module
監控模組

實現實時監控、性能跟踪和警報系統
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque

class MetricType(Enum):
    """指標類型枚舉"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    """警報嚴重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Metric:
    """指標數據結構"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    unit: str = ""

@dataclass
class Alert:
    """警報數據結構"""
    alert_id: str
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class PerformanceMetric:
    """性能指標"""
    metric_name: str
    value: float
    threshold: float
    status: str  # ok, warning, critical
    timestamp: datetime

class RealTimeMonitor:
    """實時監控系統"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.monitoring_session = None
        
        # 數據存儲
        self.metrics_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Alert] = []
        self.active_sessions: Dict[str, datetime] = {}
        
        # 監控配置
        self.metrics_interval = self.config.get("metrics_interval", 30)  # 秒
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        
    async def start_monitoring(self, session_id: str) -> Dict[str, Any]:
        """開始監控會話"""
        if self.is_monitoring:
            return {"success": False, "error": "Monitoring already active"}
        
        try:
            self.is_monitoring = True
            self.monitoring_session = session_id
            self.active_sessions[session_id] = datetime.now()
            
            # 啟動監控任務
            asyncio.create_task(self._monitoring_loop(session_id))
            
            self.logger.info(f"Started monitoring session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "started_at": datetime.now().isoformat(),
                "metrics_interval": self.metrics_interval
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_monitoring(self, session_id: str) -> Dict[str, Any]:
        """停止監控會話"""
        if not self.is_monitoring:
            return {"success": False, "error": "No active monitoring"}
        
        try:
            self.is_monitoring = False
            self.monitoring_session = None
            
            if session_id in self.active_sessions:
                session_start = self.active_sessions[session_id]
                duration = (datetime.now() - session_start).total_seconds()
                del self.active_sessions[session_id]
            else:
                duration = 0
            
            self.logger.info(f"Stopped monitoring session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "stopped_at": datetime.now().isoformat(),
                "duration_seconds": duration,
                "metrics_collected": self._get_metrics_count(session_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    async def _monitoring_loop(self, session_id: str) -> None:
        """監控循環"""
        while self.is_monitoring and self.monitoring_session == session_id:
            try:
                # 收集系統指標
                await self._collect_system_metrics(session_id)
                
                # 收集應用指標
                await self._collect_application_metrics(session_id)
                
                # 檢查警報條件
                await self._check_alert_conditions(session_id)
                
                # 清理舊數據
                await self._cleanup_old_data()
                
                # 等待下次收集
                await asyncio.sleep(self.metrics_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # 錯誤時短暫等待
    
    async def _collect_system_metrics(self, session_id: str) -> None:
        """收集系統指標"""
        # CPU使用率
        cpu_metric = Metric(
            name="system_cpu_usage",
            value=self._get_cpu_usage(),
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            unit="percent"
        )
        await self._store_metric(session_id, cpu_metric)
        
        # 內存使用率
        memory_metric = Metric(
            name="system_memory_usage",
            value=self._get_memory_usage(),
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            unit="percent"
        )
        await self._store_metric(session_id, memory_metric)
        
        # 磁盘使用率
        disk_metric = Metric(
            name="system_disk_usage",
            value=self._get_disk_usage(),
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            unit="percent"
        )
        await self._store_metric(session_id, disk_metric)
    
    async def _collect_application_metrics(self, session_id: str) -> None:
        """收集應用指標"""
        # 請求計數
        request_metric = Metric(
            name="app_requests_total",
            value=self._get_request_count(),
            metric_type=MetricType.COUNTER,
            timestamp=datetime.now(),
            unit="count"
        )
        await self._store_metric(session_id, request_metric)
        
        # 響應時間
        response_time_metric = Metric(
            name="app_response_time",
            value=self._get_average_response_time(),
            metric_type=MetricType.TIMER,
            timestamp=datetime.now(),
            unit="milliseconds"
        )
        await self._store_metric(session_id, response_time_metric)
        
        # 錯誤率
        error_rate_metric = Metric(
            name="app_error_rate",
            value=self._get_error_rate(),
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            unit="percent"
        )
        await self._store_metric(session_id, error_rate_metric)
    
    async def _check_alert_conditions(self, session_id: str) -> None:
        """檢查警報條件"""
        # 檢查CPU使用率
        cpu_metrics = list(self.metrics_store.get(f"{session_id}_system_cpu_usage", []))
        if cpu_metrics:
            latest_cpu = cpu_metrics[-1].value
            if latest_cpu > self.alert_thresholds.get("cpu_warning", 80):
                await self._trigger_alert(
                    session_id=session_id,
                    severity=AlertSeverity.HIGH,
                    message=f"High CPU usage: {latest_cpu:.1f}%",
                    source="system_monitor"
                )
        
        # 檢查內存使用率
        memory_metrics = list(self.metrics_store.get(f"{session_id}_system_memory_usage", []))
        if memory_metrics:
            latest_memory = memory_metrics[-1].value
            if latest_memory > self.alert_thresholds.get("memory_warning", 85):
                await self._trigger_alert(
                    session_id=session_id,
                    severity=AlertSeverity.HIGH,
                    message=f"High memory usage: {latest_memory:.1f}%",
                    source="system_monitor"
                )
        
        # 檢查錯誤率
        error_metrics = list(self.metrics_store.get(f"{session_id}_app_error_rate", []))
        if error_metrics:
            latest_error_rate = error_metrics[-1].value
            if latest_error_rate > self.alert_thresholds.get("error_rate_warning", 5):
                await self._trigger_alert(
                    session_id=session_id,
                    severity=AlertSeverity.CRITICAL,
                    message=f"High error rate: {latest_error_rate:.1f}%",
                    source="application_monitor"
                )
    
    async def _trigger_alert(self, session_id: str, severity: AlertSeverity, 
                           message: str, source: str) -> None:
        """觸發警報"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            message=message,
            source=source,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        # 記錄警報
        self.logger.warning(f"ALERT [{severity.value.upper()}] {source}: {message}")
        
        # 調用警報回調
        if "alert_callback" in self.config:
            try:
                await self.config["alert_callback"](alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
        
        # 保留最近100個警報
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    async def _store_metric(self, session_id: str, metric: Metric) -> None:
        """存儲指標"""
        metric_key = f"{session_id}_{metric.name}"
        self.metrics_store[metric_key].append(metric)
    
    async def _cleanup_old_data(self) -> None:
        """清理舊數據"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # 清理舊指標
        for key in list(self.metrics_store.keys()):
            metrics = self.metrics_store[key]
            self.metrics_store[key] = deque(
                (m for m in metrics if m.timestamp > cutoff_time),
                maxlen=1000
            )
        
        # 清理舊警報
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        
        # 清理舊會話
        old_sessions = [
            session_id for session_id, start_time in self.active_sessions.items()
            if start_time < cutoff_time
        ]
        for session_id in old_sessions:
            del self.active_sessions[session_id]
    
    # 模擬方法（實際實現中會連接真實的監控系統）
    def _get_cpu_usage(self) -> float:
        """獲取CPU使用率"""
        import random
        return random.uniform(20, 90)
    
    def _get_memory_usage(self) -> float:
        """獲取內存使用率"""
        import random
        return random.uniform(30, 85)
    
    def _get_disk_usage(self) -> float:
        """獲取磁盤使用率"""
        import random
        return random.uniform(10, 70)
    
    def _get_request_count(self) -> float:
        """獲取請求計數"""
        import random
        return random.uniform(100, 1000)
    
    def _get_average_response_time(self) -> float:
        """獲取平均響應時間"""
        import random
        return random.uniform(50, 500)
    
    def _get_error_rate(self) -> float:
        """獲取錯誤率"""
        import random
        return random.uniform(0, 10)
    
    def _get_metrics_count(self, session_id: str) -> int:
        """獲取會話指標總數"""
        count = 0
        for key in self.metrics_store.keys():
            if key.startswith(f"{session_id}_"):
                count += len(self.metrics_store[key])
        return count
    
    def get_current_metrics(self, session_id: str) -> Dict[str, Any]:
        """獲取當前指標"""
        current_metrics = {}
        
        for key, metrics in self.metrics_store.items():
            if key.startswith(f"{session_id}_"):
                metric_name = key.replace(f"{session_id}_", "")
                if metrics:
                    latest_metric = metrics[-1]
                    current_metrics[metric_name] = {
                        "value": latest_metric.value,
                        "unit": latest_metric.unit,
                        "timestamp": latest_metric.timestamp.isoformat(),
                        "type": latest_metric.metric_type.value
                    }
        
        return current_metrics
    
    def get_recent_alerts(self, session_id: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """獲取最近警報"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        if session_id:
            alerts = [a for a in alerts if session_id in str(a)]
        
        return [asdict(alert) for alert in alerts]
    
    async def health_check(self) -> Dict[str, Any]:
        """監控系統健康檢查"""
        return {
            "status": "healthy" if self.is_monitoring or len(self.active_sessions) > 0 else "idle",
            "is_monitoring": self.is_monitoring,
            "active_sessions": len(self.active_sessions),
            "total_metrics": sum(len(metrics) for metrics in self.metrics_store.values()),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "last_collection": datetime.now().isoformat()
        }

class PerformanceTracker:
    """性能跟踪器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_history: List[Dict[str, Any]] = []
        self.generation_metrics: Dict[str, PerformanceMetric] = {}
        
    async def record_generation(self, generation_id: str, metrics: Dict[str, Any]) -> None:
        """記錄生成指標"""
        record = {
            "generation_id": generation_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "performance_score": self._calculate_performance_score(metrics)
        }
        
        self.performance_history.append(record)
        
        # 保留最近1000條記錄
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        self.logger.info(f"Recorded generation metrics for {generation_id}")
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """計算性能分數"""
        score = 100.0
        
        # 執行時間評分
        execution_time = metrics.get("execution_time", 600)
        if execution_time > 600:  # 超過10分鐘
            score -= (execution_time - 600) / 10
        
        # 成功率評分
        success = metrics.get("success", False)
        if not success:
            score -= 50
        
        # 輸出質量評分
        output_size = metrics.get("output_size", 0)
        if output_size < 1000:  # 輸出太小
            score -= 20
        
        return max(0, min(100, score))
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """獲取性能摘要"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [
            r for r in self.performance_history 
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if not recent_records:
            return {"message": "No recent performance data"}
        
        # 計算統計數據
        scores = [r["performance_score"] for r in recent_records]
        execution_times = [r["metrics"].get("execution_time", 0) for r in recent_records]
        success_count = sum(1 for r in recent_records if r["metrics"].get("success", False))
        
        return {
            "total_generations": len(recent_records),
            "success_rate": (success_count / len(recent_records)) * 100,
            "average_score": sum(scores) / len(scores),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "best_score": max(scores),
            "worst_score": min(scores),
            "period_hours": hours
        }
    
    def get_trends(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """獲取指標趨勢"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [
            r for r in self.performance_history 
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if not recent_records:
            return {"message": "No recent data"}
        
        # 提取指標數據
        values = []
        timestamps = []
        
        for record in recent_records:
            if metric_name in record["metrics"]:
                values.append(record["metrics"][metric_name])
                timestamps.append(record["timestamp"])
        
        if not values:
            return {"message": f"No data for metric {metric_name}"}
        
        # 計算趨勢
        if len(values) >= 2:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0
        
        return {
            "metric": metric_name,
            "current_value": values[-1] if values else None,
            "average_value": sum(values) / len(values),
            "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "data_points": len(values),
            "period_hours": hours
        }

__all__ = [
    "RealTimeMonitor",
    "PerformanceTracker",
    "Metric",
    "Alert",
    "PerformanceMetric",
    "MetricType",
    "AlertSeverity"
]