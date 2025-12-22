"""
MachineNativeOps Auto-Monitor - 儲存管理 (Storage Management)
===========================================================

管理指標數據的持久化儲存。
Manages persistent storage of metric data.
"""

import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class MetricRecord:
    """表示一條指標記錄 / Represents a metric record."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典 / Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels
        }


class TimeSeriesStorage:
    """
    時間序列指標儲存 / Time-series metrics storage.
    使用 SQLite 作為後端 / Uses SQLite as backend.
    """
    
    def __init__(self, db_path: str):
        """
        初始化時間序列儲存 / Initialize time-series storage.
        
        Args:
            db_path: 數據庫文件路徑 / Database file path
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.connection: Optional[sqlite3.Connection] = None
        
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化數據庫架構 / Initialize database schema."""
        try:
            # 確保目錄存在 / Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 連接數據庫 / Connect to database
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # 創建指標表 / Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    labels TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 創建索引以提高查詢效能 / Create indexes for query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name 
                ON metrics(name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
            
            self.connection.commit()
            self.logger.info(f"Database initialized at: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_metric(self, name: str, value: float, 
                    timestamp: Optional[datetime] = None,
                    labels: Optional[Dict[str, str]] = None):
        """
        儲存單個指標 / Store a single metric.
        
        Args:
            name: 指標名稱 / Metric name
            value: 指標值 / Metric value
            timestamp: 時間戳（可選）/ Timestamp (optional)
            labels: 標籤（可選）/ Labels (optional)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if labels is None:
            labels = {}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO metrics (name, value, timestamp, labels)
                VALUES (?, ?, ?, ?)
                """,
                (name, value, timestamp, json.dumps(labels))
            )
            self.connection.commit()
        
        except Exception as e:
            self.logger.error(f"Error storing metric {name}: {e}")
    
    def store_metrics(self, metrics: Dict[str, float],
                     timestamp: Optional[datetime] = None):
        """
        批量儲存指標 / Store multiple metrics in batch.
        
        Args:
            metrics: 指標字典（名稱 -> 值）/ Metrics dictionary (name -> value)
            timestamp: 時間戳（可選）/ Timestamp (optional)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            cursor = self.connection.cursor()
            
            # 準備批量插入數據 / Prepare batch insert data
            data = [
                (name, value, timestamp, json.dumps({}))
                for name, value in metrics.items()
            ]
            
            cursor.executemany(
                """
                INSERT INTO metrics (name, value, timestamp, labels)
                VALUES (?, ?, ?, ?)
                """,
                data
            )
            
            self.connection.commit()
            self.logger.debug(f"Stored {len(metrics)} metrics")
        
        except Exception as e:
            self.logger.error(f"Error storing metrics batch: {e}")
    
    def query_metrics(self, name: str,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     limit: int = 1000) -> List[MetricRecord]:
        """
        查詢指標數據 / Query metric data.
        
        Args:
            name: 指標名稱 / Metric name
            start_time: 開始時間（可選）/ Start time (optional)
            end_time: 結束時間（可選）/ End time (optional)
            limit: 最大返回數量 / Maximum number of results
            
        Returns:
            指標記錄列表 / List of metric records
        """
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT name, value, timestamp, labels FROM metrics WHERE name = ?"
            params = [name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 轉換為 MetricRecord 物件 / Convert to MetricRecord objects
            records = []
            for row in rows:
                records.append(MetricRecord(
                    name=row[0],
                    value=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    labels=json.loads(row[3]) if row[3] else {}
                ))
            
            return records
        
        except Exception as e:
            self.logger.error(f"Error querying metrics: {e}")
            return []
    
    def cleanup_old_data(self, retention_days: int = 30):
        """
        清理過期數據 / Clean up old data.
        
        Args:
            retention_days: 保留天數 / Number of days to retain
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old metric records")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        獲取儲存統計信息 / Get storage statistics.
        
        Returns:
            統計信息字典 / Statistics dictionary
        """
        try:
            cursor = self.connection.cursor()
            
            # 總記錄數 / Total records
            cursor.execute("SELECT COUNT(*) FROM metrics")
            total_records = cursor.fetchone()[0]
            
            # 不同指標數量 / Distinct metrics count
            cursor.execute("SELECT COUNT(DISTINCT name) FROM metrics")
            distinct_metrics = cursor.fetchone()[0]
            
            # 最舊和最新的記錄時間 / Oldest and newest record times
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM metrics")
            oldest, newest = cursor.fetchone()
            
            return {
                'total_records': total_records,
                'distinct_metrics': distinct_metrics,
                'oldest_record': oldest,
                'newest_record': newest,
                'db_path': self.db_path
            }
        
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def close(self):
        """關閉數據庫連接 / Close database connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")


class StorageManager:
    """
    儲存管理器 / Storage manager.
    統一管理不同類型的儲存後端 / Manages different storage backends.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化儲存管理器 / Initialize storage manager.
        
        Args:
            config: 儲存配置 / Storage configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.enabled = config.get('enabled', True)
        
        # 初始化儲存後端 / Initialize storage backend
        backend_type = config.get('backend', 'timeseries')
        
        if backend_type == 'timeseries':
            db_path = config.get('path', '/var/lib/machinenativeops/metrics/metrics.db')
            self.backend = TimeSeriesStorage(db_path)
        else:
            raise ValueError(f"Unsupported storage backend: {backend_type}")
        
        # 設置數據保留策略 / Set data retention policy
        self.retention_days = config.get('retention_days', 30)
    
    def store_metrics(self, metrics: Dict[str, float]):
        """
        儲存指標 / Store metrics.
        
        Args:
            metrics: 指標字典 / Metrics dictionary
        """
        if not self.enabled:
            return
        
        try:
            self.backend.store_metrics(metrics)
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    def query_metrics(self, name: str, **kwargs) -> List[MetricRecord]:
        """
        查詢指標 / Query metrics.
        
        Args:
            name: 指標名稱 / Metric name
            **kwargs: 其他查詢參數 / Additional query parameters
            
        Returns:
            指標記錄列表 / List of metric records
        """
        return self.backend.query_metrics(name, **kwargs)
    
    def cleanup(self):
        """執行數據清理 / Perform data cleanup."""
        if not self.enabled:
            return
        
        self.backend.cleanup_old_data(self.retention_days)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        獲取儲存統計信息 / Get storage statistics.
        
        Returns:
            統計信息字典 / Statistics dictionary
        """
        if not self.enabled:
            return {'enabled': False}
        
        stats = self.backend.get_stats()
        stats['enabled'] = True
        stats['retention_days'] = self.retention_days
        return stats
    
    def close(self):
        """關閉儲存管理器 / Close storage manager."""
        if self.enabled and self.backend:
            self.backend.close()
