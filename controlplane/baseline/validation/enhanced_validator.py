#!/usr/bin/env python3

"""
Enhanced Root Layer Validator
增强根层验证器 - 包含跨文件一致性检查、智能修复建议、新增文件验证
"""

from __future__ import annotations

import sys
import yaml
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
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
class ValidationIssue:
    """验证问题"""
    severity: str  # critical, high, medium, low, info
    category: str  # schema, consistency, reference, dependency, best_practice
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: Optional[str]
    auto_fixable: bool
    related_files: List[str]


@dataclass
class FileMetrics:
    """文件指标"""
    file_path: str
    file_type: str
    size_kb: float
    entity_count: int
    reference_count: int
    dependency_count: int
    complexity_score: int
    quality_score: int


class EnhancedRootValidator:
    """增强根层验证器"""
    
    def __init__(self, workspace_root: str = None):
        if workspace_root is None:
            workspace_root = self._get_repo_root()
        
        self.workspace_root = Path(workspace_root)
        self.baseline_root = self.workspace_root / "controlplane" / "baseline"
        self.overlay_root = self.workspace_root / "controlplane" / "overlay"
        self.evidence_root = self.overlay_root / "evidence" / "validation"
        self.registry_root = self.baseline_root / "registries"
        self.specs_root = self.baseline_root / "specifications"
        self.config_root = self.baseline_root / "config"
        
        self.results = {
            "validation_id": self._generate_validation_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "workspace": str(self.workspace_root),
            "stages": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "info": 0
            },
            "issues": [],
            "metrics": {},
            "pass": False
        }
        
        # 确保证据目录存在
        self.evidence_root.mkdir(parents=True, exist_ok=True)
    
    def _get_repo_root(self) -> Path:
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
            # Fallback to environment variable or relative path
            import os
            workspace = os.environ.get("MACHINENATIVEOPS_WORKSPACE")
            if workspace:
                return Path(workspace)
            return Path(__file__).resolve().parents[3]
    
    def _generate_validation_id(self) -> str:
        """生成验证ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"enhanced_validation_{timestamp}"
    
    def _load_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """安全加载YAML文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, FileNotFoundError, UnicodeDecodeError) as e:
            return None
    
    def _calculate_file_hash(self, path: Path) -> str:
        """计算文件哈希 - 使用 sha3-512 符合治理规范"""
        try:
            content = path.read_text(encoding='utf-8')
            if HASH_ALGO == 'sha3_512':
                return hashlib.sha3_512(content.encode()).hexdigest()
            else:
                return hashlib.sha256(content.encode()).hexdigest()
        except (OSError, UnicodeDecodeError):
            return "unavailable"
    
    def validate_schema_compliance(self) -> List[ValidationIssue]:
        """验证模式合规性"""
        issues = []
        
        # 定义各类型文件的模式
        schemas = self._load_validation_schemas()
        
        # 扩展验证范围 - 包括 gates.map.yaml 和其他根层文件
        validation_files = list(self.config_root.glob("root.*.yaml"))
        
        # 添加 gates.map.yaml 如果存在
        gates_map = self.config_root / "gates.map.yaml"
        if gates_map.exists():
            validation_files.append(gates_map)
        
        for file_path in validation_files:
            file_type = self._determine_file_type(file_path.name)
            
            if file_type in schemas:
                schema = schemas[file_type]
                content = self._load_yaml(file_path)
                
                if content is None:
                    issues.append(ValidationIssue(
                        severity="critical",
                        category="schema",
                        file_path=str(file_path.relative_to(self.workspace_root)),
                        line_number=None,
                        message="无法解析YAML文件",
                        suggestion="检查YAML语法和文件编码",
                        auto_fixable=False,
                        related_files=[]
                    ))
                    continue
                
                # 验证必需字段
                for required_field in schema.get("required_fields", []):
                    if required_field not in content:
                        issues.append(ValidationIssue(
                            severity="high",
                            category="schema",
                            file_path=str(file_path.relative_to(self.workspace_root)),
                            line_number=None,
                            message=f"缺少必需字段: {required_field}",
                            suggestion=f"添加字段: {required_field}: <value>",
                            auto_fixable=True,
                            related_files=[]
                        ))
                
                # 验证字段类型
                for field_name, field_schema in schema.get("fields", {}).items():
                    if field_name in content:
                        expected_type = field_schema.get("type")
                        actual_value = content[field_name]
                        
                        if not self._validate_field_type(actual_value, expected_type):
                            issues.append(ValidationIssue(
                                severity="medium",
                                category="schema",
                                file_path=str(file_path.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"字段类型不匹配: {field_name} 应为 {expected_type}",
                                suggestion=f"将 {field_name} 的值转换为 {expected_type} 类型",
                                auto_fixable=False,
                                related_files=[]
                            ))
        
        return issues
    
    def validate_cross_file_consistency(self) -> List[ValidationIssue]:
        """验证跨文件一致性"""
        issues = []
        
        # 加载所有配置文件
        all_configs = {}
        for config_file in self.config_root.glob("root.*.yaml"):
            content = self._load_yaml(config_file)
            if content:
                all_configs[config_file.name] = {
                    "path": config_file,
                    "content": content
                }
        
        # 检查版本一致性
        versions = {}
        for file_name, config_info in all_configs.items():
            content = config_info["content"]
            if "version" in content:
                versions[file_name] = content["version"]
        
        if len(set(versions.values())) > 1:
            issues.append(ValidationIssue(
                severity="medium",
                category="consistency",
                file_path="multiple",
                line_number=None,
                message="发现版本不一致",
                suggestion=f"统一所有配置文件的版本号，当前版本: {versions}",
                auto_fixable=True,
                related_files=list(versions.keys())
            ))
        
        # 检查命名规范一致性 - 修复逻辑
        naming_patterns = {}
        for spec_file in self.specs_root.glob("root.specs.*.yaml"):
            content = self._load_yaml(spec_file)
            if content and "patterns" in content:
                # 使用完整文件名作为key，而不是假设有"naming"这个key
                naming_patterns[spec_file.stem] = content["patterns"]
        
        # 验证实际文件名是否符合命名规范
        for config_file in self.config_root.glob("root.*.yaml"):
            file_name = config_file.name
            # 检查所有命名规范
            for spec_name, patterns in naming_patterns.items():
                if "file_patterns" in patterns:
                    for pattern_name, pattern_regex in patterns["file_patterns"].items():
                        if not re.match(pattern_regex, file_name):
                            issues.append(ValidationIssue(
                                severity="low",
                                category="consistency",
                                file_path=str(config_file.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"文件名可能不符合命名规范: {pattern_name}",
                                suggestion=f"检查文件名是否符合模式: {pattern_regex}",
                                auto_fixable=False,
                                related_files=[f"controlplane/baseline/specifications/{spec_name}.yaml"]
                            ))
        
        return issues
    
    def validate_reference_integrity(self) -> List[ValidationIssue]:
        """验证引用完整性"""
        issues = []
        
        # 收集所有可用的URN
        available_urns = set()
        
        # 从注册表收集URN
        for registry_file in self.registry_root.glob("root.registry.*.yaml"):
            content = self._load_yaml(registry_file)
            if content and "entries" in content:
                for entry in content["entries"]:
                    if "urn" in entry:
                        available_urns.add(entry["urn"])
        
        # 检查配置文件中的URN引用
        for config_file in self.config_root.glob("root.*.yaml"):
            content = self._load_yaml(config_file)
            if content:
                referenced_urns = self._extract_urns(content)
                
                for urn in referenced_urns:
                    if urn not in available_urns:
                        issues.append(ValidationIssue(
                            severity="high",
                            category="reference",
                            file_path=str(config_file.relative_to(self.workspace_root)),
                            line_number=None,
                            message=f"引用的URN不存在: {urn}",
                            suggestion=f"在相应的注册表中创建URN条目或检查引用是否正确",
                            auto_fixable=False,
                            related_files=self._find_registry_files_for_urn(urn)
                        ))
        
        # 检查文件内部引用 - 修复regex捕获群组问题
        for config_file in self.config_root.glob("root.*.yaml"):
            content = self._load_yaml(config_file)
            if content:
                file_references = self._extract_file_references(content)
                
                for ref_file in file_references:
                    ref_path = self.workspace_root / ref_file
                    if not ref_path.exists():
                        issues.append(ValidationIssue(
                            severity="medium",
                            category="reference",
                            file_path=str(config_file.relative_to(self.workspace_root)),
                            line_number=None,
                            message=f"引用的文件不存在: {ref_file}",
                            suggestion=f"创建文件 {ref_file} 或修复引用路径",
                            auto_fixable=False,
                            related_files=[ref_file]
                        ))
        
        return issues
    
    def validate_dependency_graph(self) -> List[ValidationIssue]:
        """验证依赖图"""
        issues = []
        
        # 构建依赖图
        dependency_graph = defaultdict(set)
        all_files = set()
        missing_dependencies = defaultdict(set)  # 跟踪缺失的依赖
        
        for config_file in self.config_root.glob("root.*.yaml"):
            file_name = config_file.name
            all_files.add(file_name)
            
            content = self._load_yaml(config_file)
            if content:
                dependencies = self._extract_dependencies(content)
                
                for dep in dependencies:
                    # 添加所有依赖到图中，包括不存在的
                    dependency_graph[file_name].add(dep)
                    
                    # 跟踪缺失的依赖
                    if dep not in all_files:
                        dep_path = self.config_root / dep
                        if not dep_path.exists():
                            missing_dependencies[file_name].add(dep)
        
        # 检查缺失的依赖
        for file_name, missing_deps in missing_dependencies.items():
            for dep in missing_deps:
                issues.append(ValidationIssue(
                    severity="high",
                    category="dependency",
                    file_path=f"controlplane/baseline/config/{file_name}",
                    line_number=None,
                    message=f"依赖的文件不存在: {dep}",
                    suggestion=f"创建文件 {dep} 或移除依赖引用",
                    auto_fixable=False,
                    related_files=[dep]
                ))
        
        # 检查循环依赖
        cycles = self._detect_cycles(dependency_graph)
        for cycle in cycles:
            issues.append(ValidationIssue(
                severity="critical",
                category="dependency",
                file_path="multiple",
                line_number=None,
                message=f"检测到循环依赖: {' -> '.join(cycle)}",
                suggestion="重构依赖关系以消除循环",
                auto_fixable=False,
                related_files=list(cycle)
            ))
        
        return issues
    
    def validate_data_integrity(self) -> List[ValidationIssue]:
        """验证数据完整性 - 改进空值检查逻辑"""
        issues = []
        
        for config_file in self.config_root.glob("root.*.yaml"):
            content = self._load_yaml(config_file)
            if content:
                # 定义必填字段（根据文件类型）
                required_fields = self._get_required_fields(config_file.name)
                
                # 只检查必填字段的空值
                empty_fields = self._find_empty_required_fields(content, required_fields)
                
                if empty_fields:
                    issues.append(ValidationIssue(
                        severity="medium",
                        category="best_practice",
                        file_path=str(config_file.relative_to(self.workspace_root)),
                        line_number=None,
                        message=f"必填字段为空: {', '.join(empty_fields)}",
                        suggestion="为必填字段提供有效值",
                        auto_fixable=False,
                        related_files=[]
                    ))
        
        return issues
    
    def _get_required_fields(self, file_name: str) -> List[str]:
        """获取文件的必填字段列表"""
        # 根据文件类型定义必填字段
        if "config" in file_name:
            return ["version", "metadata"]
        elif "registry" in file_name:
            return ["entries"]
        elif "specs" in file_name:
            return ["patterns"]
        return []
    
    def _find_empty_required_fields(self, data: Any, required_fields: List[str], path: str = "") -> List[str]:
        """查找必填字段中的空值"""
        empty_fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 只检查必填字段
                if key in required_fields:
                    if value is None or (isinstance(value, str) and not value.strip()):
                        empty_fields.append(current_path)
                
                # 递归检查嵌套结构
                if isinstance(value, (dict, list)):
                    nested_empty = self._find_empty_required_fields(value, required_fields, current_path)
                    empty_fields.extend(nested_empty)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, (dict, list)):
                    nested_empty = self._find_empty_required_fields(item, required_fields, current_path)
                    empty_fields.extend(nested_empty)
        
        return empty_fields
    
    def _calculate_complexity(self, data: Any, current_depth: int = 0) -> int:
        """计算数据复杂度 - 修复空集合问题"""
        if current_depth > 10:  # 防止无限递归
            return current_depth
        
        if isinstance(data, dict):
            if not data:  # 空字典
                return current_depth
            return max([self._calculate_complexity(v, current_depth + 1) for v in data.values()])
        elif isinstance(data, list):
            if not data:  # 空列表
                return current_depth
            return max([self._calculate_complexity(item, current_depth + 1) for item in data])
        else:
            return current_depth
    
    def _extract_file_references(self, data: Any) -> List[str]:
        """提取文件引用 - 修复regex捕获群组问题"""
        references = []
        
        def extract_from_value(value):
            if isinstance(value, str):
                # 使用非捕获群组避免返回副档名
                matches = re.findall(r'[\w\-./]+\.(?:yaml|yml|md|py|sh)', value)
                references.extend(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
        
        extract_from_value(data)
        return list(set(references))
    
    def _extract_urns(self, data: Any) -> List[str]:
        """提取URN引用"""
        urns = []
        
        def extract_from_value(value):
            if isinstance(value, str):
                # 使用更精确的URN模式匹配平台规范
                matches = re.findall(r'urn:axiom:(?:module|device|namespace):[a-zA-Z0-9_-]+:[a-zA-Z0-9._-]+', value)
                urns.extend(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
        
        extract_from_value(data)
        return list(set(urns))
    
    def _extract_dependencies(self, data: Any) -> List[str]:
        """提取依赖关系"""
        dependencies = []
        
        # 查找显式依赖声明
        if isinstance(data, dict):
            if "dependencies" in data:
                deps = data["dependencies"]
                if isinstance(deps, list):
                    dependencies.extend(deps)
            
            if "requires" in data:
                reqs = data["requires"]
                if isinstance(reqs, list):
                    dependencies.extend(reqs)
            
            # 递归查找
            for value in data.values():
                if isinstance(value, (dict, list)):
                    dependencies.extend(self._extract_dependencies(value))
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    dependencies.extend(self._extract_dependencies(item))
        
        return list(set(dependencies))
    
    def _detect_cycles(self, graph: Dict[str, set]) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _find_registry_files_for_urn(self, urn: str) -> List[str]:
        """查找URN对应的注册表文件"""
        # 根据URN类型推断可能的注册表文件
        if "module" in urn:
            return ["controlplane/baseline/registries/root.registry.modules.yaml"]
        elif "device" in urn:
            return ["controlplane/baseline/registries/root.registry.devices.yaml"]
        elif "namespace" in urn:
            return ["controlplane/baseline/registries/root.registry.namespaces.yaml"]
        return []
    
    def _determine_file_type(self, file_name: str) -> str:
        """确定文件类型"""
        if "config" in file_name:
            return "config"
        elif "registry" in file_name:
            return "registry"
        elif "specs" in file_name:
            return "spec"
        elif "gates" in file_name:
            return "gates"
        return "unknown"
    
    def _load_validation_schemas(self) -> Dict[str, Dict]:
        """加载验证模式"""
        # 简化的模式定义
        return {
            "config": {
                "required_fields": ["version", "metadata"],
                "fields": {
                    "version": {"type": "string"},
                    "metadata": {"type": "dict"}
                }
            },
            "registry": {
                "required_fields": ["entries"],
                "fields": {
                    "entries": {"type": "list"}
                }
            },
            "spec": {
                "required_fields": ["patterns"],
                "fields": {
                    "patterns": {"type": "dict"}
                }
            },
            "gates": {
                "required_fields": ["gates"],
                "fields": {
                    "gates": {"type": "list"}
                }
            }
        }
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """验证字段类型"""
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True
        
        return isinstance(value, expected_python_type)
    
    def generate_enhanced_report(self, issues: List[ValidationIssue]) -> str:
        """生成增强报告"""
        # 转换为字典以便统计
        issues_dicts = [asdict(issue) for issue in issues]
        
        # 统计
        critical_high_issues = [i for i in issues_dicts if i["severity"] in ["critical", "high"]]
        medium_issues = [i for i in issues_dicts if i["severity"] == "medium"]
        auto_fixable_issues = [i for i in issues_dicts if i["auto_fixable"]]
        
        # 更新summary
        self.results["summary"]["failed"] = len(critical_high_issues)
        self.results["summary"]["warnings"] = len(medium_issues)
        self.results["summary"]["total_checks"] = len(issues_dicts)
        self.results["issues"] = issues_dicts
        
        # 生成报告
        report_lines = [
            "# Enhanced Validation Report",
            f"Validation ID: {self.results['validation_id']}",
            f"Timestamp: {self.results['timestamp']}",
            "",
            "## Summary",
            f"- Total Issues: {len(issues_dicts)}",
            f"- Critical/High: {len(critical_high_issues)}",
            f"- Medium: {len(medium_issues)}",
            f"- Auto-fixable: {len(auto_fixable_issues)}",
            ""
        ]
        
        if critical_high_issues:
            report_lines.extend([
                "## Critical/High Issues",
                ""
            ])
            for issue in critical_high_issues[:10]:
                report_lines.append(f"- [{issue['severity'].upper()}] {issue['file_path']}: {issue['message']}")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        report_path = self.evidence_root / f"{self.results['validation_id']}_report.md"
        report_path.write_text(report_content, encoding="utf-8")
        
        # 保存JSON结果
        json_path = self.evidence_root / f"{self.results['validation_id']}_results.json"
        json_path.write_text(json.dumps(self.results, indent=2), encoding="utf-8")
        
        return str(report_path)
    
    def run_validation(self) -> bool:
        """运行完整验证"""
        all_issues = []
        
        print("Running enhanced validation...")
        
        # 运行各项验证
        print("- Schema compliance...")
        all_issues.extend(self.validate_schema_compliance())
        
        print("- Cross-file consistency...")
        all_issues.extend(self.validate_cross_file_consistency())
        
        print("- Reference integrity...")
        all_issues.extend(self.validate_reference_integrity())
        
        print("- Dependency graph...")
        all_issues.extend(self.validate_dependency_graph())
        
        print("- Data integrity...")
        all_issues.extend(self.validate_data_integrity())
        
        # 生成报告
        report_path = self.generate_enhanced_report(all_issues)
        print(f"\nValidation complete. Report: {report_path}")
        print(f"Total issues: {len(all_issues)}")
        
        # 判断是否通过
        critical_high = [i for i in all_issues if i.severity in ["critical", "high"]]
        self.results["pass"] = len(critical_high) == 0
        
        return self.results["pass"]


def main():
    """主函数"""
    validator = EnhancedRootValidator()
    passed = validator.run_validation()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()