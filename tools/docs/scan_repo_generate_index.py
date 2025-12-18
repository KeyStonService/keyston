#!/usr/bin/env python3
"""
Repository Scanner and Index Generator
倉庫掃描與索引生成器

Scans the repository and automatically generates a docs-index.yaml file
based on discovered documentation files.

Usage:
    python tools/docs/scan_repo_generate_index.py
    python tools/docs/scan_repo_generate_index.py --output docs/generated-index.yaml
    python tools/docs/scan_repo_generate_index.py --dry-run
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# Domain mapping based on directory structure
DOMAIN_MAPPING = {
    'automation': ['automation/', 'automation/'],
    'core': ['core/'],
    'frontend': ['frontend/', 'ui/'],
    'infrastructure': ['infrastructure/', 'src/autonomous/deployment/', 'k8s/'],
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


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_title_from_markdown(file_path: Path) -> str:
    """Extract title from markdown file (first H1 heading)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    return file_path.stem.replace('_', ' ').replace('-', ' ').title()


def extract_description_from_markdown(file_path: Path) -> str:
    """Extract description from markdown file (first non-empty paragraph after title)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Skip frontmatter if present
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) > 2:
                    content = parts[2]
            
            # Find first paragraph after title
            lines = content.split('\n')
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


def determine_domain(file_path: str) -> str:
    """Determine domain based on file path."""
    for domain, prefixes in DOMAIN_MAPPING.items():
        for prefix in prefixes:
            if file_path.startswith(prefix):
                return domain
    return 'docs'


def determine_layer(domain: str) -> str:
    """Determine layer based on domain."""
    return LAYER_MAPPING.get(domain, 'governance-ops')


def determine_type(file_path: Path) -> str:
    """Determine type based on file extension."""
    suffix = file_path.suffix.lower()
    base_type = TYPE_MAPPING.get(suffix, 'markdown')
    
    # Special cases
    name = file_path.name.lower()
    if name == 'readme.md':
        return 'readme'
    if 'api' in name:
        return 'api-reference'
    if name.endswith('.schema.json'):
        return 'schema'
    if 'workflow' in str(file_path) or file_path.suffix in ['.yaml', '.yml']:
        if '.github/workflows' in str(file_path):
            return 'workflow'
    if 'policy' in name or 'policies' in str(file_path):
        return 'policy'
    
    return base_type


def generate_id(file_path: str) -> str:
    """Generate a unique ID from file path."""
    # Remove extension and replace path separators
    id_base = file_path.replace('/', '_').replace('.', '_')
    # Remove leading/trailing underscores
    id_base = id_base.strip('_')
    # Convert to lowercase and replace multiple underscores
    id_base = re.sub(r'_+', '_', id_base.lower())
    # Remove invalid characters
    id_base = re.sub(r'[^a-z0-9_-]', '', id_base)
    return id_base


def extract_tags(file_path: Path, content: str = None) -> list[str]:
    """Extract relevant tags from file path and content."""
    tags = set()
    
    # Add tags from path components
    parts = file_path.parts
    for part in parts:
        part_lower = part.lower()
        if part_lower not in ['docs', 'src', 'lib', 'index']:
            clean_tag = re.sub(r'[^a-z0-9-]', '', part_lower)
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
    
    return sorted(list(tags))[:5]  # Limit to 5 tags


def scan_repository(repo_root: Path, include_patterns: list[str] = None) -> list[dict[str, Any]]:
    """Scan repository and generate index entries."""
    if include_patterns is None:
        include_patterns = ['**/*.md', '**/README.md']
    
    items = []
    seen_paths = set()
    
    for pattern in include_patterns:
        for file_path in repo_root.glob(pattern):
            # Skip hidden directories and common exclusions
            rel_path = file_path.relative_to(repo_root)
            rel_str = str(rel_path)
            
            if any(part.startswith('.') for part in rel_path.parts):
                if '.github' not in rel_str:  # Allow .github
                    continue
            
            if rel_str in seen_paths:
                continue
            seen_paths.add(rel_str)
            
            # Skip node_modules, dist, etc.
            if any(skip in rel_str for skip in ['node_modules', 'dist/', '__pycache__', '.git/']):
                continue
            
            # Generate entry
            domain = determine_domain(rel_str)
            file_type = determine_type(file_path)
            
            entry = {
                'id': generate_id(rel_str),
                'path': rel_str,
                'title': extract_title_from_markdown(file_path) if file_path.suffix == '.md' else file_path.stem.replace('_', ' ').title(),
                'domain': domain,
                'layer': determine_layer(domain),
                'type': file_type,
                'tags': extract_tags(file_path),
                'owner': 'platform-team',
                'status': 'stable',
                'description': extract_description_from_markdown(file_path) if file_path.suffix == '.md' else f"Documentation for {file_path.name}"
            }
            
            items.append(entry)
    
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
    parser = argparse.ArgumentParser(description='Scan repository and generate docs index')
    parser.add_argument('--output', '-o', default='docs/generated-index.yaml', help='Output file path')
    parser.add_argument('--dry-run', action='store_true', help='Print output without writing file')
    parser.add_argument('--json', action='store_true', help='Output as JSON instead of YAML')
    parser.add_argument('--include', nargs='+', default=['**/*.md'], help='Glob patterns to include')
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    print("🔍 掃描倉庫中...")
    print(f"   Repo root: {repo_root}")
    print()
    
    # Scan repository
    items = scan_repository(repo_root, args.include)
    print(f"✅ 發現 {len(items)} 個文件")
    
    # Generate index
    index = generate_index(items)
    
    if args.dry_run:
        print()
        print("📄 生成的索引預覽:")
        print("-" * 60)
        if args.json:
            print(json.dumps(index, indent=2, ensure_ascii=False))
        else:
            print(yaml.dump(index, allow_unicode=True, default_flow_style=False, sort_keys=False))
    else:
        output_path = repo_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if args.json:
                json.dump(index, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"💾 索引已寫入: {output_path}")
    
    print()
    print("📊 摘要:")
    print(f"   • 總文件數: {len(items)}")
    domains = set(item['domain'] for item in items)
    print(f"   • 涵蓋域: {', '.join(sorted(domains))}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
