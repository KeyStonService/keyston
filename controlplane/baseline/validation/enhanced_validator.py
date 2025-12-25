#!/usr/bin/env python3

"""
Enhanced Root Layer Validator
增强根层验证器 - 包含跨文件一致性检查、智能修复建议、新增文件验证
"""

from __future__ import annotations

import os
import sys
import yaml
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


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
            workspace_root = os.environ.get("MACHINENATIVEOPS_WORKSPACE")
        if workspace_root is None:
            workspace_root = Path(__file__).resolve().parents[3]
        
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
        """计算文件哈希"""
        try:
            content = path.read_text(encoding='utf-8')
            return hashlib.sha256(content.encode()).hexdigest()
        except (OSError, UnicodeDecodeError):
            return "unavailable"
    
    def validate_schema_compliance(self) -> List[ValidationIssue]:
        """验证模式合规性"""
        issues = []
        
        # 定义各类型文件的模式
        schemas = self._load_validation_schemas()
        
        for file_path in self.config_root.glob("root.*.yaml"):
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
        
        # 检查时间戳一致性
        timestamps = {}
        for file_name, config_info in all_configs.items():
            content = config_info["content"]
            timestamp_fields = ["created", "updated", "last_modified"]
            for field in timestamp_fields:
                if field in content:
                    timestamps[f"{file_name}:{field}"] = content[field]
        
        # 检查命名规范一致性
        naming_patterns = {}
        for spec_file in self.specs_root.glob("root.specs.*.yaml"):
            content = self._load_yaml(spec_file)
            if content and "patterns" in content:
                naming_patterns[spec_file.name] = content["patterns"]
        
        # 验证实际文件名是否符合命名规范
        for config_file in self.config_root.glob("root.*.yaml"):
            file_name = config_file.name
            if "naming" in naming_patterns:
                patterns = naming_patterns["naming"].get("file_patterns", {})
                for pattern_name, pattern_regex in patterns.items():
                    if not re.match(pattern_regex, file_name):
                        issues.append(ValidationIssue(
                            severity="medium",
                            category="consistency",
                            file_path=str(config_file.relative_to(self.workspace_root)),
                            line_number=None,
                            message=f"文件名不符合命名规范: {pattern_name}",
                            suggestion=f"将文件名修改为符合模式的格式",
                            auto_fixable=False,
                            related_files=["controlplane/baseline/specifications/root.specs.naming.yaml"]
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
        
        # 检查文件内部引用
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
        
        # 收集所有配置文件
        config_files = list(self.config_root.glob("root.*.yaml"))
        spec_files = list(self.specs_root.glob("root.specs.*.yaml"))
        registry_files = list(self.registry_root.glob("root.registry.*.yaml"))
        
        all_files.update([f.name for f in config_files])
        all_files.update([f.name for f in spec_files])
        all_files.update([f.name for f in registry_files])
        
        # 分析依赖关系
        for file_path in config_files + spec_files + registry_files:
            content = self._load_yaml(file_path)
            if content:
                file_name = file_path.name
                dependencies = self._extract_dependencies(content)
                
                for dep in dependencies:
                    if dep in all_files:
                        dependency_graph[file_name].add(dep)
        
        # 检查循环依赖
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for file_name in all_files:
            if file_name not in visited:
                if has_cycle(file_name):
                    issues.append(ValidationIssue(
                        severity="high",
                        category="dependency",
                        file_path=file_name,
                        line_number=None,
                        message=f"检测到循环依赖，涉及文件: {file_name}",
                        suggestion="重构依赖关系以消除循环",
                        auto_fixable=False,
                        related_files=list(dependency_graph[file_name])
                    ))
        
        # 检查缺失的依赖
        for file_name, deps in dependency_graph.items():
            for dep in deps:
                if dep not in all_files:
                    issues.append(ValidationIssue(
                        severity="medium",
                        category="dependency",
                        file_path=file_name,
                        line_number=None,
                        message=f"依赖的文件不存在: {dep}",
                        suggestion=f"创建缺失的文件或移除依赖",
                        auto_fixable=False,
                        related_files=[dep]
                    ))
        
        return issues
    
    def validate_new_files(self) -> List[ValidationIssue]:
        """验证新增文件"""
        issues = []
        
        # 验证新增的规范文件
        new_spec_files = [
            "root.specs.namespace.yaml",
            "root.specs.paths.yaml", 
            "root.specs.urn.yaml"
        ]
        
        for spec_file in new_spec_files:
            spec_path = self.specs_root / spec_file
            if spec_path.exists():
                content = self._load_yaml(spec_path)
                if not content:
                    continue
                
                # 验证namespace规范
                if "namespace" in spec_file:
                    required_fields = ["namespaces", "hierarchy", "validation_rules"]
                    for field in required_fields:
                        if field not in content:
                            issues.append(ValidationIssue(
                                severity="high",
                                category="schema",
                                file_path=str(spec_path.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"namespace规范缺少必需字段: {field}",
                                suggestion=f"添加 {field} 定义",
                                auto_fixable=True,
                                related_files=[]
                            ))
                
                # 验证paths规范
                elif "paths" in spec_file:
                    required_fields = ["path_patterns", "validation_rules", "mapping_rules"]
                    for field in required_fields:
                        if field not in content:
                            issues.append(ValidationIssue(
                                severity="high",
                                category="schema",
                                file_path=str(spec_path.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"paths规范缺少必需字段: {field}",
                                suggestion=f"添加 {field} 定义",
                                auto_fixable=True,
                                related_files=[]
                            ))
                
                # 验证URN规范
                elif "urn" in spec_file:
                    required_fields = ["urn_format", "namespace_rules", "validation_rules"]
                    for field in required_fields:
                        if field not in content:
                            issues.append(ValidationIssue(
                                severity="high",
                                category="schema",
                                file_path=str(spec_path.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"URN规范缺少必需字段: {field}",
                                suggestion=f"添加 {field} 定义",
                                auto_fixable=True,
                                related_files=[]
                            ))
        
        # 验证新增的注册表文件
        new_registry_files = [
            "root.registry.devices.yaml",
            "root.registry.namespaces.yaml"
        ]
        
        for registry_file in new_registry_files:
            registry_path = self.registry_root / registry_file
            if registry_path.exists():
                content = self._load_yaml(registry_path)
                if not content:
                    continue
                
                # 验证注册表结构
                if "entries" not in content:
                    issues.append(ValidationIssue(
                        severity="high",
                        category="schema",
                        file_path=str(registry_path.relative_to(self.workspace_root)),
                        line_number=None,
                        message="注册表文件缺少entries字段",
                        suggestion="添加entries数组定义",
                        auto_fixable=True,
                        related_files=[]
                    ))
                else:
                    entries = content["entries"]
                    if not isinstance(entries, list):
                        issues.append(ValidationIssue(
                            severity="high",
                            category="schema",
                            file_path=str(registry_path.relative_to(self.workspace_root)),
                            line_number=None,
                            message="entries字段必须是数组类型",
                            suggestion="将entries改为数组格式",
                            auto_fixable=True,
                            related_files=[]
                        ))
                    else:
                        for i, entry in enumerate(entries):
                            if not isinstance(entry, dict):
                                issues.append(ValidationIssue(
                                    severity="medium",
                                    category="schema",
                                    file_path=str(registry_path.relative_to(self.workspace_root)),
                                    line_number=None,
                                    message=f"entries[{i}] 必须是对象类型",
                                    suggestion="将条目改为对象格式",
                                    auto_fixable=True,
                                    related_files=[]
                                ))
        
        # 验证gates.map.yaml
        gates_file = self.config_root / "gates.map.yaml"
        if gates_file.exists():
            content = self._load_yaml(gates_file)
            if content:
                # 验证必需字段
                required_fields = ["version", "gates", "execution_order"]
                for field in required_fields:
                    if field not in content:
                        issues.append(ValidationIssue(
                            severity="high",
                            category="schema",
                            file_path=str(gates_file.relative_to(self.workspace_root)),
                            line_number=None,
                            message=f"gates.map.yaml缺少必需字段: {field}",
                            suggestion=f"添加 {field} 定义",
                            auto_fixable=True,
                            related_files=[]
                        ))
                
                # 验证gate定义
                if "gates" in content:
                    gates = content["gates"]
                    for gate_name, gate_config in gates.items():
                        if not isinstance(gate_config, dict):
                            issues.append(ValidationIssue(
                                severity="medium",
                                category="schema",
                                file_path=str(gates_file.relative_to(self.workspace_root)),
                                line_number=None,
                                message=f"gate '{gate_name}' 配置必须是对象类型",
                                suggestion="将gate配置改为对象格式",
                                auto_fixable=True,
                                related_files=[]
                            ))
                        else:
                            required_gate_fields = ["enabled", "description"]
                            for field in required_gate_fields:
                                if field not in gate_config:
                                    issues.append(ValidationIssue(
                                        severity="medium",
                                        category="schema",
                                        file_path=str(gates_file.relative_to(self.workspace_root)),
                                        line_number=None,
                                        message=f"gate '{gate_name}' 缺少必需字段: {field}",
                                        suggestion=f"添加 {field} 定义",
                                        auto_fixable=True,
                                        related_files=[]
                                    ))
        
        return issues
    
    def calculate_file_metrics(self) -> Dict[str, FileMetrics]:
        """计算文件指标"""
        metrics = {}
        
        all_files = []
        all_files.extend(self.config_root.glob("root.*.yaml"))
        all_files.extend(self.specs_root.glob("root.specs.*.yaml"))
        all_files.extend(self.registry_root.glob("root.registry.*.yaml"))
        
        for file_path in all_files:
            content = self._load_yaml(file_path)
            if not content:
                continue
            
            file_size_kb = file_path.stat().st_size / 1024
            entity_count = len(self._extract_entities(content))
            reference_count = len(self._extract_urns(content)) + len(self._extract_file_references(content))
            dependency_count = len(self._extract_dependencies(content))
            
            # 计算复杂度分数
            complexity_score = self._calculate_complexity(content)
            
            # 计算质量分数
            quality_score = self._calculate_quality_score(content, file_path.name)
            
            metrics[str(file_path.relative_to(self.workspace_root))] = FileMetrics(
                file_path=str(file_path.relative_to(self.workspace_root)),
                file_type=self._determine_file_type(file_path.name),
                size_kb=round(file_size_kb, 2),
                entity_count=entity_count,
                reference_count=reference_count,
                dependency_count=dependency_count,
                complexity_score=complexity_score,
                quality_score=quality_score
            )
        
        return metrics
    
    def generate_enhanced_report(self) -> str:
        """生成增强报告"""
        issues = []
        
        # 执行所有验证
        issues.extend(self.validate_schema_compliance())
        issues.extend(self.validate_cross_file_consistency())
        issues.extend(self.validate_reference_integrity())
        issues.extend(self.validate_dependency_graph())
        issues.extend(self.validate_new_files())
        
        # 计算指标
        metrics = self.calculate_file_metrics()
        
        # 更新结果
        self.results["issues"] = [asdict(issue) for issue in issues]
        self.results["metrics"] = {k: asdict(v) for k, v in metrics.items()}
        
        # 统计
        self.results["summary"]["total_checks"] = len(issues)
        self.results["summary"]["failed"] = len([i for i in issues if i["severity"] in ["critical", "high"]])
        self.results["summary"]["warnings"] = len([i for i in issues if i["severity"] == "medium"])
        self.results["summary"]["info"] = len([i for i in issues if i["severity"] in ["low", "info"]])
        self.results["summary"]["passed"] = max(0, len(issues) - self.results["summary"]["failed"])
        
        # 判断是否通过
        self.results["pass"] = self.results["summary"]["failed"] == 0
        
        # 生成报告内容
        report_lines = [
            f"# Enhanced Root Layer Validation Report",
            f"**Validation ID**: {self.results['validation_id']}",
            f"**Timestamp**: {self.results['timestamp']}",
            f"**Workspace**: {self.results['workspace']}",
            "",
            "## 📊 Summary",
            f"- **Total Checks**: {self.results['summary']['total_checks']}",
            f"- **Passed**: {self.results['summary']['passed']}",
            f"- **Failed**: {self.results['summary']['failed']}",
            f"- **Warnings**: {self.results['summary']['warnings']}",
            f"- **Info**: {self.results['summary']['info']}",
            f"- **Status**: {'✅ PASSED' if self.results['pass'] else '❌ FAILED'}",
            "",
            "## 🚨 Critical & High Issues"
        ]
        
        critical_high_issues = [i for i in issues if i["severity"] in ["critical", "high"]]
        if critical_high_issues:
            for issue in critical_high_issues:
                report_lines.extend([
                    f"### {issue['severity'].upper()}: {issue['message']}",
                    f"- **File**: `{issue['file_path']}`",
                    f"- **Category**: {issue['category']}",
                    f"- **Suggestion**: {issue['suggestion'] or 'No suggestion available'}",
                    f"- **Auto-fixable**: {'Yes' if issue['auto_fixable'] else 'No'}",
                    ""
                ])
        else:
            report_lines.append("✅ No critical or high issues found!")
        
        report_lines.extend([
            "",
            "## ⚠️ Medium Issues"
        ])
        
        medium_issues = [i for i in issues if i["severity"] == "medium"]
        if medium_issues:
            for issue in medium_issues:
                report_lines.extend([
                    f"### {issue['message']}",
                    f"- **File**: `{issue['file_path']}`",
                    f"- **Category**: {issue['category']}",
                    f"- **Suggestion**: {issue['suggestion'] or 'No suggestion available'}",
                    ""
                ])
        else:
            report_lines.append("✅ No medium issues found!")
        
        report_lines.extend([
            "",
            "## 📈 File Metrics",
            ""
        ])
        
        # 按质量分数排序
        sorted_metrics = sorted(metrics.items(), key=lambda x: x[1].quality_score, reverse=True)
        
        for file_path, metric in sorted_metrics:
            status = "🟢" if metric.quality_score >= 90 else "🟡" if metric.quality_score >= 70 else "🔴"
            report_lines.extend([
                f"{status} **{metric.file_path}** ({metric.file_type})",
                f"- Quality Score: {metric.quality_score}/100",
                f"- Size: {metric.size_kb} KB",
                f"- Entities: {metric.entity_count}",
                f"- References: {metric.reference_count}",
                f"- Dependencies: {metric.dependency_count}",
                f"- Complexity: {metric.complexity_score}",
                ""
            ])
        
        report_lines.extend([
            "",
            "## 🔧 Auto-fixable Issues",
            ""
        ])
        
        auto_fixable_issues = [i for i in issues if i["auto_fixable"]]
        if auto_fixable_issues:
            for issue in auto_fixable_issues:
                report_lines.extend([
                    f"- `{issue['file_path']}`: {issue['message']}",
                    f"  **Fix**: {issue['suggestion']}",
                    ""
                ])
        else:
            report_lines.append("✅ No auto-fixable issues found!")
        
        return "\n".join(report_lines)
    
    def save_results(self) -> None:
        """保存验证结果"""
        # 保存Markdown报告
        report_content = self.generate_enhanced_report()
        report_path = self.evidence_root / "enhanced_validation_report.md"
        report_path.write_text(report_content, encoding="utf-8")
        
        # 保存JSON结果
        json_path = self.evidence_root / "enhanced_validation_results.json"
        json_path.write_text(
            json.dumps(self.results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        print(f"Enhanced validation report saved: {report_path}")
        print(f"Enhanced validation results saved: {json_path}")
    
    # 辅助方法
    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """加载验证模式"""
        return {
            "config": {
                "required_fields": ["version"],
                "fields": {
                    "version": {"type": "string"},
                    "created": {"type": "string"},
                    "updated": {"type": "string"}
                }
            },
            "spec": {
                "required_fields": ["version", "rules"],
                "fields": {
                    "version": {"type": "string"},
                    "rules": {"type": "array"}
                }
            },
            "registry": {
                "required_fields": ["version", "entries"],
                "fields": {
                    "version": {"type": "string"},
                    "entries": {"type": "array"}
                }
            }
        }
    
    def _determine_file_type(self, filename: str) -> str:
        """确定文件类型"""
        if "config" in filename or filename.startswith("root.") and not any(x in filename for x in ["specs.", "registry.", "gates."]):
            return "config"
        elif "specs." in filename:
            return "spec"
        elif "registry." in filename:
            return "registry"
        elif "gates." in filename:
            return "gates"
        else:
            return "other"
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """验证字段类型"""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        expected_python_type = type_map.get(expected_type)
        return expected_python_type and isinstance(value, expected_python_type)
    
    def _extract_urns(self, content: Dict[str, Any]) -> Set[str]:
        """提取URN引用"""
        urns = set()
        content_str = json.dumps(content, ensure_ascii=False)
        urn_pattern = r'urn:[:\w\-.]+'
        urns.update(re.findall(urn_pattern, content_str))
        return urns
    
    def _extract_file_references(self, content: Dict[str, Any]) -> Set[str]:
        """提取文件引用"""
        references = set()
        content_str = json.dumps(content, ensure_ascii=False)
        
        # 匹配文件路径模式
        file_patterns = [
            r'[\w\-./]+\.(yaml|yml|md|py|sh)',
            r'controlplane/[\w\-./]+',
            r'workspace/[\w\-./]+'
        ]
        
        for pattern in file_patterns:
            references.update(re.findall(pattern, content_str))
        
        return references
    
    def _extract_dependencies(self, content: Dict[str, Any]) -> Set[str]:
        """提取依赖关系"""
        dependencies = set()
        
        # 从depends_on字段提取
        if "depends_on" in content:
            if isinstance(content["depends_on"], list):
                dependencies.update(content["depends_on"])
            elif isinstance(content["depends_on"], str):
                dependencies.add(content["depends_on"])
        
        # 从imports字段提取
        if "imports" in content:
            if isinstance(content["imports"], list):
                dependencies.update(content["imports"])
        
        return dependencies
    
    def _extract_entities(self, content: Dict[str, Any]) -> Set[str]:
        """提取实体"""
        entities = set()
        
        # 提取键名
        entities.update(content.keys())
        
        # 递归提取嵌套实体
        def extract_nested(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    entities.add(key)
                    extract_nested(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_nested(item)
        
        extract_nested(content)
        return entities
    
    def _calculate_complexity(self, content: Dict[str, Any]) -> int:
        """计算复杂度分数"""
        complexity = 0
        
        # 基于嵌套深度
        def calculate_depth(obj, current_depth=0):
            if isinstance(obj, dict):
                return max([calculate_depth(v, current_depth + 1) for v in obj.values()])
            elif isinstance(obj, list):
                return max([calculate_depth(item, current_depth + 1) for item in obj])
            else:
                return current_depth
        
        depth = calculate_depth(content)
        complexity += depth * 10
        
        # 基于对象数量
        def count_objects(obj):
            if isinstance(obj, dict):
                return 1 + sum(count_objects(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_objects(item) for item in obj)
            else:
                return 0
        
        object_count = count_objects(content)
        complexity += object_count * 5
        
        # 基于数组长度
        def count_array_items(obj):
            if isinstance(obj, list):
                return len(obj) + sum(count_array_items(item) for item in obj)
            elif isinstance(obj, dict):
                return sum(count_array_items(v) for v in obj.values())
            else:
                return 0
        
        array_items = count_array_items(content)
        complexity += array_items * 2
        
        return min(complexity, 100)  # 限制最大值
    
    def _calculate_quality_score(self, content: Dict[str, Any], filename: str) -> int:
        """计算质量分数"""
        score = 100
        
        # 检查必需字段
        required_fields = ["version"]
        for field in required_fields:
            if field not in content:
                score -= 20
        
        # 检查文档完整性
        doc_fields = ["description", "created", "updated"]
        for field in doc_fields:
            if field not in content:
                score -= 5
        
        # 检查命名规范
        if not self._validate_naming_convention(filename, content):
            score -= 10
        
        # 检查数据完整性
        if not self._validate_data_integrity(content):
            score -= 15
        
        return max(score, 0)
    
    def _validate_naming_convention(self, filename: str, content: Dict[str, Any]) -> bool:
        """验证命名规范"""
        # 简单的命名规范检查
        if filename.startswith("root."):
            return True
        return False
    
    def _validate_data_integrity(self, content: Dict[str, Any]) -> bool:
        """验证数据完整性"""
        # 检查是否有空值
        def check_empty(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if value is None or value == "":
                        return False
                    if not check_empty(value):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not check_empty(item):
                        return False
            return True
        
        return check_empty(content)
    
    def _find_registry_files_for_urn(self, urn: str) -> List[str]:
        """查找URN对应的注册表文件"""
        related_files = []
        
        for registry_file in self.registry_root.glob("root.registry.*.yaml"):
            content = self._load_yaml(registry_file)
            if content and "entries" in content:
                for entry in content["entries"]:
                    if entry.get("urn") == urn:
                        related_files.append(str(registry_file.relative_to(self.workspace_root)))
                        break
        
        return related_files


def main():
    """主函数"""
    validator = EnhancedRootValidator()
    validator.save_results()
    
    # 输出结果摘要
    print(f"\n=== Enhanced Validation Summary ===")
    print(f"Total Checks: {validator.results['summary']['total_checks']}")
    print(f"Passed: {validator.results['summary']['passed']}")
    print(f"Failed: {validator.results['summary']['failed']}")
    print(f"Warnings: {validator.results['summary']['warnings']}")
    print(f"Status: {'PASSED' if validator.results['pass'] else 'FAILED'}")
    
    return 0 if validator.results['pass'] else 1


if __name__ == "__main__":
    sys.exit(main())