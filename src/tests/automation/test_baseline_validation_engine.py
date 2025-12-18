#!/usr/bin/env python3
"""
Unit tests for BaselineValidationEngine
"""

import subprocess
import unittest
from unittest.mock import Mock, mock_open, patch

from tools.automation.engines.baseline_validation_engine import (
    STATUS_EMOJI,
    BaselineValidationEngine,
    Status,
    ValidationResult,
    get_status_emoji,
)


class TestStatusConstants(unittest.TestCase):
    """Test Status constants and emoji mapping"""

    def test_status_constants_exist(self):
        """Test that Status class has required constants"""
        self.assertEqual(Status.PASS, "PASS")
        self.assertEqual(Status.FAIL, "FAIL")
        self.assertEqual(Status.WARN, "WARN")

    def test_status_emoji_mapping_complete(self):
        """Test that all status constants have emoji mappings"""
        self.assertIn(Status.PASS, STATUS_EMOJI)
        self.assertIn(Status.FAIL, STATUS_EMOJI)
        self.assertIn(Status.WARN, STATUS_EMOJI)

    def test_get_status_emoji_pass(self):
        """Test emoji retrieval for PASS status"""
        self.assertEqual(get_status_emoji(Status.PASS), "✅")

    def test_get_status_emoji_fail(self):
        """Test emoji retrieval for FAIL status"""
        self.assertEqual(get_status_emoji(Status.FAIL), "❌")

    def test_get_status_emoji_warn(self):
        """Test emoji retrieval for WARN status"""
        self.assertEqual(get_status_emoji(Status.WARN), "⚠️")

    def test_get_status_emoji_unknown(self):
        """Test emoji retrieval for unknown status returns empty string"""
        self.assertEqual(get_status_emoji("UNKNOWN"), "")


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass"""

    def test_validation_result_creation(self):
        """Test ValidationResult can be created with required fields"""
        result = ValidationResult(
            check_name="test_check", status=Status.PASS, message="Test message"
        )
        self.assertEqual(result.check_name, "test_check")
        self.assertEqual(result.status, Status.PASS)
        self.assertEqual(result.message, "Test message")
        self.assertIsInstance(result.details, dict)
        self.assertIsInstance(result.timestamp, str)

    def test_validation_result_with_details(self):
        """Test ValidationResult with custom details"""
        details = {"count": 5, "items": ["a", "b"]}
        result = ValidationResult(
            check_name="test_check", status=Status.PASS, message="Test message", details=details
        )
        self.assertEqual(result.details, details)

    def test_validation_result_with_auto_fix(self):
        """Test ValidationResult with auto-fix suggestions"""
        result = ValidationResult(
            check_name="test_check",
            status=Status.FAIL,
            message="Test failure",
            auto_fix_suggestion="Run this command",
            remediation_command="kubectl apply -f fix.yaml",
        )
        self.assertEqual(result.auto_fix_suggestion, "Run this command")
        self.assertEqual(result.remediation_command, "kubectl apply -f fix.yaml")


class TestValidateNamespaceName(unittest.TestCase):
    """Test namespace name validation"""

    def test_valid_namespace_simple(self):
        """Test simple valid namespace name"""
        self.assertTrue(BaselineValidationEngine.validate_namespace_name("test"))

    def test_valid_namespace_with_hyphen(self):
        """Test valid namespace name with hyphens"""
        self.assertTrue(BaselineValidationEngine.validate_namespace_name("test-namespace"))

    def test_valid_namespace_with_numbers(self):
        """Test valid namespace name with numbers"""
        self.assertTrue(BaselineValidationEngine.validate_namespace_name("test123"))

    def test_invalid_namespace_uppercase(self):
        """Test invalid namespace with uppercase letters"""
        self.assertFalse(BaselineValidationEngine.validate_namespace_name("TestNamespace"))

    def test_invalid_namespace_start_hyphen(self):
        """Test invalid namespace starting with hyphen"""
        self.assertFalse(BaselineValidationEngine.validate_namespace_name("-test"))

    def test_invalid_namespace_end_hyphen(self):
        """Test invalid namespace ending with hyphen"""
        self.assertFalse(BaselineValidationEngine.validate_namespace_name("test-"))

    def test_invalid_namespace_too_long(self):
        """Test invalid namespace exceeding 63 characters"""
        long_name = "a" * 64
        self.assertFalse(BaselineValidationEngine.validate_namespace_name(long_name))

    def test_valid_namespace_max_length(self):
        """Test valid namespace at max length (63 chars)"""
        max_name = "a" * 63
        self.assertTrue(BaselineValidationEngine.validate_namespace_name(max_name))


class TestBaselineValidationEngine(unittest.TestCase):
    """Test BaselineValidationEngine class"""

    def test_init_creates_unique_log_file(self):
        """Test that initialization creates unique log file names"""
        engine1 = BaselineValidationEngine()
        engine2 = BaselineValidationEngine()
        # Log files should be different due to UUID
        self.assertNotEqual(engine1.log_file, engine2.log_file)
        # Both should contain the timestamp pattern
        self.assertIn("/tmp/baseline-validation-", engine1.log_file)
        self.assertIn("/tmp/baseline-validation-", engine2.log_file)
        # Both should end with .log
        self.assertTrue(engine1.log_file.endswith(".log"))
        self.assertTrue(engine2.log_file.endswith(".log"))

    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_log_writes_to_file(self, mock_print, mock_file):
        """Test that log method writes to file"""
        engine = BaselineValidationEngine()
        engine.log("Test message")
        mock_file.assert_called()
        mock_print.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_add_result_uses_status_constants(self, mock_print, mock_file):
        """Test that add_result properly uses Status constants"""
        engine = BaselineValidationEngine()
        engine.add_result("test_check", Status.PASS, "Test message")

        self.assertEqual(len(engine.validation_results), 1)
        result = engine.validation_results[0]
        self.assertEqual(result.status, Status.PASS)
        self.assertEqual(result.check_name, "test_check")
        self.assertEqual(result.message, "Test message")

    @patch("subprocess.run")
    def test_run_kubectl_success(self, mock_run):
        """Test successful kubectl command execution"""
        mock_run.return_value = Mock(returncode=0, stdout="output")
        engine = BaselineValidationEngine()
        success, output = engine.run_kubectl(["version"])

        self.assertTrue(success)
        self.assertEqual(output, "output")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_kubectl_timeout(self, mock_run):
        """Test kubectl command timeout handling"""
        mock_run.side_effect = subprocess.TimeoutExpired("kubectl", 30)
        engine = BaselineValidationEngine()
        success, output = engine.run_kubectl(["version"])

        self.assertFalse(success)
        self.assertIn("Timeout", output)

    @patch("subprocess.run")
    def test_run_kubectl_process_error(self, mock_run):
        """Test kubectl CalledProcessError handling"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "kubectl")
        engine = BaselineValidationEngine()
        success, output = engine.run_kubectl(["version"])

        self.assertFalse(success)
        self.assertIn("Process error", output)

    @patch("subprocess.run")
    def test_run_kubectl_generic_error(self, mock_run):
        """Test kubectl generic exception handling"""
        mock_run.side_effect = Exception("Generic error")
        engine = BaselineValidationEngine()
        success, output = engine.run_kubectl(["version"])

        self.assertFalse(success)
        self.assertEqual(output, "Generic error")

    def test_generate_report_uses_status_constants(self):
        """Test that generate_report correctly counts status using constants"""
        engine = BaselineValidationEngine()
        engine.validation_results = [
            ValidationResult("check1", Status.PASS, "msg1"),
            ValidationResult("check2", Status.FAIL, "msg2"),
            ValidationResult("check3", Status.WARN, "msg3"),
            ValidationResult("check4", Status.PASS, "msg4"),
        ]

        report = engine.generate_report()

        self.assertEqual(report["total_checks"], 4)
        self.assertEqual(report["passed"], 2)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["warnings"], 1)
        self.assertIn("health_score", report)
        self.assertIn("auto_evolution", report)

    def test_generate_report_with_auto_remediation(self):
        """Test that generate_report includes auto-remediation plan"""
        engine = BaselineValidationEngine()
        engine.validation_results = [
            ValidationResult("check1", Status.PASS, "msg1"),
            ValidationResult(
                "check2",
                Status.FAIL,
                "msg2",
                auto_fix_suggestion="Fix this",
                remediation_command="kubectl fix",
            ),
        ]

        report = engine.generate_report()

        self.assertEqual(report["auto_evolution"]["remediations_available"], 1)
        self.assertEqual(len(report["auto_evolution"]["remediation_plan"]), 1)
        self.assertEqual(report["auto_evolution"]["remediation_plan"][0]["suggestion"], "Fix this")

    @patch("builtins.open", new_callable=mock_open)
    @patch("subprocess.run")
    def test_check_prerequisites_fail_no_kubectl(self, mock_run, mock_file):
        """Test prerequisites check fails when kubectl is not available"""
        mock_run.return_value = Mock(returncode=1, stdout="")
        engine = BaselineValidationEngine()

        result = engine.check_prerequisites()

        self.assertFalse(result)
        # Should have one FAIL result
        self.assertTrue(any(r.status == Status.FAIL for r in engine.validation_results))


class TestUniqueFileGeneration(unittest.TestCase):
    """Test that file generation uses UUID to avoid collisions"""

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("subprocess.run")
    def test_json_report_has_unique_name(self, mock_run, mock_json_dump, mock_file):
        """Test that JSON report files have unique names"""
        # Mock successful kubectl calls
        mock_run.return_value = Mock(returncode=0, stdout='{"items":[]}')

        engine = BaselineValidationEngine()

        # Capture what filenames are used
        filenames_used = []

        def capture_filename(filename, mode):
            if "baseline-validation-" in filename and filename.endswith(".json"):
                filenames_used.append(filename)
            return mock_open()(filename, mode)

        with patch("builtins.open", side_effect=capture_filename):
            engine.run_all_validations()

        # Should have created a JSON report with unique identifier
        self.assertTrue(any(".json" in f for f in filenames_used))


if __name__ == "__main__":
    unittest.main()
