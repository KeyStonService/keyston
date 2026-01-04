#!/usr/bin/env python3
"""
fs-map-generator.py - Automatic Filesystem Mapping Generator
MachineNativeOps Hierarchical fs.map Architecture

This script automatically:
1. Scans the repository directory structure
2. Generates fs.map files for each module boundary
3. Updates root.fs.index with discovered mappings
4. Validates and reports drift

Usage:
    ./bin/fs-map-generator.py                    # Validate only
    ./bin/fs-map-generator.py --regenerate       # Regenerate all fs.map files
    ./bin/fs-map-generator.py --check-drift      # Check for drift
    ./bin/fs-map-generator.py --fix-drift        # Auto-fix drift
    ./bin/fs-map-generator.py --report           # Generate coverage report

Author: MachineNativeOps Team
Version: 1.0.0
"""

import os
import sys
import json
import yaml
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


def normalize_physical_path(physical_path: str) -> str:
    """Normalize physical paths for consistent coverage calculations.

    Example:
        normalize_physical_path("./") -> "."
    """
    normalized = physical_path.strip()

    if normalized in {'', '.'}:
        return '.'

    if normalized.startswith('./'):
        normalized = normalized[2:]
    elif normalized.startswith('/'):
        normalized = normalized[1:]

    return normalized or '.'

# =============================================================================
# Configuration
# =============================================================================

@dataclass
class GeneratorConfig:
    """Configuration for fs.map generation"""
    repo_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Directories to exclude from scanning
    exclude_patterns: Set[str] = field(default_factory=lambda: {
        '.git', 'node_modules', '__pycache__', '.venv', '*.egg-info',
        'workspace-archive', 'workspace-problematic', '.githooks',
        'coverage', 'dist', 'build', '.cache', '.pytest_cache'
    })

    # Maximum depth for directory scanning
    max_depth: int = 4

    # Module boundary markers (files that indicate a module boundary)
    module_markers: Set[str] = field(default_factory=lambda: {
        'package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod',
        'README.md', 'fs.map', '__init__.py', 'setup.py'
    })

    # Directories that should always have fs.map (even without markers)
    force_module_dirs: Set[str] = field(default_factory=lambda: {
        'controlplane', 'workspace', 'chatops', 'web',
        'workspace/src', 'workspace/config', 'workspace/docs',
        'chatops/services', 'chatops/deploy', 'chatops/scripts'
    })

    # Permission patterns
    permission_patterns: Dict[str, dict] = field(default_factory=lambda: {
        'secrets': {'permissions': '-rwx------', 'fs_type': 'ext4', 'mount': 'relatime,rw'},
        'config': {'permissions': '-rwxr-xr-x', 'fs_type': 'ext4', 'mount': 'relatime,rw'},
        'logs': {'permissions': '-rwxr-xr-x', 'fs_type': 'ext4', 'mount': 'relatime,rw'},
        'tmp': {'permissions': '-rwxrwxrwx', 'fs_type': 'tmpfs', 'mount': 'size=1G,rw,nosuid,nodev'},
        'cache': {'permissions': '-rwxr-xr-x', 'fs_type': 'ext4', 'mount': 'relatime,rw'},
        'default': {'permissions': '-rwxr-xr-x', 'fs_type': 'ext4', 'mount': 'relatime,rw'}
    })


@dataclass
class DirectoryInfo:
    """Information about a directory"""
    path: Path
    relative_path: str
    logical_name: str
    depth: int
    is_module_boundary: bool
    has_marker: Optional[str]
    subdirs: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)


@dataclass
class FsMapEntry:
    """A single fs.map entry"""
    logical_name: str
    physical_path: str
    fs_type: str
    mount_options: str
    permissions: str
    description: str

    def to_line(self) -> str:
        return f"{self.logical_name}:{self.physical_path}:{self.fs_type}:{self.mount_options}:{self.permissions}:{self.description}"


def get_mapped_directories(generated_maps: Dict[str, List[FsMapEntry]]) -> Set[str]:
    """Return normalized, deduplicated directory paths from generated maps.

    Example:
        ["./a", "./a", "./b"] -> {"a", "b"}
    """
    return {
        normalize_physical_path(entry.physical_path)
        for entries in generated_maps.values()
        for entry in entries
    }


def compute_coverage_percentage(total_dirs: int, mapped_count: int) -> float:
    """Compute coverage percentage using a shared calculation."""
    if total_dirs == 0:
        return 100.0

    return round((mapped_count / total_dirs) * 100, 2)


# =============================================================================
# Directory Scanner
# =============================================================================

class DirectoryScanner:
    """Scans repository and identifies module boundaries"""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.directories: Dict[str, DirectoryInfo] = {}

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        name = path.name
        for pattern in self.config.exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False

    def get_relative_path(self, path: Path) -> str:
        """Get path relative to repo root"""
        try:
            return str(path.relative_to(self.config.repo_root))
        except ValueError:
            return str(path)

    def path_to_logical_name(self, relative_path: str) -> str:
        """Convert path to logical name"""
        # Replace path separators with underscores
        name = relative_path.replace('/', '_').replace('\\', '_')
        # Replace dots with underscores
        name = name.replace('.', '_')
        # Remove leading underscore if present
        name = name.lstrip('_')
        # Handle special cases
        if not name:
            name = 'root'
        return name.lower()

    def is_module_boundary(self, path: Path, relative_path: str) -> Tuple[bool, Optional[str]]:
        """Check if directory is a module boundary"""
        # Check if in force list
        if relative_path in self.config.force_module_dirs:
            return True, 'force_module'

        # Check for marker files
        for marker in self.config.module_markers:
            marker_path = path / marker
            if marker_path.exists():
                return True, marker

        return False, None

    def scan(self) -> Dict[str, DirectoryInfo]:
        """Scan repository and return directory info"""
        self.directories = {}
        self._scan_recursive(self.config.repo_root, 0)
        return self.directories

    def _scan_recursive(self, path: Path, depth: int):
        """Recursively scan directories"""
        if depth > self.config.max_depth:
            return

        if self.should_exclude(path):
            return

        relative_path = self.get_relative_path(path)
        if relative_path == '.':
            relative_path = ''

        logical_name = self.path_to_logical_name(relative_path) if relative_path else 'root'
        is_boundary, marker = self.is_module_boundary(path, relative_path)

        subdirs = []
        files = []

        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not self.should_exclude(item):
                    subdirs.append(item.name)
                    self._scan_recursive(item, depth + 1)
                elif item.is_file():
                    files.append(item.name)
        except PermissionError:
            pass

        dir_info = DirectoryInfo(
            path=path,
            relative_path=relative_path or '.',
            logical_name=logical_name,
            depth=depth,
            is_module_boundary=is_boundary,
            has_marker=marker,
            subdirs=subdirs,
            files=files
        )

        self.directories[relative_path or '.'] = dir_info


# =============================================================================
# fs.map Generator
# =============================================================================

class FsMapGenerator:
    """Generates fs.map files from scanned directories"""

    def __init__(self, config: GeneratorConfig, scanner: DirectoryScanner):
        self.config = config
        self.scanner = scanner
        self.generated_maps: Dict[str, List[FsMapEntry]] = {}

    def get_permissions(self, dir_name: str) -> dict:
        """Get permissions based on directory name patterns"""
        dir_lower = dir_name.lower()
        for pattern, perms in self.config.permission_patterns.items():
            if pattern in dir_lower:
                return perms
        return self.config.permission_patterns['default']

    def generate_entry(self, dir_info: DirectoryInfo) -> FsMapEntry:
        """Generate a single fs.map entry"""
        perms = self.get_permissions(dir_info.path.name)

        # Generate description
        description = f"{dir_info.path.name} directory"
        if dir_info.has_marker:
            description += f" (module: {dir_info.has_marker})"

        return FsMapEntry(
            logical_name=dir_info.logical_name,
            physical_path=f"./{dir_info.relative_path}" if dir_info.relative_path != '.' else '.',
            fs_type=perms['fs_type'],
            mount_options=perms['mount'],
            permissions=perms['permissions'],
            description=description
        )

    def generate_module_fsmap(self, module_path: str) -> List[FsMapEntry]:
        """Generate fs.map entries for a module and its children"""
        entries = []

        for rel_path, dir_info in self.scanner.directories.items():
            # Include if it's the module itself or a direct child
            if rel_path == module_path:
                entries.append(self.generate_entry(dir_info))
            elif rel_path.startswith(module_path + '/'):
                # Calculate relative depth within module
                module_depth = module_path.count('/') + 1 if module_path else 0
                dir_depth = rel_path.count('/')
                if dir_depth <= module_depth + 2:  # Include up to 2 levels deep
                    entries.append(self.generate_entry(dir_info))

        return entries

    def generate_all(self) -> Dict[str, List[FsMapEntry]]:
        """Generate all fs.map files"""
        self.generated_maps = {}

        # Find all module boundaries
        module_boundaries = [
            (rel_path, dir_info)
            for rel_path, dir_info in self.scanner.directories.items()
            if dir_info.is_module_boundary
        ]

        # Generate fs.map for each module boundary
        for rel_path, dir_info in module_boundaries:
            entries = self.generate_module_fsmap(rel_path)
            if entries:
                fsmap_path = f"{rel_path}/fs.map" if rel_path != '.' else 'root.fs.map'
                self.generated_maps[fsmap_path] = entries

        return self.generated_maps

    def write_fsmap(self, fsmap_path: str, entries: List[FsMapEntry], module_name: str):
        """Write fs.map file to disk"""
        full_path = self.config.repo_root / fsmap_path

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()

        content = f"""# =============================================================================
# {module_name} Filesystem Mapping
# Auto-generated by fs-map-generator.py
# =============================================================================
# Generated: {timestamp}
# Module: {module_name}
# Entries: {len(entries)}
#
# DO NOT MANUALLY EDIT - Run `./bin/fs-map-generator.py --regenerate` to update
# =============================================================================

# Format: logical_name:physical_path:filesystem_type:mount_options:permissions:description

"""

        for entry in sorted(entries, key=lambda e: e.physical_path):
            content += entry.to_line() + '\n'

        content += f"""
# =============================================================================
# End of {module_name} fs.map ({len(entries)} entries)
# =============================================================================
"""

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return full_path


# =============================================================================
# Index Updater
# =============================================================================

class IndexUpdater:
    """Updates root.fs.index with discovered fs.map files"""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.index_path = config.repo_root / 'root.fs.index'

    def update_index(self, generated_maps: Dict[str, List[FsMapEntry]]):
        """Update the root.fs.index file"""
        timestamp = datetime.now().isoformat()

        # Calculate statistics
        total_mappings = sum(len(entries) for entries in generated_maps.values())
        total_directories = len(generated_maps)

        # Read existing index to preserve manual configurations
        existing_index = self._read_existing_index()

        # Generate includes section
        includes = []
        for fsmap_path in sorted(generated_maps.keys()):
            scope = fsmap_path.replace('/fs.map', '').replace('fs.map', 'root').replace('/', '.')
            priority = 1000 - (fsmap_path.count('/') * 100)

            includes.append({
                'path': fsmap_path,
                'scope': scope,
                'priority': priority,
                'type': 'auto-generated',
                'entries': len(generated_maps[fsmap_path])
            })

        # Update status section
        if existing_index:
            existing_index['status'] = {
                'last_sync': timestamp,
                'total_fs_maps': len(generated_maps),
                'total_mappings': total_mappings,
                'total_directories': total_directories,
                'coverage_percentage': self._calculate_coverage(generated_maps),
                'drift_status': 'synced',
                'validation_status': 'passed'
            }
            existing_index['spec']['includes'] = includes

            with open(self.index_path, 'w', encoding='utf-8') as f:
                yaml.dump(existing_index, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _read_existing_index(self) -> Optional[dict]:
        """Read existing index file"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        return None

    def _calculate_coverage(self, generated_maps: Dict[str, List[FsMapEntry]]) -> float:
        """Calculate coverage percentage"""
        total_dirs = len([
            d for d in self.config.repo_root.rglob('*')
            if d.is_dir() and not any(p in str(d) for p in self.config.exclude_patterns)
        ])

        mapped_dirs = get_mapped_directories(generated_maps)

        return compute_coverage_percentage(total_dirs, len(mapped_dirs))


# =============================================================================
# Hierarchical Index Generator
# =============================================================================

class HierarchicalIndexGenerator:
    """Generates hierarchical fs.index files for each module boundary"""

    # Modules that should have their own fs.index
    INDEX_MODULES = {
        'controlplane',
        'workspace',
        'chatops',
        'web',
        'workspace/src',
        'workspace/config',
        'chatops/services',
        'chatops/deploy',
    }

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.generated_indexes: Dict[str, dict] = {}

    def generate_all(self, generated_maps: Dict[str, List[FsMapEntry]]) -> Dict[str, dict]:
        """Generate hierarchical fs.index files"""
        self.generated_indexes = {}
        timestamp = datetime.now().isoformat()

        # Group fs.map files by their parent module
        module_maps: Dict[str, List[str]] = {}

        for fsmap_path in generated_maps.keys():
            # Find which module this fs.map belongs to
            for module in sorted(self.INDEX_MODULES, key=len, reverse=True):
                if fsmap_path.startswith(module + '/') or fsmap_path == f"{module}/fs.map":
                    if module not in module_maps:
                        module_maps[module] = []
                    module_maps[module].append(fsmap_path)
                    break

        # Generate fs.index for each module
        for module, maps in module_maps.items():
            index_data = self._create_index_data(module, maps, generated_maps, timestamp)
            self.generated_indexes[f"{module}/fs.index"] = index_data

        # Generate root.fs.index that aggregates all sub-indexes
        root_index = self._create_root_index(generated_maps, timestamp)
        self.generated_indexes['root.fs.index'] = root_index

        return self.generated_indexes

    def _create_index_data(self, module: str, maps: List[str],
                          generated_maps: Dict[str, List[FsMapEntry]],
                          timestamp: str) -> dict:
        """Create index data for a single module"""
        includes = []
        total_entries = 0

        for fsmap_path in sorted(maps):
            entries_count = len(generated_maps.get(fsmap_path, []))
            total_entries += entries_count

            # Calculate relative path from module
            if fsmap_path.startswith(module + '/'):
                rel_path = fsmap_path[len(module) + 1:]
            else:
                rel_path = fsmap_path

            includes.append({
                'path': rel_path,
                'scope': rel_path.replace('/fs.map', '').replace('fs.map', module.split('/')[-1]),
                'entries': entries_count,
                'type': 'auto-generated'
            })

        # Check for child indexes
        child_indexes = []
        for idx_module in self.INDEX_MODULES:
            if idx_module.startswith(module + '/') and idx_module != module:
                child_indexes.append(f"{idx_module.replace(module + '/', '')}/fs.index")

        return {
            'apiVersion': 'machinenativeops.io/v1',
            'kind': 'FilesystemIndex',
            'metadata': {
                'name': f"{module.replace('/', '-')}-filesystem-index",
                'scope': module,
                'generated': timestamp,
                'auto_generated': True
            },
            'spec': {
                'includes': includes,
                'child_indexes': child_indexes if child_indexes else None,
                'statistics': {
                    'fs_maps': len(maps),
                    'total_entries': total_entries
                }
            }
        }

    def _create_root_index(self, generated_maps: Dict[str, List[FsMapEntry]],
                          timestamp: str) -> dict:
        """Create root.fs.index that aggregates all sub-indexes"""
        # Get all sub-indexes (only top-level modules)
        sub_indexes = []
        for module in sorted(self.INDEX_MODULES):
            if '/' not in module:  # Only top-level
                sub_indexes.append({
                    'path': f"{module}/fs.index",
                    'scope': module,
                    'type': 'auto-generated'
                })

        # Get all fs.map files
        all_maps = []
        for fsmap_path in sorted(generated_maps.keys()):
            all_maps.append({
                'path': fsmap_path,
                'scope': fsmap_path.replace('/fs.map', '').replace('fs.map', 'root').replace('/', '.'),
                'entries': len(generated_maps[fsmap_path]),
                'type': 'auto-generated'
            })

        total_mappings = sum(len(entries) for entries in generated_maps.values())

        return {
            'apiVersion': 'machinenativeops.io/v1',
            'kind': 'FilesystemIndex',
            'metadata': {
                'name': 'root-filesystem-index',
                'namespace': 'machinenativenops',
                'generated': timestamp,
                'auto_generated': True,
                'labels': {
                    'machinenativeops.io/component': 'filesystem',
                    'machinenativeops.io/layer': 'root',
                    'machinenativeops.io/managed-by': 'fs-map-generator'
                }
            },
            'spec': {
                'hierarchy': {
                    'strategy': 'hierarchical',
                    'child_indexes': sub_indexes
                },
                'includes': all_maps,
                'aggregation': {
                    'strategy': 'hierarchical',
                    'conflict_resolution': {
                        'strategy': 'priority',
                        'log_conflicts': True
                    },
                    'namespace_prefix': {
                        'enabled': True,
                        'separator': '_'
                    }
                },
                'validation': {
                    'require_all_includes': True,
                    'check_conflicts': True,
                    'validate_permissions': True,
                    'verify_paths': True
                }
            },
            'status': {
                'last_sync': timestamp,
                'total_fs_maps': len(generated_maps),
                'total_mappings': total_mappings,
                'total_indexes': len(self.INDEX_MODULES) + 1,
                'drift_status': 'synced',
                'validation_status': 'passed'
            }
        }

    def write_all(self) -> List[Path]:
        """Write all generated fs.index files to disk"""
        written_files = []

        for index_path, index_data in self.generated_indexes.items():
            full_path = self.config.repo_root / index_path

            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write YAML with header comment
            content = f"""# =============================================================================
# {index_data['metadata'].get('name', 'Filesystem Index')}
# Auto-generated by fs-map-generator.py
# =============================================================================
# Generated: {index_data['metadata'].get('generated', 'unknown')}
# Scope: {index_data['metadata'].get('scope', 'root')}
#
# DO NOT MANUALLY EDIT - Run `./bin/fs-map-generator.py --regenerate` to update
# =============================================================================

"""
            content += yaml.dump(index_data, default_flow_style=False,
                                allow_unicode=True, sort_keys=False)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            written_files.append(full_path)

        return written_files


# =============================================================================
# Drift Checker
# =============================================================================

class DriftChecker:
    """Checks for drift between fs.map files and actual directory structure"""

    def __init__(self, config: GeneratorConfig, scanner: DirectoryScanner):
        self.config = config
        self.scanner = scanner
        self.drift_report: Dict[str, List[str]] = {
            'new_directories': [],
            'removed_directories': [],
            'modified': []
        }

    def check_drift(self) -> Dict[str, List[str]]:
        """Check for drift and return report"""
        actual_dirs = set(self.scanner.directories.keys())
        mapped_dirs = self._get_mapped_directories()

        # Find new directories (in actual but not in maps)
        self.drift_report['new_directories'] = sorted(actual_dirs - mapped_dirs)

        # Find removed directories (in maps but not in actual)
        self.drift_report['removed_directories'] = sorted(mapped_dirs - actual_dirs)

        return self.drift_report

    def _get_mapped_directories(self) -> Set[str]:
        """Get all directories currently in fs.map files"""
        mapped = set()

        for fsmap_file in self.config.repo_root.rglob('fs.map'):
            try:
                with open(fsmap_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                path = normalize_physical_path(parts[1])
                                if path:
                                    mapped.add(path)
            except Exception:
                pass

        return mapped

    def has_drift(self) -> bool:
        """Check if there is any drift"""
        return bool(self.drift_report['new_directories'] or
                   self.drift_report['removed_directories'] or
                   self.drift_report['modified'])


# =============================================================================
# Report Generator
# =============================================================================

class ReportGenerator:
    """Generates coverage and drift reports"""

    def __init__(self, config: GeneratorConfig):
        self.config = config

    def generate_report(self, scanner: DirectoryScanner,
                       generator: FsMapGenerator,
                       drift_checker: DriftChecker) -> str:
        """Generate comprehensive report"""
        timestamp = datetime.now().isoformat()

        total_dirs = len(scanner.directories)
        module_boundaries = len([d for d in scanner.directories.values() if d.is_module_boundary])
        total_mappings = sum(len(entries) for entries in generator.generated_maps.values())
        mapped_dirs = get_mapped_directories(generator.generated_maps)
        coverage_percentage = compute_coverage_percentage(total_dirs, len(mapped_dirs))

        report = f"""# Filesystem Mapping Report
# Generated: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Total Directories Scanned | {total_dirs} |
| Module Boundaries Detected | {module_boundaries} |
| fs.map Files Generated | {len(generator.generated_maps)} |
| Total Mappings | {total_mappings} |
| Coverage | {coverage_percentage}% |

## Module Boundaries

| Path | Marker | Subdirs | Files |
|------|--------|---------|-------|
"""

        for rel_path, dir_info in sorted(scanner.directories.items()):
            if dir_info.is_module_boundary:
                report += f"| {rel_path or '.'} | {dir_info.has_marker or 'force'} | {len(dir_info.subdirs)} | {len(dir_info.files)} |\n"

        report += f"""
## Generated fs.map Files

| File | Entries |
|------|---------|
"""

        for fsmap_path, entries in sorted(generator.generated_maps.items()):
            report += f"| {fsmap_path} | {len(entries)} |\n"

        if drift_checker.drift_report['new_directories']:
            report += f"""
## Drift: New Directories

"""
            for d in drift_checker.drift_report['new_directories'][:20]:
                report += f"- {d}\n"
            if len(drift_checker.drift_report['new_directories']) > 20:
                report += f"- ... and {len(drift_checker.drift_report['new_directories']) - 20} more\n"

        return report


# =============================================================================
# Main CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Automatic Filesystem Mapping Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    ./bin/fs-map-generator.py                    # Validate only
    ./bin/fs-map-generator.py --regenerate       # Regenerate all fs.map files
    ./bin/fs-map-generator.py --check-drift      # Check for drift
    ./bin/fs-map-generator.py --fix-drift        # Auto-fix drift
    ./bin/fs-map-generator.py --report           # Generate coverage report
        """
    )

    parser.add_argument('--regenerate', action='store_true',
                       help='Regenerate all fs.map files')
    parser.add_argument('--check-drift', action='store_true',
                       help='Check for drift between fs.map and actual structure')
    parser.add_argument('--fix-drift', action='store_true',
                       help='Automatically fix drift')
    parser.add_argument('--report', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    args = parser.parse_args()

    # Initialize
    config = GeneratorConfig()
    scanner = DirectoryScanner(config)

    print("🔍 Scanning repository structure...")
    directories = scanner.scan()
    print(f"   Found {len(directories)} directories")

    module_boundaries = [d for d in directories.values() if d.is_module_boundary]
    print(f"   Detected {len(module_boundaries)} module boundaries")

    # Generate mappings
    generator = FsMapGenerator(config, scanner)
    generated_maps = generator.generate_all()
    print(f"   Generated {len(generated_maps)} fs.map configurations")

    # Check drift
    drift_checker = DriftChecker(config, scanner)
    drift_report = drift_checker.check_drift()

    if args.check_drift:
        print("\n📊 Drift Report:")
        if drift_report['new_directories']:
            print(f"   New directories: {len(drift_report['new_directories'])}")
            if args.verbose:
                for d in drift_report['new_directories'][:10]:
                    print(f"      + {d}")
        if drift_report['removed_directories']:
            print(f"   Removed directories: {len(drift_report['removed_directories'])}")
            if args.verbose:
                for d in drift_report['removed_directories'][:10]:
                    print(f"      - {d}")
        if not drift_checker.has_drift():
            print("   ✅ No drift detected")

    if args.regenerate or args.fix_drift:
        if args.dry_run:
            print("\n🔧 Would generate the following fs.map files:")
            for fsmap_path in sorted(generated_maps.keys()):
                print(f"   📄 {fsmap_path} ({len(generated_maps[fsmap_path])} entries)")
        else:
            print("\n🔧 Writing fs.map files...")
            for fsmap_path, entries in generated_maps.items():
                module_name = fsmap_path.replace('/fs.map', '').replace('fs.map', 'root')
                written_path = generator.write_fsmap(fsmap_path, entries, module_name)
                print(f"   ✅ {fsmap_path} ({len(entries)} entries)")

            # Generate hierarchical indexes
            print("\n📑 Generating hierarchical fs.index files...")
            index_generator = HierarchicalIndexGenerator(config)
            index_generator.generate_all(generated_maps)
            written_indexes = index_generator.write_all()
            for idx_path in written_indexes:
                rel_path = str(idx_path.relative_to(config.repo_root))
                print(f"   ✅ {rel_path}")
            print(f"   Total: {len(written_indexes)} fs.index files")

    if args.report:
        report_gen = ReportGenerator(config)
        report = report_gen.generate_report(scanner, generator, drift_checker)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 Report written to: {args.output}")
        else:
            print("\n" + report)

    # Summary
    total_mappings = sum(len(entries) for entries in generated_maps.values())
    print(f"\n✨ Summary: {len(generated_maps)} fs.map files, {total_mappings} total mappings")

    if drift_checker.has_drift() and not args.fix_drift and not args.regenerate:
        print("⚠️  Drift detected. Run with --fix-drift to auto-fix.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
