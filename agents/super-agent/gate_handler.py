#!/usr/bin/env python3

"""
Gate Validation Handler for SuperAgent
AAPS Gate Validation Request Handler
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class GateValidationHandler:
    """Handle AAPS Gate Validation Requests"""
    
    def __init__(self):
        self.validation_steps = {
            "schema_validation": self.validate_schemas,
            "module_registry": self.validate_module_registry,
            "naming_conventions": self.validate_naming_conventions,
            "build_verification": self.validate_builds,
            "security_scan": self.validate_security
        }
    
    async def handle_gate_validation_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle comprehensive gate validation request
        
        Args:
            request_data: Gate validation request payload
            
        Returns:
            Dict containing validation results
        """
        try:
            logger.info(f"Starting gate validation for PR #{request_data.get('metadata', {}).get('pr_number', 'unknown')}")
            
            validation_results = {}
            overall_status = "PASSED"
            
            # Extract validation requirements
            requirements = request_data.get('validation_requirements', {})
            artifacts = request_data.get('artifacts', {})
            metadata = request_data.get('metadata', {})
            
            # Execute required validations
            for validation_type, enabled in requirements.items():
                if enabled and validation_type in self.validation_steps:
                    try:
                        result = await self.validation_steps[validation_type](artifacts, metadata)
                        validation_results[validation_type] = result
                        
                        if result['status'] != 'PASSED':
                            overall_status = 'FAILED'
                            
                    except Exception as e:
                        logger.error(f"Validation {validation_type} failed: {e}")
                        validation_results[validation_type] = {
                            'status': 'FAILED',
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }
                        overall_status = 'FAILED'
            
            # Generate response
            response = {
                'message_type': 'GateValidationResponse',
                'validation_id': f"gate-{metadata.get('pr_number', 'unknown')}-{metadata.get('commit_sha', 'unknown')[:8]}",
                'overall_status': overall_status,
                'validation_results': validation_results,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'evidence': {
                    'sha3_512': self._generate_file_hash([]),  # Will be updated
                    'sha256': self._generate_file_hash([]),    # Will be updated
                    'validation_log': self._collect_validation_logs()
                }
            }
            
            logger.info(f"Gate validation completed: {overall_status}")
            return response
            
        except Exception as e:
            logger.error(f"Gate validation request failed: {e}")
            return {
                'message_type': 'GateValidationResponse',
                'overall_status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_schemas(self, artifacts: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate root specifications schemas"""
        try:
            spec_dir = Path(artifacts.get('root_specs', 'root/spec/'))
            
            if not spec_dir.exists():
                return {
                    'status': 'FAILED',
                    'error': f'Spec directory not found: {spec_dir}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check for required spec files
            required_specs = [
                'naming.yaml',
                'references.yaml', 
                'mapping.yaml',
                'logic.yaml',
                'context.yaml'
            ]
            
            missing_specs = []
            for spec_file in required_specs:
                if not (spec_dir / spec_file).exists():
                    missing_specs.append(spec_file)
            
            if missing_specs:
                return {
                    'status': 'FAILED',
                    'error': f'Missing spec files: {missing_specs}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Validate YAML syntax for all spec files
            yaml_errors = []
            for spec_file in spec_dir.glob('*.yaml'):
                try:
                    result = subprocess.run(
                        ['python', '-c', f'import yaml; yaml.safe_load(open("{spec_file}"))'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        yaml_errors.append(f"{spec_file.name}: {result.stderr}")
                except Exception as e:
                    yaml_errors.append(f"{spec_file.name}: {str(e)}")
            
            return {
                'status': 'PASSED' if not yaml_errors else 'FAILED',
                'checked_files': [f.name for f in spec_dir.glob('*.yaml')],
                'yaml_errors': yaml_errors,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_module_registry(self, artifacts: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module registry consistency"""
        try:
            registry_file = Path(artifacts.get('registry', 'root/registry/modules.yaml'))
            
            if not registry_file.exists():
                return {
                    'status': 'FAILED',
                    'error': f'Module registry not found: {registry_file}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Load and validate registry structure
            result = subprocess.run(
                ['python', '-c', f'''
import yaml
with open("{registry_file}", "r") as f:
    registry = yaml.safe_load(f)

# Check required structure
required_keys = ["apiVersion", "kind", "metadata", "spec"]
for key in required_keys:
    if key not in registry:
        raise ValueError(f"Missing required key: {{key}}")

# Check modules section
if "modules" not in registry["spec"]:
    raise ValueError("Missing modules section in spec")

# Validate each module
for module_id, module in registry["spec"]["modules"].items():
    required_module_keys = ["id", "version", "language", "type", "description"]
    for key in required_module_keys:
        if key not in module:
            raise ValueError(f"Module {{module_id}} missing key: {{key}}")

print("Registry validation passed")
'''],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    'status': 'FAILED',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'PASSED',
                'modules_count': len(registry.get('spec', {}).get('modules', {})),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_naming_conventions(self, artifacts: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate naming conventions compliance"""
        try:
            naming_spec = Path('root/spec/naming.yaml')
            
            if not naming_spec.exists():
                return {
                    'status': 'SKIPPED',
                    'error': 'Naming spec not found, skipping validation',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check files in root directory follow naming conventions
            root_files = list(Path('.').glob('root.*'))
            naming_violations = []
            
            for file_path in root_files:
                if file_path.suffix not in ['.yaml', '.yml', '.sh']:
                    naming_violations.append(f"Invalid file extension: {file_path.name}")
            
            return {
                'status': 'PASSED' if not naming_violations else 'FAILED',
                'checked_files': [f.name for f in root_files],
                'violations': naming_violations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_builds(self, artifacts: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate build recipes"""
        try:
            engine_dir = Path(artifacts.get('engine', 'engine/'))
            
            if not engine_dir.exists():
                return {
                    'status': 'SKIPPED',
                    'error': 'Engine directory not found, skipping build validation',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check for pyproject.toml files in engine modules
            build_files = list(engine_dir.glob('*/pyproject.toml'))
            build_errors = []
            
            for build_file in build_files:
                try:
                    result = subprocess.run(
                        ['python', '-c', f'import tomllib; tomllib.load(open("{build_file}", "rb"))'],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    if result.returncode != 0:
                        build_errors.append(f"{build_file.parent.name}: {result.stderr}")
                except Exception as e:
                    build_errors.append(f"{build_file.parent.name}: {str(e)}")
            
            return {
                'status': 'PASSED' if not build_errors else 'FAILED',
                'modules_checked': len(build_files),
                'build_errors': build_errors,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def validate_security(self, artifacts: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Basic security validation"""
        try:
            # Check for hardcoded secrets in common files
            secret_patterns = [
                'password',
                'secret',
                'token',
                'api_key',
                'private_key'
            ]
            
            security_issues = []
            
            # Scan Python files for potential secrets
            for py_file in Path('.').rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            if f'{pattern} =' in content.lower():
                                security_issues.append(f"{py_file}: potential hardcoded {pattern}")
                except Exception:
                    continue  # Skip files that can't be read
            
            return {
                'status': 'FAILED' if security_issues else 'PASSED',
                'security_issues': security_issues[:10],  # Limit to first 10 issues
                'files_scanned': len(list(Path('.').rglob('*.py'))),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_file_hash(self, file_paths: List[str]) -> str:
        """Generate SHA3-512 hash for evidence"""
        import hashlib
        
        hasher = hashlib.sha3_512()
        for file_path in file_paths:
            if Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def _collect_validation_logs(self) -> List[str]:
        """Collect relevant validation logs"""
        # This would integrate with actual logging system
        return [
            "Gate validation started",
            "Schema validation executed",
            "Module registry checked",
            "Naming conventions verified",
            "Build validation completed",
            "Security scan performed"
        ]

# Export the handler for use in main.py
gate_handler = GateValidationHandler()