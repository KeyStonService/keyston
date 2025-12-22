"""
Data Collectors Module
數據收集模組

Collects metrics, logs, and events from various sources for monitoring.
"""

import logging
import psutil
import platform
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Represents a metric data point."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class LogEntry:
    """Represents a log entry."""
    level: str
    message: str
    timestamp: datetime
    source: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class Event:
    """Represents a system event."""
    type: str
    description: str
    timestamp: datetime
    severity: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
        }


class MetricsCollector:
    """Collects system and application metrics."""
    
    def __init__(self, interval: int = 10):
        self.interval = interval
        self.last_collection = None
    
    def collect(self) -> Dict:
        """Collect current metrics."""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'cpu_count': psutil.cpu_count(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'disk_percent': psutil.disk_usage('/').percent,
                'disk_free_gb': psutil.disk_usage('/').free / (1024**3),
                'disk_total_gb': psutil.disk_usage('/').total / (1024**3),
                'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024**2),
                'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024**2),
                'process_count': len(psutil.pids()),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            }
            
            self.last_collection = datetime.now()
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    def collect_process_metrics(self, pid: Optional[int] = None) -> Dict:
        """Collect metrics for a specific process."""
        try:
            process = psutil.Process(pid) if pid else psutil.Process()
            
            return {
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_percent': process.memory_percent(),
                'memory_mb': process.memory_info().rss / (1024**2),
                'num_threads': process.num_threads(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            return {}


class LogCollector:
    """Collects logs from various sources."""
    
    def __init__(self):
        self.log_buffer: List[LogEntry] = []
    
    def collect(self) -> List[LogEntry]:
        """Collect recent logs."""
        # In a real implementation, this would collect from log files,
        # syslog, or other log sources
        logs = self.log_buffer.copy()
        self.log_buffer.clear()
        return logs
    
    def add_log(self, level: str, message: str, source: str, metadata: Dict = None):
        """Add a log entry to the buffer."""
        entry = LogEntry(
            level=level,
            message=message,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
        )
        self.log_buffer.append(entry)


class EventCollector:
    """Collects system events."""
    
    def __init__(self):
        self.event_buffer: List[Event] = []
        self._last_check = datetime.now()
    
    def collect(self) -> List[Event]:
        """Collect recent events."""
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        
        # Auto-detect system events
        self._detect_system_events()
        
        return events
    
    def _detect_system_events(self):
        """Detect and record system events."""
        # Check for high resource usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > 90:
            self.add_event(
                type='high_cpu',
                description=f'High CPU usage detected: {cpu_usage}%',
                severity='warning'
            )
        
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > 90:
            self.add_event(
                type='high_memory',
                description=f'High memory usage detected: {memory_usage}%',
                severity='warning'
            )
    
    def add_event(self, type: str, description: str, severity: str, metadata: Dict = None):
        """Add an event to the buffer."""
        event = Event(
            type=type,
            description=description,
            timestamp=datetime.now(),
            severity=severity,
            metadata=metadata or {},
        )
        self.event_buffer.append(event)


class KubernetesCollector:
    """Collects metrics from Kubernetes clusters."""
    
    def __init__(self):
        self.enabled = False
        # In a real implementation, initialize k8s client here
    
    def collect_pod_metrics(self) -> List[Dict]:
        """Collect metrics from all pods."""
        # Placeholder for Kubernetes integration
        return []
    
    def collect_node_metrics(self) -> List[Dict]:
        """Collect metrics from all nodes."""
        # Placeholder for Kubernetes integration
        return []
Metrics collectors for system, quantum, and Kubernetes monitoring
"""

import os
import psutil
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

try:
    from kubernetes import client, config
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False

from .config import QuantumConfig, ServicesConfig

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    load_average: Optional[tuple]
    uptime: float
    process_count: int
    timestamp: str

@dataclass
class QuantumMetrics:
    """Quantum metrics data structure"""
    fidelity: float
    coherence_time: float
    error_rate: float
    qubits_active: int
    state_vector: str
    timestamp: str

class SystemCollector:
    """System metrics collector"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def collect(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Load average (Unix only)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except (AttributeError, OSError):
                # Windows doesn't have load average
                pass
            
            # System info
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            # Process count
            process_count = len(psutil.pids())
            
            metrics = {
                'timestamp': timestamp,
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_current': cpu_freq.current if cpu_freq else None,
                    'frequency_min': cpu_freq.min if cpu_freq else None,
                    'frequency_max': cpu_freq.max if cpu_freq else None,
                },
                'memory': {
                    'total_bytes': memory.total,
                    'available_bytes': memory.available,
                    'used_bytes': memory.used,
                    'usage_percent': memory.percent,
                    'buffers_bytes': getattr(memory, 'buffers', 0),
                    'cached_bytes': getattr(memory, 'cached', 0),
                },
                'disk': {
                    'total_bytes': disk.total,
                    'used_bytes': disk.used,
                    'free_bytes': disk.free,
                    'usage_percent': (disk.used / disk.total) * 100,
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                    'errors_in': network.errin,
                    'errors_out': network.errout,
                    'drop_in': network.dropin,
                    'drop_out': network.dropout,
                },
                'system': {
                    'uptime_seconds': uptime,
                    'boot_time': boot_time,
                    'process_count': process_count,
                    'load_average': load_avg,
                    'os_info': {
                        'system': os.name,
                        'platform': os.uname().sysname if hasattr(os, 'uname') else None,
                        'release': os.uname().release if hasattr(os, 'uname') else None,
                        'version': os.uname().version if hasattr(os, 'uname') else None,
                    }
                }
            }
            
            # Flatten for easier database storage
            flat_metrics = self._flatten_metrics(metrics)
            
            self.logger.debug(f"Collected system metrics: {len(flat_metrics)} fields")
            return flat_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            raise
    
    def _flatten_metrics(self, metrics: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested metrics dictionary"""
        flat = {}
        
        for key, value in metrics.items():
            if key == 'timestamp':
                flat['timestamp'] = value
            elif isinstance(value, dict):
                nested_flat = self._flatten_metrics(value, f"{prefix}{key}_")
                flat.update(nested_flat)
            elif isinstance(value, tuple):
                for i, item in enumerate(value):
                    flat[f"{prefix}{key}_{i}"] = item
            else:
                flat[f"{prefix}{key}"] = value
        
        return flat

class QuantumCollector:
    """Quantum metrics collector"""
    
    def __init__(self, config: QuantumConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def collect(self) -> Dict[str, Any]:
        """Collect quantum metrics"""
        if not self.config.enabled:
            return {'quantum_enabled': False}
        
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Simulate quantum metrics (in real implementation, this would connect to actual quantum hardware)
            metrics = {
                'timestamp': timestamp,
                'quantum_enabled': True,
                'quantum_fidelity': self._get_quantum_fidelity(),
                'quantum_coherence_time': self._get_quantum_coherence_time(),
                'quantum_error_rate': self._get_quantum_error_rate(),
                'quantum_qubits_active': self._get_active_qubits(),
                'quantum_state_vector': '|ψ⟩',  # Simplified state representation
            }
            
            self.logger.debug(f"Collected quantum metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect quantum metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'quantum_enabled': True,
                'quantum_error': str(e)
            }
    
    def _get_quantum_fidelity(self) -> float:
        """Get quantum fidelity (simulated)"""
        # In real implementation, this would query quantum hardware
        return max(0.0, min(1.0, self.config.fidelity_threshold + (hash(time.time()) % 100 - 50) / 1000))
    
    def _get_quantum_coherence_time(self) -> float:
        """Get quantum coherence time (simulated)"""
        # In real implementation, this would measure actual coherence
        return self.config.coherence_time_threshold + (hash(time.time()) % 100) / 10
    
    def _get_quantum_error_rate(self) -> float:
        """Get quantum error rate (simulated)"""
        # In real implementation, this would measure actual error rates
        return max(0.0, self.config.error_rate_threshold - (hash(time.time()) % 100) / 10000)
    
    def _get_active_qubits(self) -> int:
        """Get number of active qubits (simulated)"""
        # In real implementation, this would count active qubits
        return (hash(time.time()) % 50) + 1

class KubernetesCollector:
    """Kubernetes services collector"""
    
    def __init__(self, config: ServicesConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Kubernetes client
        self.k8s_client = None
        if KUBERNETES_AVAILABLE:
            try:
                config.load_incluster_config()  # For running in-cluster
                self.k8s_client = client.CoreV1Api()
                self.logger.info("Kubernetes client initialized (in-cluster)")
            except config.ConfigException:
                try:
                    config.load_kube_config()  # For local development
                    self.k8s_client = client.CoreV1Api()
                    self.logger.info("Kubernetes client initialized (kubeconfig)")
                except Exception:
                    self.logger.warning("Kubernetes client initialization failed")
    
    def collect(self) -> Dict[str, Any]:
        """Collect Kubernetes metrics"""
        if not self.k8s_client:
            return {
                'kubernetes_enabled': False,
                'kubernetes_error': 'Kubernetes client not available'
            }
        
        try:
            timestamp = datetime.utcnow().isoformat()
            metrics = {
                'timestamp': timestamp,
                'kubernetes_enabled': True,
            }
            
            # Collect service metrics
            if self.config.auto_discover:
                services_metrics = self._collect_services()
                metrics.update(services_metrics)
            
            # Collect deployment metrics
            deployments_metrics = self._collect_deployments()
            metrics.update(deployments_metrics)
            
            # Collect pod metrics
            pods_metrics = self._collect_pods()
            metrics.update(pods_metrics)
            
            self.logger.debug(f"Collected Kubernetes metrics: {len(metrics)} fields")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect Kubernetes metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'kubernetes_enabled': True,
                'kubernetes_error': str(e)
            }
    
    def _collect_services(self) -> Dict[str, Any]:
        """Collect Kubernetes services metrics"""
        try:
            services = []
            total_services = 0
            healthy_services = 0
            
            for namespace in self.config.discovery_namespaces:
                svc_list = self.k8s_client.list_namespaced_service(namespace)
                
                for svc in svc_list.items:
                    total_services += 1
                    
                    service_info = {
                        'name': svc.metadata.name,
                        'namespace': svc.metadata.namespace,
                        'cluster_ip': svc.spec.cluster_ip,
                        'ports': len(svc.spec.ports) if svc.spec.ports else 0,
                        'selector': svc.spec.selector,
                        'labels': svc.metadata.labels or {},
                    }
                    
                    # Check if service has endpoints (health indicator)
                    try:
                        endpoints = self.k8s_client.read_namespaced_endpoints(
                            svc.metadata.name, namespace
                        )
                        service_info['has_endpoints'] = bool(endpoints.subsets)
                        if endpoints.subsets:
                            healthy_services += 1
                    except Exception:
                        service_info['has_endpoints'] = False
                    
                    services.append(service_info)
            
            return {
                'kubernetes_services_total': total_services,
                'kubernetes_services_healthy': healthy_services,
                'kubernetes_services_details': services,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect services: {e}")
            return {'kubernetes_services_error': str(e)}
    
    def _collect_deployments(self) -> Dict[str, Any]:
        """Collect Kubernetes deployments metrics"""
        try:
            from kubernetes import client as k8s_client
            apps_client = k8s_client.AppsV1Api()
            
            deployments = []
            total_deployments = 0
            ready_deployments = 0
            
            for namespace in self.config.discovery_namespaces:
                deploy_list = apps_client.list_namespaced_deployment(namespace)
                
                for deploy in deploy_list.items:
                    total_deployments += 1
                    
                    deployment_info = {
                        'name': deploy.metadata.name,
                        'namespace': deploy.metadata.namespace,
                        'replicas': deploy.spec.replicas or 0,
                        'ready_replicas': deploy.status.ready_replicas or 0,
                        'available_replicas': deploy.status.available_replicas or 0,
                        'conditions': [],
                    }
                    
                    # Parse conditions
                    for condition in deploy.status.conditions or []:
                        deployment_info['conditions'].append({
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason,
                            'message': condition.message,
                        })
                    
                    # Check if deployment is ready
                    if (deploy.status.ready_replicas or 0) == (deploy.spec.replicas or 0):
                        ready_deployments += 1
                    
                    deployments.append(deployment_info)
            
            return {
                'kubernetes_deployments_total': total_deployments,
                'kubernetes_deployments_ready': ready_deployments,
                'kubernetes_deployments_details': deployments,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect deployments: {e}")
            return {'kubernetes_deployments_error': str(e)}
    
    def _collect_pods(self) -> Dict[str, Any]:
        """Collect Kubernetes pods metrics"""
        try:
            pods = []
            total_pods = 0
            running_pods = 0
            
            for namespace in self.config.discovery_namespaces:
                pod_list = self.k8s_client.list_namespaced_pod(namespace)
                
                for pod in pod_list.items:
                    total_pods += 1
                    
                    pod_info = {
                        'name': pod.metadata.name,
                        'namespace': pod.metadata.namespace,
                        'phase': pod.status.phase,
                        'node_name': pod.spec.node_name,
                        'ip': pod.status.pod_ip,
                        'container_count': len(pod.spec.containers),
                        'container_statuses': [],
                    }
                    
                    # Container status
                    for container_status in pod.status.container_statuses or []:
                        pod_info['container_statuses'].append({
                            'name': container_status.name,
                            'ready': container_status.ready,
                            'restart_count': container_status.restart_count,
                            'state': container_status.state,
                        })
                    
                    if pod.status.phase == 'Running':
                        running_pods += 1
                    
                    pods.append(pod_info)
            
            return {
                'kubernetes_pods_total': total_pods,
                'kubernetes_pods_running': running_pods,
                'kubernetes_pods_details': pods,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect pods: {e}")
            return {'kubernetes_pods_error': str(e)}
