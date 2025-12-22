"""
MachineNativeOps Auto-Monitor - Main Application
=================================================

Main application class for the auto-monitor system.
"""

import logging
import time
import threading
from typing import Dict, Any
from datetime import datetime

from .config import AutoMonitorConfig
from .collectors import MetricsCollector, SystemCollector, ServiceCollector
from .alerts import AlertManager
from .儲存 import StorageManager


class AutoMonitorApp:
    """
    Main application class for MachineNativeOps Auto-Monitor.
    """
    
    def __init__(self, config: AutoMonitorConfig):
        """
        Initialize auto-monitor application.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self._stop_event = threading.Event()
        
        # Initialize components
        self.logger.info("Initializing auto-monitor components...")
        
        # Metrics collectors
        self.system_collector = SystemCollector(config.collectors.get('system', {}))
        self.service_collector = ServiceCollector(config.collectors.get('service', {}))
        self.metrics_collector = MetricsCollector([
            self.system_collector,
            self.service_collector
        ])
        
        # Alert manager
        self.alert_manager = AlertManager(config.alerts)
        
        # Storage manager
        self.storage_manager = StorageManager(config.storage)
        
        self.logger.info("Auto-monitor initialization complete")
    
    def run(self):
        """Run auto-monitor in foreground mode."""
        self.running = True
        self.logger.info("Starting auto-monitor collection loop...")
        
        try:
            while self.running:
                self._collect_and_process()
                time.sleep(self.config.collection_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        
        finally:
            self.shutdown()
    
    def run_daemon(self):
        """Run auto-monitor as daemon."""
        self.running = True
        self.logger.info("Starting auto-monitor daemon...")
        
        # Start collection thread
        collector_thread = threading.Thread(target=self._collection_loop, daemon=True)
        collector_thread.start()
        
        # Wait for stop event
        self._stop_event.wait()
        
        self.shutdown()
    
    def _collection_loop(self):
        """Main collection loop for daemon mode."""
        self.logger.info("Collection loop started")
        
        while self.running and not self._stop_event.is_set():
            try:
                self._collect_and_process()
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}", exc_info=True)
            
            self._stop_event.wait(timeout=self.config.collection_interval)
        
        self.logger.info("Collection loop stopped")
    
    def _collect_and_process(self):
        """Collect metrics, evaluate alerts, and store data."""
        collection_start = time.time()
        
        try:
            # Collect metrics
            self.logger.debug("Collecting metrics...")
            metrics = self.metrics_collector.collect_all()
            
            metrics_count = len(metrics)
            self.logger.debug(f"Collected {metrics_count} metrics")
            
            # Evaluate alerts
            if self.config.alerts.get('enabled', True):
                self.logger.debug("Evaluating alerts...")
                self.alert_manager.evaluate_metrics(metrics)
            
            # Store metrics
            if not self.config.dry_run and self.config.storage.get('enabled', True):
                self.logger.debug("Storing metrics...")
                self.storage_manager.store_metrics(metrics)
            
            # Log statistics
            collection_duration = time.time() - collection_start
            self.logger.info(
                f"Collection completed: {metrics_count} metrics in {collection_duration:.2f}s"
            )
            
            # Log active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            if active_alerts:
                self.logger.info(f"Active alerts: {len(active_alerts)}")
                for alert in active_alerts:
                    self.logger.info(f"  - {alert.name} [{alert.severity.value}]")
        
        except Exception as e:
            self.logger.error(f"Error in collect and process: {e}", exc_info=True)
    
    def shutdown(self):
        """Shutdown auto-monitor gracefully."""
        self.logger.info("Shutting down auto-monitor...")
        
        self.running = False
        self._stop_event.set()
        
        # Close storage
        if self.storage_manager:
            self.storage_manager.close()
        
        self.logger.info("Auto-monitor shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status."""
        return {
            'running': self.running,
            'version': self.config.version,
            'namespace': self.config.namespace,
            'collection_interval': self.config.collection_interval,
            'dry_run': self.config.dry_run,
            'metrics': {
                'collectors': len(self.metrics_collector.collectors),
                'last_collection': datetime.now().isoformat()
            },
            'alerts': self.alert_manager.get_stats(),
            'storage': self.storage_manager.get_stats()
        }
