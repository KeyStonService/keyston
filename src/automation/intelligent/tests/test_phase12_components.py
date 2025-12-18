"""
Tests for Phase 12: GitHub Issues CI Error Auto-Handler System
"""

import pytest
from datetime import datetime, timedelta

# Import Phase 12 components
import sys
sys.path.insert(0, '/home/runner/work/SynergyMesh/SynergyMesh')

from core.ci_error_handler.ci_error_analyzer import (
    CIErrorAnalyzer, ErrorCategory, ErrorSeverity, CIError, ErrorPattern
)
from core.ci_error_handler.issue_manager import (
    IssueManager, IssueTemplate, IssueStatus, CIIssue
)
from core.ci_error_handler.auto_fix_engine import (
    AutoFixEngine, FixStrategy, FixResult, FixAttempt, FixRule
)
from core.ci_error_handler.fix_status_tracker import (
    FixStatusTracker, FixStatus, FixMetrics, FixHistory
)


# ============ CI Error Analyzer Tests ============

class TestCIErrorAnalyzer:
    """Tests for CIErrorAnalyzer"""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes with default patterns"""
        analyzer = CIErrorAnalyzer()
        assert len(analyzer.patterns) > 0
    
    def test_analyze_eslint_error(self):
        """Test detecting ESLint errors"""
        analyzer = CIErrorAnalyzer()
        log = """
        src/index.ts:10:5  error  Unexpected var, use let or const instead  no-var eslint
        """
        errors = analyzer.analyze_log(log, source="github_actions")
        assert len(errors) > 0
        assert any(e.category == ErrorCategory.LINT_ERROR for e in errors)
    
    def test_analyze_jest_failure(self):
        """Test detecting Jest test failures"""
        analyzer = CIErrorAnalyzer()
        log = """
        FAIL src/components/Button.test.tsx
        """
        errors = analyzer.analyze_log(log, source="github_actions")
        assert len(errors) > 0
        assert any(e.category == ErrorCategory.TEST_FAILURE for e in errors)
    
    def test_analyze_typescript_error(self):
        """Test detecting TypeScript compilation errors"""
        analyzer = CIErrorAnalyzer()
        log = """
        error TS2304: Cannot find name 'undefined_variable'
        """
        errors = analyzer.analyze_log(log, source="github_actions")
        assert len(errors) > 0
        assert any(e.category == ErrorCategory.TYPE_ERROR for e in errors)
    
    def test_analyze_npm_dependency_error(self):
        """Test detecting NPM dependency errors"""
        analyzer = CIErrorAnalyzer()
        log = """
        npm ERR! ERESOLVE could not resolve peer dependency
        """
        errors = analyzer.analyze_log(log, source="github_actions")
        assert len(errors) > 0
        assert any(e.category == ErrorCategory.DEPENDENCY_ERROR for e in errors)
    
    def test_auto_fixable_detection(self):
        """Test detecting auto-fixable errors"""
        analyzer = CIErrorAnalyzer()
        log = "10:5 error Missing semicolon eslint"
        errors = analyzer.analyze_log(log)
        auto_fixable = analyzer.get_auto_fixable_errors(errors)
        assert len(auto_fixable) > 0
    
    def test_error_summary(self):
        """Test error summary generation"""
        analyzer = CIErrorAnalyzer()
        log = """
        error TS2304: Cannot find name 'x'
        FAIL src/test.test.tsx
        """
        errors = analyzer.analyze_log(log)
        summary = analyzer.summarize_errors(errors)
        assert 'total' in summary
        assert 'by_category' in summary
    
    def test_custom_pattern(self):
        """Test adding custom patterns"""
        analyzer = CIErrorAnalyzer()
        custom = ErrorPattern(
            pattern_id="custom_error",
            category=ErrorCategory.BUILD_ERROR,
            regex=r"CUSTOM_ERROR_PATTERN",
            severity=ErrorSeverity.HIGH,
            description="Custom error"
        )
        analyzer.add_pattern(custom)
        
        log = "CUSTOM_ERROR_PATTERN detected"
        errors = analyzer.analyze_log(log)
        assert any(e.title == "Custom error" for e in errors)


# ============ Issue Manager Tests ============

class TestIssueManager:
    """Tests for IssueManager"""
    
    def test_manager_initialization(self):
        """Test manager initializes with default template"""
        manager = IssueManager()
        assert 'default' in manager.templates
    
    def test_create_issue_content(self):
        """Test creating issue content from error"""
        manager = IssueManager()
        error = CIError(
            error_id="ERR-001",
            category=ErrorCategory.BUILD_ERROR,
            severity=ErrorSeverity.HIGH,
            title="Build failed",
            message="npm run build failed"
        )
        workflow_info = {
            'workflow_name': 'CI',
            'run_id': '123',
            'url': 'https://github.com/test/repo/actions/runs/123',
            'branch': 'main',
            'commit_sha': 'abc123'
        }
        
        content = manager.create_issue_content(error, workflow_info)
        assert 'title' in content
        assert 'body' in content
        assert 'labels' in content
    
    def test_register_issue(self):
        """Test registering a new issue"""
        manager = IssueManager()
        error = CIError(
            error_id="ERR-002",
            category=ErrorCategory.TEST_FAILURE,
            severity=ErrorSeverity.MEDIUM,
            title="Test failed",
            message="Test assertion failed"
        )
        
        issue = manager.register_issue(error, {}, issue_id=123)
        assert issue.issue_id == 123
        assert issue.status == IssueStatus.OPEN
    
    def test_update_status(self):
        """Test updating issue status"""
        manager = IssueManager()
        error = CIError(
            error_id="ERR-003",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error"
        )
        
        manager.register_issue(error, {})
        updated = manager.update_status("ERR-003", IssueStatus.RESOLVED)
        assert updated is not None
        assert updated.status == IssueStatus.RESOLVED
    
    def test_add_fix_attempt(self):
        """Test adding fix attempt to issue"""
        manager = IssueManager()
        error = CIError(
            error_id="ERR-004",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error"
        )
        
        manager.register_issue(error, {})
        fix_info = {'method': 'auto_fix', 'command': 'npm run lint -- --fix'}
        updated = manager.add_fix_attempt("ERR-004", fix_info)
        assert len(updated.fix_attempts) == 1
    
    def test_duplicate_detection(self):
        """Test detecting duplicate issues"""
        manager = IssueManager()
        error1 = CIError(
            error_id="ERR-005",
            category=ErrorCategory.BUILD_ERROR,
            severity=ErrorSeverity.HIGH,
            title="Build failed",
            message="npm run build failed in src/index.ts",
            file_path="src/index.ts"
        )
        error2 = CIError(
            error_id="ERR-006",
            category=ErrorCategory.BUILD_ERROR,
            severity=ErrorSeverity.HIGH,
            title="Build failed",
            message="npm run build failed in src/index.ts again",
            file_path="src/index.ts"
        )
        
        manager.register_issue(error1, {})
        duplicate = manager.check_duplicate(error2)
        assert duplicate is not None
    
    def test_get_statistics(self):
        """Test getting issue statistics"""
        manager = IssueManager()
        for i in range(3):
            error = CIError(
                error_id=f"ERR-{i}",
                category=ErrorCategory.BUILD_ERROR,
                severity=ErrorSeverity.HIGH,
                title=f"Error {i}",
                message=f"Error message {i}"
            )
            manager.register_issue(error, {})
        
        stats = manager.get_statistics()
        assert stats['total'] == 3


# ============ Auto Fix Engine Tests ============

class TestAutoFixEngine:
    """Tests for AutoFixEngine"""
    
    def test_engine_initialization(self):
        """Test engine initializes with default rules"""
        engine = AutoFixEngine()
        assert len(engine.rules) > 0
    
    def test_analyze_fix_options(self):
        """Test analyzing fix options for error"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-001",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="ESLint error",
            message="Missing semicolon eslint"
        )
        
        options = engine.analyze_fix_options(error)
        assert 'matching_rules' in options
        assert 'recommended_strategy' in options
    
    def test_generate_fix_suggestion(self):
        """Test generating fix suggestion"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-002",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Prettier error",
            message="Code style Prettier formatting issue"
        )
        
        result = engine.generate_fix_suggestion(error)
        assert isinstance(result, FixResult)
    
    def test_create_fix_attempt(self):
        """Test creating fix attempt"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-003",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error"
        )
        
        attempt = engine.create_fix_attempt(
            error,
            FixStrategy.AUTO_FIX,
            "Auto-fix ESLint errors",
            files_modified=["src/index.ts"]
        )
        
        assert attempt.error_id == "ERR-003"
        assert attempt.strategy == FixStrategy.AUTO_FIX
    
    def test_record_attempt_result(self):
        """Test recording attempt result"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-004",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error"
        )
        
        attempt = engine.create_fix_attempt(
            error,
            FixStrategy.CREATE_PR,
            "Create fix PR"
        )
        
        updated = engine.record_attempt_result(
            attempt.attempt_id,
            success=True,
            pr_number=123,
            pr_url="https://github.com/test/repo/pull/123"
        )
        
        assert updated.success is True
        assert updated.pr_number == 123
    
    def test_generate_fix_pr_content(self):
        """Test generating PR content"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-005",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error",
            file_path="src/index.ts"
        )
        
        content = engine.generate_fix_pr_content(
            error,
            "Fixed lint error",
            "- let x = 1;\n+ const x = 1;"
        )
        
        assert 'branch_name' in content
        assert 'title' in content
        assert 'body' in content
    
    def test_custom_fix_rule(self):
        """Test adding custom fix rule"""
        engine = AutoFixEngine()
        custom_rule = FixRule(
            rule_id="custom_rule",
            category=ErrorCategory.BUILD_ERROR,
            pattern=r"CUSTOM_BUILD_ERROR",
            fix_command="custom-fix-command",
            fix_description="Custom fix"
        )
        engine.add_rule(custom_rule)
        
        error = CIError(
            error_id="ERR-006",
            category=ErrorCategory.BUILD_ERROR,
            severity=ErrorSeverity.HIGH,
            title="Build error",
            message="CUSTOM_BUILD_ERROR occurred"
        )
        
        options = engine.analyze_fix_options(error)
        assert any(r['rule_id'] == 'custom_rule' for r in options['matching_rules'])
    
    def test_get_statistics(self):
        """Test getting fix statistics"""
        engine = AutoFixEngine()
        error = CIError(
            error_id="ERR-007",
            category=ErrorCategory.LINT_ERROR,
            severity=ErrorSeverity.LOW,
            title="Lint error",
            message="ESLint error"
        )
        
        engine.create_fix_attempt(error, FixStrategy.AUTO_FIX, "Fix")
        stats = engine.get_statistics()
        assert stats['total'] == 1


# ============ Fix Status Tracker Tests ============

class TestFixStatusTracker:
    """Tests for FixStatusTracker"""
    
    def test_tracker_initialization(self):
        """Test tracker initialization"""
        tracker = FixStatusTracker()
        assert tracker._tracked_fixes == {}
    
    def test_start_tracking(self):
        """Test starting fix tracking"""
        tracker = FixStatusTracker()
        tracked = tracker.start_tracking(
            error_id="ERR-001",
            error_category="lint_error",
            issue_number=123
        )
        
        assert tracked.error_id == "ERR-001"
        assert tracked.status == FixStatus.PENDING
        assert len(tracked.history) == 1
    
    def test_update_status(self):
        """Test updating fix status"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-002", "build_error")
        
        updated = tracker.update_status(
            "ERR-002",
            FixStatus.IN_PROGRESS,
            "Fix attempt started"
        )
        
        assert updated.status == FixStatus.IN_PROGRESS
        assert len(updated.history) == 2
    
    def test_link_pr(self):
        """Test linking PR to fix"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-003", "lint_error")
        
        updated = tracker.link_pr(
            "ERR-003",
            pr_number=456,
            pr_url="https://github.com/test/repo/pull/456"
        )
        
        assert updated.pr_number == 456
        assert updated.status == FixStatus.PR_CREATED
    
    def test_mark_pr_merged(self):
        """Test marking PR as merged"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-004", "test_failure")
        tracker.link_pr("ERR-004", 789, "https://github.com/test/repo/pull/789")
        
        updated = tracker.mark_pr_merged(
            "ERR-004",
            commit_sha="abc123",
            merged_by="test_user"
        )
        
        assert updated.status == FixStatus.PR_MERGED
        assert updated.resolved_by == "test_user"
    
    def test_mark_verified(self):
        """Test marking fix as verified"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-005", "security_scan")
        
        updated = tracker.mark_verified("ERR-005", "CI passed")
        
        assert updated.status == FixStatus.VERIFIED
        assert updated.verification_status == "verified"
    
    def test_mark_failed(self):
        """Test marking fix as failed"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-006", "deployment_error")
        
        updated = tracker.mark_failed("ERR-006", "Deployment still failing")
        
        assert updated.status == FixStatus.FAILED
        assert updated.verification_status == "failed"
    
    def test_get_pending_fixes(self):
        """Test getting pending fixes"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-007", "lint_error")
        tracker.start_tracking("ERR-008", "build_error")
        tracker.mark_verified("ERR-008", "Fixed")
        
        pending = tracker.get_pending_fixes()
        assert len(pending) == 1
        assert pending[0].error_id == "ERR-007"
    
    def test_calculate_metrics(self):
        """Test calculating fix metrics"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-009", "lint_error")
        tracker.start_tracking("ERR-010", "build_error")
        tracker.mark_verified("ERR-009", "Fixed")
        tracker.mark_failed("ERR-010", "Failed")
        
        metrics = tracker.calculate_metrics()
        assert metrics.total_errors == 2
        assert metrics.successful_fixes == 1
        assert metrics.failed_fixes == 1
    
    def test_generate_summary_report(self):
        """Test generating summary report"""
        tracker = FixStatusTracker()
        tracker.start_tracking("ERR-011", "test_failure")
        tracker.mark_verified("ERR-011", "Fixed")
        
        report = tracker.generate_summary_report()
        assert 'metrics' in report
        assert 'pending_count' in report
        assert 'resolved_count' in report


# ============ Integration Tests ============

class TestPhase12Integration:
    """Integration tests for Phase 12 components"""
    
    def test_full_ci_error_flow(self):
        """Test full flow from error detection to fix tracking"""
        # 1. Analyze error
        analyzer = CIErrorAnalyzer()
        log = "error TS2304: Cannot find name 'undefined_var'"
        errors = analyzer.analyze_log(log)
        assert len(errors) > 0
        error = errors[0]
        
        # 2. Create issue
        manager = IssueManager()
        workflow_info = {
            'workflow_name': 'CI',
            'run_id': '123',
            'url': 'https://example.com',
            'branch': 'main',
            'commit_sha': 'abc'
        }
        issue = manager.register_issue(error, workflow_info, issue_id=100)
        assert issue.issue_id == 100
        
        # 3. Generate fix suggestion
        engine = AutoFixEngine()
        suggestion = engine.generate_fix_suggestion(error)
        assert isinstance(suggestion, FixResult)
        
        # 4. Track fix
        tracker = FixStatusTracker()
        tracked = tracker.start_tracking(
            error.error_id,
            error.category.value,
            issue.issue_id
        )
        
        # 5. Create and record fix attempt
        attempt = engine.create_fix_attempt(
            error,
            FixStrategy.CREATE_PR,
            "Fix type error"
        )
        tracker.add_attempt(error.error_id, attempt)
        
        # 6. Link PR
        tracker.link_pr(error.error_id, 200, "https://github.com/test/pull/200")
        
        # 7. Mark merged and verified
        tracker.mark_pr_merged(error.error_id, "def456", "developer")
        tracker.mark_verified(error.error_id, "CI passed")
        
        # 8. Update issue status
        manager.update_status(error.error_id, IssueStatus.RESOLVED)
        
        # Verify final state
        final_tracked = tracker.get_tracked_fix(error.error_id)
        assert final_tracked.status == FixStatus.VERIFIED
        
        final_issue = manager.get_issue(error.error_id)
        assert final_issue.status == IssueStatus.RESOLVED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
