"""
第三階段功能測試
Phase 3 Tests - Policy Simulator and Language Boundary
"""

import pytest
from pathlib import Path
import sys

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.dependency import Dependency, DependencyAnalysis, DependencyType, Ecosystem
from models.update import UpdateType, UpdatePolicy
from utils.policy_simulator import (
    PolicySimulator, 
    SimulationScenario, 
    SimulationMode,
    SimulationResult
)
from utils.language_boundary import (
    LanguageBoundary, 
    OutputLanguage, 
    LanguageRegistry,
    t,
    msg,
    get_language_boundary
)


class TestSimulationScenario:
    """模擬情境測試"""
    
    def test_conservative_scenario(self):
        """測試保守模式情境"""
        scenario = SimulationScenario.conservative()
        
        assert scenario.mode == SimulationMode.CONSERVATIVE
        assert scenario.name == "保守更新"
        assert scenario.update_policy["patch"] == UpdatePolicy.AUTO
        assert scenario.update_policy["minor"] == UpdatePolicy.MANUAL
        assert scenario.update_policy["major"] == UpdatePolicy.MANUAL
    
    def test_balanced_scenario(self):
        """測試平衡模式情境"""
        scenario = SimulationScenario.balanced()
        
        assert scenario.mode == SimulationMode.BALANCED
        assert scenario.update_policy["patch"] == UpdatePolicy.AUTO
        assert scenario.update_policy["minor"] == UpdatePolicy.PR
        assert scenario.update_policy["major"] == UpdatePolicy.MANUAL
    
    def test_aggressive_scenario(self):
        """測試積極模式情境"""
        scenario = SimulationScenario.aggressive()
        
        assert scenario.mode == SimulationMode.AGGRESSIVE
        assert scenario.update_policy["patch"] == UpdatePolicy.AUTO
        assert scenario.update_policy["minor"] == UpdatePolicy.AUTO
        assert scenario.update_policy["major"] == UpdatePolicy.PR
    
    def test_security_only_scenario(self):
        """測試安全優先情境"""
        scenario = SimulationScenario.security_only()
        
        assert scenario.mode == SimulationMode.SECURITY_ONLY
        assert scenario.update_policy.get("security") == UpdatePolicy.AUTO


class TestPolicySimulator:
    """政策模擬器測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.simulator = PolicySimulator()
        
        # 創建測試用分析結果
        self.analysis = DependencyAnalysis(
            analysis_id="test-123",
            project="test-project",
            ecosystem=Ecosystem.NPM
        )
        
        # 添加測試依賴
        deps = [
            Dependency(
                name="express",
                current_version="4.18.0",
                latest_version="4.21.2",
                ecosystem=Ecosystem.NPM,
                dep_type=DependencyType.DIRECT
            ),
            Dependency(
                name="lodash",
                current_version="4.17.0",
                latest_version="4.17.21",
                ecosystem=Ecosystem.NPM,
                dep_type=DependencyType.DIRECT
            ),
            Dependency(
                name="vulnerable-pkg",
                current_version="1.0.0",
                latest_version="2.0.0",
                ecosystem=Ecosystem.NPM,
                has_vulnerability=True,
                vulnerability_count=2
            ),
        ]
        
        for dep in deps:
            self.analysis.add_dependency(dep)
    
    def test_simulate_conservative(self):
        """測試保守模式模擬"""
        scenario = SimulationScenario.conservative()
        result = self.simulator.simulate(self.analysis, scenario)
        
        assert isinstance(result, SimulationResult)
        assert result.total_dependencies == 3
        assert len(result.updates_proposed) > 0
    
    def test_simulate_all_scenarios(self):
        """測試所有情境模擬"""
        results = self.simulator.simulate_all(self.analysis)
        
        assert len(results) == 4  # 4 種預設情境
        
        modes = [r.scenario.mode for r in results]
        assert SimulationMode.CONSERVATIVE in modes
        assert SimulationMode.BALANCED in modes
        assert SimulationMode.AGGRESSIVE in modes
        assert SimulationMode.SECURITY_ONLY in modes
    
    def test_compare_scenarios(self):
        """測試情境比較"""
        results = self.simulator.simulate_all(self.analysis)
        comparison = self.simulator.compare_scenarios(results)
        
        assert "scenarios" in comparison
        assert "recommendation" in comparison
        assert "analysis" in comparison
        
        assert len(comparison["scenarios"]) == 4
        assert comparison["recommendation"]["scenario"] is not None
    
    def test_risk_score_calculation(self):
        """測試風險評分計算"""
        scenario = SimulationScenario.aggressive()
        result = self.simulator.simulate(self.analysis, scenario)
        
        # 風險評分應該在 0-100 之間
        assert 0 <= result.risk_score <= 100
    
    def test_time_estimation(self):
        """測試時間估算"""
        scenario = SimulationScenario.balanced()
        result = self.simulator.simulate(self.analysis, scenario)
        
        # 預估時間應該 >= 0
        assert result.estimated_time_hours >= 0
    
    def test_add_custom_scenario(self):
        """測試添加自定義情境"""
        custom = SimulationScenario(
            name="自定義策略",
            mode=SimulationMode.BALANCED,
            description="測試用自定義策略",
            update_policy={
                "patch": UpdatePolicy.AUTO,
                "minor": UpdatePolicy.AUTO,
                "major": UpdatePolicy.MANUAL
            }
        )
        
        self.simulator.add_custom_scenario(custom)
        results = self.simulator.simulate_all(self.analysis)
        
        # 應該有 5 個情境（4 預設 + 1 自定義）
        assert len(results) == 5
    
    def test_generate_report(self):
        """測試報告生成"""
        results = self.simulator.simulate_all(self.analysis)
        report = self.simulator.generate_report(results)
        
        assert isinstance(report, str)
        assert "政策模擬報告" in report
        assert "保守更新" in report
        assert "推薦策略" in report
    
    def test_security_only_filters_non_vulnerable(self):
        """測試安全優先模式過濾非漏洞依賴"""
        scenario = SimulationScenario.security_only()
        result = self.simulator.simulate(self.analysis, scenario)
        
        # 只有有漏洞的依賴應該被更新
        for update in result.updates_proposed:
            assert update.is_security_fix


class TestLanguageRegistry:
    """語言註冊表測試"""
    
    def test_terms_exist(self):
        """測試術語存在"""
        assert "dependency" in LanguageRegistry.TERMS
        assert "vulnerability" in LanguageRegistry.TERMS
        assert "update" in LanguageRegistry.TERMS
    
    def test_messages_exist(self):
        """測試消息存在"""
        assert "analysis_started" in LanguageRegistry.MESSAGES
        assert "vulnerability_found" in LanguageRegistry.MESSAGES
        assert "update_completed" in LanguageRegistry.MESSAGES


class TestLanguageBoundary:
    """語言邊界測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.lb = LanguageBoundary()
    
    def test_default_language(self):
        """測試預設語言"""
        assert self.lb.default_lang == OutputLanguage.ZH_TW
    
    def test_translate_term(self):
        """測試術語翻譯"""
        result = self.lb.t("dependency")
        assert result == "依賴項"
        
        result = self.lb.t("vulnerability")
        assert result == "漏洞"
    
    def test_translate_with_language(self):
        """測試指定語言翻譯"""
        result = self.lb.t("dependency", lang=OutputLanguage.EN)
        assert result == "Dependency"
        
        result = self.lb.t("dependency", lang=OutputLanguage.ZH_TW)
        assert result == "依賴項"
    
    def test_format_message(self):
        """測試消息格式化"""
        result = self.lb.msg(
            "analysis_started",
            project="test-project"
        )
        assert "test-project" in result
        assert "分析" in result
    
    def test_format_message_with_language(self):
        """測試指定語言消息"""
        result = self.lb.msg(
            "analysis_started",
            lang=OutputLanguage.EN,
            project="test-project"
        )
        assert "test-project" in result
        assert "Starting" in result
    
    def test_add_custom_term(self):
        """測試添加自定義術語"""
        self.lb.add_term("custom_key", "自定義值", "Custom Value", "自定义值")
        
        result = self.lb.t("custom_key")
        assert result == "自定義值"
    
    def test_set_language(self):
        """測試切換語言"""
        self.lb.set_language(OutputLanguage.EN)
        
        result = self.lb.t("dependency")
        assert result == "Dependency"
        
        # 重置
        self.lb.set_language(OutputLanguage.ZH_TW)
    
    def test_format_severity(self):
        """測試嚴重程度格式化"""
        assert self.lb.format_severity("CRITICAL") == "嚴重"
        assert self.lb.format_severity("HIGH") == "高"
        assert self.lb.format_severity("MEDIUM") == "中"
        assert self.lb.format_severity("LOW") == "低"
    
    def test_format_update_type(self):
        """測試更新類型格式化"""
        assert self.lb.format_update_type("MAJOR") == "主版本"
        assert self.lb.format_update_type("MINOR") == "次版本"
        assert self.lb.format_update_type("PATCH") == "修補版本"
    
    def test_format_policy(self):
        """測試策略格式化"""
        assert self.lb.format_policy("auto") == "自動更新"
        assert self.lb.format_policy("pr") == "拉取請求"
        assert self.lb.format_policy("manual") == "人工審查"
    
    def test_get_all_terms(self):
        """測試獲取所有術語"""
        terms = self.lb.get_all_terms()
        
        assert isinstance(terms, dict)
        assert "dependency" in terms
        assert "vulnerability" in terms
    
    def test_unknown_term(self):
        """測試未知術語"""
        result = self.lb.t("unknown_key_123")
        assert result == "unknown_key_123"  # 返回原始鍵值


class TestGlobalLanguageFunctions:
    """全域語言函數測試"""
    
    def test_t_function(self):
        """測試 t() 快捷函數"""
        result = t("dependency")
        assert result == "依賴項"
    
    def test_msg_function(self):
        """測試 msg() 快捷函數"""
        result = msg("analysis_started", project="test")
        assert "test" in result
    
    def test_get_language_boundary(self):
        """測試獲取全域實例"""
        lb = get_language_boundary()
        assert isinstance(lb, LanguageBoundary)


class TestSimulationResultSerialization:
    """模擬結果序列化測試"""
    
    def test_to_dict(self):
        """測試轉換為字典"""
        scenario = SimulationScenario.balanced()
        result = SimulationResult(
            scenario=scenario,
            total_dependencies=10,
            auto_updates=3,
            pr_updates=2,
            manual_updates=1,
            skipped_updates=0,
            risk_score=25.5,
            estimated_time_hours=1.5
        )
        
        data = result.to_dict()
        
        assert "scenario" in data
        assert "summary" in data
        assert "risk_assessment" in data
        
        assert data["scenario"]["name"] == "平衡更新"
        assert data["summary"]["total_dependencies"] == 10
        assert data["risk_assessment"]["risk_score"] == 25.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
