#!/usr/bin/env python3
"""
Generate a Knowledge Graph from the repository structure and MN-DOC entities.

This script scans the repository and creates a knowledge graph representation
that can be used for visualization, querying, and governance analysis.

Usage:
  python tools/docs/generate_knowledge_graph.py \
    --repo-root . \
    --output docs/knowledge-graph.yaml

  python tools/docs/generate_knowledge_graph.py --help
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Try to import yaml, provide helpful error if not available
try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# File patterns to include/exclude
INCLUDE_PATTERNS = [
    "*.py", "*.ts", "*.js", "*.yaml", "*.yml", "*.json", "*.md",
]
EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build", ".venv",
    "venv", ".tox", ".pytest_cache", ".mypy_cache", "legacy",
}

# Directory to node type mapping (lowercase enums for schema compliance, with Chinese labels)
# Valid node types per schema: system, subsystem, component, module, file, directory, config, document, workflow, schema, capability, feature, tag
DIR_TYPE_MAPPING = {
    "core": ("subsystem", "子系統"),
    "automation": ("subsystem", "子系統"),
    "governance": ("subsystem", "子系統"),
    "config": ("config", "設定"),
    "docs": ("document", "文件"),
    "tests": ("module", "模組"),
    "tools": ("module", "模組"),
    "infrastructure": ("module", "模組"),
    "mcp-servers": ("module", "MCP伺服器"),  # "module" is used as schema has no MCP-specific type
    "agent": ("module", "模組"),
}

# File suffix to node type mapping (lowercase enums for schema compliance)
FILE_TYPE_MAPPING = {
    ".py": ("module", "模組"),
    ".ts": ("module", "模組"),
    ".js": ("module", "模組"),
    ".yaml": ("config", "設定"),
    ".yml": ("config", "設定"),
    ".json": ("config", "設定"),
    ".md": ("document", "文件"),
}


class KnowledgeGraphGenerator:
    """Generate knowledge graph from repository structure."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.node_ids: set[str] = set()
    
    def generate(self) -> dict[str, Any]:
        """Generate the complete knowledge graph."""
        # Add root system node
        self._add_system_node()
        
        # Scan directory structure
        self._scan_directories()
        
        # Load and process MN-DOC entities
        self._process_mndoc_entities()
        
        # Process config files
        self._process_config_files()
        
        # Generate statistics
        stats = self._generate_statistics()
        
        return {
            "$schema": "https://schema.superroot.kn/mndoc/knowledge-graph/v1",
            "version": "1.0.0",
            "id": "unmanned-island-knowledge-graph",
            "title": "Unmanned Island System Knowledge Graph",
            "description": "Knowledge graph representation of the repository structure and entities",
            "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "source_repo": str(self.repo_root),
            "nodes": self.nodes,
            "edges": self.edges,
            "statistics": stats,
            "meta": {
                "generator": "generate_knowledge_graph.py",
                "version": "1.0.0",
            },
        }
    
    def _add_node(self, node_id: str, node_type: str, label: str,
                  path: str | None = None, description: str | None = None,
                  properties: dict | None = None, tags: list | None = None) -> bool:
        """Add a node to the graph. Returns True if added, False if duplicate."""
        if node_id in self.node_ids:
            return False
        
        node = {
            "id": node_id,
            "type": node_type,
            "label": label,
        }
        if path:
            node["path"] = path
        if description:
            node["description"] = description
        if properties:
            node["properties"] = properties
        if tags:
            node["tags"] = tags
        
        self.nodes.append(node)
        self.node_ids.add(node_id)
        return True
    
    def _add_edge(self, source: str, target: str, edge_type: str,
                  label: str | None = None, weight: float | None = None) -> None:
        """Add an edge to the graph."""
        edge = {
            "source": source,
            "target": target,
            "type": edge_type,
        }
        if label:
            edge["label"] = label
        if weight is not None:
            edge["weight"] = weight
        
        self.edges.append(edge)
    
    def _add_system_node(self) -> None:
        """Add the root system node."""
        self._add_node(
            node_id="system:unmanned-island",
            node_type="system",
            label="Unmanned Island System",
            description="Enterprise-grade cloud-native intelligent automation platform",
            properties={"label_zh": "系統"},
            tags=["cloud-native", "automation", "governance"],
        )
    
    def _scan_directories(self) -> None:
        """Scan repository directories and create nodes."""
        for item in self.repo_root.iterdir():
            if item.name.startswith(".") and item.name not in [".github"]:
                continue
            if item.name in EXCLUDE_DIRS:
                continue
            
            if item.is_dir():
                self._process_directory(item, parent_id="system:unmanned-island")
    
    def _process_directory(self, dir_path: Path, parent_id: str, depth: int = 0) -> None:
        """Process a directory and its contents."""
        if depth > 3:  # Limit depth
            return
        
        rel_path = dir_path.relative_to(self.repo_root)
        dir_name = dir_path.name
        
        # Determine node type (lowercase enum with Chinese label)
        type_info = DIR_TYPE_MAPPING.get(dir_name, ("directory", "目錄"))
        node_type = type_info[0]
        label_zh = type_info[1]
        
        # Create node ID
        node_id = f"dir:{rel_path}".replace("/", ":")
        
        # Add directory node with Chinese label in properties
        self._add_node(
            node_id=node_id,
            node_type=node_type,
            label=dir_name,
            path=str(rel_path),
            properties={"label_zh": label_zh},
        )
        
        # Add edge from parent
        self._add_edge(parent_id, node_id, "contains")
        
        # Process subdirectories (limited depth)
        if depth < 2:
            for item in dir_path.iterdir():
                if item.name.startswith("."):
                    continue
                if item.name in EXCLUDE_DIRS:
                    continue
                
                if item.is_dir():
                    self._process_directory(item, node_id, depth + 1)
                elif item.is_file() and item.suffix in [".py", ".ts", ".js", ".yaml", ".yml"]:
                    self._process_file(item, node_id)
    
    def _process_file(self, file_path: Path, parent_id: str) -> None:
        """Process a file and create a node."""
        rel_path = file_path.relative_to(self.repo_root)
        
        # Determine file type (lowercase enum with Chinese label)
        type_info = FILE_TYPE_MAPPING.get(file_path.suffix, ("file", "檔案"))
        node_type = type_info[0]
        label_zh = type_info[1]
        
        node_id = f"file:{rel_path}".replace("/", ":")
        
        self._add_node(
            node_id=node_id,
            node_type=node_type,
            label=file_path.name,
            path=str(rel_path),
            properties={"label_zh": label_zh},
        )
        
        self._add_edge(parent_id, node_id, "contains")
    
    def _process_mndoc_entities(self) -> None:
        """Process MN-DOC entity files."""
        mndoc_dir = self.repo_root / "docs" / "mndoc"
        if not mndoc_dir.exists():
            return
        
        # Process subsystems
        subsystems_dir = mndoc_dir / "subsystems"
        if subsystems_dir.exists():
            for yaml_file in subsystems_dir.glob("*.yaml"):
                self._process_mndoc_file(yaml_file, "subsystem", "子系統")
        
        # Process components
        components_dir = mndoc_dir / "components"
        if components_dir.exists():
            for yaml_file in components_dir.glob("*.yaml"):
                self._process_mndoc_file(yaml_file, "component", "元件")
    
    def _process_mndoc_file(self, file_path: Path, default_type: str, label_zh: str) -> None:
        """Process a single MN-DOC YAML file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            entity_id = data.get("id", file_path.stem)
            entity_type = data.get("type", default_type)
            title = data.get("title", entity_id)
            
            # Map entity type to lowercase enum for schema compliance
            type_map = {
                "subsystem": "subsystem",
                "component": "component",
            }
            node_type = type_map.get(entity_type.lower(), default_type) if isinstance(entity_type, str) else default_type
            
            node_id = f"entity:{entity_id}"
            
            self._add_node(
                node_id=node_id,
                node_type=node_type,
                label=title,
                path=str(file_path.relative_to(self.repo_root)),
                description=data.get("description"),
                properties={"label_zh": label_zh},
                tags=data.get("tags", []),
            )
            
            # Add edge to system
            self._add_edge("system:unmanned-island", node_id, "contains")
            
            # Process capabilities
            capabilities = data.get("capabilities", [])
            for cap in capabilities:
                cap_id = f"capability:{cap}" if isinstance(cap, str) else f"capability:{cap.get('id', 'unknown')}"
                cap_label = cap if isinstance(cap, str) else cap.get("name", cap.get("id", "unknown"))
                
                if self._add_node(
                    node_id=cap_id,
                    node_type="capability",
                    label=cap_label,
                    properties={"label_zh": "功能"},
                ):
                    self._add_edge(node_id, cap_id, "provides")
            
        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}")
    
    def _process_config_files(self) -> None:
        """Process main configuration files."""
        seen_targets: set[Path] = set()
        config_files = [
            "machinenativeops.yaml",
            "synergymesh.yaml",
            "config/system-manifest.yaml",
            "config/system-module-map.yaml",
            "config/unified-config-index.yaml",
        ]
        
        for config_path in config_files:
            full_path = self.repo_root / config_path
            if full_path.exists():
                resolved_path = full_path.resolve()
                if resolved_path in seen_targets:
                    continue
                node_id = f"config:{config_path}".replace("/", ":")
                self._add_node(
                    node_id=node_id,
                    node_type="config",
                    label=full_path.name,
                    path=config_path,
                    properties={"label_zh": "設定"},
                )
                self._add_edge("system:unmanned-island", node_id, "configures")
                seen_targets.add(resolved_path)
    
    def _generate_statistics(self) -> dict[str, Any]:
        """Generate graph statistics."""
        nodes_by_type: dict[str, int] = {}
        edges_by_type: dict[str, int] = {}
        
        for node in self.nodes:
            node_type = node["type"]
            nodes_by_type[node_type] = nodes_by_type.get(node_type, 0) + 1
        
        for edge in self.edges:
            edge_type = edge["type"]
            edges_by_type[edge_type] = edges_by_type.get(edge_type, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": nodes_by_type,
            "edges_by_type": edges_by_type,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a Knowledge Graph from the repository structure"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/knowledge-graph.yaml"),
        help="Output path for knowledge graph (default: docs/knowledge-graph.yaml)",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output to stdout instead of writing to file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output",
    )
    
    args = parser.parse_args()
    
    if not args.repo_root.exists():
        print(f"Error: Repository root not found: {args.repo_root}")
        sys.exit(1)
    
    if args.verbose:
        print(f"Scanning: {args.repo_root.absolute()}")
    
    # Generate knowledge graph
    generator = KnowledgeGraphGenerator(args.repo_root)
    graph = generator.generate()
    
    # Format output
    if args.format == "json":
        output = json.dumps(graph, indent=2, ensure_ascii=False)
    else:
        output = yaml.dump(
            graph,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=100,
        )
    
    # Output
    if args.dry_run:
        print(output)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"✅ Generated: {args.output}")
        
        if args.verbose:
            stats = graph["statistics"]
            print(f"   - Nodes: {stats['total_nodes']}")
            print(f"   - Edges: {stats['total_edges']}")
            print(f"   - Node types: {', '.join(stats['nodes_by_type'].keys())}")


if __name__ == "__main__":
    main()
