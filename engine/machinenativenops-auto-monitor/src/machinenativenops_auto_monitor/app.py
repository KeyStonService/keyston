"""
Main application for MachineNativeOps Auto Monitor
Core monitoring logic without auto-installation
"""

import os
import sys
import time
import threading
import logging
import signal
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

import psutil
from prometheus_client import start_http_server, Gauge, Counter, Histogram
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .config import Config
from .collectors import SystemCollector, QuantumCollector, KubernetesCollector
from .storage import DatabaseManager
from .alerts import AlertManager

class MachineNativeOpsAutoMonitor:
    """Main monitoring application class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(config.database.path)
        self.system_collector = SystemCollector()
        self.quantum_collector = QuantumCollector(config.quantum)
        self.k8s_collector = KubernetesCollector(config.services)
        self.alert_manager = AlertManager(config.monitoring, config.auto_repair)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # FastAPI application
        self.app = FastAPI(
            title="MachineNativeOps Auto Monitor",
            description="System monitoring with quantum state tracking",
            version=config.version,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self._setup_fastapi_routes()
        
        # Control flags
        self._running = False
        self._shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.logger.info("MachineNativeOps Auto Monitor initialized")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.metrics = {
            'cpu_usage': Gauge('machinenativenops_cpu_usage_percent', 'CPU usage percentage'),
            'memory_usage': Gauge('machinenativenops_memory_usage_percent', 'Memory usage percentage'),
            'disk_usage': Gauge('machinenativenops_disk_usage_percent', 'Disk usage percentage'),
            'network_bytes_sent': Gauge('machinenativenops_network_bytes_sent_total', 'Total bytes sent'),
            'network_bytes_recv': Gauge('machinenativenops_network_bytes_recv_total', 'Total bytes received'),
            'quantum_fidelity': Gauge('machinenativenops_quantum_fidelity', 'Quantum state fidelity'),
            'quantum_coherence_time': Gauge('machinenativenops_quantum_coherence_time_microseconds', 'Quantum coherence time'),
            'quantum_error_rate': Gauge('machinenativenops_quantum_error_rate', 'Quantum error rate'),
            'active_services': Gauge('machinenativenops_active_services_count', 'Number of active services'),
            'collection_duration': Histogram('machinenativenops_collection_duration_seconds', 'Collection duration'),
            'alerts_total': Counter('machinenativenops_alerts_total', 'Total alerts triggered'),
        }
        
        self.logger.info("Prometheus metrics initialized")
    
    def _setup_fastapi_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                # Basic health checks
                db_status = self.db_manager.health_check()
                system_load = psutil.cpu_percent(interval=0.1)
                
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": self.config.version,
                    "architecture_hash": self.config.architecture_hash,
                    "database_status": "ok" if db_status else "error",
                    "system_load": system_load,
                    "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
                }
                
                # Include service status if not healthy
                if system_load > 90:
                    health_data["status"] = "degraded"
                    health_data["warnings"] = ["High system load"]
                
                return JSONResponse(health_data)
                
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint - handled by prometheus_client"""
            pass
        
        @self.app.get("/status")
        async def status():
            """Detailed status endpoint"""
            try:
                recent_metrics = self.db_manager.get_recent_metrics(limit=10)
                alerts = self.alert_manager.get_active_alerts()
                
                status_data = {
                    "status": "running" if self._running else "stopped",
                    "timestamp": datetime.utcnow().isoformat(),
                    "config": {
                        "monitoring_interval": self.config.monitoring.interval,
                        "prometheus_port": self.config.monitoring.prometheus_port,
                        "quantum_enabled": self.config.quantum.enabled,
                        "auto_repair_enabled": self.config.auto_repair.enabled,
                    },
                    "recent_metrics_count": len(recent_metrics),
                    "active_alerts_count": len(alerts),
                    "database_stats": self.db_manager.get_stats()
                }
                
                return JSONResponse(status_data)
                
            except Exception as e:
                self.logger.error(f"Status check failed: {e}")
                raise HTTPException(status_code=500, detail="Status check failed")
        
        @self.app.get("/api/v1/metrics")
        async def get_metrics(limit: int = 100):
            """Get recent metrics"""
            try:
                metrics = self.db_manager.get_recent_metrics(limit=limit)
                return JSONResponse({"metrics": metrics, "count": len(metrics)})
            except Exception as e:
                self.logger.error(f"Failed to get metrics: {e}")
                raise HTTPException(status_code=500, detail="Failed to retrieve metrics")
        
        @self.app.get("/api/v1/alerts")
        async def get_alerts():
            """Get active alerts"""
            try:
                alerts = self.alert_manager.get_active_alerts()
                return JSONResponse({"alerts": alerts, "count": len(alerts)})
            except Exception as e:
                self.logger.error(f"Failed to get alerts: {e}")
                raise HTTPException(status_code=500, detail="Failed to retrieve alerts")
    
    def collect_once(self) -> Dict[str, Any]:
        """Perform one-time metrics collection"""
        self.logger.info("Starting one-time metrics collection")
        
        start_time = time.time()
        metrics = {}
        
        try:
            # System metrics collection
            system_metrics = self.system_collector.collect()
            metrics.update(system_metrics)
            
            # Quantum metrics (if enabled)
            if self.config.quantum.enabled:
                try:
                    quantum_metrics = self.quantum_collector.collect()
                    metrics.update(quantum_metrics)
                except Exception as e:
                    self.logger.warning(f"Quantum collection failed: {e}")
                    metrics["quantum_error"] = str(e)
            
            # Kubernetes services metrics
            try:
                k8s_metrics = self.k8s_collector.collect()
                metrics.update(k8s_metrics)
            except Exception as e:
                self.logger.warning(f"Kubernetes collection failed: {e}")
                metrics["kubernetes_error"] = str(e)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Store to database
            self.db_manager.store_metrics(metrics)
            
            # Check for alerts
            self.alert_manager.check_alerts(metrics)
            
            duration = time.time() - start_time
            metrics['collection_duration'] = duration
            
            self.logger.info(f"Collection completed in {duration:.2f}s")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            raise
    
    def _update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Update Prometheus gauge metrics"""
        gauge_mappings = {
            'cpu_usage': 'cpu_usage_percent',
            'memory_usage': 'memory_usage_percent', 
            'disk_usage': 'disk_usage_percent',
            'network_bytes_sent': 'network_bytes_sent_total',
            'network_bytes_recv': 'network_bytes_recv_total',
            'quantum_fidelity': 'quantum_fidelity',
            'quantum_coherence_time': 'quantum_coherence_time_microseconds',
            'quantum_error_rate': 'quantum_error_rate',
            'active_services': 'active_services_count',
        }
        
        for metric_key, gauge_name in gauge_mappings.items():
            if metric_key in metrics and isinstance(metrics[metric_key], (int, float)):
                self.metrics[gauge_name].set(metrics[metric_key])
        
        # Update collection duration histogram
        if 'collection_duration' in metrics:
            self.metrics['collection_duration'].observe(metrics['collection_duration'])
    
    def run_serve(self):
        """Run monitoring service in daemon mode"""
        self.logger.info("Starting MachineNativeOps Auto Monitor service")
        
        self._running = True
        self.start_time = time.time()
        
        # Start Prometheus HTTP server
        start_http_server(self.config.monitoring.prometheus_port)
        self.logger.info(f"Prometheus server started on port {self.config.monitoring.prometheus_port}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        try:
            self.logger.info("Service running. Press Ctrl+C to stop.")
            self._shutdown_event.wait()
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
        finally:
            self._shutdown()
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running and not self._shutdown_event.is_set():
            try:
                self.collect_once()
                
                # Wait for next collection interval
                self._shutdown_event.wait(self.config.monitoring.interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                # Continue running even if individual collection fails
                self._shutdown_event.wait(min(60, self.config.monitoring.interval))
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self._shutdown_event.set()
    
    def _shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down MachineNativeOps Auto Monitor")
        
        self._running = False
        self._shutdown_event.set()
        
        # Close database connection
        self.db_manager.close()
        
        self.logger.info("Shutdown complete")