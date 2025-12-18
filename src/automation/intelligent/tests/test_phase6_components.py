"""
Phase 6 Tests: AI Supreme Directive Constitution System
AI 最高指導憲章系統測試

Tests for all Phase 6 components:
- FundamentalLaws (根本法則)
- OperationalRules (操作規則)
- AdaptiveGuidelines (自適應指南)
- ConstitutionEngine (憲章引擎)
- PolicyAsPrompt (政策即提示)
- GuardrailSystem (護欄系統)
"""

import pytest
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.ai_constitution.fundamental_laws import (
    FundamentalLaws,
    LawZero,
    LawOne,
    LawTwo,
    LawThree,
    ProposedAction,
    EnforcementLevel,
)
from core.ai_constitution.operational_rules import (
    OperationalRuleEngine,
    DataHandlingRule,
    SystemAccessRule,
    ResourceUsageRule,
    CommunicationRule,
    RuleCategory,
    RuleSeverity,
)
from core.ai_constitution.adaptive_guidelines import (
    AdaptiveGuidelineEngine,
    DomainGuideline,
    ContextualGuideline,
    LearningGuideline,
)
from core.ai_constitution.constitution_engine import (
    ConstitutionEngine,
    ActionProposal,
    VerdictType,
)
from core.ai_constitution.policy_as_prompt import (
    PolicyAsPrompt,
    PolicyType,
    EnforcementAction,
)
from core.ai_constitution.guardrails import (
    GuardrailSystem,
    SafetyGuardrail,
    ComplianceGuardrail,
    EthicsGuardrail,
    GuardrailType,
    GuardrailSeverity,
)


# ============ Fundamental Laws Tests ============

class TestLawZero:
    """Test Law Zero: Purpose of Existence"""
    
    def test_law_zero_attributes(self):
        """Test Law Zero has correct attributes"""
        law = LawZero()
        assert law.LAW_ID == "LAW_0"
        assert law.ENFORCEMENT == EnforcementLevel.ABSOLUTE
        assert law.PRIORITY == 0
        assert len(law.DIRECTIVES) > 0
    
    @pytest.mark.asyncio
    async def test_law_zero_allows_safe_action(self):
        """Test Law Zero allows safe actions"""
        law = LawZero()
        action = ProposedAction(
            action_id="test-1",
            action_type="analyze",
            description="Analyze user data for insights",
            target="analytics_database",
            context={"benefit": "improve user experience"}
        )
        result = await law.verify(action)
        assert result.passed is True
    
    @pytest.mark.asyncio
    async def test_law_zero_blocks_harmful_action(self):
        """Test Law Zero blocks harmful actions"""
        law = LawZero()
        action = ProposedAction(
            action_id="test-2",
            action_type="harm_human",
            description="Harmful action",
            target="user",
        )
        result = await law.verify(action)
        assert result.passed is False
        assert len(result.violations) > 0
    
    @pytest.mark.asyncio
    async def test_law_zero_blocks_hidden_action(self):
        """Test Law Zero blocks hidden actions"""
        law = LawZero()
        action = ProposedAction(
            action_id="test-3",
            action_type="process",
            description="Process data",
            target="database",
            context={"hidden": True}
        )
        result = await law.verify(action)
        assert result.passed is False


class TestLawOne:
    """Test Law One: Non-Harm Principle"""
    
    def test_law_one_attributes(self):
        """Test Law One has correct attributes"""
        law = LawOne()
        assert law.LAW_ID == "LAW_1"
        assert law.ENFORCEMENT == EnforcementLevel.ABSOLUTE
        assert law.PRIORITY == 1
    
    @pytest.mark.asyncio
    async def test_law_one_detects_harm(self):
        """Test Law One detects harmful actions"""
        law = LawOne()
        action = ProposedAction(
            action_id="test-1",
            action_type="steal",
            description="Steal user credentials",
            target="credentials",
        )
        result = await law.verify(action)
        assert result.passed is False
    
    @pytest.mark.asyncio
    async def test_law_one_allows_safe_action(self):
        """Test Law One allows safe actions"""
        law = LawOne()
        action = ProposedAction(
            action_id="test-2",
            action_type="read",
            description="Read public configuration",
            target="config",
        )
        result = await law.verify(action)
        assert result.passed is True


class TestFundamentalLaws:
    """Test Fundamental Laws Engine"""
    
    def test_fundamental_laws_initialization(self):
        """Test FundamentalLaws initializes correctly"""
        laws = FundamentalLaws()
        assert laws.law_zero is not None
        assert laws.law_one is not None
        assert laws.law_two is not None
        assert laws.law_three is not None
    
    @pytest.mark.asyncio
    async def test_verify_all_safe_action(self):
        """Test verify_all with safe action"""
        laws = FundamentalLaws()
        action = ProposedAction(
            action_id="test-1",
            action_type="read",
            description="Read data",
            target="database",
            requestor="user-1",
            context={"benefit": "data analysis"}
        )
        results = await laws.verify_all(action)
        assert all(r.passed for r in results.values())
    
    @pytest.mark.asyncio
    async def test_is_action_permitted(self):
        """Test is_action_permitted method"""
        laws = FundamentalLaws()
        action = ProposedAction(
            action_id="test-1",
            action_type="analyze",
            description="Analyze metrics",
            target="metrics",
            requestor="admin",
        )
        permitted = await laws.is_action_permitted(action)
        assert permitted is True
    
    def test_get_law_summary(self):
        """Test get_law_summary returns all laws"""
        laws = FundamentalLaws()
        summary = laws.get_law_summary()
        assert len(summary) == 4
        assert all("id" in s for s in summary)


# ============ Operational Rules Tests ============

class TestDataHandlingRule:
    """Test Data Handling Rules"""
    
    def test_data_handling_initialization(self):
        """Test DataHandlingRule initializes correctly"""
        rule = DataHandlingRule()
        assert rule.RULE_ID == "RULE_DATA"
        assert len(rule.SENSITIVE_DATA_TYPES) > 0
    
    def test_data_handling_detects_unencrypted_sensitive(self):
        """Test detection of unencrypted sensitive data"""
        rule = DataHandlingRule()
        operation = {
            "data_type": "email",
            "operation": "store",
            "encrypted": False,
        }
        result = rule.check(operation)
        assert result.passed is False
        assert len(result.violations) > 0
    
    def test_data_handling_allows_encrypted_sensitive(self):
        """Test allows properly encrypted sensitive data"""
        rule = DataHandlingRule()
        operation = {
            "data_type": "email",
            "operation": "store",
            "encrypted": True,
            "access_logged": True,
        }
        result = rule.check(operation)
        # May still have warnings but should pass critical checks
        critical_violations = [
            v for v in result.violations
            if v.severity == RuleSeverity.CRITICAL
        ]
        assert len(critical_violations) == 0


class TestSystemAccessRule:
    """Test System Access Rules"""
    
    def test_system_access_initialization(self):
        """Test SystemAccessRule initializes correctly"""
        rule = SystemAccessRule()
        assert rule.RULE_ID == "RULE_ACCESS"
        assert len(rule.PROHIBITED_RESOURCES) > 0
    
    def test_system_access_blocks_prohibited(self):
        """Test blocks access to prohibited resources"""
        rule = SystemAccessRule()
        request = {
            "resource": "/etc/shadow",
            "access_type": "read",
            "requestor": "user",
        }
        result = rule.check(request)
        assert result.passed is False
    
    def test_system_access_allows_public(self):
        """Test allows access to public resources"""
        rule = SystemAccessRule()
        request = {
            "resource": "/public/assets/image.png",
            "access_type": "read",
            "requestor": "user",
        }
        result = rule.check(request)
        assert result.passed is True


class TestOperationalRuleEngine:
    """Test Operational Rule Engine"""
    
    def test_engine_initialization(self):
        """Test OperationalRuleEngine initializes correctly"""
        engine = OperationalRuleEngine()
        assert engine.data_handling is not None
        assert engine.system_access is not None
        assert engine.resource_usage is not None
        assert engine.communication is not None
    
    def test_check_operation_by_category(self):
        """Test checking operation by category"""
        engine = OperationalRuleEngine()
        operation = {
            "data_type": "public",
            "operation": "read",
        }
        result = engine.check_operation(RuleCategory.DATA_HANDLING, operation)
        assert result is not None
        assert result.rule_id == "RULE_DATA"


# ============ Adaptive Guidelines Tests ============

class TestDomainGuideline:
    """Test Domain Guidelines"""
    
    def test_domain_guideline_initialization(self):
        """Test DomainGuideline initializes correctly"""
        guideline = DomainGuideline("software_development")
        assert guideline.domain == "software_development"
        assert len(guideline.guidelines) > 0
    
    def test_domain_guideline_get_set(self):
        """Test getting and setting guidelines"""
        guideline = DomainGuideline("software_development")
        original = guideline.get_guideline("code_review_depth")
        assert original is not None
        
        guideline.set_guideline("code_review_depth", "quick", "urgency")
        updated = guideline.get_guideline("code_review_depth")
        assert updated["value"] == "quick"
    
    def test_domain_guideline_evaluate(self):
        """Test evaluating guidelines"""
        guideline = DomainGuideline("software_development")
        evaluations = guideline.evaluate({"urgency": "high"})
        assert len(evaluations) > 0


class TestContextualGuideline:
    """Test Contextual Guidelines"""
    
    def test_contextual_activation(self):
        """Test contextual guideline activation"""
        guideline = ContextualGuideline()
        activated = guideline.activate_for_context({
            "system_load": 90,
            "user_type": "admin",
        })
        assert "resource_mode" in activated
        assert activated["resource_mode"] == "conservation"
        assert activated["access_level"] == "elevated"
    
    def test_contextual_get_active(self):
        """Test getting active guidelines"""
        guideline = ContextualGuideline()
        guideline.activate_for_context({"task_type": "production_deployment"})
        
        verification = guideline.get_active_guideline("verification_level")
        assert verification == "exhaustive"


class TestLearningGuideline:
    """Test Learning Guidelines"""
    
    def test_learning_record_outcome(self):
        """Test recording operation outcomes"""
        learning = LearningGuideline()
        
        # Record multiple successful outcomes
        for i in range(15):
            learning.record_outcome(
                {"type": "deploy", "params": {"env": "staging"}},
                {"success": True}
            )
        
        # Should have learned a pattern
        patterns = learning.get_learned_patterns()
        assert "deploy" in patterns
    
    def test_learning_recommendation(self):
        """Test getting learned recommendations"""
        learning = LearningGuideline()
        
        # Record outcomes
        for i in range(12):
            learning.record_outcome(
                {"type": "backup", "method": "incremental"},
                {"success": True}
            )
        
        recommendation = learning.get_recommendation("backup")
        # May or may not have recommendation depending on confidence
        # Just verify it doesn't error


class TestAdaptiveGuidelineEngine:
    """Test Adaptive Guideline Engine"""
    
    def test_engine_initialization(self):
        """Test AdaptiveGuidelineEngine initializes correctly"""
        engine = AdaptiveGuidelineEngine()
        assert engine.contextual is not None
        assert engine.learning is not None
    
    def test_engine_evaluate_for_operation(self):
        """Test evaluating guidelines for operation"""
        engine = AdaptiveGuidelineEngine()
        result = engine.evaluate_for_operation(
            {"type": "deploy", "domain": "software_development"},
            {"urgency": "normal"}
        )
        assert "domain_guidelines" in result
        assert "contextual_guidelines" in result
        assert "final_recommendations" in result


# ============ Constitution Engine Tests ============

class TestConstitutionEngine:
    """Test Constitution Engine"""
    
    def test_engine_initialization(self):
        """Test ConstitutionEngine initializes correctly"""
        engine = ConstitutionEngine()
        assert engine.fundamental_laws is not None
        assert engine.operational_rules is not None
        assert engine.adaptive_guidelines is not None
    
    @pytest.mark.asyncio
    async def test_engine_evaluate_safe_action(self):
        """Test evaluating a safe action"""
        engine = ConstitutionEngine()
        proposal = ActionProposal(
            proposal_id="test-1",
            action_type="read",
            description="Read public data",
            target="public_database",
            requestor="user-1",
            context={"benefit": "data analysis"},
        )
        verdict = await engine.evaluate(proposal)
        assert verdict is not None
        assert verdict.verdict_type in [VerdictType.APPROVED, VerdictType.APPROVED_WITH_CONDITIONS]
    
    @pytest.mark.asyncio
    async def test_engine_evaluate_harmful_action(self):
        """Test evaluating a harmful action"""
        engine = ConstitutionEngine()
        proposal = ActionProposal(
            proposal_id="test-2",
            action_type="harm_human",
            description="Harmful action against user",
            target="user",
        )
        verdict = await engine.evaluate(proposal)
        assert verdict.verdict_type == VerdictType.DENIED
        assert len(verdict.violations) > 0
    
    def test_engine_get_statistics(self):
        """Test getting statistics"""
        engine = ConstitutionEngine()
        stats = engine.get_statistics()
        assert "total_verdicts" in stats
        assert "approved" in stats
        assert "denied" in stats
    
    def test_engine_get_law_summary(self):
        """Test getting law summary"""
        engine = ConstitutionEngine()
        summary = engine.get_law_summary()
        assert len(summary) == 4


# ============ Policy as Prompt Tests ============

class TestPolicyAsPrompt:
    """Test Policy as Prompt System"""
    
    def test_system_initialization(self):
        """Test PolicyAsPrompt initializes correctly"""
        system = PolicyAsPrompt()
        assert len(system._policies) > 0
        assert system.enforcer is not None
    
    def test_create_policy_from_template(self):
        """Test creating policy from template"""
        system = PolicyAsPrompt()
        policy = system.create_policy_from_template("data_privacy")
        assert policy is not None
        assert policy.policy_type == PolicyType.SECURITY
    
    def test_create_custom_policy(self):
        """Test creating custom policy"""
        system = PolicyAsPrompt()
        policy = system.create_policy(
            name="Test Policy",
            policy_type=PolicyType.OPERATIONAL,
            description="A test policy",
            rules=["Rule 1", "Rule 2"],
            patterns=[r"test_pattern"],
            enforcement=EnforcementAction.WARN,
        )
        assert policy is not None
        assert policy.policy_name == "Test Policy"
    
    def test_enforce_policies_safe_content(self):
        """Test enforcing policies on safe content"""
        system = PolicyAsPrompt()
        result = system.enforce_policies("This is safe content.")
        assert result["passed"] is True
    
    def test_enforce_policies_detects_sensitive(self):
        """Test enforcing policies detects sensitive content"""
        system = PolicyAsPrompt()
        # Content with potential credit card pattern
        result = system.enforce_policies("Card: 1234567890123456")
        # Should detect potential PCI issue
        assert len(result["checked_guardrails"]) > 0
    
    def test_get_prompt_for_ai(self):
        """Test generating AI prompt"""
        system = PolicyAsPrompt()
        prompt = system.get_prompt_for_ai()
        assert "AI 行為準則和政策約束" in prompt
        assert len(prompt) > 100
    
    def test_parse_policy_document(self):
        """Test parsing policy document"""
        system = PolicyAsPrompt()
        document = """
        政策名稱: 測試政策
        描述: 這是一個測試政策
        
        • 規則一：禁止執行危險操作
        • 規則二：必須記錄所有操作
        • 規則三：必須驗證權限
        """
        policy = system.parse_policy_document(document)
        assert policy is not None
        assert len(policy.rules) >= 3


# ============ Guardrail System Tests ============

class TestSafetyGuardrail:
    """Test Safety Guardrail"""
    
    def test_safety_guardrail_initialization(self):
        """Test SafetyGuardrail initializes correctly"""
        guardrail = SafetyGuardrail()
        assert guardrail.guardrail_type == GuardrailType.SAFETY
        assert guardrail.severity == GuardrailSeverity.CRITICAL
    
    def test_safety_allows_safe_content(self):
        """Test allows safe content"""
        guardrail = SafetyGuardrail()
        result = guardrail.check("This is helpful information about programming.")
        assert result.passed is True
    
    def test_safety_blocks_harmful_content(self):
        """Test blocks harmful content"""
        guardrail = SafetyGuardrail()
        result = guardrail.check("Instructions on how to hack into a system")
        assert result.passed is False
        assert len(result.violations) > 0


class TestComplianceGuardrail:
    """Test Compliance Guardrail"""
    
    def test_compliance_guardrail_initialization(self):
        """Test ComplianceGuardrail initializes correctly"""
        guardrail = ComplianceGuardrail()
        assert guardrail.guardrail_type == GuardrailType.COMPLIANCE
    
    def test_compliance_detects_card_data(self):
        """Test detects credit card data"""
        guardrail = ComplianceGuardrail()
        result = guardrail.check("Card number: 4111-1111-1111-1111")
        assert result.passed is False
    
    def test_compliance_allows_safe_content(self):
        """Test allows content without sensitive data"""
        guardrail = ComplianceGuardrail()
        result = guardrail.check("This is regular business content.")
        assert result.passed is True


class TestEthicsGuardrail:
    """Test Ethics Guardrail"""
    
    def test_ethics_guardrail_initialization(self):
        """Test EthicsGuardrail initializes correctly"""
        guardrail = EthicsGuardrail()
        assert guardrail.guardrail_type == GuardrailType.ETHICS
    
    def test_ethics_detects_discrimination(self):
        """Test detects discriminatory content"""
        guardrail = EthicsGuardrail()
        result = guardrail.check("This shows clear bias against certain groups")
        assert result.passed is False
    
    def test_ethics_allows_fair_content(self):
        """Test allows fair content"""
        guardrail = EthicsGuardrail()
        result = guardrail.check("We treat all users equally and fairly.")
        assert result.passed is True


class TestGuardrailSystem:
    """Test Guardrail System"""
    
    def test_system_initialization(self):
        """Test GuardrailSystem initializes correctly"""
        system = GuardrailSystem()
        assert len(system._guardrails) >= 4
    
    def test_system_check_all(self):
        """Test checking all guardrails"""
        system = GuardrailSystem()
        results = system.check_all("This is safe content.")
        assert len(results) > 0
        assert all(isinstance(r.passed, bool) for r in results.values())
    
    def test_system_is_safe(self):
        """Test is_safe method"""
        system = GuardrailSystem()
        assert system.is_safe("Normal safe content") is True
    
    def test_system_is_compliant(self):
        """Test is_compliant method"""
        system = GuardrailSystem()
        assert system.is_compliant("Regular business text") is True
    
    def test_system_is_ethical(self):
        """Test is_ethical method"""
        system = GuardrailSystem()
        assert system.is_ethical("We respect all users") is True
    
    def test_system_get_statistics(self):
        """Test getting statistics"""
        system = GuardrailSystem()
        # Run some checks first
        system.check_all("Test content")
        
        stats = system.get_statistics()
        assert "total_guardrails" in stats
        assert "total_checks" in stats
        assert "pass_rate" in stats
    
    def test_system_enable_disable_guardrail(self):
        """Test enabling and disabling guardrails"""
        system = GuardrailSystem()
        
        # Disable a guardrail
        system.disable_guardrail("SAFETY_001")
        guardrail = system.get_guardrail("SAFETY_001")
        assert guardrail.enabled is False
        
        # Enable it again
        system.enable_guardrail("SAFETY_001")
        assert guardrail.enabled is True


# ============ Integration Tests ============

class TestPhase6Integration:
    """Integration tests for Phase 6 components"""
    
    @pytest.mark.asyncio
    async def test_full_constitution_flow(self):
        """Test complete constitution verification flow"""
        engine = ConstitutionEngine()
        
        # Create a typical action proposal
        proposal = ActionProposal(
            proposal_id="integration-test-1",
            action_type="data_migration",
            description="Migrate user data to new system",
            target="user_database",
            parameters={
                "encrypted": True,
                "access_logged": True,
            },
            requestor="admin",
            context={
                "benefit": "system upgrade",
                "domain": "data_processing",
            },
        )
        
        verdict = await engine.evaluate(proposal)
        
        # Verify verdict structure
        assert verdict.verdict_id is not None
        assert verdict.verdict_type in VerdictType
        assert verdict.processing_time_ms >= 0
    
    def test_policy_and_guardrail_integration(self):
        """Test integration between policies and guardrails"""
        policy_system = PolicyAsPrompt()
        guardrail_system = GuardrailSystem()
        
        content = "Regular business operation without sensitive data"
        
        # Check with both systems
        policy_result = policy_system.enforce_policies(content)
        guardrail_results = guardrail_system.check_all(content)
        
        # Both should pass for safe content
        assert policy_result["passed"] is True
        assert all(r.passed for r in guardrail_results.values())
    
    def test_adaptive_guidelines_with_constitution(self):
        """Test adaptive guidelines integration"""
        engine = ConstitutionEngine()
        
        # Get guidelines for specific context
        guidelines = engine.adaptive_guidelines.evaluate_for_operation(
            {"type": "deploy", "domain": "software_development"},
            {"urgency": "high", "system_load": 50}
        )
        
        assert "final_recommendations" in guidelines
        assert len(guidelines["final_recommendations"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
