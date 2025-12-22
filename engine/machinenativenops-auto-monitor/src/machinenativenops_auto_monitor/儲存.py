"""
儲存模組 (Storage Module)
數據儲存後端

Provides storage backends for metrics, logs, events, and alerts.
支援多種儲存後端：記憶體、文件、資料庫
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from collections import deque

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def store_metrics(self, metrics: Dict):
        """Store metrics data."""
        pass
    
    @abstractmethod
    def store_logs(self, logs: List):
        """Store log entries."""
        pass
    
    @abstractmethod
    def store_events(self, events: List):
        """Store events."""
        pass
    
    @abstractmethod
    def store_alert(self, alert):
        """Store an alert."""
        pass
    
    @abstractmethod
    def get_metrics(self, start_time: Optional[datetime] = None, 
                    end_time: Optional[datetime] = None) -> List[Dict]:
        """Retrieve metrics within time range."""
        pass
    
    @abstractmethod
    def get_metrics_count(self) -> int:
        """Get total count of stored metrics."""
        pass
    
    @abstractmethod
    def get_logs_count(self) -> int:
        """Get total count of stored logs."""
        pass
    
    @abstractmethod
    def get_events_count(self) -> int:
        """Get total count of stored events."""
        pass


class InMemoryStorage(StorageBackend):
    """In-memory storage backend using deque for efficiency."""
    
    def __init__(self, max_items: int = 10000):
        self.max_items = max_items
        self.metrics = deque(maxlen=max_items)
        self.logs = deque(maxlen=max_items)
        self.events = deque(maxlen=max_items)
        self.alerts = deque(maxlen=max_items)
        logger.info(f"✅ Initialized InMemoryStorage (max_items={max_items})")
    
    def store_metrics(self, metrics: Dict):
        """Store metrics in memory."""
        metrics['_stored_at'] = datetime.now().isoformat()
        self.metrics.append(metrics)
    
    def store_logs(self, logs: List):
        """Store logs in memory."""
        for log in logs:
            if hasattr(log, 'to_dict'):
                log_dict = log.to_dict()
            else:
                log_dict = log
            log_dict['_stored_at'] = datetime.now().isoformat()
            self.logs.append(log_dict)
    
    def store_events(self, events: List):
        """Store events in memory."""
        for event in events:
            if hasattr(event, 'to_dict'):
                event_dict = event.to_dict()
            else:
                event_dict = event
            event_dict['_stored_at'] = datetime.now().isoformat()
            self.events.append(event_dict)
    
    def store_alert(self, alert):
        """Store alert in memory."""
        if hasattr(alert, 'to_dict'):
            alert_dict = alert.to_dict()
        else:
            alert_dict = alert
        alert_dict['_stored_at'] = datetime.now().isoformat()
        self.alerts.append(alert_dict)
    
    def get_metrics(self, start_time: Optional[datetime] = None, 
                    end_time: Optional[datetime] = None) -> List[Dict]:
        """Retrieve metrics within time range."""
        if start_time is None and end_time is None:
            return list(self.metrics)
        
        filtered = []
        for metric in self.metrics:
            timestamp = datetime.fromisoformat(metric.get('timestamp', ''))
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            filtered.append(metric)
        
        return filtered
    
    def get_metrics_count(self) -> int:
        """Get total count of stored metrics."""
        return len(self.metrics)
    
    def get_logs_count(self) -> int:
        """Get total count of stored logs."""
        return len(self.logs)
    
    def get_events_count(self) -> int:
        """Get total count of stored events."""
        return len(self.events)
    
    def get_alerts_count(self) -> int:
        """Get total count of stored alerts."""
        return len(self.alerts)


class FileStorage(StorageBackend):
    """File-based storage backend using JSON files."""
    
    def __init__(self, storage_path: Path, retention_days: int = 7):
        self.storage_path = Path(storage_path)
        self.retention_days = retention_days
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / 'metrics').mkdir(exist_ok=True)
        (self.storage_path / 'logs').mkdir(exist_ok=True)
        (self.storage_path / 'events').mkdir(exist_ok=True)
        (self.storage_path / 'alerts').mkdir(exist_ok=True)
        
        logger.info(f"✅ Initialized FileStorage at {self.storage_path}")
    
    def _get_daily_file(self, data_type: str, date: datetime = None) -> Path:
        """Get file path for a specific date."""
        if date is None:
            date = datetime.now()
        filename = f"{date.strftime('%Y-%m-%d')}.jsonl"
        return self.storage_path / data_type / filename
    
    def _append_to_file(self, file_path: Path, data: Dict):
        """Append data to JSONL file."""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
    
    def store_metrics(self, metrics: Dict):
        """Store metrics to file."""
        metrics['_stored_at'] = datetime.now().isoformat()
        file_path = self._get_daily_file('metrics')
        self._append_to_file(file_path, metrics)
    
    def store_logs(self, logs: List):
        """Store logs to file."""
        file_path = self._get_daily_file('logs')
        for log in logs:
            if hasattr(log, 'to_dict'):
                log_dict = log.to_dict()
            else:
                log_dict = log
            log_dict['_stored_at'] = datetime.now().isoformat()
            self._append_to_file(file_path, log_dict)
    
    def store_events(self, events: List):
        """Store events to file."""
        file_path = self._get_daily_file('events')
        for event in events:
            if hasattr(event, 'to_dict'):
                event_dict = event.to_dict()
            else:
                event_dict = event
            event_dict['_stored_at'] = datetime.now().isoformat()
            self._append_to_file(file_path, event_dict)
    
    def store_alert(self, alert):
        """Store alert to file."""
        if hasattr(alert, 'to_dict'):
            alert_dict = alert.to_dict()
        else:
            alert_dict = alert
        alert_dict['_stored_at'] = datetime.now().isoformat()
        file_path = self._get_daily_file('alerts')
        self._append_to_file(file_path, alert_dict)
    
    def get_metrics(self, start_time: Optional[datetime] = None, 
                    end_time: Optional[datetime] = None) -> List[Dict]:
        """Retrieve metrics from files."""
        # Simplified implementation - read from today's file
        file_path = self._get_daily_file('metrics')
        if not file_path.exists():
            return []
        
        metrics = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    metrics.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading metrics: {e}")
        
        return metrics
    
    def get_metrics_count(self) -> int:
        """Get approximate count of stored metrics."""
        return len(self.get_metrics())
    
    def get_logs_count(self) -> int:
        """Get approximate count of stored logs."""
        file_path = self._get_daily_file('logs')
        if not file_path.exists():
            return 0
        return sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
    
    def get_events_count(self) -> int:
        """Get approximate count of stored events."""
        file_path = self._get_daily_file('events')
        if not file_path.exists():
            return 0
        return sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
    
    def cleanup_old_files(self):
        """Remove files older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for data_type in ['metrics', 'logs', 'events', 'alerts']:
            data_dir = self.storage_path / data_type
            for file_path in data_dir.glob('*.jsonl'):
                try:
                    # Extract date from filename
                    date_str = file_path.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        logger.info(f"🗑️  Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up {file_path}: {e}")
