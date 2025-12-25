#!/usr/bin/env python3

"""
Knowledge Graph Visualizer
知识图谱可视化系统 - 为实体关系提供可视化界面
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class KnowledgeGraphVisualizer:
    """知识图谱可视化器"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.knowledge_graph_path = repo_root / "workspace/docs/knowledge_graph.json"
        self.visualization_dir = repo_root / "workspace/docs/visualizations"
        self.visualization_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure D3.js is available locally for offline mode
        self.d3_local_path = repo_root / "workspace/docs/assets/d3.v7.min.js"
        self._ensure_d3_available()
    
    def _ensure_d3_available(self):
        """确保D3.js在本地可用（离线模式支持）"""
        if not self.d3_local_path.exists():
            self.d3_local_path.parent.mkdir(parents=True, exist_ok=True)
            # Download D3.js if not available
            try:
                import urllib.request
                url = "https://d3js.org/d3.v7.min.js"
                urllib.request.urlretrieve(url, self.d3_local_path)
                print(f"Downloaded D3.js to {self.d3_local_path}")
            except Exception as e:
                print(f"Warning: Could not download D3.js: {e}")
                print("Visualization will require internet connection")
    
    def load_graph(self) -> Dict[str, Any]:
        """加载知识图谱"""
        if not self.knowledge_graph_path.exists():
            return {"entities": {}, "relationships": [], "last_updated": ""}
        
        try:
            with open(self.knowledge_graph_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"entities": {}, "relationships": [], "last_updated": ""}
    
    def _get_node_color(self, node_type: str, impact_level: str) -> str:
        """获取节点颜色"""
        color_map = {
            ("config", "high"): "#ff6b6b",    # 红色
            ("config", "medium"): "#feca57",   # 黄色
            ("config", "low"): "#48dbfb",     # 蓝色
            ("spec", "high"): "#ff9ff3",      # 粉色
            ("spec", "medium"): "#feca57",    # 黄色
            ("spec", "low"): "#48dbfb",       # 蓝色
            ("registry", "high"): "#ff6b6b",  # 红色
            ("registry", "medium"): "#feca57", # 黄色
            ("registry", "low"): "#48dbfb",   # 蓝色
            ("workflow", "high"): "#00d2d3",  # 青色
            ("workflow", "medium"): "#54a0ff", # 浅蓝
            ("workflow", "low"): "#5f27cd",   # 紫色
            ("doc", "high"): "#ff9ff3",       # 粉色
            ("doc", "medium"): "#c8d6e5",     # 灰色
            ("doc", "low"): "#c8d6e5",        # 灰色
        }
        return color_map.get((node_type, impact_level), "#95afc0")
    
    def _get_node_size(self, priority: int) -> int:
        """获取节点大小"""
        if priority >= 100:
            return 40
        elif priority >= 90:
            return 35
        elif priority >= 80:
            return 30
        elif priority >= 50:
            return 25
        else:
            return 20
    
    def _get_edge_width(self, strength: str) -> int:
        """获取边的宽度"""
        if strength == "strong":
            return 3
        elif strength == "medium":
            return 2
        else:
            return 1
    
    def _sanitize_csv_field(self, field: str) -> str:
        """防止CSV注入攻击"""
        if isinstance(field, str) and field and field[0] in ['=', '+', '-', '@']:
            return "'" + field
        return field
    
    def generate_d3_visualization(self) -> str:
        """生成D3.js可视化"""
        graph = self.load_graph()
        
        # 收集所有存在的实体ID
        entity_ids = set(graph["entities"].keys())
        
        nodes = []
        edges = []
        
        # 生成节点
        for entity_id, entity_data in graph["entities"].items():
            node = {
                "id": entity_id,
                "label": entity_id.split("/")[-1],  # 只显示文件名
                "fullLabel": entity_id,
                "type": entity_data["type"],
                "category": entity_data["category"],
                "priority": entity_data["priority"],
                "impact_level": entity_data["impact_level"],
                "color": self._get_node_color(entity_data["type"], entity_data["impact_level"]),
                "size": self._get_node_size(entity_data["priority"]),
                "group": entity_data["category"],
                "last_modified": entity_data["last_modified"]
            }
            nodes.append(node)
        
        # 生成边 - 只包含两端都存在的关系
        for relationship in graph["relationships"]:
            source = relationship["source"]
            target = relationship["target"]
            
            # 只添加source和target都在nodes中的边
            if source in entity_ids and target in entity_ids:
                edge = {
                    "source": source,
                    "target": target,
                    "type": relationship["type"],
                    "strength": relationship["strength"],
                    "width": self._get_edge_width(relationship["strength"]),
                    "timestamp": relationship["timestamp"]
                }
                edges.append(edge)
        
        # 将图数据保存为单独的JSON文件（优化性能）
        graph_data = {"nodes": nodes, "edges": edges}
        graph_data_path = self.visualization_dir / "graph_data.json"
        graph_data_path.write_text(
            json.dumps(graph_data, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # 生成HTML可视化页面
        html_content = self._generate_html_template(graph["last_updated"])
        
        output_path = self.visualization_dir / "knowledge_graph.html"
        output_path.write_text(html_content, encoding="utf-8")
        
        return str(output_path)
    
    def _generate_html_template(self, last_updated: str) -> str:
        """生成HTML模板"""
        # 使用相对路径引用本地D3.js
        d3_script = '../assets/d3.v7.min.js' if self.d3_local_path.exists() else 'https://d3js.org/d3.v7.min.js'
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MachineNativeOps 知识图谱</title>
    <script src="{d3_script}"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        
        .controls {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        
        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .control-group label {{
            font-weight: 500;
            color: #495057;
        }}
        
        .control-group select, .control-group input {{
            padding: 5px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }}
        
        button {{
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
        }}
        
        button:hover {{
            background: #0056b3;
        }}
        
        #graph {{
            width: 100%;
            height: 600px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: #ffffff;
        }}
        
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            max-width: 300px;
        }}
        
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .legend h3 {{
            margin-top: 0;
            color: #495057;
        }}
        
        .legend-items {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }}
        
        .stats {{
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 8px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 MachineNativeOps 知识图谱</h1>
            <p>最后更新: {last_updated}</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>节点类型过滤:</label>
                <select id="typeFilter">
                    <option value="all">全部</option>
                    <option value="config">配置文件</option>
                    <option value="spec">规范文件</option>
                    <option value="registry">注册表</option>
                    <option value="workflow">工作流</option>
                    <option value="doc">文档</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>影响级别:</label>
                <select id="impactFilter">
                    <option value="all">全部</option>
                    <option value="high">高</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                </select>
            </div>
            
            <button onclick="resetZoom()">重置缩放</button>
            <button onclick="togglePhysics()">切换物理模拟</button>
        </div>
        
        <div id="graph"></div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value" id="nodeCount">0</div>
                <div class="stat-label">节点总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="edgeCount">0</div>
                <div class="stat-label">关系总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="configCount">0</div>
                <div class="stat-label">配置文件</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="specCount">0</div>
                <div class="stat-label">规范文件</div>
            </div>
        </div>
        
        <div class="legend">
            <h3>图例说明</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff6b6b;"></div>
                    <span>高影响配置</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #feca57;"></div>
                    <span>中等影响</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #48dbfb;"></div>
                    <span>低影响</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff9ff3;"></div>
                    <span>规范文件</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #00d2d3;"></div>
                    <span>工作流</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        // 从外部JSON文件加载图谱数据（优化性能）
        fetch('./graph_data.json')
            .then(response => response.json())
            .then(data => {{
                initializeGraph(data.nodes, data.edges);
            }})
            .catch(error => {{
                console.error('Error loading graph data:', error);
            }});
        
        function initializeGraph(nodes, edges) {{
            // 初始化统计
            document.getElementById('nodeCount').textContent = nodes.length;
            document.getElementById('edgeCount').textContent = edges.length;
            document.getElementById('configCount').textContent = nodes.filter(n => n.type === 'config').length;
            document.getElementById('specCount').textContent = nodes.filter(n => n.type === 'spec').length;
            
            // 创建SVG
            const width = document.getElementById('graph').clientWidth;
            const height = 600;
            
            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // 创建缩放行为
            const zoom = d3.zoom()
                .scaleExtent([0.1, 3])
                .on('zoom', (event) => {{
                    g.attr('transform', event.transform);
                }});
            
            svg.call(zoom);
            
            const g = svg.append('g');
            
            // 创建力导向布局
            let simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => d.size + 5));
            
            // 创建箭头标记
            svg.append('defs').append('marker')
                .attr('id', 'arrowhead')
                .attr('viewBox', '-0 -5 10 10')
                .attr('refX', 15)
                .attr('refY', 0)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
                .attr('fill', '#999');
            
            // 创建边
            const link = g.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(edges)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => d.width)
                .attr('marker-end', 'url(#arrowhead)');
            
            // 创建节点
            const node = g.append('g')
                .attr('class', 'nodes')
                .selectAll('g')
                .data(nodes)
                .enter().append('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // 添加节点圆形
            node.append('circle')
                .attr('r', d => d.size)
                .attr('fill', d => d.color)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
                .on('mouseover', showTooltip)
                .on('mouseout', hideTooltip);
            
            // 添加节点标签
            node.append('text')
                .text(d => d.label)
                .attr('x', d => d.size + 5)
                .attr('y', 4)
                .attr('font-size', '12px')
                .attr('font-weight', '500');
            
            // 更新力导向图
            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
            }});
            
            // 拖拽功能
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
            
            // 工具提示
            const tooltip = document.getElementById('tooltip');
            
            function showTooltip(event, d) {{
                tooltip.innerHTML = `
                    <strong>${{d.fullLabel}}</strong><br/>
                    类型: ${{d.type}}<br/>
                    类别: ${{d.category}}<br/>
                    影响级别: ${{d.impact_level}}<br/>
                    优先级: ${{d.priority}}<br/>
                    最后修改: ${{d.last_modified}}
                `;
                tooltip.style.left = event.pageX + 10 + 'px';
                tooltip.style.top = event.pageY + 10 + 'px';
                tooltip.style.opacity = 1;
            }}
            
            function hideTooltip() {{
                tooltip.style.opacity = 0;
            }}
            
            // 控制功能
            window.resetZoom = function() {{
                svg.transition().duration(750).call(
                    zoom.transform,
                    d3.zoomIdentity.translate(width/2, height/2).scale(1)
                );
            }}
            
            let physicsEnabled = true;
            window.togglePhysics = function() {{
                physicsEnabled = !physicsEnabled;
                if (physicsEnabled) {{
                    simulation.alpha(1).restart();
                }} else {{
                    simulation.stop();
                }}
            }}
            
            // 过滤功能
            document.getElementById('typeFilter').addEventListener('change', applyFilters);
            document.getElementById('impactFilter').addEventListener('change', applyFilters);
            
            function applyFilters() {{
                const typeFilter = document.getElementById('typeFilter').value;
                const impactFilter = document.getElementById('impactFilter').value;
                
                node.style('opacity', d => {{
                    if (typeFilter !== 'all' && d.type !== typeFilter) return 0.1;
                    if (impactFilter !== 'all' && d.impact_level !== impactFilter) return 0.1;
                    return 1;
                }});
                
                link.style('opacity', d => {{
                    if (typeFilter !== 'all') {{
                        if (d.source.type !== typeFilter && d.target.type !== typeFilter) return 0.1;
                    }}
                    if (impactFilter !== 'all') {{
                        if (d.source.impact_level !== impactFilter && d.target.impact_level !== impactFilter) return 0.1;
                    }}
                    return 0.6;
                }});
            }}
        }}
    </script>
</body>
</html>"""
    
    def generate_static_report(self) -> str:
        """生成静态报告"""
        graph = self.load_graph()
        
        if not graph["entities"]:
            return "知识图谱为空，无法生成报告。"
        
        # 统计分析
        entity_types = defaultdict(int)
        impact_levels = defaultdict(int)
        categories = defaultdict(int)
        
        for entity_id, entity_data in graph["entities"].items():
            entity_types[entity_data["type"]] += 1
            impact_levels[entity_data["impact_level"]] += 1
            categories[entity_data["category"]] += 1
        
        # 关系统计
        relationship_types = defaultdict(int)
        relationship_strengths = defaultdict(int)
        
        for rel in graph["relationships"]:
            relationship_types[rel["type"]] += 1
            relationship_strengths[rel["strength"]] += 1
        
        # 生成报告
        report_lines = [
            "# 知识图谱分析报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"最后更新: {graph.get('last_updated', '未知')}",
            "",
            "## 📊 统计概览",
            f"- 实体总数: {len(graph['entities'])}",
            f"- 关系总数: {len(graph['relationships'])}",
            "",
            "## 🏷️ 实体类型分布",
        ]
        
        for entity_type, count in sorted(entity_types.items()):
            report_lines.append(f"- {entity_type}: {count}")
        
        report_lines.extend([
            "",
            "## 🎯 影响级别分布",
        ])
        
        for impact_level, count in sorted(impact_levels.items()):
            report_lines.append(f"- {impact_level}: {count}")
        
        report_lines.extend([
            "",
            "## 📁 类别分布",
        ])
        
        for category, count in sorted(categories.items()):
            report_lines.append(f"- {category}: {count}")
        
        report_lines.extend([
            "",
            "## 🔗 关系类型分布",
        ])
        
        for rel_type, count in sorted(relationship_types.items()):
            report_lines.append(f"- {rel_type}: {count}")
        
        report_lines.extend([
            "",
            "## 💪 关系强度分布",
        ])
        
        for strength, count in sorted(relationship_strengths.items()):
            report_lines.append(f"- {strength}: {count}")
        
        # 高优先级实体
        high_priority_entities = [
            (entity_id, entity_data) for entity_id, entity_data in graph["entities"].items()
            if entity_data.get("priority", 0) >= 90
        ]
        
        if high_priority_entities:
            report_lines.extend([
                "",
                "## ⚡ 高优先级实体 (Priority ≥ 90)",
            ])
            
            for entity_id, entity_data in sorted(high_priority_entities, key=lambda x: x[1].get("priority", 0), reverse=True):
                report_lines.append(f"- `{entity_id}` (Priority: {entity_data.get('priority', 0)}, Impact: {entity_data.get('impact_level', 'unknown')})")
        
        # 关键关系
        strong_relationships = [
            rel for rel in graph["relationships"] if rel.get("strength") == "strong"
        ]
        
        if strong_relationships:
            report_lines.extend([
                "",
                "## 🔒 强依赖关系",
            ])
            
            for rel in strong_relationships[:20]:  # Limit to first 20
                report_lines.append(f"- `{rel['source']}` → `{rel['target']}` ({rel.get('type', 'unknown')})")
            
            if len(strong_relationships) > 20:
                report_lines.append(f"- ... 还有 {len(strong_relationships) - 20} 个强依赖关系")
        
        report_content = "\n".join(report_lines)
        
        output_path = self.visualization_dir / "knowledge_graph_report.md"
        output_path.write_text(report_content, encoding="utf-8")
        
        return str(output_path)
    
    def export_graph_data(self) -> str:
        """导出图谱数据为标准格式"""
        graph = self.load_graph()
        
        # 导出为CSV格式 - 带CSV注入防护
        entities_lines = ["id,type,category,priority,impact_level,last_modified"]
        for entity_id, entity_data in graph["entities"].items():
            entities_lines.append(
                f'"{self._sanitize_csv_field(entity_id)}",'
                f'"{entity_data["type"]}",'
                f'"{entity_data["category"]}",'
                f'{entity_data["priority"]},'
                f'"{entity_data["impact_level"]}",'
                f'"{entity_data["last_modified"]}"'
            )
        entities_csv = "\n".join(entities_lines) + "\n"
        
        relationships_lines = ["source,target,type,strength,timestamp"]
        for rel in graph["relationships"]:
            relationships_lines.append(
                f'"{self._sanitize_csv_field(rel["source"])}",'
                f'"{self._sanitize_csv_field(rel["target"])}",'
                f'"{rel["type"]}",'
                f'"{rel["strength"]}",'
                f'"{rel["timestamp"]}"'
            )
        relationships_csv = "\n".join(relationships_lines) + "\n"
        
        output_dir = self.visualization_dir / "exports"
        output_dir.mkdir(exist_ok=True)
        
        entities_path = output_dir / "entities.csv"
        relationships_path = output_dir / "relationships.csv"
        
        entities_path.write_text(entities_csv, encoding="utf-8")
        relationships_path.write_text(relationships_csv, encoding="utf-8")
        
        return str(output_dir)


def get_repo_root() -> Path:
    """获取仓库根目录 - 使用 git 命令而非硬编码路径"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # Fallback to relative path if git command fails
        return Path(__file__).resolve().parents[4]


def main():
    """主函数"""
    repo_root = get_repo_root()
    visualizer = KnowledgeGraphVisualizer(repo_root)
    
    # 生成可视化
    html_path = visualizer.generate_d3_visualization()
    print(f"知识图谱可视化已生成: {html_path}")
    
    # 生成报告
    report_path = visualizer.generate_static_report()
    print(f"知识图谱报告已生成: {report_path}")
    
    # 导出数据
    export_dir = visualizer.export_graph_data()
    print(f"图谱数据已导出: {export_dir}")


if __name__ == "__main__":
    main()