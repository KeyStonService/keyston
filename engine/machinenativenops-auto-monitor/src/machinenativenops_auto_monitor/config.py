"""
Configuration Module
配置模組

Handles configuration loading and management for the auto-monitor system.
"""

import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    """Configuration for the auto-monitor system."""
    
    # Application settings
    mode: str = 'development'  # 'development' or 'production'
    port: int = 8080
    host: str = '0.0.0.0'
    
    # Collection intervals (in seconds)
    collection_interval: int = 10
    log_collection_interval: int = 5
    event_collection_interval: int = 15
    
    # Storage settings
    storage_backend: str = 'memory'  # 'memory', 'file', 'database'
    storage_path: Optional[str] = None
    retention_days: int = 7
    
    # Alert settings
    enable_alerts: bool = True
    alert_channels: list = field(default_factory=list)
    
    # Namespace configuration
    namespace: str = 'machinenativeops'
    registry: str = 'registry.machinenativeops.io'
    certificate_path: str = 'etc/machinenativeops/pkl'
    cluster_token: str = 'super-agent-etcd-cluster'
    
    # Feature flags
    enable_kubernetes: bool = False
    enable_metrics_export: bool = True
    enable_log_aggregation: bool = True
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'MonitorConfig':
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from: {config_path}")
            return cls(**data)
            
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            logger.info("Using default configuration")
            return cls.default()
    
    @classmethod
    def default(cls) -> 'MonitorConfig':
        """Get default configuration."""
        return cls()
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def to_yaml(self, output_path: Path):
        """Save configuration to YAML file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            logger.info(f"Configuration saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.mode not in ['development', 'production']:
            logger.error(f"Invalid mode: {self.mode}")
            return False
        
        if self.port < 1 or self.port > 65535:
            logger.error(f"Invalid port: {self.port}")
            return False
        
        if self.collection_interval < 1:
            logger.error(f"Invalid collection_interval: {self.collection_interval}")
            return False
        
        logger.info("✅ Configuration validated successfully")
        return True


def create_default_config_file(output_path: Path):
    """Create a default configuration file."""
    config = MonitorConfig.default()
    config.to_yaml(output_path)
    print(f"✅ Created default configuration file: {output_path}")


if __name__ == "__main__":
    # Create a sample configuration file
    sample_path = Path("config.example.yaml")
    create_default_config_file(sample_path)
