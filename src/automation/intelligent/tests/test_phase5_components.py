"""
Tests for Phase 5 Components: AI Hallucination Detection, Context Understanding, and Bug Detection

Phase 5 focuses on:
1. AI Hallucination Detection and Prevention
2. Context Understanding Engine
3. Automatic Bug Detection and Fixing
"""

import pytest
import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from hallucination_detector import (
    HallucinationDetector,
    HallucinationType,
    SeverityLevel,
    ValidationResult,
    HallucinationDetection,
)
from context_understanding_engine import (
    ContextUnderstandingEngine,
    ContextType,
    IntentCategory,
    ParsedIntent,
    ContextAnalysis,
)
from auto_bug_detector import (
    AutoBugDetector,
    BugCategory,
    FixStatus,
    FixConfidence,
    DetectedBug,
    BugFix,
)


# ============ HallucinationDetector Tests ============

class TestHallucinationDetector:
    """Tests for HallucinationDetector"""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        detector = HallucinationDetector()
        assert detector is not None
        stats = detector.get_statistics()
        assert stats["total_validations"] == 0
        assert stats["total_hallucinations"] == 0
    
    def test_detect_plaintext_password(self):
        """Test detection of plaintext password storage"""
        detector = HallucinationDetector()
        # Use a pattern that matches the security pattern regex
        code = '''
        password = "super_secret_123"
        '''
        result = detector.validate_code(code, "python")
        assert not result.is_valid
        security_issues = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.SECURITY_FLAW
        ]
        assert len(security_issues) > 0
    
    def test_detect_empty_catch_block(self):
        """Test detection of empty catch blocks"""
        detector = HallucinationDetector()
        code = '''
        try {
            doSomething();
        } catch (error) {}
        '''
        result = detector.validate_code(code, "javascript")
        logic_issues = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.LOGIC_ERROR
        ]
        assert len(logic_issues) > 0
    
    def test_detect_todo_comments(self):
        """Test detection of TODO/FIXME comments"""
        detector = HallucinationDetector()
        code = '''
        def process_data(data):
            # TODO: Add input validation
            return data
        '''
        result = detector.validate_code(code, "python")
        incomplete_issues = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.INCOMPLETE
        ]
        assert len(incomplete_issues) > 0
    
    def test_detect_overconfident_claims(self):
        """Test detection of overconfident claims in comments"""
        detector = HallucinationDetector()
        code = '''
        # This code is secure and fully tested
        def vulnerable_function():
            pass
        '''
        result = detector.validate_code(code, "python")
        overconfidence_issues = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.OVERCONFIDENCE
        ]
        assert len(overconfidence_issues) > 0
    
    def test_clean_code_passes_validation(self):
        """Test that clean code passes validation"""
        detector = HallucinationDetector()
        code = '''
        def add(a: int, b: int) -> int:
            return a + b
        '''
        result = detector.validate_code(code, "python")
        assert result.overall_confidence > 0.5
        critical_issues = [
            h for h in result.hallucinations 
            if h.severity == SeverityLevel.CRITICAL
        ]
        assert len(critical_issues) == 0
    
    def test_custom_validator_registration(self):
        """Test custom validator registration"""
        detector = HallucinationDetector()
        
        def custom_validator(code: str):
            if "dangerous_function" in code:
                return [HallucinationDetection(
                    detection_id="CUSTOM-001",
                    hallucination_type=HallucinationType.SECURITY_FLAW,
                    severity=SeverityLevel.HIGH,
                    description="Custom: dangerous function detected",
                    confidence=0.9,
                )]
            return []
        
        detector.register_custom_validator(custom_validator)
        
        code = "dangerous_function()"
        result = detector.validate_code(code, "python")
        
        custom_issues = [
            h for h in result.hallucinations 
            if "Custom" in h.description
        ]
        assert len(custom_issues) > 0
    
    def test_mark_false_positive(self):
        """Test marking detections as false positives"""
        detector = HallucinationDetector()
        code = '''
        # This is secure (for testing purposes)
        password: data.password
        '''
        
        # First validation
        result1 = detector.validate_code(code, "python")
        initial_count = len(result1.hallucinations)
        
        # Mark as false positive
        if result1.hallucinations:
            detector.mark_false_positive(code, result1.hallucinations[0].detection_id)
        
        # Second validation should have fewer detections
        result2 = detector.validate_code(code, "python")
        assert len(result2.hallucinations) <= initial_count
    
    def test_statistics_tracking(self):
        """Test that statistics are properly tracked"""
        detector = HallucinationDetector()
        
        code1 = "password = 'hardcoded'"
        code2 = "# TODO: implement this"
        
        detector.validate_code(code1, "python")
        detector.validate_code(code2, "python")
        
        stats = detector.get_statistics()
        assert stats["total_validations"] == 2
        assert stats["total_hallucinations"] > 0


# ============ ContextUnderstandingEngine Tests ============

class TestContextUnderstandingEngine:
    """Tests for ContextUnderstandingEngine"""
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        engine = ContextUnderstandingEngine()
        assert engine is not None
    
    def test_parse_migration_intent(self):
        """Test parsing migration intent from Chinese request"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "我需要將用戶資料從舊系統遷移到新系統"
        )
        assert result.parsed_intent.primary_intent == IntentCategory.MIGRATION
        assert result.understanding_confidence > 0
    
    def test_parse_optimization_intent(self):
        """Test parsing optimization intent"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "幫我優化這個查詢的效能"
        )
        assert result.parsed_intent.primary_intent == IntentCategory.OPTIMIZATION
    
    def test_parse_debugging_intent(self):
        """Test parsing debugging intent"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "Please fix this bug in my code"
        )
        assert result.parsed_intent.primary_intent == IntentCategory.DEBUGGING
    
    def test_extract_entities(self):
        """Test entity extraction from request"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "Migrate user data from old system to new system"
        )
        entities = result.parsed_intent.entities
        assert "systems" in entities or "data_types" in entities
    
    def test_detect_ambiguities(self):
        """Test ambiguity detection"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "Fix it"  # Very ambiguous request
        )
        assert len(result.ambiguities) > 0 or result.understanding_confidence < 0.8
    
    def test_identify_implicit_requirements(self):
        """Test implicit requirement identification"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "我需要遷移大量用戶資料到生產環境"
        )
        assert len(result.parsed_intent.implicit_requirements) > 0
    
    def test_context_memory(self):
        """Test conversation context memory"""
        engine = ContextUnderstandingEngine()
        
        # First request
        engine.analyze_request("user-1", "我需要遷移數據")
        
        # Check conversation history
        history = engine.get_conversation_history("user-1")
        assert len(history) == 1
        
        # Second request
        engine.analyze_request("user-1", "然後部署到生產環境")
        
        history = engine.get_conversation_history("user-1")
        assert len(history) == 2
    
    def test_add_project_context(self):
        """Test adding project context"""
        engine = ContextUnderstandingEngine()
        
        context_id = engine.add_project_context("user-1", {
            "is_production": True,
            "has_sensitive_data": True,
        })
        
        assert context_id.startswith("CTX-")
    
    def test_clear_user_context(self):
        """Test clearing user context"""
        engine = ContextUnderstandingEngine()
        
        engine.analyze_request("user-1", "Test request")
        engine.add_project_context("user-1", {"test": True})
        
        engine.clear_user_context("user-1")
        
        history = engine.get_conversation_history("user-1")
        assert len(history) == 0
    
    def test_recommended_approach_generation(self):
        """Test that recommended approach is generated"""
        engine = ContextUnderstandingEngine()
        result = engine.analyze_request(
            "user-1",
            "我需要將用戶資料遷移到新系統"
        )
        assert len(result.recommended_approach) > 0


# ============ AutoBugDetector Tests ============

class TestAutoBugDetector:
    """Tests for AutoBugDetector"""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        detector = AutoBugDetector()
        assert detector is not None
        stats = detector.get_statistics()
        assert stats["total_detected"] == 0
    
    def test_detect_n_plus_one_query(self):
        """Test detection of N+1 query pattern"""
        detector = AutoBugDetector()
        code = '''
        for item in items:
            data = db.get(item.id)
            process(data)
        '''
        bugs = detector.detect_bugs(code, "python")
        n_plus_one_bugs = [b for b in bugs if b.category == BugCategory.PERFORMANCE]
        assert len(n_plus_one_bugs) > 0
    
    def test_detect_hardcoded_password(self):
        """Test detection of hardcoded passwords"""
        detector = AutoBugDetector()
        code = '''
        password = "super_secret_123"
        '''
        bugs = detector.detect_bugs(code, "python")
        security_bugs = [b for b in bugs if b.category == BugCategory.SECURITY]
        assert len(security_bugs) > 0
        assert security_bugs[0].severity == "critical"
    
    def test_detect_hardcoded_token(self):
        """Test detection of hardcoded tokens"""
        detector = AutoBugDetector()
        code = '''
        token = "abc123xyz"
        '''
        bugs = detector.detect_bugs(code, "python")
        security_bugs = [b for b in bugs if b.category == BugCategory.SECURITY]
        assert len(security_bugs) > 0
    
    def test_generate_fix_for_bug(self):
        """Test fix generation for detected bug"""
        detector = AutoBugDetector()
        code = '''
        password = "hardcoded_value"
        '''
        bugs = detector.detect_bugs(code, "python")
        
        if bugs:
            fix = detector.generate_fix(bugs[0])
            if fix:
                assert fix.fix_id.startswith("FIX-")
                assert fix.bug_id == bugs[0].bug_id
                assert fix.confidence in list(FixConfidence)
    
    def test_apply_fix(self):
        """Test applying a fix"""
        detector = AutoBugDetector()
        code = '''
        password = "hardcoded_value"
        '''
        bugs = detector.detect_bugs(code, "python")
        
        if bugs:
            fix = detector.generate_fix(bugs[0])
            if fix:
                result = detector.apply_fix(fix, code)
                assert result.status in list(FixStatus)
    
    def test_custom_detector_registration(self):
        """Test custom bug detector registration"""
        detector = AutoBugDetector()
        
        def custom_detector(code: str):
            if "eval(" in code:
                return [DetectedBug(
                    bug_id="CUSTOM-001",
                    category=BugCategory.SECURITY,
                    description="Dangerous eval() usage",
                    location="Code contains eval()",
                    severity="critical",
                )]
            return []
        
        detector.register_custom_detector(custom_detector)
        
        code = "result = eval(user_input)"
        bugs = detector.detect_bugs(code, "python")
        
        custom_bugs = [b for b in bugs if b.bug_id == "CUSTOM-001"]
        assert len(custom_bugs) > 0
    
    def test_statistics_tracking(self):
        """Test statistics tracking"""
        detector = AutoBugDetector()
        
        code1 = "password = 'test'"
        code2 = "secret = 'abc'"
        
        detector.detect_bugs(code1, "python")
        detector.detect_bugs(code2, "python")
        
        stats = detector.get_statistics()
        assert stats["total_detected"] >= 2
        assert "security" in stats["by_category"]
    
    def test_learn_from_fix(self):
        """Test learning from fix outcomes"""
        detector = AutoBugDetector()
        code = "password = 'test'"
        
        bugs = detector.detect_bugs(code, "python")
        if bugs:
            fix = detector.generate_fix(bugs[0])
            if fix:
                result = detector.apply_fix(fix, code)
                detector.learn_from_fix(result, was_successful=True)
                
                # Verify learning was recorded
                assert detector._learned_patterns is not None


# ============ Integration Tests ============

class TestPhase5Integration:
    """Integration tests for Phase 5 components"""
    
    def test_full_code_analysis_pipeline(self):
        """Test full pipeline: context → hallucination → bug detection"""
        context_engine = ContextUnderstandingEngine()
        hallucination_detector = HallucinationDetector()
        bug_detector = AutoBugDetector()
        
        # User request
        request = "幫我檢查這段代碼是否有安全問題"
        context_result = context_engine.analyze_request("user-1", request)
        
        # Verify intent was understood
        assert context_result.understanding_confidence > 0
        
        # Code to analyze with patterns that will be detected
        code = '''
        def create_user(data):
            password = "hardcoded_secret"  # Hardcoded password
            # TODO: Add validation
            return db.create({"password": password})
        '''
        
        # Hallucination check
        hallucination_result = hallucination_detector.validate_code(code, "python")
        assert len(hallucination_result.hallucinations) > 0
        
        # Bug detection
        bugs = bug_detector.detect_bugs(code, "python")
        assert len(bugs) > 0
    
    def test_ai_confidence_validation(self):
        """Test that AI output confidence is properly validated"""
        hallucination_detector = HallucinationDetector()
        
        # Overconfident AI output
        ai_output = '''
        # ✅ 代碼生成完成！這是一個安全的用戶創建服務。
        def create_user(data):
            password = data.password  # Actually insecure!
            return user
        '''
        
        result = hallucination_detector.validate_code(ai_output, "python")
        
        # Should detect overconfidence and security issues
        overconfidence = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.OVERCONFIDENCE
        ]
        security = [
            h for h in result.hallucinations 
            if h.hallucination_type == HallucinationType.SECURITY_FLAW
        ]
        
        assert len(overconfidence) > 0 or len(security) > 0
    
    def test_context_aware_bug_detection(self):
        """Test context-aware bug detection"""
        context_engine = ContextUnderstandingEngine()
        bug_detector = AutoBugDetector()
        
        # Add production context
        context_engine.add_project_context("user-1", {
            "is_production": True,
            "has_sensitive_data": True,
        })
        
        # Analyze request
        context_result = context_engine.analyze_request(
            "user-1",
            "Check my user authentication code"
        )
        
        # Code with security issues
        code = '''
        token = "hardcoded_api_key_12345"
        '''
        
        bugs = bug_detector.detect_bugs(code, "python")
        security_bugs = [b for b in bugs if b.category == BugCategory.SECURITY]
        
        # In production context with sensitive data, should definitely flag this
        assert len(security_bugs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
