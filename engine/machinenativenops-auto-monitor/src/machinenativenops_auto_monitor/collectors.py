"""
MachineNativeOps Auto-Monitor - Metrics Collectors
===================================================

Collects metrics from various sources (system, services, custom).
"""

import logging
import psutil
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metric:
    """Represents a collected metric."""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'labels': self.labels,
            'timestamp': self.timestamp.isoformat()
        }


class BaseCollector(ABC):
    """Base class for all metric collectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize collector.
        
        Args:
            config: Collector configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def collect(self) -> Dict[str, float]:
        """
        Collect metrics.
        
        Returns:
            Dictionary of metric name to value
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if collector is enabled."""
        return self.enabled


class SystemCollector(BaseCollector):
    """Collects system-level metrics (CPU, memory, disk, network)."""
    
    def collect(self) -> Dict[str, float]:
        """Collect system metrics."""
        if not self.enabled:
            return {}
        
        metrics = {}
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics['system_cpu_percent'] = cpu_percent
            
            cpu_count = psutil.cpu_count()
            metrics['system_cpu_count'] = cpu_count
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics['system_memory_total'] = memory.total
            metrics['system_memory_available'] = memory.available
            metrics['system_memory_percent'] = memory.percent
            metrics['system_memory_used'] = memory.used
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['system_disk_total'] = disk.total
            metrics['system_disk_used'] = disk.used
            metrics['system_disk_free'] = disk.free
            metrics['system_disk_percent'] = disk.percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            metrics['system_network_bytes_sent'] = net_io.bytes_sent
            metrics['system_network_bytes_recv'] = net_io.bytes_recv
            metrics['system_network_packets_sent'] = net_io.packets_sent
            metrics['system_network_packets_recv'] = net_io.packets_recv
            
            # Load average (Unix only)
            try:
                load1, load5, load15 = psutil.getloadavg()
                metrics['system_load_1'] = load1
                metrics['system_load_5'] = load5
                metrics['system_load_15'] = load15
            except (AttributeError, OSError):
                # Not available on Windows
                pass
            
            self.logger.debug(f"Collected {len(metrics)} system metrics")
        
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
        
        return metrics


class ServiceCollector(BaseCollector):
    """Collects metrics from services via health endpoints."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize service collector."""
        super().__init__(config)
        self.services = config.get('services', [])
        self.timeout = config.get('timeout', 5)
    
    def collect(self) -> Dict[str, float]:
        """Collect service metrics."""
        if not self.enabled:
            return {}
        
        metrics = {}
        
        for service in self.services:
            service_name = service.get('name')
            health_url = service.get('health_url')
            metrics_url = service.get('metrics_url')
            
            if not service_name or not health_url:
                continue
            
            try:
                # Check service health
                health_response = requests.get(
                    health_url,
                    timeout=self.timeout
                )
                
                is_healthy = health_response.status_code == 200
                metrics[f'service_{service_name}_healthy'] = 1.0 if is_healthy else 0.0
                metrics[f'service_{service_name}_response_time'] = health_response.elapsed.total_seconds()
                
                # Collect custom metrics if available
                if metrics_url:
                    metrics_response = requests.get(
                        metrics_url,
                        timeout=self.timeout
                    )
                    
                    if metrics_response.status_code == 200:
                        service_metrics = metrics_response.json()
                        
                        # Add service metrics with prefix
                        for key, value in service_metrics.items():
                            if isinstance(value, (int, float)):
                                metrics[f'service_{service_name}_{key}'] = float(value)
            
            except requests.RequestException as e:
                self.logger.error(f"Error collecting metrics for {service_name}: {e}")
                metrics[f'service_{service_name}_healthy'] = 0.0
            
            except Exception as e:
                self.logger.error(f"Unexpected error for {service_name}: {e}")
        
        self.logger.debug(f"Collected {len(metrics)} service metrics")
        
        return metrics


class CustomMetricCollector(BaseCollector):
    """Collects custom application-specific metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize custom metric collector."""
        super().__init__(config)
        self.metric_sources = config.get('sources', [])
    
    def collect(self) -> Dict[str, float]:
        """Collect custom metrics."""
        if not self.enabled:
            return {}
        
        metrics = {}
        
        # Placeholder for custom metric collection
        # In production, this would integrate with application-specific
        # metric sources, databases, APIs, etc.
        
        for source in self.metric_sources:
            source_name = source.get('name')
            source_type = source.get('type')
            
            # Example: could support different source types
            # - database queries
            # - file-based metrics
            # - external APIs
            # - message queues
            
            self.logger.debug(f"Collecting from custom source: {source_name}")
        
        return metrics


class MetricsCollector:
    """
    Aggregates metrics from multiple collectors.
    """
    
    def __init__(self, collectors: List[BaseCollector]):
        """
        Initialize metrics collector.
        
        Args:
            collectors: List of metric collectors
        """
        self.collectors = collectors
        self.logger = logging.getLogger(__name__)
    
    def collect_all(self) -> Dict[str, float]:
        """
        Collect metrics from all enabled collectors.
        
        Returns:
            Dictionary of all collected metrics
        """
        all_metrics = {}
        
        for collector in self.collectors:
            if not collector.is_enabled():
                continue
            
            try:
                collector_metrics = collector.collect()
                all_metrics.update(collector_metrics)
            
            except Exception as e:
                self.logger.error(
                    f"Error collecting from {collector.__class__.__name__}: {e}"
                )
        
        return all_metrics
    
    def add_collector(self, collector: BaseCollector):
        """
        Add a new collector.
        
        Args:
            collector: Collector to add
        """
        self.collectors.append(collector)
    
    def remove_collector(self, collector_class):
        """
        Remove a collector by class.
        
        Args:
            collector_class: Class of collector to remove
        """
        self.collectors = [
            c for c in self.collectors
            if not isinstance(c, collector_class)
        ]
