#!/usr/bin/env python3

"""
Enhanced Memory Synchronization System
增强记忆同步系统 - 包含智能内容分析、知识图谱集成、跨文件关联检测
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Use sha3-512 for cryptographic hashing (governance compliance)
try:
    import hashlib
    # Verify sha3_512 is available
    hashlib.sha3_512()
    HASH_ALGO = 'sha3_512'
except (AttributeError, ValueError):
    # Fallback to sha256 if sha3_512 not available
    HASH_ALGO = 'sha256'


@dataclass
class FileAnalysis:
    """文件分析结果"""
    path: str
    type: str  # config, spec, registry, doc, workflow
    category: str
    priority: int
    dependencies: List[str]
    impact_level: str  # high, medium, low
    content_hash: str
    entities: List[str]
    relationships: List[Dict[str, Any]]


@dataclass
class ChangeAnalysis:
    """变更分析结果"""
    sha: str
    author: str
    subject: str
    timestamp: str
    added: List[FileAnalysis]
    modified: List[FileAnalysis]
    deleted: List[str]
    total_impact: str


class EnhancedMemorySync:
    """增强记忆同步系统"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.controlplane = repo_root / "controlplane"
        self.workspace = repo_root / "workspace"
        self.knowledge_graph_path = repo_root / "workspace/docs/knowledge_graph.json"
        self.memory_index_path = repo_root / "workspace/docs/memory_index.json"
        
    def _run(self, cmd: List[str]) -> subprocess.CompletedProcess[str]:
        """执行命令"""
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=self.repo_root)
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip() or "no output"
            raise RuntimeError(f"Command '{' '.join(cmd)}' failed ({exc.returncode}): {message}") from exc

    def _now(self) -> str:
        """获取当前时间戳"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _get_file_hash(self, path: Path) -> str:
        """获取文件内容哈希 - 使用 sha3-512 符合治理规范"""
        try:
            content = path.read_text(encoding="utf-8")
            if HASH_ALGO == 'sha3_512':
                return hashlib.sha3_512(content.encode()).hexdigest()
            else:
                return hashlib.sha256(content.encode()).hexdigest()
        except (OSError, UnicodeDecodeError):
            return "unavailable"

    def _extract_dependencies(self, content: str, file_path: str) -> List[str]:
        """提取文件依赖关系"""
        dependencies = []
        
        # Extract YAML imports/includes
        yaml_imports = re.findall(r'(?:import|include|extends):\s*["\']?([^\s"\']+)["\']?', content)
        dependencies.extend(yaml_imports)
        
        # Extract Python imports (relative to repo)
        py_imports = re.findall(r'from\s+([a-zA-Z0-9_.]+)\s+import', content)
        dependencies.extend(py_imports)
        
        # Extract file references with proper path patterns
        file_refs = re.findall(r'[\w\-./]+\.(?:yaml|yml|md|py|sh)', content)
        dependencies.extend(file_refs)
        
        # Remove duplicates and self-references
        dependencies = list(set(dep for dep in dependencies if dep != file_path))
        
        return dependencies

    def _analyze_file(self, file_path: str) -> FileAnalysis:
        """分析文件类型和内容"""
        full_path = self.repo_root / file_path
        
        # 确定文件类型
        if file_path.endswith(('.yaml', '.yml')):
            if 'root.' in file_path and 'config' in file_path:
                file_type = 'config'
            elif 'specs.' in file_path:
                file_type = 'spec'
            elif 'registry.' in file_path:
                file_type = 'registry'
            elif 'workflow' in file_path or file_path.startswith('.github/workflows/'):
                file_type = 'workflow'
            else:
                file_type = 'config'
        elif file_path.endswith('.md'):
            file_type = 'doc'
        elif file_path.endswith('.py'):
            file_type = 'script'
        else:
            file_type = 'other'
        
        # 确定类别
        if 'controlplane/' in file_path:
            category = 'controlplane'
        elif 'workspace/' in file_path:
            category = 'workspace'
        elif '.github/' in file_path:
            category = 'automation'
        else:
            category = 'root'
        
        # 确定优先级
        priority_map = {
            'config': 100,
            'spec': 90,
            'registry': 95,
            'workflow': 80,
            'doc': 50,
            'script': 70
        }
        priority = priority_map.get(file_type, 30)
        
        # 提取实体和关系
        entities = []
        relationships = []
        dependencies = []
        
        try:
            content = full_path.read_text(encoding="utf-8")
            
            # 提取URN引用 - 使用更精确的模式匹配平台规范
            # Pattern: urn:axiom:module:<name>:<version>
            urns = re.findall(r'urn:axiom:(?:module|device|namespace):[a-zA-Z0-9_-]+:[a-zA-Z0-9._-]+', content)
            entities.extend(urns)
            
            # 提取模块名
            modules = re.findall(r'\b[A-Za-z][A-Za-z0-9_-]+\.(?:yaml|yml|py|md)\b', content)
            entities.extend(modules)
            
            # 提取依赖关系
            dependencies = self._extract_dependencies(content, file_path)
            
            # 分析依赖关系
            if file_type in ['config', 'spec']:
                for entity in entities:
                    if entity != file_path:
                        relationships.append({
                            'type': 'depends_on',
                            'target': entity,
                            'strength': 'strong' if entity.startswith('urn:') else 'weak'
                        })
            
        except (OSError, UnicodeDecodeError):
            pass
        
        # 确定影响级别
        impact_map = {
            'config': 'high',
            'spec': 'high',
            'registry': 'high',
            'workflow': 'medium',
            'doc': 'low'
        }
        impact_level = impact_map.get(file_type, 'low')
        
        return FileAnalysis(
            path=file_path,
            type=file_type,
            category=category,
            priority=priority,
            dependencies=dependencies,  # Now properly populated
            impact_level=impact_level,
            content_hash=self._get_file_hash(full_path),
            entities=list(set(entities)),
            relationships=relationships
        )

    def _get_changed_files(self) -> Dict[str, Any]:
        """获取变更文件信息"""
        result = self._run([
            "git", "log", "-1", "--name-status", "--pretty=format:%H%n%an%n%s"
        ])
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        
        if len(lines) < 3:
            return {
                "sha": "", "author": "", "subject": "", 
                "files": [], "added": 0, "modified": 0, "deleted": 0
            }
        
        sha, author, subject = lines[0], lines[1], lines[2]
        files_info = []
        
        for line in lines[3:]:
            # Fixed: Use proper tab separator
            parts = line.split("\t")
            if len(parts) >= 2:
                status, file_path = parts[0], parts[1]
                files_info.append((status, file_path))
        
        # Fixed: Return actual subject instead of hardcoded "subject"
        return {
            "sha": sha, "author": author, "subject": subject,
            "files": files_info, "added": 0, "modified": 0, "deleted": 0
        }

    def _analyze_changes(self) -> ChangeAnalysis:
        """分析变更"""
        files_info = self._get_changed_files()
        timestamp = self._now()
        
        added = []
        modified = []
        deleted = []
        
        high_impact_count = 0
        
        for status, file_path in files_info["files"]:
            if status.startswith("A"):
                analysis = self._analyze_file(file_path)
                added.append(analysis)
                if analysis.impact_level == 'high':
                    high_impact_count += 1
            elif status.startswith("M"):
                analysis = self._analyze_file(file_path)
                modified.append(analysis)
                if analysis.impact_level == 'high':
                    high_impact_count += 1
            elif status.startswith("D"):
                deleted.append(file_path)
        
        # 确定总体影响级别
        if high_impact_count >= 3:
            total_impact = "critical"
        elif high_impact_count >= 1:
            total_impact = "high"
        elif len(added) + len(modified) >= 5:
            total_impact = "medium"
        else:
            total_impact = "low"
        
        return ChangeAnalysis(
            sha=files_info["sha"],
            author=files_info["author"],
            subject=files_info["subject"],
            timestamp=timestamp,
            added=added,
            modified=modified,
            deleted=deleted,
            total_impact=total_impact
        )

    def _deduplicate_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重关系 - 保留最新的关系记录"""
        # Use (source, target, type) as key, keep latest by timestamp
        rel_dict = {}
        for rel in relationships:
            key = (rel["source"], rel["target"], rel["type"])
            if key not in rel_dict or rel["timestamp"] > rel_dict[key]["timestamp"]:
                rel_dict[key] = rel
        
        return list(rel_dict.values())

    def _update_knowledge_graph(self, analysis: ChangeAnalysis) -> None:
        """更新知识图谱"""
        # 加载现有图谱
        graph = {"entities": {}, "relationships": [], "last_updated": ""}
        
        if self.knowledge_graph_path.exists():
            try:
                graph = json.loads(self.knowledge_graph_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        # 更新实体
        for file_analysis in analysis.added + analysis.modified:
            entity_id = file_analysis.path
            graph["entities"][entity_id] = {
                "type": file_analysis.type,
                "category": file_analysis.category,
                "priority": file_analysis.priority,
                "impact_level": file_analysis.impact_level,
                "last_modified": analysis.timestamp,
                "content_hash": file_analysis.content_hash,
                "entities": file_analysis.entities,
                "dependencies": file_analysis.dependencies
            }
        
        # 更新关系
        for file_analysis in analysis.added + analysis.modified:
            for relationship in file_analysis.relationships:
                rel = {
                    "source": file_analysis.path,
                    "target": relationship["target"],
                    "type": relationship["type"],
                    "strength": relationship["strength"],
                    "timestamp": analysis.timestamp
                }
                graph["relationships"].append(rel)
        
        # 去重关系
        graph["relationships"] = self._deduplicate_relationships(graph["relationships"])
        
        # 清理删除的实体
        for deleted_file in analysis.deleted:
            if deleted_file in graph["entities"]:
                del graph["entities"][deleted_file]
            graph["relationships"] = [
                rel for rel in graph["relationships"] 
                if rel["source"] != deleted_file and rel["target"] != deleted_file
            ]
        
        graph["last_updated"] = analysis.timestamp
        
        # 确保目录存在
        self.knowledge_graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存图谱
        self.knowledge_graph_path.write_text(
            json.dumps(graph, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )

    def _generate_insights(self, analysis: ChangeAnalysis) -> List[str]:
        """生成智能洞察"""
        insights = []
        
        # 分析变更模式
        total_changes = len(analysis.added) + len(analysis.modified)
        
        if total_changes >= 10:
            insights.append(f"🔄 大规模变更：本次提交包含 {total_changes} 个文件变更")
        
        # 分析配置变更
        config_changes = [f for f in analysis.added + analysis.modified if f.type == 'config']
        if config_changes:
            insights.append(f"⚙️ 配置变更：{len(config_changes)} 个配置文件被修改")
            
            # 检查关键配置
            critical_configs = [f for f in config_changes if 'root.' in f.path]
            if critical_configs:
                insights.append(f"🔧 根配置变更：{len(critical_configs)} 个根配置文件被影响")
        
        # 分析规范变更
        spec_changes = [f for f in analysis.added + analysis.modified if f.type == 'spec']
        if spec_changes:
            insights.append(f"📋 规范变更：{len(spec_changes)} 个规范文件被更新")
        
        # 分析依赖关系
        all_relationships = []
        for file_analysis in analysis.added + analysis.modified:
            all_relationships.extend(file_analysis.relationships)
        
        if all_relationships:
            strong_deps = [r for r in all_relationships if r.get('strength') == 'strong']
            if strong_deps:
                insights.append(f"🔗 强依赖：发现 {len(strong_deps)} 个强依赖关系")
        
        # 影响评估
        if analysis.total_impact == 'critical':
            insights.append("🚨 关键影响：本次变更可能影响系统核心功能")
        elif analysis.total_impact == 'high':
            insights.append("⚠️ 高影响：建议进行充分测试")
        
        return insights

    def _enhanced_memory_body(self, analysis: ChangeAnalysis) -> str:
        """生成增强的记忆内容"""
        insights = self._generate_insights(analysis)
        
        sections = [
            f"### 🧠 增强记忆更新 ({analysis.timestamp})",
            f"**变更影响级别**: {analysis.total_impact.upper()}",
            f"**Commit**: {analysis.sha} ({analysis.subject})",
            f"**作者**: {analysis.author}",
            "",
            "**📊 变更统计**:",
            f"- 新增文件: {len(analysis.added)}",
            f"- 修改文件: {len(analysis.modified)}",
            f"- 删除文件: {len(analysis.deleted)}",
            ""
        ]
        
        # 添加智能洞察
        if insights:
            sections.append("**🔍 智能洞察**:")
            for insight in insights:
                sections.append(f"- {insight}")
            sections.append("")
        
        # 添加高优先级变更详情
        high_priority_changes = [
            f for f in analysis.added + analysis.modified 
            if f.priority >= 90
        ]
        
        if high_priority_changes:
            sections.append("**⚡ 高优先级变更**:")
            for file_analysis in high_priority_changes[:5]:
                sections.append(f"- `{file_analysis.path}` ({file_analysis.type}, 影响级别: {file_analysis.impact_level})")
            
            if len(high_priority_changes) > 5:
                sections.append(f"- ... 还有 {len(high_priority_changes) - 5} 个高优先级变更")
            sections.append("")
        
        # 添加实体关系摘要
        all_entities = set()
        for file_analysis in analysis.added + analysis.modified:
            all_entities.update(file_analysis.entities)
        
        if all_entities:
            sections.append("**🏷️ 相关实体**:")
            entities_list = sorted(list(all_entities))[:10]
            for entity in entities_list:
                sections.append(f"- `{entity}`")
            
            if len(all_entities) > 10:
                sections.append(f"- ... 还有 {len(all_entities) - 10} 个实体")
            sections.append("")
        
        # 添加知识图谱统计
        if self.knowledge_graph_path.exists():
            try:
                graph = json.loads(self.knowledge_graph_path.read_text(encoding="utf-8"))
                sections.append("**📊 知识图谱统计**:")
                sections.append(f"- 实体总数: {len(graph.get('entities', {}))}")
                sections.append(f"- 关系总数: {len(graph.get('relationships', []))}")
                sections.append(f"- 最后更新: {graph.get('last_updated', '未知')}")
                sections.append("")
            except:
                pass
        
        return "\n".join(sections)

    def _update_section(self, path: Path, start: str, end: str, body: str) -> bool:
        """更新文档片段 - 改进的正则替换逻辑"""
        try:
            # Ensure path exists
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            
            content = path.read_text(encoding="utf-8")
            block = f"{start}\n{body}\n{end}"
            
            if start in content and end in content:
                # Use non-greedy match with anchored markers
                pattern = rf"{re.escape(start)}.*?{re.escape(end)}"
                new_content = re.sub(
                    pattern,
                    block,
                    content,
                    count=1,  # Only replace first occurrence
                    flags=re.DOTALL,
                )
            else:
                new_content = f"{block}\n\n{content}"
            
            if new_content != content:
                path.write_text(new_content, encoding="utf-8")
                return True
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Failed to update {path}: {e}")
        
        return False

    def sync_memory(self) -> bool:
        """执行记忆同步"""
        analysis = self._analyze_changes()
        
        # 更新知识图谱
        self._update_knowledge_graph(analysis)
        
        # 更新记忆文件
        project_memory = self.repo_root / "controlplane/governance/docs/PROJECT_MEMORY.md"
        conversation_log = self.repo_root / "workspace/projects/CONVERSATION_LOG.md"
        
        updated = False
        
        # 更新项目记忆
        enhanced_body = self._enhanced_memory_body(analysis)
        updated |= self._update_section(
            project_memory,
            "<!-- AUTO-MEMORY-UPDATE:START -->",
            "<!-- AUTO-MEMORY-UPDATE:END -->",
            enhanced_body,
        )
        
        # 更新对话记录
        conversation_body = "\n".join([
            f"### {analysis.timestamp} - 增强记忆更新",
            f"- 目标: 智能分析变更并更新知识图谱",
            f"- 影响: {analysis.total_impact}",
            f"- 实体识别: {len(set().union(*[f.entities for f in analysis.added + analysis.modified]))}",
            f"- 关系发现: {sum(len(f.relationships) for f in analysis.added + analysis.modified)}",
        ])
        
        updated |= self._update_section(
            conversation_log,
            "<!-- AUTO-CONVERSATION-LOG:START -->",
            "<!-- AUTO-CONVERSATION-LOG:END -->",
            conversation_body,
        )
        
        if updated:
            print("Enhanced memory synchronization completed.")
            print(f"Knowledge graph updated: {len(analysis.added + analysis.modified)} files analyzed")
        else:
            print("No memory updates required.")
        
        return updated


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
    
    sync = EnhancedMemorySync(repo_root)
    sync.sync_memory()


if __name__ == "__main__":
    main()