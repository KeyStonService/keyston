"""
Database storage for metrics data
SQLite-based storage with proper schema and retention
"""

import sqlite3
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

from .config import DatabaseConfig

class DatabaseManager:
    """SQLite database manager for metrics storage"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Thread lock for database operations
        self._lock = threading.Lock()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(timestamp),
                    INDEX(created_at)
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(timestamp),
                    INDEX(alert_type),
                    INDEX(resolved)
                )
            ''')
            
            # Create system_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(timestamp),
                    INDEX(event_type),
                    INDEX(component)
                )
            ''')
            
            conn.commit()
            self.logger.info("Database schema initialized")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with thread safety"""
        with self._lock:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics data"""
        try:
            timestamp = metrics.get('timestamp', datetime.utcnow().isoformat())
            data_json = json.dumps(metrics, default=str)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO metrics (timestamp, data) VALUES (?, ?)',
                    (timestamp, data_json)
                )
                conn.commit()
            
            self.logger.debug(f"Stored metrics for timestamp: {timestamp}")
            
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")
            raise
    
    def get_metrics(self, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve metrics data"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM metrics WHERE 1=1'
                params = []
                
                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())
                
                query += ' ORDER BY timestamp DESC'
                
                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    try:
                        data = json.loads(row['data'])
                        data['id'] = row['id']
                        data['created_at'] = row['created_at']
                        metrics.append(data)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to decode metrics data: {e}")
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve metrics: {e}")
            raise
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM metrics ORDER BY timestamp DESC LIMIT ?',
                    (limit,)
                )
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    try:
                        data = json.loads(row['data'])
                        data['id'] = row['id']
                        metrics.append(data)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Failed to decode metrics data")
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get recent metrics: {e}")
            raise
    
    def store_alert(self, alert_type: str, severity: str, message: str, 
                   data: Optional[Dict[str, Any]] = None):
        """Store alert data"""
        try:
            timestamp = datetime.utcnow().isoformat()
            data_json = json.dumps(data) if data else None
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO alerts (timestamp, alert_type, severity, message, data)
                       VALUES (?, ?, ?, ?, ?)''',
                    (timestamp, alert_type, severity, message, data_json)
                )
                conn.commit()
            
            self.logger.info(f"Stored alert: {alert_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
            raise
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active (unresolved) alerts"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT * FROM alerts WHERE resolved = FALSE 
                       ORDER BY timestamp DESC'''
                )
                rows = cursor.fetchall()
                
                alerts = []
                for row in rows:
                    data = json.loads(row['data']) if row['data'] else {}
                    alert = {
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'alert_type': row['alert_type'],
                        'severity': row['severity'],
                        'message': row['message'],
                        'data': data,
                        'created_at': row['created_at'],
                    }
                    alerts.append(alert)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {e}")
            raise
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''UPDATE alerts SET resolved = TRUE, resolved_at = CURRENT_TIMESTAMP 
                       WHERE id = ?''',
                    (alert_id,)
                )
                conn.commit()
            
            self.logger.info(f"Resolved alert: {alert_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {e}")
            raise
    
    def store_system_event(self, event_type: str, component: str, message: str,
                          data: Optional[Dict[str, Any]] = None):
        """Store system event"""
        try:
            timestamp = datetime.utcnow().isoformat()
            data_json = json.dumps(data) if data else None
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO system_events (timestamp, event_type, component, message, data)
                       VALUES (?, ?, ?, ?, ?)''',
                    (timestamp, event_type, component, message, data_json)
                )
                conn.commit()
            
            self.logger.debug(f"Stored system event: {event_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to store system event: {e}")
            raise
    
    def get_system_events(self, event_type: Optional[str] = None,
                         component: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get system events"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM system_events WHERE 1=1'
                params = []
                
                if event_type:
                    query += ' AND event_type = ?'
                    params.append(event_type)
                
                if component:
                    query += ' AND component = ?'
                    params.append(component)
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    data = json.loads(row['data']) if row['data'] else {}
                    event = {
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'event_type': row['event_type'],
                        'component': row['component'],
                        'message': row['message'],
                        'data': data,
                        'created_at': row['created_at'],
                    }
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to get system events: {e}")
            raise
    
    def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old data based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            cutoff_iso = cutoff_date.isoformat()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean old metrics
                cursor.execute(
                    'DELETE FROM metrics WHERE created_at < ?',
                    (cutoff_iso,)
                )
                metrics_deleted = cursor.rowcount
                
                # Clean old resolved alerts
                cursor.execute(
                    '''DELETE FROM alerts 
                       WHERE resolved = TRUE AND resolved_at < ?''',
                    (cutoff_iso,)
                )
                alerts_deleted = cursor.rowcount
                
                # Clean old system events
                cursor.execute(
                    'DELETE FROM system_events WHERE created_at < ?',
                    (cutoff_iso,)
                )
                events_deleted = cursor.rowcount
                
                conn.commit()
                
                # Vacuum database to reclaim space
                cursor.execute('VACUUM')
                conn.commit()
                
                self.logger.info(
                    f"Cleanup completed: {metrics_deleted} metrics, "
                    f"{alerts_deleted} alerts, {events_deleted} events"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table sizes
                cursor.execute('SELECT COUNT(*) FROM metrics')
                metrics_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM alerts WHERE resolved = FALSE')
                active_alerts = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM system_events')
                events_count = cursor.fetchone()[0]
                
                # Get database file size
                try:
                    db_size = self.db_path.stat().st_size
                except FileNotFoundError:
                    db_size = 0
                
                # Get oldest and newest records
                cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM metrics')
                oldest_newest = cursor.fetchone()
                
                stats = {
                    'total_records': metrics_count + active_alerts + events_count,
                    'metrics_count': metrics_count,
                    'active_alerts': active_alerts,
                    'events_count': events_count,
                    'size_bytes': db_size,
                    'oldest_record': oldest_newest[0],
                    'newest_record': oldest_newest[1],
                    'database_path': str(self.db_path),
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            raise
    
    def health_check(self) -> bool:
        """Perform database health check"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                return True
                
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connections"""
        # SQLite connections are closed automatically in context manager
        self.logger.info("Database connections closed")