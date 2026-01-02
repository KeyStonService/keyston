#!/usr/bin/env python3
"""
根因分析引擎
Root Cause Analysis Engine

功能：
1. 智能漏洞分類
2. 影響鏈追蹤
3. 風險評分計算
4. 根因識別
"""

import json
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict
from pathlib import Path

class RootCauseType(Enum):
    """根因類型枚舉"""
    LOGIC_ERROR = "邏輯錯誤"
    MISSING_VALIDATION = "缺少驗證"
    UNSAFE_OPERATION = "不安全操作"
    RESOURCE_LEAK = "資源洩漏"
    RACE_CONDITION = "競態條件"
    INJECTION = "注入攻擊"
    CRYPTO_ISSUE = "加密問題"
    AUTH_ISSUE = "認證問題"
    CONFIGURATION = "配置問題"
    DEPENDENCY = "依賴問題"
    CODE_QUALITY = "代碼質量"
    COMPLIANCE = "合規性"
    PERFORMANCE = "性能問題"

@dataclass
class RootCause:
    """根因數據結構"""
    type: str
    description: str
    evidence: str
    confidence: float
    affected_components: List[str]
    impact_chain: List[str]
    risk_score: float
    recommendations: List[str]

class RootCauseAnalyzer:
    """
    根因分析器
    
    智能分析代碼掃描結果，識別漏洞的根本原因、影響鏈和風險評估。
    
    Attributes:
        scan_results: 代碼掃描器生成的掃描結果
        analysis: 根因分析的完整結果數據結構
    """
    
    # CWE 到根因類型的映射
    CWE_MAPPING = {
        'CWE-89': RootCauseType.INJECTION,
        'CWE-79': RootCauseType.INJECTION,
        'CWE-78': RootCauseType.INJECTION,
        'CWE-20': RootCauseType.MISSING_VALIDATION,
        'CWE-362': RootCauseType.RACE_CONDITION,
        'CWE-401': RootCauseType.RESOURCE_LEAK,
        'CWE-327': RootCauseType.CRYPTO_ISSUE,
        'CWE-287': RootCauseType.AUTH_ISSUE,
        'CWE-256': RootCauseType.CONFIGURATION,
        'CWE-1390': RootCauseType.DEPENDENCY,
    }
    
    # 嚴重性權重
    SEVERITY_WEIGHTS = {
        'critical': 10.0,
        'high': 7.5,
        'medium': 5.0,
        'low': 2.5
    }
    
    def __init__(self, scan_results: Dict) -> None:
        """
        初始化根因分析器
        
        Args:
            scan_results: 代碼掃描結果字典
        """
        self.scan_results = scan_results
        self.analysis = {
            "metadata": {
                "analysis_time": datetime.utcnow().isoformat(),
                "analyzer_version": "1.0.0"
            },
            "root_causes": [],
            "impact_chain": {},
            "affected_components": [],
            "risk_assessment": {},
            "recommendations": {}
        }
    
    def analyze(self) -> Dict:
        """
        執行完整的根因分析
        
        Returns:
            包含根因、影響鏈、受影響組件、風險評估和修復建議的字典
        """
        print("🔍 開始根因分析...")
        
        # 1. 識別根本原因
        print("\n🎯 識別根本原因...")
        self.analysis["root_causes"] = self._identify_root_causes()
        
        # 2. 追蹤影響鏈
        print("\n🔗 追蹤影響鏈...")
        self.analysis["impact_chain"] = self._trace_impact_chain()
        
        # 3. 找出受影響組件
        print("\n📦 找出受影響組件...")
        self.analysis["affected_components"] = self._find_affected_components()
        
        # 4. 計算風險評分
        print("\n📊 計算風險評分...")
        self.analysis["risk_assessment"] = self._calculate_risk_assessment()
        
        # 5. 生成修復建議
        print("\n💡 生成修復建議...")
        self.analysis["recommendations"] = self._generate_recommendations()
        
        print("\n✅ 根因分析完成!")
        return self.analysis
    
    def _identify_root_causes(self) -> List[Dict]:
        """識別根本原因"""
        causes = []
        all_findings = self._get_all_findings()
        
        # 按類型分組漏洞
        causes_by_type = defaultdict(list)
        
        for vuln in all_findings:
            cause_type = self._classify_cause(vuln)
            
            cause_info = {
                "type": cause_type.value,
                "description": self._generate_description(vuln),
                "evidence": vuln.get('code_snippet', ''),
                "confidence": self._calculate_confidence(vuln),
                "severity": vuln.get('severity', 'low'),
                "location": vuln.get('location', ''),
                "cwe_id": vuln.get('cwe_id', 'N/A')
            }
            
            causes_by_type[cause_type.value].append(cause_info)
        
        # 聚合同類型的根因
        for cause_type, cause_list in causes_by_type.items():
            if cause_list:
                # 計算平均置信度
                avg_confidence = sum(c['confidence'] for c in cause_list) / len(cause_list)
                
                # 聚合受影響組件
                affected_components = list(set(c['location'] for c in cause_list))
                
                # 生成統一的根因
                root_cause = {
                    "type": cause_type,
                    "count": len(cause_list),
                    "severity_distribution": self._get_severity_distribution(cause_list),
                    "confidence": avg_confidence,
                    "affected_components": affected_components,
                    "description": f"檢測到 {len(cause_list)} 個 {cause_type} 相關問題",
                    "examples": cause_list[:3],  # 最多顯示3個示例
                    "tool": self._get_primary_tool(cause_list)
                }
                
                causes.append(root_cause)
        
        # 按嚴重性和數量排序
        causes.sort(key=lambda x: (
            self._calculate_type_severity_score(x['severity_distribution']),
            x['count']
        ), reverse=True)
        
        return causes
    
    def _classify_cause(self, vuln: Dict) -> RootCauseType:
        """分類漏洞原因"""
        cwe = str(vuln.get('cwe_id', ''))
        vuln_type = vuln.get('type', '').lower()
        
        # 首先嘗試 CWE 映射
        if cwe in self.CWE_MAPPING:
            return self.CWE_MAPPING[cwe]
        
        # 根據漏洞類型推斷
        if 'injection' in vuln_type or 'sql' in vuln_type or 'xss' in vuln_type:
            return RootCauseType.INJECTION
        elif 'validation' in vuln_type or 'sanitize' in vuln_type:
            return RootCauseType.MISSING_VALIDATION
        elif 'password' in vuln_type or 'credential' in vuln_type or 'secret' in vuln_type:
            return RootCauseType.AUTH_ISSUE
        elif 'encrypt' in vuln_type or 'crypto' in vuln_type:
            return RootCauseType.CRYPTO_ISSUE
        elif 'leak' in vuln_type or 'resource' in vuln_type:
            return RootCauseType.RESOURCE_LEAK
        elif 'race' in vuln_type or 'concurrent' in vuln_type:
            return RootCauseType.RACE_CONDITION
        elif 'config' in vuln_type:
            return RootCauseType.CONFIGURATION
        elif 'dependency' in vuln_type or 'version' in vuln_type:
            return RootCauseType.DEPENDENCY
        elif 'quality' in vuln_type or 'style' in vuln_type:
            return RootCauseType.CODE_QUALITY
        elif 'compliance' in vuln_type or 'license' in vuln_type or 'doc' in vuln_type:
            return RootCauseType.COMPLIANCE
        elif 'performance' in vuln_type:
            return RootCauseType.PERFORMANCE
        else:
            return RootCauseType.LOGIC_ERROR
    
    def _generate_description(self, vuln: Dict) -> str:
        """生成根因描述"""
        vuln_type = vuln.get('type', 'Unknown')
        location = vuln.get('location', 'unknown location')
        
        return f"在 {location} 發現 {vuln_type}"
    
    def _calculate_confidence(self, vuln: Dict) -> float:
        """計算置信度"""
        tool = vuln.get('tool', '')
        
        # 不同工具的置信度權重
        tool_confidence = {
            'bandit': 0.85,
            'semgrep': 0.90,
            'custom': 0.70,
            'dependency': 0.95,
            'quality': 0.80,
            'performance': 0.60,
            'compliance': 1.0
        }
        
        base_confidence = tool_confidence.get(tool, 0.5)
        
        # 根據嚴重性調整
        severity = vuln.get('severity', 'low')
        severity_multiplier = {
            'critical': 1.0,
            'high': 0.95,
            'medium': 0.90,
            'low': 0.85
        }
        
        return base_confidence * severity_multiplier.get(severity, 0.8)
    
    def _trace_impact_chain(self) -> Dict:
        """追蹤影響鏈"""
        impact_chain = {}
        all_findings = self._get_all_findings()
        
        # 按文件分組分析
        files_to_findings = defaultdict(list)
        for vuln in all_findings:
            file_path = vuln.get('file_path', 'unknown')
            files_to_findings[file_path].append(vuln)
        
        # 分析每個文件的影響鏈
        for file_path, findings in files_to_findings.items():
            chain = []
            
            # 按嚴重性排序
            sorted_findings = sorted(
                findings,
                key=lambda x: self.SEVERITY_WEIGHTS.get(x.get('severity', 'low'), 0),
                reverse=True
            )
            
            # 構建影響鏈
            for vuln in sorted_findings:
                chain.append({
                    "severity": vuln.get('severity'),
                    "type": vuln.get('type'),
                    "line": vuln.get('line_number'),
                    "potential_impact": self._assess_potential_impact(vuln)
                })
            
            if chain:
                impact_chain[file_path] = chain
        
        return impact_chain
    
    def _assess_potential_impact(self, vuln: Dict) -> str:
        """評估潛在影響"""
        severity = vuln.get('severity', 'low')
        vuln_type = vuln.get('type', '').lower()
        
        impact_map = {
            'critical': '可能導致系統完全受控或數據完全洩漏',
            'high': '可能導致嚴重安全漏洞或數據洩漏',
            'medium': '可能導致中等風險或功能異常',
            'low': '輕微影響，建議修復'
        }
        
        base_impact = impact_map.get(severity, '輕微影響')
        
        # 根據類型細化
        if 'injection' in vuln_type:
            return base_impact.replace('可能', '極高概率')
        elif 'leak' in vuln_type:
            return "可能導致資源耗盡或數據洩漏"
        
        return base_impact
    
    def _find_affected_components(self) -> List[Dict]:
        """找出受影響的組件"""
        components = []
        all_findings = self._get_all_findings()
        
        # 按目錄分組
        dirs_to_findings = defaultdict(list)
        for vuln in all_findings:
            file_path = vuln.get('file_path', '')
            dir_path = str(Path(file_path).parent) if file_path else 'root'
            dirs_to_findings[dir_path].append(vuln)
        
        # 分析每個組件
        for dir_path, findings in dirs_to_findings.items():
            severity_counts = defaultdict(int)
            for vuln in findings:
                severity_counts[vuln.get('severity', 'low')] += 1
            
            components.append({
                "path": dir_path,
                "total_findings": len(findings),
                "severity_breakdown": dict(severity_counts),
                "risk_level": self._calculate_component_risk_level(severity_counts),
                "top_issues": sorted(findings, key=lambda x: self.SEVERITY_WEIGHTS.get(x.get('severity', 'low'), 0), reverse=True)[:3]
            })
        
        # 按風險級別排序
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        components.sort(key=lambda x: risk_order.get(x['risk_level'], 4))
        
        return components
    
    def _calculate_component_risk_level(self, severity_counts: Dict) -> str:
        """計算組件風險級別"""
        if severity_counts.get('critical', 0) > 0:
            return 'critical'
        elif severity_counts.get('high', 0) > 0:
            return 'high'
        elif severity_counts.get('medium', 0) > 2:
            return 'high'
        elif severity_counts.get('medium', 0) > 0:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_risk_assessment(self) -> Dict:
        """計算風險評估"""
        all_findings = self._get_all_findings()
        
        # 計算總體風險評分
        total_risk_score = 0
        for vuln in all_findings:
            severity = vuln.get('severity', 'low')
            confidence = vuln.get('confidence', 0.5)
            total_risk_score += self.SEVERITY_WEIGHTS.get(severity, 0) * confidence
        
        # 風險等級
        if total_risk_score > 50:
            risk_level = 'critical'
        elif total_risk_score > 30:
            risk_level = 'high'
        elif total_risk_score > 10:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            "total_risk_score": round(total_risk_score, 2),
            "risk_level": risk_level,
            "findings_by_severity": self._count_by_severity(all_findings),
            "high_risk_areas": self._identify_high_risk_areas(all_findings),
            "recommendations": self._get_risk_recommendations(risk_level)
        }
    
    def _generate_recommendations(self) -> Dict:
        """生成修復建議"""
        recommendations = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_actions": [],
            "best_practices": []
        }
        
        # 根據根因類型生成建議
        for cause in self.analysis.get("root_causes", []):
            cause_type = cause.get("type", "")
            severity_dist = cause.get("severity_distribution", {})
            
            if severity_dist.get('critical', 0) > 0 or severity_dist.get('high', 0) > 0:
                recommendations["immediate_actions"].append(
                    f"優先修復 {cause_type} 相關的高嚴重性問題"
                )
            else:
                recommendations["short_term_actions"].append(
                    f"修復 {cause_type} 問題"
                )
        
        # 通用最佳實踐
        recommendations["best_practices"] = [
            "實施代碼審查流程",
            "使用靜態分析工具進行持續監控",
            "定期進行安全培訓",
            "建立漏洞響應計劃",
            "使用依賴項掃描工具",
            "實施自動化測試"
        ]
        
        return recommendations
    
    def _get_all_findings(self) -> List[Dict]:
        """獲取所有發現"""
        findings = []
        for category in ['security', 'dependencies', 'code_quality', 'performance', 'compliance']:
            findings.extend(self.scan_results.get(category, []))
        return findings
    
    def _get_severity_distribution(self, cause_list: List[Dict]) -> Dict:
        """獲取嚴重性分佈"""
        distribution = defaultdict(int)
        for cause in cause_list:
            severity = cause.get('severity', 'low')
            distribution[severity] += 1
        return dict(distribution)
    
    def _get_primary_tool(self, cause_list: List[Dict]) -> str:
        """獲取主要工具"""
        tools = defaultdict(int)
        for cause in cause_list:
            tools[cause.get('tool', 'unknown')] += 1
        return max(tools.items(), key=lambda x: x[1])[0] if tools else 'unknown'
    
    def _calculate_type_severity_score(self, severity_dist: Dict) -> float:
        """計算類型嚴重性分數"""
        score = 0
        for severity, count in severity_dist.items():
            score += self.SEVERITY_WEIGHTS.get(severity, 0) * count
        return score
    
    def _count_by_severity(self, findings: List[Dict]) -> Dict:
        """按嚴重性計數"""
        counts = defaultdict(int)
        for finding in findings:
            counts[finding.get('severity', 'low')] += 1
        return dict(counts)
    
    def _identify_high_risk_areas(self, findings: List[Dict]) -> List[str]:
        """識別高風險區域"""
        areas = []
        
        # 統計文件風險
        file_risk = defaultdict(float)
        for vuln in findings:
            file_path = vuln.get('file_path', 'unknown')
            severity = vuln.get('severity', 'low')
            file_risk[file_path] += self.SEVERITY_WEIGHTS.get(severity, 0)
        
        # 選取前5個高風險文件
        sorted_files = sorted(file_risk.items(), key=lambda x: x[1], reverse=True)[:5]
        for file_path, risk in sorted_files:
            areas.append(f"{file_path} (風險分數: {risk:.1f})")
        
        return areas
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """獲取風險建議"""
        if risk_level == 'critical':
            return [
                "⚠️ 立即採取行動！",
                "修復所有關鍵和高嚴重性漏洞",
                "考慮暫停新功能開發，專注於安全修復"
            ]
        elif risk_level == 'high':
            return [
                "計劃在1-2周內修復高優先級問題",
                "加強代碼審查流程"
            ]
        elif risk_level == 'medium':
            return [
                "在下次迭代的計劃修復",
                "建立定期掃描機制"
            ]
        else:
            return [
                "持續監控和維護",
                "定期進行代碼質量檢查"
            ]
    
    def save_analysis(self, output_path: str) -> None:
        """
        保存分析結果到 JSON 文件
        
        Args:
            output_path: 輸出文件路徑
        """
        with open(output_path, 'w') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        print(f"\n📊 根因分析結果已保存至: {output_path}")

def main() -> None:
    """
    主執行函數
    
    從命令行讀取掃描結果並執行根因分析，將結果保存到指定文件。
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python root_cause_analyzer.py <scan_results.json> [output_path]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "root-cause-analysis.json"
    
    # 讀取掃描結果
    with open(input_path) as f:
        scan_results = json.load(f)
    
    # 執行分析
    analyzer = RootCauseAnalyzer(scan_results)
    analysis = analyzer.analyze()
    
    # 保存結果
    analyzer.save_analysis(output_path)
    
    # 打印摘要
    print("\n" + "="*60)
    print("根因分析摘要")
    print("="*60)
    print(f"總體風險評分: {analysis['risk_assessment']['total_risk_score']}")
    print(f"風險等級: {analysis['risk_assessment']['risk_level'].upper()}")
    print(f"識別的根因類型: {len(analysis['root_causes'])}")
    print(f"受影響組件: {len(analysis['affected_components'])}")

if __name__ == "__main__":
    main()