"""
Configuration Manager - Unified configuration management

This module provides centralized configuration management for all
SynergyMesh phases and components.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


@dataclass
class PhaseConfig:
    """Configuration for a specific phase"""
    phase_id: int
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConfiguration:
    """Complete system configuration"""
    # General
    name: str = "SynergyMesh"
    version: str = "2.0.0"
    environment: Environment = Environment.DEVELOPMENT
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance
    max_concurrent_tasks: int = 100
    task_timeout_seconds: int = 300
    request_timeout_seconds: int = 30
    
    # Health & Monitoring
    health_check_interval_seconds: int = 60
    metrics_collection_interval_seconds: int = 30
    
    # Safety
    enable_safety_mechanisms: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    enable_auto_rollback: bool = True
    
    # Automation
    enable_auto_remediation: bool = True
    enable_self_learning: bool = True
    enable_auto_scaling: bool = False
    
    # Integration
    enable_mcp_servers: bool = True
    enable_slsa_provenance: bool = True
    enable_cloud_delegation: bool = True
    
    # Phase configurations
    phase_configs: Dict[int, PhaseConfig] = field(default_factory=dict)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'environment': self.environment.value,
            'log_level': self.log_level,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'task_timeout_seconds': self.task_timeout_seconds,
            'health_check_interval_seconds': self.health_check_interval_seconds,
            'enable_safety_mechanisms': self.enable_safety_mechanisms,
            'enable_circuit_breaker': self.enable_circuit_breaker,
            'enable_auto_remediation': self.enable_auto_remediation,
            'enable_mcp_servers': self.enable_mcp_servers,
            'enable_slsa_provenance': self.enable_slsa_provenance,
            'enable_cloud_delegation': self.enable_cloud_delegation,
            'phase_configs': {
                k: {'phase_id': v.phase_id, 'enabled': v.enabled, 'settings': v.settings}
                for k, v in self.phase_configs.items()
            },
            'custom_settings': self.custom_settings
        }


class ConfigurationManager:
    """
    Configuration Manager - 配置管理器
    
    Centralized configuration management providing:
    - Environment-specific configurations
    - Phase-specific settings
    - Dynamic configuration updates
    - Configuration validation
    - Secret management integration
    """
    
    def __init__(self, base_config: Optional[SystemConfiguration] = None):
        """Initialize the configuration manager"""
        self._config = base_config or SystemConfiguration()
        self._config_sources: List[str] = []
        self._watchers: List[callable] = []
        self._last_updated: Optional[datetime] = None
        self._validation_errors: List[str] = []
        
        # Initialize default phase configs
        self._init_default_phase_configs()
        
    def _init_default_phase_configs(self) -> None:
        """Initialize default configurations for all phases"""
        phase_defaults = {
            1: {'name': 'Core Autonomous Coordination', 'critical': True},
            2: {'name': 'Advanced Interaction & Orchestration'},
            3: {'name': 'AI Decision Engine'},
            4: {'name': 'Autonomous Trust & Governance'},
            5: {'name': 'AI Quality & Bug Prevention'},
            6: {'name': 'AI Supreme Directive Constitution', 'critical': True},
            7: {'name': 'Knowledge & Skills Training'},
            8: {'name': 'Execution Engine & Tech Stack'},
            9: {'name': 'Complete Execution Architecture'},
            10: {'name': 'Safety Mechanisms', 'critical': True},
            11: {'name': 'Intelligent Monitoring & Remediation'},
            12: {'name': 'CI Error Auto-Handler'},
            13: {'name': 'Deep Verifiable YAML System'},
            14: {'name': 'Advanced System Architecture'},
            15: {'name': 'Intelligent Automation'},
            16: {'name': 'Autonomous System'},
            17: {'name': 'Intelligent Hyperautomation'},
            18: {'name': 'Automation Architect'},
            19: {'name': 'MCP Servers Enhanced'},
            20: {'name': 'SLSA L3 Provenance System'},
            21: {'name': 'Cloud Agent Delegation'},
            22: {'name': 'Unified System Integration', 'critical': True},
        }
        
        for phase_id, defaults in phase_defaults.items():
            if phase_id not in self._config.phase_configs:
                self._config.phase_configs[phase_id] = PhaseConfig(
                    phase_id=phase_id,
                    settings=defaults
                )
                
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a file
        
        Args:
            file_path: Path to configuration file (JSON or YAML)
            
        Returns:
            True if loaded successfully
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Configuration file not found: {file_path}")
                return False
                
            with open(path, 'r') as f:
                if path.suffix in ('.yaml', '.yml'):
                    import yaml
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
                    
            self._apply_config_data(data)
            self._config_sources.append(file_path)
            self._last_updated = datetime.now(timezone.utc)
            
            logger.info(f"Loaded configuration from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
            return False
            
    def load_from_env(self, prefix: str = "SYNERGYMESH_") -> None:
        """
        Load configuration from environment variables
        
        Args:
            prefix: Environment variable prefix
        """
        env_mappings = {
            'ENVIRONMENT': ('environment', lambda x: Environment(x.lower())),
            'LOG_LEVEL': ('log_level', str),
            'MAX_CONCURRENT_TASKS': ('max_concurrent_tasks', int),
            'TASK_TIMEOUT': ('task_timeout_seconds', int),
            'HEALTH_CHECK_INTERVAL': ('health_check_interval_seconds', int),
            'ENABLE_SAFETY': ('enable_safety_mechanisms', lambda x: x.lower() == 'true'),
            'ENABLE_CIRCUIT_BREAKER': ('enable_circuit_breaker', lambda x: x.lower() == 'true'),
            'ENABLE_AUTO_REMEDIATION': ('enable_auto_remediation', lambda x: x.lower() == 'true'),
            'ENABLE_MCP_SERVERS': ('enable_mcp_servers', lambda x: x.lower() == 'true'),
            'ENABLE_SLSA': ('enable_slsa_provenance', lambda x: x.lower() == 'true'),
            'ENABLE_CLOUD_DELEGATION': ('enable_cloud_delegation', lambda x: x.lower() == 'true'),
        }
        
        for env_suffix, (attr, converter) in env_mappings.items():
            env_var = f"{prefix}{env_suffix}"
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(self._config, attr, converter(value))
                    logger.debug(f"Set {attr} from {env_var}")
                except Exception as e:
                    logger.warning(f"Failed to parse {env_var}: {e}")
                    
        self._config_sources.append('environment')
        self._last_updated = datetime.now(timezone.utc)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        parts = key.split('.')
        value = self._config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            elif hasattr(self._config, 'custom_settings') and part in self._config.custom_settings:
                return self._config.custom_settings[part]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        parts = key.split('.')
        
        if len(parts) == 1:
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                self._config.custom_settings[key] = value
        else:
            # Navigate to parent and set
            parent = self._config
            for part in parts[:-1]:
                if hasattr(parent, part):
                    parent = getattr(parent, part)
                elif isinstance(parent, dict):
                    parent = parent.setdefault(part, {})
                    
            final_key = parts[-1]
            if hasattr(parent, final_key):
                setattr(parent, final_key, value)
            elif isinstance(parent, dict):
                parent[final_key] = value
                
        self._last_updated = datetime.now(timezone.utc)
        self._notify_watchers(key, value)
        
    def get_phase_config(self, phase_id: int) -> Optional[PhaseConfig]:
        """Get configuration for a specific phase"""
        return self._config.phase_configs.get(phase_id)
        
    def set_phase_config(self, phase_id: int, config: PhaseConfig) -> None:
        """Set configuration for a specific phase"""
        self._config.phase_configs[phase_id] = config
        self._last_updated = datetime.now(timezone.utc)
        
    def enable_phase(self, phase_id: int) -> bool:
        """Enable a phase"""
        phase_config = self._config.phase_configs.get(phase_id)
        if phase_config:
            phase_config.enabled = True
            return True
        return False
        
    def disable_phase(self, phase_id: int) -> bool:
        """Disable a phase"""
        phase_config = self._config.phase_configs.get(phase_id)
        if phase_config:
            phase_config.enabled = False
            return True
        return False
        
    def is_phase_enabled(self, phase_id: int) -> bool:
        """Check if a phase is enabled"""
        phase_config = self._config.phase_configs.get(phase_id)
        return phase_config.enabled if phase_config else False
        
    def validate(self) -> bool:
        """
        Validate the configuration
        
        Returns:
            True if configuration is valid
        """
        self._validation_errors.clear()
        
        # Validate general settings
        if self._config.max_concurrent_tasks < 1:
            self._validation_errors.append("max_concurrent_tasks must be >= 1")
            
        if self._config.task_timeout_seconds < 1:
            self._validation_errors.append("task_timeout_seconds must be >= 1")
            
        if self._config.health_check_interval_seconds < 5:
            self._validation_errors.append("health_check_interval_seconds must be >= 5")
            
        # Validate phase configs
        for phase_id, phase_config in self._config.phase_configs.items():
            if phase_id < 1 or phase_id > 22:
                self._validation_errors.append(f"Invalid phase_id: {phase_id}")
                
        return len(self._validation_errors) == 0
        
    def get_validation_errors(self) -> List[str]:
        """Get validation errors from last validation"""
        return self._validation_errors.copy()
        
    def watch(self, callback: callable) -> None:
        """Register a configuration change watcher"""
        self._watchers.append(callback)
        
    def unwatch(self, callback: callable) -> None:
        """Unregister a configuration change watcher"""
        if callback in self._watchers:
            self._watchers.remove(callback)
            
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration as dictionary"""
        return self._config.to_dict()
        
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to a file
        
        Args:
            file_path: Path to save configuration
            
        Returns:
            True if saved successfully
        """
        try:
            path = Path(file_path)
            data = self.export_config()
            
            with open(path, 'w') as f:
                if path.suffix in ('.yaml', '.yml'):
                    import yaml
                    yaml.safe_dump(data, f, default_flow_style=False)
                else:
                    json.dump(data, f, indent=2)
                    
            logger.info(f"Saved configuration to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            return False
            
    def get_environment(self) -> Environment:
        """Get current environment"""
        return self._config.environment
        
    def is_production(self) -> bool:
        """Check if running in production"""
        return self._config.environment == Environment.PRODUCTION
        
    def is_development(self) -> bool:
        """Check if running in development"""
        return self._config.environment == Environment.DEVELOPMENT
        
    @property
    def config(self) -> SystemConfiguration:
        """Get the system configuration"""
        return self._config
        
    @property
    def last_updated(self) -> Optional[datetime]:
        """Get last update timestamp"""
        return self._last_updated
        
    @property
    def config_sources(self) -> List[str]:
        """Get list of configuration sources"""
        return self._config_sources.copy()
        
    def _apply_config_data(self, data: Dict[str, Any]) -> None:
        """Apply configuration data from dictionary"""
        for key, value in data.items():
            if key == 'environment' and isinstance(value, str):
                self._config.environment = Environment(value.lower())
            elif key == 'phase_configs' and isinstance(value, dict):
                for phase_id_str, phase_data in value.items():
                    phase_id = int(phase_id_str)
                    self._config.phase_configs[phase_id] = PhaseConfig(
                        phase_id=phase_id,
                        enabled=phase_data.get('enabled', True),
                        settings=phase_data.get('settings', {}),
                        overrides=phase_data.get('overrides', {})
                    )
            elif hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                self._config.custom_settings[key] = value
                
    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify watchers of configuration change"""
        for watcher in self._watchers:
            try:
                watcher(key, value)
            except Exception as e:
                logger.error(f"Configuration watcher error: {e}")


# Factory function
def create_configuration_manager(
    config: Optional[SystemConfiguration] = None
) -> ConfigurationManager:
    """Create a new ConfigurationManager instance"""
    return ConfigurationManager(config)


# Default configuration for production
def get_production_config() -> SystemConfiguration:
    """Get production-ready configuration"""
    return SystemConfiguration(
        environment=Environment.PRODUCTION,
        log_level="WARNING",
        max_concurrent_tasks=200,
        enable_safety_mechanisms=True,
        enable_circuit_breaker=True,
        enable_auto_rollback=True,
        enable_auto_remediation=True,
        enable_mcp_servers=True,
        enable_slsa_provenance=True,
        enable_cloud_delegation=True
    )


# Default configuration for development
def get_development_config() -> SystemConfiguration:
    """Get development configuration"""
    return SystemConfiguration(
        environment=Environment.DEVELOPMENT,
        log_level="DEBUG",
        max_concurrent_tasks=10,
        enable_safety_mechanisms=True,
        enable_circuit_breaker=False,
        enable_auto_rollback=False,
        enable_auto_remediation=False,
        enable_mcp_servers=True,
        enable_slsa_provenance=True,
        enable_cloud_delegation=True
    )
