#!/usr/bin/env python3
"""
Auto Upgrade Environment Configuration - Enterprise Edition
自動升級系統環境配置 - 企業版

Purpose: Automatically detect and install missing dependencies
When a dependency is missing, upgrade the environment instead of degrading functionality
當缺少依賴時，自動升級系統環境配置，而非降級功能

Enhanced Features:
- Parallel installation of multiple dependencies
- Dependency version conflict detection
- Caching of installed dependencies
- Support for config file-based dependencies
- Intelligent recommendation of related dependencies
"""

import sys
import subprocess
import importlib
import logging
import json
import asyncio
import concurrent.futures
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from packaging import version
from packaging.requirements import Requirement
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoUpgradeEnvironment:
    """
    自動升級環境管理器
    Automatically upgrades environment when dependencies are missing
    """
    
    # Define dependency mapping
    DEPENDENCY_MAP = {
        'dotenv': {
            'package': 'python-dotenv',
            'import_name': 'dotenv',
            'pip_install': 'python-dotenv>=1.0.0',
            'description': '環境變量管理 (Environment variable management)',
            'optional': True
        },
        'loguru': {
            'package': 'loguru',
            'import_name': 'loguru',
            'pip_install': 'loguru>=0.7.2',
            'description': '增強日誌功能 (Enhanced logging)',
            'optional': True
        },
        'pytest': {
            'package': 'pytest',
            'import_name': 'pytest',
            'pip_install': 'pytest>=8.0.0',
            'description': '測試框架 (Testing framework)',
            'optional': True,
            'dev_only': True
        },
        'pytest_asyncio': {
            'package': 'pytest-asyncio',
            'import_name': 'pytest_asyncio',
            'pip_install': 'pytest-asyncio>=0.23.5',
            'description': '異步測試支持 (Async testing support)',
            'optional': True,
            'dev_only': True
        },
    }
    
    def __init__(self, auto_install: bool = True, cache_dir: Optional[Path] = None):
        """
        Initialize auto upgrade environment
        
        Args:
            auto_install: Whether to automatically install missing dependencies
            cache_dir: Directory for caching installation status
        """
        self.auto_install = auto_install
        self.missing_deps = []
        self.installed_deps = []
        self.cache_dir = cache_dir or Path.home() / '.cache' / 'auto_upgrade_env'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'installed_packages.json'
        self.conflict_log = []
        
        # Load cache
        self._load_cache()
        
    def _load_cache(self):
        """Load installation cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save installation cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, package: str) -> str:
        """Generate cache key for a package"""
        return hashlib.md5(package.encode()).hexdigest()
    
    def check_dependency(self, import_name: str) -> bool:
        """
        Check if a dependency is available
        
        Args:
            import_name: Name to use in import statement
            
        Returns:
            True if dependency is available, False otherwise
        """
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
    
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """
        Get installed version of a package
        
        Args:
            package_name: Package name
            
        Returns:
            Version string or None if not installed
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass
        return None
    
    def detect_version_conflicts(self, packages: List[str]) -> List[Dict[str, str]]:
        """
        Detect version conflicts between packages
        
        Args:
            packages: List of package specifications
            
        Returns:
            List of conflicts detected
        """
        conflicts = []
        requirements = {}
        
        for pkg_spec in packages:
            try:
                req = Requirement(pkg_spec)
                pkg_name = req.name.lower()
                
                if pkg_name in requirements:
                    # Check for version conflicts
                    existing_req = requirements[pkg_name]
                    if str(req.specifier) != str(existing_req.specifier):
                        conflicts.append({
                            'package': pkg_name,
                            'existing': str(existing_req),
                            'new': str(req),
                            'severity': 'warning'
                        })
                else:
                    requirements[pkg_name] = req
            except Exception as e:
                logger.warning(f"Failed to parse requirement {pkg_spec}: {e}")
        
        return conflicts
    
    def recommend_dependencies(self, dep_name: str) -> List[str]:
        """
        Recommend related dependencies
        
        Args:
            dep_name: Dependency name
            
        Returns:
            List of recommended dependencies
        """
        recommendations = {
            'pytest': ['pytest-asyncio', 'pytest-cov'],
            'fastapi': ['uvicorn', 'pydantic'],
            'django': ['djangorestframework', 'celery'],
            'flask': ['flask-cors', 'flask-sqlalchemy'],
            'numpy': ['pandas', 'matplotlib'],
            'pandas': ['numpy', 'openpyxl'],
            'requests': ['urllib3', 'certifi'],
        }
        
        return recommendations.get(dep_name, [])
    
    def install_package(self, pip_package: str, use_cache: bool = True) -> Tuple[bool, str]:
        """
        Install a package using pip with caching support
        
        Args:
            pip_package: Package specification for pip (e.g., 'loguru>=0.7.2')
            use_cache: Whether to use cache for installation status
            
        Returns:
            Tuple of (success, message)
        """
        cache_key = self._get_cache_key(pip_package)
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached.get('success'):
                logger.info(f"✓ 使用緩存 Using cache: {pip_package}")
                return True, f"Installed from cache: {pip_package}"
        
        try:
            logger.info(f"正在安裝 Installing: {pip_package}")
            
            # Use subprocess to install
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', pip_package, '--quiet'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            if success:
                logger.info(f"✓ 安裝成功 Installed: {pip_package}")
                # Update cache
                self.cache[cache_key] = {
                    'package': pip_package,
                    'success': True,
                    'timestamp': subprocess.check_output(
                        ['date', '+%Y-%m-%d %H:%M:%S'], text=True
                    ).strip() if sys.platform != 'win32' else 'now'
                }
                self._save_cache()
                return True, f"Successfully installed {pip_package}"
            else:
                logger.error(f"✗ 安裝失敗 Failed: {pip_package}\n{result.stderr}")
                return False, f"Failed to install {pip_package}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ 安裝超時 Timeout: {pip_package}")
            return False, f"Installation timeout for {pip_package}"
        except Exception as e:
            logger.error(f"✗ 安裝錯誤 Error: {str(e)}")
            return False, f"Installation error: {str(e)}"
    
    def install_packages_parallel(self, packages: List[str], max_workers: int = 3) -> Dict[str, Tuple[bool, str]]:
        """
        Install multiple packages in parallel
        
        Args:
            packages: List of package specifications
            max_workers: Maximum number of parallel installations
            
        Returns:
            Dictionary mapping package names to (success, message) tuples
        """
        logger.info(f"並行安裝 Parallel installation: {len(packages)} packages with {max_workers} workers")
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pkg = {
                executor.submit(self.install_package, pkg): pkg 
                for pkg in packages
            }
            
            for future in concurrent.futures.as_completed(future_to_pkg):
                pkg = future_to_pkg[future]
                try:
                    success, message = future.result()
                    results[pkg] = (success, message)
                except Exception as e:
                    logger.error(f"並行安裝異常 Parallel install error for {pkg}: {e}")
                    results[pkg] = (False, str(e))
        
        return results
    
    def check_and_upgrade(self, dependencies: List[str]) -> Dict[str, bool]:
        """
        Check dependencies and auto-upgrade if missing
        
        Args:
            dependencies: List of dependency names to check
            
        Returns:
            Dictionary mapping dependency names to availability status
        """
        results = {}
        
        for dep_name in dependencies:
            if dep_name not in self.DEPENDENCY_MAP:
                logger.warning(f"未知依賴 Unknown dependency: {dep_name}")
                results[dep_name] = False
                continue
            
            dep_info = self.DEPENDENCY_MAP[dep_name]
            import_name = dep_info['import_name']
            
            # Check if already available
            if self.check_dependency(import_name):
                logger.info(f"✓ 依賴可用 Available: {dep_name}")
                results[dep_name] = True
                continue
            
            # If not available and auto_install is enabled
            if self.auto_install:
                logger.info(f"⚠ 缺少依賴 Missing dependency: {dep_name}")
                logger.info(f"   {dep_info['description']}")
                logger.info(f"   正在自動升級環境... Auto-upgrading environment...")
                
                success, message = self.install_package(dep_info['pip_install'])
                
                if success:
                    self.installed_deps.append(dep_name)
                    results[dep_name] = True
                    logger.info(f"✓ 環境升級成功 Environment upgraded for: {dep_name}")
                else:
                    self.missing_deps.append(dep_name)
                    results[dep_name] = False
                    
                    if not dep_info.get('optional', False):
                        logger.error(f"✗ 必需依賴安裝失敗 Required dependency failed: {dep_name}")
                    else:
                        logger.warning(f"⚠ 可選依賴安裝失敗 Optional dependency failed: {dep_name}")
            else:
                self.missing_deps.append(dep_name)
                results[dep_name] = False
                logger.warning(f"⚠ 缺少依賴（自動安裝已禁用）Missing: {dep_name}")
        
        return results
    
    def upgrade_all_optional(self) -> Dict[str, bool]:
        """
        Upgrade all optional dependencies
        
        Returns:
            Dictionary mapping dependency names to installation status
        """
        logger.info("=== 升級所有可選依賴 Upgrading all optional dependencies ===")
        
        optional_deps = [
            name for name, info in self.DEPENDENCY_MAP.items()
            if info.get('optional', False) and not info.get('dev_only', False)
        ]
        
        return self.check_and_upgrade(optional_deps)
    
    def load_dependencies_from_config(self, config_path: Path) -> List[str]:
        """
        Load dependencies from configuration file
        
        Supports:
        - requirements.txt
        - pyproject.toml
        - environment.yml
        - .auto-upgrade.json
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            List of package specifications
        """
        packages = []
        
        try:
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return packages
            
            file_name = config_path.name.lower()
            
            if file_name == 'requirements.txt':
                # Parse requirements.txt
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Remove inline comments
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        if line and not line.startswith('#'):
                            packages.append(line)
            
            elif file_name == 'pyproject.toml':
                # Parse pyproject.toml (basic support)
                import re
                with open(config_path, 'r') as f:
                    content = f.read()
                    # Extract dependencies from [project.dependencies]
                    deps_match = re.search(r'\[project\.dependencies\](.*?)\[', content, re.DOTALL)
                    if deps_match:
                        deps_section = deps_match.group(1)
                        for line in deps_section.split('\n'):
                            line = line.strip().strip('"').strip("'").strip(',')
                            if line and not line.startswith('#'):
                                packages.append(line)
            
            elif file_name.endswith('.json'):
                # Parse JSON config
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'dependencies' in config:
                        packages.extend(config['dependencies'])
            
            elif file_name == 'environment.yml':
                # Parse conda environment.yml (basic support)
                import re
                with open(config_path, 'r') as f:
                    content = f.read()
                    # Extract pip dependencies
                    pip_match = re.search(r'- pip:(.*?)(?:\n[^ ]|\Z)', content, re.DOTALL)
                    if pip_match:
                        pip_section = pip_match.group(1)
                        for line in pip_section.split('\n'):
                            line = line.strip().lstrip('- ').strip()
                            if line:
                                packages.append(line)
            
            logger.info(f"✓ 從配置文件加載 Loaded {len(packages)} dependencies from {config_path}")
            
        except Exception as e:
            logger.error(f"✗ 加載配置文件失敗 Failed to load config: {e}")
        
        return packages
    
    def upgrade_from_config(self, config_path: Path, parallel: bool = True) -> Dict[str, bool]:
        """
        Upgrade dependencies from configuration file
        
        Args:
            config_path: Path to configuration file
            parallel: Whether to use parallel installation
            
        Returns:
            Dictionary mapping package names to installation status
        """
        packages = self.load_dependencies_from_config(config_path)
        
        if not packages:
            logger.warning("No dependencies found in config file")
            return {}
        
        # Detect conflicts
        conflicts = self.detect_version_conflicts(packages)
        if conflicts:
            logger.warning(f"⚠ 檢測到 {len(conflicts)} 個版本衝突 Detected version conflicts:")
            for conflict in conflicts:
                logger.warning(f"  - {conflict['package']}: {conflict['existing']} vs {conflict['new']}")
                self.conflict_log.append(conflict)
        
        # Install packages
        if parallel and len(packages) > 1:
            logger.info(f"使用並行安裝 Using parallel installation for {len(packages)} packages")
            install_results = self.install_packages_parallel(packages)
            
            results = {}
            for pkg, (success, message) in install_results.items():
                pkg_name = pkg.split('>=')[0].split('==')[0].split('<')[0].strip()
                results[pkg_name] = success
                if success:
                    self.installed_deps.append(pkg_name)
                else:
                    self.missing_deps.append(pkg_name)
            
            return results
        else:
            # Sequential installation
            results = {}
            for pkg in packages:
                success, message = self.install_package(pkg)
                pkg_name = pkg.split('>=')[0].split('==')[0].split('<')[0].strip()
                results[pkg_name] = success
                if success:
                    self.installed_deps.append(pkg_name)
                else:
                    self.missing_deps.append(pkg_name)
            
            return results
    
    def get_summary(self) -> str:
        """
        Get upgrade summary with enhanced information
        
        Returns:
            Summary string
        """
        summary = "\n=== 環境升級摘要 Environment Upgrade Summary ===\n"
        
        if self.installed_deps:
            summary += f"\n✓ 已安裝依賴 Installed ({len(self.installed_deps)}):\n"
            for dep in self.installed_deps:
                if dep in self.DEPENDENCY_MAP:
                    summary += f"  - {dep}: {self.DEPENDENCY_MAP[dep]['description']}\n"
                    # Show recommendations
                    recommendations = self.recommend_dependencies(dep)
                    if recommendations:
                        summary += f"    💡 推薦相關依賴 Recommended: {', '.join(recommendations)}\n"
                else:
                    summary += f"  - {dep}\n"
        
        if self.missing_deps:
            summary += f"\n⚠ 未能安裝 Failed to install ({len(self.missing_deps)}):\n"
            for dep in self.missing_deps:
                if dep in self.DEPENDENCY_MAP:
                    summary += f"  - {dep}: {self.DEPENDENCY_MAP[dep]['description']}\n"
                    if self.DEPENDENCY_MAP[dep].get('optional', False):
                        summary += f"    (可選依賴，功能可能受限 Optional, features may be limited)\n"
                else:
                    summary += f"  - {dep}\n"
        
        if self.conflict_log:
            summary += f"\n⚠ 版本衝突 Version Conflicts ({len(self.conflict_log)}):\n"
            for conflict in self.conflict_log:
                summary += f"  - {conflict['package']}: {conflict['existing']} ⇄ {conflict['new']}\n"
        
        # Cache statistics
        if hasattr(self, 'cache') and self.cache:
            summary += f"\n📦 緩存信息 Cache Info:\n"
            summary += f"  - 已緩存包 Cached packages: {len(self.cache)}\n"
            summary += f"  - 緩存位置 Cache location: {self.cache_file}\n"
        
        if not self.installed_deps and not self.missing_deps:
            summary += "\n✓ 所有依賴已就緒 All dependencies ready\n"
        
        return summary


def auto_upgrade_on_import():
    """
    Automatically upgrade environment when module is imported
    當模組被導入時自動升級環境
    """
    upgrader = AutoUpgradeEnvironment(auto_install=True)
    
    # Check core optional dependencies
    core_deps = ['dotenv', 'loguru']
    
    logger.info("=== 自動環境升級檢查 Auto Environment Upgrade Check ===")
    upgrader.check_and_upgrade(core_deps)
    
    # Print summary
    print(upgrader.get_summary())
    
    return upgrader


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Auto Upgrade Environment Configuration'
    )
    parser.add_argument(
        '--upgrade-all',
        action='store_true',
        help='Upgrade all optional dependencies'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Check dependencies without installing'
    )
    parser.add_argument(
        '--deps',
        nargs='+',
        help='Specific dependencies to check/upgrade'
    )
    parser.add_argument(
        '--from-config',
        type=str,
        help='Load dependencies from config file (requirements.txt, pyproject.toml, etc.)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Use parallel installation (default: True for config files)'
    )
    parser.add_argument(
        '--detect-conflicts',
        action='store_true',
        help='Detect version conflicts without installing'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear installation cache'
    )
    parser.add_argument(
        '--recommend',
        type=str,
        help='Show recommended dependencies for a package'
    )
    
    args = parser.parse_args()
    
    # Create upgrader
    upgrader = AutoUpgradeEnvironment(auto_install=not args.check_only)
    
    print("=== 智能環境升級系統 - 企業版 Intelligent Environment Upgrade System - Enterprise ===\n")
    
    # Handle clear cache
    if args.clear_cache:
        if upgrader.cache_file.exists():
            upgrader.cache_file.unlink()
            print("✓ 緩存已清除 Cache cleared\n")
        else:
            print("⚠ 無緩存文件 No cache file found\n")
        sys.exit(0)
    
    # Handle recommendations
    if args.recommend:
        recommendations = upgrader.recommend_dependencies(args.recommend)
        if recommendations:
            print(f"💡 推薦 {args.recommend} 的相關依賴 Recommended dependencies for {args.recommend}:")
            for rec in recommendations:
                print(f"  - {rec}")
        else:
            print(f"⚠ 無推薦 No recommendations for {args.recommend}")
        print()
        sys.exit(0)
    
    # Handle from config
    if args.from_config:
        config_path = Path(args.from_config)
        
        # Detect conflicts if requested
        if args.detect_conflicts:
            packages = upgrader.load_dependencies_from_config(config_path)
            conflicts = upgrader.detect_version_conflicts(packages)
            if conflicts:
                print(f"⚠ 檢測到 {len(conflicts)} 個版本衝突 Detected {len(conflicts)} version conflicts:\n")
                for conflict in conflicts:
                    print(f"  - {conflict['package']}")
                    print(f"    Existing: {conflict['existing']}")
                    print(f"    New: {conflict['new']}")
                    print()
            else:
                print("✓ 無版本衝突 No version conflicts detected\n")
            sys.exit(0)
        
        # Upgrade from config
        upgrader.upgrade_from_config(config_path, parallel=args.parallel)
    elif args.upgrade_all:
        # Upgrade all optional dependencies
        upgrader.upgrade_all_optional()
    elif args.deps:
        # Upgrade specific dependencies
        upgrader.check_and_upgrade(args.deps)
    else:
        # Check core dependencies
        core_deps = ['dotenv', 'loguru']
        upgrader.check_and_upgrade(core_deps)
    
    # Print summary
    print(upgrader.get_summary())
    
    # Exit with appropriate code
    if upgrader.missing_deps and not all(
        AutoUpgradeEnvironment.DEPENDENCY_MAP[dep].get('optional', False)
        for dep in upgrader.missing_deps
    ):
        print("\n✗ 存在未安裝的必需依賴 Required dependencies missing")
        sys.exit(1)
    else:
        print("\n✓ 環境配置完成 Environment configuration complete")
        sys.exit(0)
