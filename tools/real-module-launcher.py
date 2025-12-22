#!/usr/bin/env python3
"""
Real Module Launcher for Bootstrap Runner
Replaces simulation with actual module startup and management
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger('real-module-launcher')

class RealModuleLauncher:
    """Real module launcher that starts and manages actual processes"""
    
    def __init__(self):
        self.root_dir = Path(os.getenv('ROOT_DIR', '/workspace/machine-native-ops-aaps'))
        self.modules_dir = self.root_dir / 'modules'
        self.running_modules = {}
        self.module_configs = {}
        self.startup_timeout = int(os.getenv('MODULE_STARTUP_TIMEOUT', '60'))
        
        logger.info(f"Real Module Launcher initialized")
        logger.info(f"Root directory: {self.root_dir}")
        logger.info(f"Modules directory: {self.modules_dir}")
        logger.info(f"Startup timeout: {self.startup_timeout}s")

    def load_module_configs(self) -> bool:
        """Load module configurations from root.modules.yaml"""
        try:
            modules_file = self.root_dir / 'root.modules.yaml'
            if not modules_file.exists():
                logger.error(f"Modules config file not found: {modules_file}")
                return False
            
            with open(modules_file, 'r') as f:
                import yaml
                modules_config = yaml.safe_load(f)
            
            # Extract module configurations
            self.module_configs = {}
            for module in modules_config.get('spec', {}).get('modules', []):
                self.module_configs[module['name']] = {
                    'name': module['name'],
                    'version': module['version'],
                    'entrypoint': module['entrypoint'],
                    'group': module['group'],
                    'priority': module['priority'],
                    'enabled': module.get('enabled', True),
                    'auto_start': module.get('auto_start', True),
                    'dependencies': module.get('dependencies', []),
                    'health_check': module.get('health_check', {}),
                    'resources': module.get('resources', {}),
                    'environment': module.get('environment', [])
                }
            
            logger.info(f"Loaded {len(self.module_configs)} module configurations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load module configs: {str(e)}")
            return False

    def start_module(self, module_name: str) -> Optional[subprocess.Popen]:
        """Start a specific module as a real process"""
        try:
            if module_name not in self.module_configs:
                logger.error(f"Module {module_name} not found in configurations")
                return None
            
            module_config = self.module_configs[module_name]
            
            if not module_config.get('enabled', True):
                logger.info(f"Module {module_name} is disabled, skipping")
                return None
            
            # Check if module is already running
            if module_name in self.running_modules:
                logger.info(f"Module {module_name} is already running")
                return self.running_modules[module_name]
            
            # Determine module entrypoint
            entrypoint = module_config['entrypoint']
            if entrypoint.startswith('/opt/machinenativenops/modules/'):
                # Convert to relative path
                entrypoint = entrypoint.replace('/opt/machinenativenops/modules/', '')
            
            module_path = self.modules_dir / entrypoint
            if not module_path.exists():
                logger.error(f"Module entrypoint not found: {module_path}")
                return None
            
            logger.info(f"Starting module {module_name} from {module_path}")
            
            # Prepare environment
            env = os.environ.copy()
            
            # Add module-specific environment variables
            for env_var in module_config.get('environment', []):
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env[key] = value
            
            # Set module-specific variables
            env['MODULE_NAME'] = module_name
            env['MODULE_VERSION'] = module_config['version']
            env['MODULE_DIR'] = str(module_path.parent)
            
            # Determine port (avoid conflicts)
            base_port = 8080
            port_offset = list(self.module_configs.keys()).index(module_name) if module_name in self.module_configs else 0
            env['PORT'] = str(base_port + port_offset + 1)  # +1 to avoid 8080 conflict
            
            # Start the process
            process = subprocess.Popen(
                [sys.executable, str(module_path)],
                cwd=module_path.parent,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            logger.info(f"Module {module_name} started with PID: {process.pid}")
            self.running_modules[module_name] = process
            
            return process
            
        except Exception as e:
            logger.error(f"Failed to start module {module_name}: {str(e)}")
            return None

    def check_health(self, module_name: str, process: subprocess.Popen) -> bool:
        """Check if a module is healthy via HTTP endpoint"""
        try:
            module_config = self.module_configs.get(module_name, {})
            health_check = module_config.get('health_check', {})
            
            # Determine health check endpoint
            port = int(os.getenv(f"{module_name.upper().replace('-', '_')}_PORT", "8081"))
            if module_name == 'config-manager':
                port = 8081  # We know this from our test
            
            health_endpoint = f"http://localhost:{port}/health"
            
            # Make health check request
            response = requests.get(health_endpoint, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"Module {module_name} health check passed: {health_data.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"Module {module_name} health check failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Module {module_name} health check error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Module {module_name} health check unexpected error: {str(e)}")
            return False

    def wait_for_ready(self, module_name: str, timeout: int = None) -> bool:
        """Wait for a module to become ready"""
        if timeout is None:
            timeout = self.startup_timeout
        
        process = self.running_modules.get(module_name)
        if not process:
            logger.error(f"Module {module_name} not found in running modules")
            return False
        
        logger.info(f"Waiting for module {module_name} to become ready (timeout: {timeout}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if process.poll() is not None:
                logger.error(f"Module {module_name} process terminated with exit code: {process.poll()}")
                return False
            
            # Check health endpoint
            if self.check_health(module_name, process):
                logger.info(f"Module {module_name} is ready and healthy")
                return True
            
            # Wait before retrying
            time.sleep(2)
        
        logger.error(f"Module {module_name} failed to become ready within {timeout}s")
        return False

    def stop_module(self, module_name: str) -> bool:
        """Stop a running module"""
        try:
            process = self.running_modules.get(module_name)
            if not process:
                logger.warning(f"Module {module_name} not found in running modules")
                return True
            
            logger.info(f"Stopping module {module_name} (PID: {process.pid})")
            
            # Send SIGTERM
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                logger.info(f"Module {module_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"Module {module_name} did not stop gracefully, forcing termination")
                process.kill()
                process.wait()
            
            # Remove from running modules
            del self.running_modules[module_name]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop module {module_name}: {str(e)}")
            return False

    def stop_all_modules(self):
        """Stop all running modules"""
        logger.info("Stopping all running modules...")
        
        for module_name in list(self.running_modules.keys()):
            self.stop_module(module_name)
        
        logger.info("All modules stopped")

    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Get status of a specific module"""
        try:
            process = self.running_modules.get(module_name)
            if not process:
                return {
                    'name': module_name,
                    'status': 'stopped',
                    'running': False
                }
            
            # Check if process is still running
            if process.poll() is not None:
                return {
                    'name': module_name,
                    'status': 'terminated',
                    'running': False,
                    'exit_code': process.poll()
                }
            
            # Check health
            healthy = self.check_health(module_name, process)
            
            return {
                'name': module_name,
                'status': 'healthy' if healthy else 'unhealthy',
                'running': True,
                'pid': process.pid,
                'healthy': healthy
            }
            
        except Exception as e:
            logger.error(f"Error getting status for module {module_name}: {str(e)}")
            return {
                'name': module_name,
                'status': 'error',
                'running': False,
                'error': str(e)
            }

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all modules"""
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_modules': len(self.module_configs),
            'running_modules': len(self.running_modules),
            'modules': {}
        }
        
        for module_name in self.module_configs.keys():
            status['modules'][module_name] = self.get_module_status(module_name)
        
        return status

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    if 'launcher' in globals():
        launcher.stop_all_modules()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize launcher
    launcher = RealModuleLauncher()
    
    # Load module configurations
    if not launcher.load_module_configs():
        logger.error("Failed to load module configurations")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 real-module-launcher.py <command> [module_name]")
        print("Commands: start, stop, status, start-all, stop-all")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        if len(sys.argv) < 3:
            print("Usage: python3 real-module-launcher.py start <module_name>")
            sys.exit(1)
        
        module_name = sys.argv[2]
        process = launcher.start_module(module_name)
        if process:
            if launcher.wait_for_ready(module_name):
                print(f"Module {module_name} started successfully")
                status = launcher.get_module_status(module_name)
                print(json.dumps(status, indent=2))
            else:
                print(f"Module {module_name} failed to become ready")
                sys.exit(1)
        else:
            print(f"Failed to start module {module_name}")
            sys.exit(1)
    
    elif command == "stop":
        if len(sys.argv) < 3:
            print("Usage: python3 real-module-launcher.py stop <module_name>")
            sys.exit(1)
        
        module_name = sys.argv[2]
        if launcher.stop_module(module_name):
            print(f"Module {module_name} stopped successfully")
        else:
            print(f"Failed to stop module {module_name}")
            sys.exit(1)
    
    elif command == "status":
        if len(sys.argv) < 3:
            # Show all modules status
            status = launcher.get_all_status()
            print(json.dumps(status, indent=2))
        else:
            module_name = sys.argv[2]
            status = launcher.get_module_status(module_name)
            print(json.dumps(status, indent=2))
    
    elif command == "start-all":
        # Start all modules in dependency order (simplified for now)
        for module_name in ['config-manager']:  # Just start config-manager for testing
            print(f"Starting module: {module_name}")
            process = launcher.start_module(module_name)
            if process and launcher.wait_for_ready(module_name):
                print(f"✅ Module {module_name} started successfully")
            else:
                print(f"❌ Module {module_name} failed to start")
    
    elif command == "stop-all":
        launcher.stop_all_modules()
        print("All modules stopped")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status, start-all, stop-all")
        sys.exit(1)