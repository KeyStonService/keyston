#!/usr/bin/env python3
"""
Optimized Repository Scanner and Index Generator
倉庫掃描與索引生成器 (優化版)

Performance improvements:
- Parallel file processing using ThreadPoolExecutor
- LRU caching for expensive operations
- Pre-compiled regex patterns
- Efficient data structures (sets vs lists)
- Reduced file I/O operations

Requirements:
    Python 3.8+
    
Usage:
    python tools/docs/scan_repo_generate_index_optimized.py
    python tools/docs/scan_repo_generate_index_optimized.py --output docs/generated-index.yaml
    python tools/docs/scan_repo_generate_index_optimized.py --benchmark
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Pre-compile regex patterns for performance
TITLE_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
TAG_CLEAN_PATTERN = re.compile(r'[^a-z0-9-]')

# Domain mapping based on directory structure
DOMAIN_MAPPING = {
    'automation': ['automation/'],
    'core': ['core/'],
    'frontend': ['frontend/', 'ui/'],
    'infrastructure': ['infrastructure/', 'deploy/', 'k8s/'],
    'tests': ['tests/', 'test-vectors/'],
    'governance': ['governance/'],
    'tools': ['tools/'],
    'ops': ['ops/'],
    'config': ['config/'],
    'docs': ['docs/'],
    'mcp-servers': ['mcp-servers/'],
    'agent': ['agent/'],
    'shared': ['shared/'],
    'bridges': ['bridges/'],
    'contracts': ['contracts/', 'core/contract_service/'],
    'runtime': ['runtime/'],
    'github': ['.github/'],
    'architecture': ['docs/architecture/'],
    'security': ['security/'],
    'guides': ['docs/guides/', 'docs/QUICK_START', 'docs/INTEGRATION']
}

# Layer mapping based on domain
LAYER_MAPPING = {
    'automation': 'ai-automation',
    'core': 'platform-core',
    'frontend': 'experience-interfaces',
    'infrastructure': 'enablement',
    'tests': 'enablement',
    'governance': 'governance-ops',
    'tools': 'enablement',
    'ops': 'governance-ops',
    'config': 'enablement',
    'docs': 'governance-ops',
    'mcp-servers': 'ai-automation',
    'agent': 'ai-automation',
    'shared': 'platform-core',
    'bridges': 'experience-interfaces',
    'contracts': 'experience-interfaces',
    'runtime': 'platform-core',
    'github': 'enablement',
    'architecture': 'platform-core',
    'security': 'governance-ops',
    'guides': 'enablement'
}

# File type mapping
TYPE_MAPPING = {
    '.md': 'markdown',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.json': 'json',
    '.ts': 'ts-module',
    '.py': 'py-module',
    '.go': 'go-module',
    '.js': 'ts-module',
    '.rego': 'policy'
}

# Exclusion sets for efficient membership testing
EXCLUDE_DIRS = {
    'node_modules', 'dist', '__pycache__', '.git', 
    '.venv', 'venv', '.tox', '.pytest_cache', '.mypy_cache', 
    'legacy', 'build', '.next'
}

EXCLUDE_PARTS = {'.git/', 'node_modules/', 'dist/', '__pycache__/'}

# Buffer size for file reading (64KB provides good balance of memory vs performance)
FILE_READ_BUFFER_SIZE = 65536


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file with optimized reading.
    Uses larger buffer size for better performance.
    """
    sha256_hash = hashlib.sha256()
    # Use optimized buffer size for better performance
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(FILE_READ_BUFFER_SIZE), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@lru_cache(maxsize=1000)
def extract_title_from_markdown_cached(file_path_str: str) -> str:
    """
    Extract title from markdown file with caching.
    Uses pre-compiled regex for performance.
    """
    file_path = Path(file_path_str)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read only first 20 lines for title
            content = ''.join(f.readline() for _ in range(20))
            match = TITLE_PATTERN.search(content)
            if match:
                return match.group(1).strip()
    except Exception:
        pass
    return file_path.stem.replace('_', ' ').replace('-', ' ').title()


@lru_cache(maxsize=1000)
def extract_description_from_markdown_cached(file_path_str: str) -> str:
    """
    Extract description from markdown file with caching.
    Optimized to read minimal content.
    """
    file_path = Path(file_path_str)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read only first 50 lines for description
            lines = [f.readline() for _ in range(50)]
            
            in_description = False
            description_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    in_description = True
                    continue
                if in_description and line and not line.startswith('#'):
                    description_lines.append(line)
                    if len(' '.join(description_lines)) > 100:
                        break
                elif in_description and not line and description_lines:
                    break
            
            if description_lines:
                desc = ' '.join(description_lines)[:400]
                return desc
    except Exception:
        pass
    return f"Documentation for {file_path.stem}"


def determine_domain(path_str: str) -> str:
    """Determine domain from path using efficient matching."""
    path_lower = path_str.lower()
    for domain, patterns in DOMAIN_MAPPING.items():
        if any(pattern in path_lower for pattern in patterns):
            return domain
    return 'general'


def determine_layer(domain: str) -> str:
    """Determine layer from domain with O(1) lookup."""
    return LAYER_MAPPING.get(domain, 'enablement')


def determine_type(file_path: Path) -> str:
    """Determine file type from extension with O(1) lookup."""
    return TYPE_MAPPING.get(file_path.suffix, 'document')


def generate_id(path_str: str) -> str:
    """Generate unique ID from path."""
    return path_str.replace('/', '-').replace('.', '-').lower()


@lru_cache(maxsize=500)
def extract_tags_cached(file_path_str: str) -> Tuple[str, ...]:
    """
    Extract relevant tags from file path with caching.
    Returns tuple for hashability (required for caching).
    """
    file_path = Path(file_path_str)
    tags = set()
    
    # Add tags from path components
    for part in file_path.parts:
        part_lower = part.lower()
        if part_lower not in {'docs', 'src', 'lib', 'index'}:
            clean_tag = TAG_CLEAN_PATTERN.sub('', part_lower)
            if clean_tag and len(clean_tag) > 2:
                tags.add(clean_tag)
    
    # Add common tags based on file name
    name = file_path.stem.lower()
    if 'readme' in name:
        tags.add('overview')
    if 'api' in name:
        tags.add('api')
    if 'config' in name:
        tags.add('configuration')
    if 'test' in name:
        tags.add('testing')
    if 'deploy' in name:
        tags.add('deployment')
    
    # Return as tuple (sorted, limited) for caching
    return tuple(sorted(tags)[:5])


def should_exclude_path(rel_path: Path) -> bool:
    """
    Fast path exclusion check using sets.
    Returns True if path should be excluded.
    """
    rel_str = str(rel_path)
    
    # Check for excluded parts
    if any(part in rel_str for part in EXCLUDE_PARTS):
        return True
    
    # Check for hidden directories (except .github)
    if any(part.startswith('.') for part in rel_path.parts):
        if '.github' not in rel_str:
            return True
    
    # Check if any directory part is in exclude set
    if any(part in EXCLUDE_DIRS for part in rel_path.parts):
        return True
    
    return False


def process_single_file(file_path: Path, repo_root: Path) -> Optional[dict[str, Any]]:
    """
    Process a single file and return its index entry.
    Designed to be called in parallel.
    """
    try:
        rel_path = file_path.relative_to(repo_root)
        
        # Quick exclusion check
        if should_exclude_path(rel_path):
            return None
        
        rel_str = str(rel_path)
        
        # Generate entry
        domain = determine_domain(rel_str)
        file_type = determine_type(file_path)
        
        # Use cached functions
        if file_path.suffix == '.md':
            title = extract_title_from_markdown_cached(str(file_path))
            description = extract_description_from_markdown_cached(str(file_path))
        else:
            title = file_path.stem.replace('_', ' ').title()
            description = f"Documentation for {file_path.name}"
        
        tags = extract_tags_cached(str(file_path))
        
        entry = {
            'id': generate_id(rel_str),
            'path': rel_str,
            'title': title,
            'domain': domain,
            'layer': determine_layer(domain),
            'type': file_type,
            'tags': list(tags),
            'owner': 'platform-team',
            'status': 'stable',
            'description': description
        }
        
        return entry
    except Exception as e:
        print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)
        return None


def scan_repository_parallel(
    repo_root: Path, 
    include_patterns: list[str] = None,
    max_workers: int = None
) -> list[dict[str, Any]]:
    """
    Scan repository in parallel using ThreadPoolExecutor.
    Significantly faster than sequential processing.
    
    Args:
        repo_root: Root directory to scan
        include_patterns: Glob patterns to include
        max_workers: Number of parallel workers. If None, defaults to min(32, (cpu_count or 1) + 4)
    """
    if max_workers is None:
        # Use ThreadPoolExecutor default: min(32, (cpu_count or 1) + 4)
        max_workers = min(32, (os.cpu_count() or 1) + 4)
    if include_patterns is None:
        include_patterns = ['**/*.md', '**/README.md']
    
    # Collect all files first (fast operation)
    all_files = set()
    for pattern in include_patterns:
        all_files.update(repo_root.glob(pattern))
    
    print(f"Found {len(all_files)} files to process...")
    
    # Process files in parallel
    items = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_single_file, file_path, repo_root): file_path
            for file_path in all_files
        }
        
        # Collect results as they complete
        for i, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                if result is not None:
                    items.append(result)
                
                # Progress indicator
                if i % 100 == 0:
                    print(f"Processed {i}/{len(all_files)} files...")
            except Exception as e:
                file_path = futures[future]
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
    
    return items


def generate_index(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate the complete index structure."""
    # Define categories
    categories = {
        'architecture': {
            'name': 'Architecture 架構',
            'description': 'System design, layers, and structural documentation'
        },
        'automation': {
            'name': 'Automation 自動化',
            'description': 'Automation systems, agents, and pipelines'
        },
        'governance': {
            'name': 'Governance 治理',
            'description': 'Policies, rules, security, and compliance'
        },
        'operations': {
            'name': 'Operations 運維',
            'description': 'Deployment, monitoring, and operational guides'
        },
        'guides': {
            'name': 'Guides 指南',
            'description': 'Getting started, tutorials, and how-to guides'
        },
        'security': {
            'name': 'Security 安全',
            'description': 'Security policies, scanning, and vulnerability management'
        }
    }
    
    # Define layers
    layers = [
        'experience-interfaces',
        'platform-core',
        'ai-automation',
        'enablement',
        'governance-ops'
    ]
    
    return {
        '$schema': 'https://schema.synergymesh.io/docs-index/v1',
        'namespace': 'synergymesh.docs',
        'version': '1.0.0',
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'categories': categories,
        'layers': layers,
        'items': items
    }


def main():
    parser = argparse.ArgumentParser(
        description='Scan repository and generate docs index (optimized version)'
    )
    parser.add_argument(
        '--output', '-o', 
        default='docs/generated-index.yaml', 
        help='Output file path'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Print output without writing file'
    )
    parser.add_argument(
        '--json', 
        action='store_true', 
        help='Output as JSON instead of YAML'
    )
    parser.add_argument(
        '--include', 
        nargs='+', 
        default=['**/*.md'], 
        help='Glob patterns to include'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: auto-detect based on CPU count)'
    )
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmark'
    )
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    print("🔍 掃描倉庫中 (優化版)...")
    print(f"   Repo root: {repo_root}")
    print(f"   Workers: {args.workers}")
    print()
    
    # Start benchmark
    start_time = time.time()
    
    # Scan repository in parallel
    items = scan_repository_parallel(repo_root, args.include, args.workers)
    
    scan_time = time.time() - start_time
    print(f"✅ 發現 {len(items)} 個文件")
    print(f"⚡ 掃描時間: {scan_time:.2f}s")
    print(f"📊 吞吐量: {len(items)/scan_time:.1f} files/s")
    
    # Generate index
    index_start = time.time()
    index = generate_index(items)
    index_time = time.time() - index_start
    
    print(f"⚡ 索引生成時間: {index_time:.2f}s")
    
    # Output
    if args.dry_run:
        if args.json:
            print(json.dumps(index, indent=2, ensure_ascii=False))
        else:
            print(yaml.dump(index, allow_unicode=True, sort_keys=False))
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if args.json:
                json.dump(index, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(index, f, allow_unicode=True, sort_keys=False)
        
        print(f"✅ 索引已寫入: {output_path}")
    
    # Total time
    total_time = time.time() - start_time
    print(f"\n🎯 總時間: {total_time:.2f}s")
    
    if args.benchmark:
        print("\n📊 Performance Metrics:")
        print(f"   Files processed: {len(items)}")
        print(f"   Scan time: {scan_time:.2f}s")
        print(f"   Index generation: {index_time:.2f}s")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Throughput: {len(items)/total_time:.1f} files/s")
        print(f"   Cache info (title): {extract_title_from_markdown_cached.cache_info()}")
        print(f"   Cache info (tags): {extract_tags_cached.cache_info()}")


if __name__ == '__main__':
    main()
