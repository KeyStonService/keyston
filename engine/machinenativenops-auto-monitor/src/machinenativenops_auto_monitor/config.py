"""
Configuration management for MachineNativeOps Auto Monitor
Following AAPS configuration standards
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator

class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    interval: int = Field(default=30, ge=1, le=3600, description="Monitoring interval in seconds")
    prometheus_port: int = Field(default=8000, ge=1024, le=65535, description="Prometheus metrics port")
    health_check_timeout: int = Field(default=5, ge=1, le=60, description="Health check timeout")
    
    # Alert thresholds
    cpu_threshold: float = Field(default=80.0, ge=0.0, le=100.0, description="CPU usage alert threshold")
    memory_threshold: float = Field(default=85.0, ge=0.0, le=100.0, description="Memory usage alert threshold")
    disk_threshold: float = Field(default=90.0, ge=0.0, le=100.0, description="Disk usage alert threshold")
    api_response_threshold: float = Field(default=2000.0, ge=0.0, description="API response time threshold (ms)")

class QuantumConfig(BaseModel):
    """Quantum monitoring configuration"""
    enabled: bool = Field(default=False, description="Enable quantum monitoring")
    fidelity_threshold: float = Field(default=0.94, ge=0.0, le=1.0, description="Quantum fidelity threshold")
    coherence_time_threshold: float = Field(default=100.0, ge=0.0, description="Coherence time threshold (μs)")
    error_rate_threshold: float = Field(default=0.01, ge=0.0, le=1.0, description="Quantum error rate threshold")
    
    # Quantum services to monitor
    services: Dict[str, str] = Field(default_factory=dict, description="Quantum service endpoints")

class ServicesConfig(BaseModel):
    """Services configuration"""
    foundation_layer: Dict[str, str] = Field(default_factory=dict, description="Foundation layer services")
    intelligence_layer: Dict[str, str] = Field(default_factory=dict, description="Intelligence layer services") 
    quantum_layer: Dict[str, str] = Field(default_factory=dict, description="Quantum layer services")
    
    # Auto-discovery
    auto_discover: bool = Field(default=True, description="Auto-discover services")
    discovery_namespaces: list[str] = Field(default_factory=lambda: ["default", "machinenativenops-system"])

class AutoRepairConfig(BaseModel):
    """Auto-repair configuration"""
    enabled: bool = Field(default=False, description="Enable auto-repair (Phase 1: disabled)")
    max_repair_attempts: int = Field(default=3, ge=1, le=10, description="Max repair attempts")
    cooldown_period: int = Field(default=300, ge=60, le=3600, description="Cooldown period (seconds)")
    
    strategies: list[str] = Field(default_factory=list, description="Repair strategies")

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file: str = Field(default="/var/log/machinenativenops/monitor.log", description="Log file path")
    max_size: str = Field(default="10MB", description="Max log file size")
    backup_count: int = Field(default=5, ge=1, le=20, description="Number of backup logs")

class DatabaseConfig(BaseModel):
    """Database configuration"""
    path: str = Field(default="/var/lib/machinenativenops/auto_monitor/metrics.db", description="Database path")
    retention_days: int = Field(default=30, ge=1, le=365, description="Data retention days")
    backup_enabled: bool = Field(default=True, description="Enable database backups")
    backup_interval: int = Field(default=3600, ge=300, le=86400, description="Backup interval (seconds)")

class NetworkConfig(BaseModel):
    """Network configuration"""
    base_url: Optional[str] = Field(default=None, description="Base URL for external services")
    timeout: int = Field(default=30, ge=1, le=300, description="Network timeout")
    retry_attempts: int = Field(default=3, ge=1, le=10, description="Retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    
    # Headers and authentication
    headers: Dict[str, str] = Field(default_factory=dict, description="Default headers")
    auth_token: Optional[str] = Field(default=None, description="Authentication token")

class Config(BaseModel):
    """Main configuration model"""
    # Core settings
    version: str = Field(default="2.0.0", description="Configuration version")
    architecture_hash: str = Field(default="e7f8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9", description="Architecture hash")
    
    # Configuration sections
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    quantum: QuantumConfig = Field(default_factory=QuantumConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    auto_repair: AutoRepairConfig = Field(default_factory=AutoRepairConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    
    @validator('architecture_hash')
    def validate_architecture_hash(cls, v):
        """Validate architecture hash"""
        if len(v) != 64:
            raise ValueError("Architecture hash must be 64 characters")
        return v
    
    class Config:
        extra = "forbid"  # Prevent additional fields

def load_config(config_path: str) -> Config:
    """Load configuration from file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Try to load from package assets
        assets_dir = Path(__file__).parent.parent / "assets"
        asset_config = assets_dir / "default_config.yaml"
        
        if asset_config.exists():
            config_file = asset_config
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Merge with environment variables
        config_data = merge_env_vars(config_data)
        
        return Config(**config_data)
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {config_path}: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load config from {config_path}: {e}")

def merge_env_vars(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge environment variables into configuration"""
    env_mappings = {
        "MONITORING_INTERVAL": ("monitoring", "interval", int),
        "PROMETHEUS_PORT": ("monitoring", "prometheus_port", int),
        "LOG_LEVEL": ("logging", "level", str),
        "LOG_FILE": ("logging", "file", str),
        "DATABASE_PATH": ("database", "path", str),
        "BASE_URL": ("network", "base_url", str),
        "AUTH_TOKEN": ("network", "auth_token", str),
        "QUANTUM_ENABLED": ("quantum", "enabled", bool),
        "AUTO_REPAIR_ENABLED": ("auto_repair", "enabled", bool),
    }
    
    for env_var, (section, key, type_func) in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            if section not in config_data:
                config_data[section] = {}
            
            # Convert value to appropriate type
            if type_func == bool:
                config_data[section][key] = value.lower() in ('true', '1', 'yes', 'on')
            else:
                config_data[section][key] = type_func(value)
    
    return config_data

def save_default_config(output_path: str) -> None:
    """Save default configuration to file"""
    config = Config()
    
    config_data = config.dict()
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2, sort_keys=False)