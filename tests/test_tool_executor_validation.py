#!/usr/bin/env python3
"""
Tests for CodeRunner validation logic - context-aware security checks
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from core.island_ai_runtime.tool_executor import (
    CodeRunner,
    ExecutionRequest,
    ToolType,
)


def create_request(code: str, language: str = "python") -> ExecutionRequest:
    """Helper to create ExecutionRequest with required parameters"""
    return ExecutionRequest(
        tool_type=ToolType.CODE_RUNNER, command=code, environment={"language": language}
    )


class TestPythonValidation:
    """Test context-aware validation for Python code"""

    def setup_method(self):
        """Setup for each test"""
        self.runner = CodeRunner()

    def test_safe_string_with_metacharacters(self):
        """String literals with shell metacharacters should be allowed"""
        code = 'print("a && b")'
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow string with &&: {reason}"

    def test_safe_string_with_pipes(self):
        """String literals with pipe characters should be allowed"""
        code = 'text = "command | grep something"'
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow string with pipe: {reason}"

    def test_comment_with_metacharacters(self):
        """Comments with shell metacharacters should be allowed"""
        code = """
# This explains: use && to chain commands
print("hello")
"""
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow comments with metacharacters: {reason}"

    def test_dangerous_eval(self):
        """Actual eval() calls should be blocked"""
        code = 'eval("print(1)")'
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block eval()"
        assert "eval" in reason.lower()

    def test_dangerous_exec(self):
        """Actual exec() calls should be blocked"""
        code = 'exec("x = 1")'
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block exec()"
        assert "exec" in reason.lower()

    def test_dangerous_os_system(self):
        """os.system calls should be blocked"""
        code = """
import os
os.system("ls")
"""
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block os.system()"
        assert "os.system" in reason.lower()

    def test_dangerous_subprocess_call(self):
        """subprocess.call should be blocked"""
        code = """
import subprocess
subprocess.call(["ls"])
"""
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block subprocess.call()"
        assert "subprocess.call" in reason.lower()

    def test_safe_normal_code(self):
        """Normal safe Python code should be allowed"""
        code = """
def greet(name):
    return f"Hello, {name}"

result = greet("World")
print(result)
"""
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow safe code: {reason}"

    def test_code_too_long(self):
        """Code exceeding length limit should be blocked"""
        code = "x = 1\n" * 10000  # Over 5000 chars
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block code that's too long"
        assert "too long" in reason.lower()

    def test_invalid_syntax(self):
        """Invalid Python syntax should be blocked"""
        code = "print(unclosed"
        request = create_request(code, "python")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block invalid syntax"
        assert "syntax" in reason.lower()


class TestJavaScriptValidation:
    """Test context-aware validation for JavaScript/Node.js code"""

    def setup_method(self):
        """Setup for each test"""
        self.runner = CodeRunner()

    def test_safe_string_with_metacharacters(self):
        """String literals with shell metacharacters should be allowed"""
        code = 'console.log("a && b");'
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow string with &&: {reason}"

    def test_comment_with_metacharacters(self):
        """Comments with shell metacharacters should be allowed"""
        code = """
// This is about && operators
console.log("hello");
"""
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow comments with metacharacters: {reason}"

    def test_multiline_comment_with_metacharacters(self):
        """Multi-line comments with shell metacharacters should be allowed"""
        code = """
/*
 * Command chaining with && and ||
 * is common in shell scripts
 */
console.log("hello");
"""
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow multi-line comments: {reason}"

    def test_dangerous_child_process(self):
        """child_process require should be blocked"""
        code = """
const cp = require('child_process');
cp.exec('ls');
"""
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block child_process"
        # The validation catches the dangerous .exec() call
        assert "exec" in reason.lower() or "child_process" in reason.lower()

    def test_dangerous_eval(self):
        """eval() calls should be blocked"""
        code = 'eval("console.log(1)");'
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block eval()"
        assert "eval" in reason.lower()

    def test_safe_normal_code(self):
        """Normal safe JavaScript code should be allowed"""
        code = """
function greet(name) {
    return `Hello, ${name}`;
}

const result = greet("World");
console.log(result);
"""
        request = create_request(code, "node")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow safe code: {reason}"


class TestBashValidation:
    """Test strict validation for Bash scripts"""

    def setup_method(self):
        """Setup for each test"""
        self.runner = CodeRunner()

    def test_safe_simple_command(self):
        """Simple safe bash commands should be allowed"""
        code = "echo 'hello world'"
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow simple echo: {reason}"

    def test_comment_with_metacharacters(self):
        """Comments with metacharacters in bash should be allowed"""
        code = """
# This shows how to use && operator
echo 'hello'
"""
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert valid, f"Should allow bash comments: {reason}"

    def test_dangerous_command_chaining(self):
        """Command chaining with && should be blocked in bash"""
        code = "echo 'hello' && cat /etc/passwd"
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block && in bash commands"

    def test_dangerous_piping(self):
        """Piping commands should be blocked"""
        code = "cat file.txt | grep secret"
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block pipe in bash"

    def test_dangerous_rm_rf(self):
        """Dangerous rm -rf should be blocked"""
        code = "rm -rf /"
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block rm -rf /"

    def test_dangerous_fork_bomb(self):
        """Fork bomb should be blocked"""
        code = ":(){ :|:& };:"
        request = create_request(code, "bash")
        valid, reason = self.runner.validate(request)
        assert not valid, "Should block fork bomb"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
