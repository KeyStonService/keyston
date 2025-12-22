#!/usr/bin/env python3
"""
MachineNativeOps Root Layer Validator
Platform-grade validation system for root layer configuration files
"""

import os
import sys
import json
import yaml
import blake3
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

class RootValidator:
    """Platform-grade root layer validation system"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.schema_file = self.root_dir / "root.validator.schema.yaml"
        self.hash_lock_file = self.root_dir / "root.hashlock.json"
        self.report_file = self.root_dir / "var" / "audit" / "root-validate-report.json"
        
        # Setup logging
        self.setup_logging()
        
        # Load validation schema
        self.schema = self.load_schema()
        
        # Initialize counters
        self.stats = {
            'total_files': 0,
            'passed_files': 0,
            'failed_files': 0,
            'warnings': 0,
            'errors': 0
        }
        
        # Validation results
        self.results = {
            'validation_run': {
                'timestamp': datetime.utcnow().isoformat(),
                'validator_version': 'v1.0.0',
                'root_directory': str(self.root_dir),
                'schema_version': self.schema.get('metadata', {}).get('version', 'unknown')
            },
            'file_results': [],
            'consistency_results': [],
            'summary': {}
        }

    def setup_logging(self):
        """Setup structured logging"""
        # Ensure log directory exists
        log_dir = self.root_dir / "var" / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "root-validator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('RootValidator')

    def load_schema(self) -> Dict[str, Any]:
        """Load validation schema"""
        try:
            with open(self.schema_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Schema file not found: {self.schema_file}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Schema YAML error: {e}")
            return {}

    def validate_file_existence(self) -> List[Dict[str, Any]]:
        """Stage 1: Check all required root files exist"""
        self.logger.info("Stage 1: File existence check")
        
        required_files = []
        for category, files in self.schema.get('spec', {}).get('root_file_types', {}).items():
            required_files.extend(files)
        
        results = []
        
        for file_pattern in required_files:
            if '*' in file_pattern:
                # Handle wildcard patterns
                matching_files = list(self.root_dir.glob(file_pattern))
                if not matching_files:
                    results.append({
                        'stage': 'file_existence',
                        'file': file_pattern,
                        'status': 'FAILED',
                        'error_code': 'ERR_FILE_NOT_FOUND',
                        'message': f"No files found matching pattern: {file_pattern}"
                    })
                    self.stats['errors'] += 1
                else:
                    for file_path in matching_files:
                        results.append({
                            'stage': 'file_existence',
                            'file': str(file_path.name),
                            'status': 'PASSED',
                            'message': f"File exists: {file_path.name}"
                        })
                        self.stats['passed_files'] += 1
                        self.stats['total_files'] += 1
            else:
                file_path = self.root_dir / file_pattern
                if file_path.exists():
                    results.append({
                        'stage': 'file_existence',
                        'file': file_pattern,
                        'status': 'PASSED',
                        'message': f"File exists: {file_pattern}"
                    })
                    self.stats['passed_files'] += 1
                    self.stats['total_files'] += 1
                else:
                    results.append({
                        'stage': 'file_existence',
                        'file': file_pattern,
                        'status': 'FAILED',
                        'error_code': 'ERR_FILE_NOT_FOUND',
                        'message': f"Required file not found: {file_pattern}"
                    })
                    self.stats['errors'] += 1
                    self.stats['failed_files'] += 1
                    self.stats['total_files'] += 1
        
        return results

    def validate_yaml_structure(self, file_path: Path) -> Dict[str, Any]:
        """Stage 2: Validate YAML structure and basic schema"""
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
            
            # Basic structure validation
            if not isinstance(content, dict):
                return {
                    'stage': 'schema_validation',
                    'file': file_path.name,
                    'status': 'FAILED',
                    'error_code': 'ERR_SCHEMA_VALIDATION_FAILED',
                    'message': 'Root content must be a dictionary'
                }
            
            # Check required universal metadata
            universal_metadata = self.schema.get('spec', {}).get('universal_metadata', {})
            required_fields = universal_metadata.get('required_fields', [])
            
            for field in required_fields:
                if field not in content:
                    return {
                        'stage': 'schema_validation',
                        'file': file_path.name,
                        'status': 'FAILED',
                        'error_code': 'ERR_SCHEMA_VALIDATION_FAILED',
                        'message': f'Missing required field: {field}'
                    }
            
            # Validate metadata structure if present
            if 'metadata' in content:
                metadata_schema = universal_metadata.get('metadata_schema', {})
                metadata = content['metadata']
                
                for required_meta_field in metadata_schema.get('required', []):
                    if required_meta_field not in metadata:
                        return {
                            'stage': 'schema_validation',
                            'file': file_path.name,
                            'status': 'FAILED',
                            'error_code': 'ERR_SCHEMA_VALIDATION_FAILED',
                            'message': f'Missing required metadata field: {required_meta_field}'
                        }
            
            return {
                'stage': 'schema_validation',
                'file': file_path.name,
                'status': 'PASSED',
                'message': 'YAML structure validation passed'
            }
            
        except yaml.YAMLError as e:
            return {
                'stage': 'schema_validation',
                'file': file_path.name,
                'status': 'FAILED',
                'error_code': 'ERR_SCHEMA_VALIDATION_FAILED',
                'message': f'YAML parsing error: {str(e)}'
            }
        except Exception as e:
            return {
                'stage': 'schema_validation',
                'file': file_path.name,
                'status': 'FAILED',
                'error_code': 'ERR_FILE_READ_ERROR',
                'message': f'File read error: {str(e)}'
            }

    def validate_consistency(self) -> List[Dict[str, Any]]:
        """Stage 3: Cross-file consistency validation"""
        self.logger.info("Stage 3: Cross-file consistency validation")
        
        results = []
        
        # Load modules.yaml for consistency checks
        modules_file = self.root_dir / "root.modules.yaml"
        if not modules_file.exists():
            results.append({
                'stage': 'consistency_validation',
                'file': 'root.modules.yaml',
                'status': 'SKIPPED',
                'message': 'Modules file not found, skipping consistency checks'
            })
            return results
        
        try:
            with open(modules_file, 'r') as f:
                modules_content = yaml.safe_load(f)
        except Exception as e:
            results.append({
                'stage': 'consistency_validation',
                'file': 'root.modules.yaml',
                'status': 'FAILED',
                'error_code': 'ERR_FILE_READ_ERROR',
                'message': f'Cannot read modules file: {str(e)}'
            })
            return results
        
        # Check dependency graph for cycles
        if 'spec' in modules_content and 'dependency_graph' in modules_content['spec']:
            dependency_graph = modules_content['spec']['dependency_graph']
            cycle_result = self.check_circular_dependencies(dependency_graph)
            results.append(cycle_result)
        
        # Check load sequence validity
        if 'spec' in modules_content and 'load_sequence' in modules_content['spec']:
            load_sequence = modules_content['spec']['load_sequence']
            seq_result = self.validate_load_sequence(load_sequence, dependency_graph)
            results.append(seq_result)
        
        return results

    def check_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> Dict[str, Any]:
        """Check for circular dependencies using DFS"""
        def dfs(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        rec_stack = set()
        
        for node in dependency_graph:
            if node not in visited:
                if dfs(node, visited, rec_stack):
                    return {
                        'stage': 'consistency_validation',
                        'file': 'root.modules.yaml',
                        'status': 'FAILED',
                        'error_code': 'ERR_CIRCULAR_DEPENDENCY',
                        'message': f'Circular dependency detected involving module: {node}'
                    }
        
        return {
            'stage': 'consistency_validation',
            'file': 'root.modules.yaml',
            'status': 'PASSED',
            'message': 'No circular dependencies found'
        }

    def validate_load_sequence(self, load_sequence: List[Dict], dependency_graph: Dict[str, List[str]]) -> Dict[str, Any]:
        """Validate that load sequence respects dependency order"""
        module_stage = {}
        
        # Build stage mapping
        for stage_info in load_sequence:
            stage_num = stage_info.get('stage', 0)
            for module in stage_info.get('modules', []):
                module_stage[module] = stage_num
        
        # Check dependencies
        for module, deps in dependency_graph.items():
            if module not in module_stage:
                continue
                
            module_stage_num = module_stage[module]
            for dep in deps:
                if dep not in module_stage:
                    continue
                    
                if module_stage_num <= module_stage[dep]:
                    return {
                        'stage': 'consistency_validation',
                        'file': 'root.modules.yaml',
                        'status': 'FAILED',
                        'error_code': 'ERR_INVALID_LOAD_SEQUENCE',
                        'message': f'Module {module} (stage {module_stage_num}) depends on {dep} (stage {module_stage[dep]}) but loads before or in same stage'
                    }
        
        return {
            'stage': 'consistency_validation',
            'file': 'root.modules.yaml',
            'status': 'PASSED',
            'message': 'Load sequence respects dependency order'
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate BLAKE3 hash of file"""
        hasher = blake3.blake3()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def create_hash_lock(self) -> Dict[str, Any]:
        """Create hash lock for critical root files"""
        hash_config = self.schema.get('spec', {}).get('hash_lock', {})
        algorithm = hash_config.get('algorithm', 'blake3')
        files_to_lock = hash_config.get('files_to_lock', [])
        
        hash_lock = {
            'algorithm': algorithm,
            'created_at': datetime.utcnow().isoformat(),
            'files': {}
        }
        
        for file_pattern in files_to_lock:
            file_path = self.root_dir / file_pattern
            if file_path.exists():
                file_hash = self.calculate_file_hash(file_path)
                hash_lock['files'][file_pattern] = {
                    'hash': file_hash,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
        
        return hash_lock

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        # Calculate summary
        self.results['summary'] = {
            'total_files_checked': self.stats['total_files'],
            'files_passed': self.stats['passed_files'],
            'files_failed': self.stats['failed_files'],
            'total_errors': self.stats['errors'],
            'total_warnings': self.stats['warnings'],
            'success_rate': (self.stats['passed_files'] / max(self.stats['total_files'], 1)) * 100,
            'overall_status': 'PASSED' if self.stats['errors'] == 0 else 'FAILED'
        }
        
        # Add hash lock if no critical errors
        if self.stats['errors'] == 0:
            self.results['hash_lock'] = self.create_hash_lock()
        
        return self.results

    def save_report(self):
        """Save validation report to file"""
        # Ensure directory exists
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        with open(self.report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Validation report saved to: {self.report_file}")

    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation pipeline"""
        self.logger.info("Starting Root Layer Validation Pipeline")
        
        # Stage 1: File existence
        existence_results = self.validate_file_existence()
        self.results['file_results'].extend(existence_results)
        
        # Stage 2: Schema validation for existing files
        for file_result in existence_results:
            if file_result['status'] == 'PASSED':
                file_path = self.root_dir / file_result['file']
                if file_path.suffix in ['.yaml', '.yml']:
                    schema_result = self.validate_yaml_structure(file_path)
                    self.results['file_results'].append(schema_result)
                    
                    if schema_result['status'] == 'FAILED':
                        self.stats['errors'] += 1
                    elif schema_result['status'] == 'PASSED':
                        self.stats['passed_files'] += 1
        
        # Stage 3: Consistency validation
        consistency_results = self.validate_consistency()
        self.results['consistency_results'].extend(consistency_results)
        
        for result in consistency_results:
            if result['status'] == 'FAILED':
                self.stats['errors'] += 1
        
        # Generate and save report
        final_report = self.generate_report()
        self.save_report()
        
        return final_report

def main():
    parser = argparse.ArgumentParser(description='MachineNativeOps Root Layer Validator')
    parser.add_argument('--root-dir', default='.', help='Root directory to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = RootValidator(args.root_dir)
    results = validator.run_validation()
    
    # Print summary
    print(f"\n=== Root Layer Validation Summary ===")
    print(f"Status: {results['summary']['overall_status']}")
    print(f"Files Checked: {results['summary']['total_files_checked']}")
    print(f"Files Passed: {results['summary']['files_passed']}")
    print(f"Files Failed: {results['summary']['files_failed']}")
    print(f"Total Errors: {results['summary']['total_errors']}")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    
    if results['summary']['overall_status'] == 'FAILED':
        print(f"\n=== Validation Errors ===")
        for result in results['file_results']:
            if result['status'] == 'FAILED':
                print(f"❌ {result['file']}: {result['message']}")
        for result in results['consistency_results']:
            if result['status'] == 'FAILED':
                print(f"❌ {result['file']}: {result['message']}")
        sys.exit(1)
    else:
        print(f"\n✅ All validations passed!")
        if 'hash_lock' in results:
            print(f"🔐 Hash lock generated for {len(results['hash_lock']['files'])} files")
        sys.exit(0)

if __name__ == "__main__":
    main()