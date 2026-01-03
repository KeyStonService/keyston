#!/usr/bin/env python3
# scripts/env/environment_manager.py
# Phase-1: Multi-language Environment Manager for Multi-Agent AI CI/CD
"""
Environment Manager for chatops multi-agent AI infrastructure.
Supports development, staging, and production environments.
"""
import os
import sys
import yaml
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    """Configuration for a single environment."""
    name: str
    variables: Dict[str, str]
    services: List[str]
    ports: Dict[str, int]
    required_variables: List[str] = None

    def __post_init__(self):
        if self.required_variables is None:
            self.required_variables = []


class EnvironmentManager:
    """
    Manages environment configuration for multi-agent AI pipelines.

    Responsibilities:
    - Load and validate environment configurations
    - Set environment variables
    - Start/stop dependent services
    - Health check services
    """

    def __init__(self, config_path: str = 'scripts/env/environments.yml'):
        self.config_path = Path(config_path)
        self.environments = self._load_config()

    def _load_config(self) -> Dict:
        """Load environment configuration from YAML file."""
        if not self.config_path.exists():
            return self._create_default_config()
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _create_default_config(self) -> Dict:
        """Create default environment configuration."""
        default_config = {
            'environments': {
                'development': {
                    'variables': {
                        'DEBUG': 'true',
                        'LOG_LEVEL': 'debug',
                        'DEPLOY_TARGET': 'dev'
                    },
                    'services': ['redis', 'postgres'],
                    'ports': {'gateway': 3000, 'engine': 8000, 'grpc': 50051},
                    'required_variables': []
                },
                'staging': {
                    'variables': {
                        'DEBUG': 'false',
                        'LOG_LEVEL': 'info',
                        'DEPLOY_TARGET': 'stage'
                    },
                    'services': ['redis', 'postgres', 'nginx'],
                    'ports': {'gateway': 80, 'engine': 8080, 'grpc': 50051},
                    'required_variables': ['STAGE_DB_URL']
                },
                'production': {
                    'variables': {
                        'DEBUG': 'false',
                        'LOG_LEVEL': 'warn',
                        'DEPLOY_TARGET': 'prod'
                    },
                    'services': ['redis-cluster', 'postgres-ha', 'nginx'],
                    'ports': {'gateway': 443, 'engine': 8443, 'grpc': 50051},
                    'required_variables': ['PROD_DB_URL', 'PROD_REDIS_URL']
                }
            },
            'agent_config': {
                'policy_agent': {
                    'enabled': True,
                    'verdict_default': 'pass'
                },
                'ci_agent': {
                    'enabled': True,
                    'trace_prefix': 'trace'
                },
                'security_agent': {
                    'enabled': True,
                    'secret_mask': True
                },
                'deploy_agent': {
                    'enabled': False,
                    'phase': 'phase-1-disabled'
                },
                'observability_agent': {
                    'enabled': True,
                    'audit_path': 'var/audit'
                },
                'repair_agent': {
                    'enabled': False,
                    'phase': 'phase-1-disabled'
                }
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        return default_config

    def setup_environment(self, env_name: str) -> bool:
        """
        Set up the specified environment.

        Args:
            env_name: Name of environment (development, staging, production)

        Returns:
            True if setup succeeded, False otherwise
        """
        if env_name not in self.environments.get('environments', {}):
            print(f"Environment '{env_name}' does not exist")
            return False

        env_config = self.environments['environments'][env_name]

        # Set environment variables
        for key, value in env_config.get('variables', {}).items():
            os.environ[key] = str(value)
            print(f"Set environment variable: {key}={value}")

        # Start required services
        services = env_config.get('services', [])
        if services:
            self._start_services(services)

        print(f"Environment '{env_name}' setup complete")
        return True

    def _start_services(self, services: List[str]):
        """Start Docker Compose services."""
        for service in services:
            try:
                result = subprocess.run(
                    ['docker-compose', 'up', '-d', service],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"Service '{service}' started successfully")
                else:
                    print(f"Service '{service}' failed to start: {result.stderr}")
            except FileNotFoundError:
                print(f"Docker Compose not installed, skipping service '{service}'")
            except subprocess.TimeoutExpired:
                print(f"Service '{service}' start timed out")
            except Exception as e:
                print(f"Error starting service '{service}': {e}")

    def validate_environment(self, env_name: str) -> bool:
        """
        Validate that an environment is properly configured.

        Args:
            env_name: Name of environment to validate

        Returns:
            True if validation passed, False otherwise
        """
        if env_name not in self.environments.get('environments', {}):
            print(f"Environment '{env_name}' not found")
            return False

        env_config = self.environments['environments'][env_name]

        # Check required environment variables
        required_vars = env_config.get('required_variables', [])
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False

        # Check service health
        services = env_config.get('services', [])
        unhealthy_services = []
        for service in services:
            if not self._check_service_health(service):
                unhealthy_services.append(service)

        if unhealthy_services:
            print(f"Unhealthy services: {', '.join(unhealthy_services)}")
            # Don't fail - services may not be running locally
            print("Note: Service health check failures may be expected in local development")

        print(f"Environment '{env_name}' validation complete")
        return True

    def _check_service_health(self, service: str) -> bool:
        """Check if a Docker Compose service is healthy."""
        try:
            result = subprocess.run(
                ['docker-compose', 'ps', service],
                capture_output=True,
                text=True,
                timeout=30
            )
            return 'Up' in result.stdout
        except Exception:
            return False

    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """Get configuration for a specific agent."""
        agent_config = self.environments.get('agent_config', {})
        return agent_config.get(agent_name)

    def list_environments(self) -> List[str]:
        """List all available environments."""
        return list(self.environments.get('environments', {}).keys())

    def get_deploy_target(self, env_name: str) -> str:
        """Get the deploy target for an environment."""
        env_config = self.environments.get('environments', {}).get(env_name, {})
        variables = env_config.get('variables', {})
        return variables.get('DEPLOY_TARGET', 'dev')


def main():
    """CLI entry point for environment manager."""
    manager = EnvironmentManager()

    if len(sys.argv) < 2:
        print("Usage: python environment_manager.py <command> [environment]")
        print("")
        print("Commands:")
        print("  setup <env>     - Set up an environment")
        print("  validate <env>  - Validate an environment")
        print("  list            - List all environments")
        print("  target <env>    - Get deploy target for environment")
        print("")
        print("Environments:", ", ".join(manager.list_environments()))
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        print("Available environments:")
        for env in manager.list_environments():
            target = manager.get_deploy_target(env)
            print(f"  - {env} (deploy-target: {target})")
        sys.exit(0)

    if len(sys.argv) < 3:
        print(f"Error: Command '{command}' requires an environment name")
        sys.exit(1)

    env_name = sys.argv[2]

    if command == 'setup':
        success = manager.setup_environment(env_name)
        if success:
            manager.validate_environment(env_name)
        sys.exit(0 if success else 1)

    elif command == 'validate':
        success = manager.validate_environment(env_name)
        sys.exit(0 if success else 1)

    elif command == 'target':
        target = manager.get_deploy_target(env_name)
        print(target)
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
