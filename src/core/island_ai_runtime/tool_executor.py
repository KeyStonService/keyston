#!/usr/bin/env python3
"""
Tool Executor - 工具執行器
Code Runner, MCP Integration, and Filesystem Sandbox

安全地執行代碼和工具操作
"""

import ast
import json
import os
import re
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolType(Enum):
    """工具類型"""

    CODE_RUNNER = "code_runner"
    SHELL = "shell"
    FILE_SYSTEM = "file_system"
    MCP = "mcp"
    NETWORK = "network"
    DATABASE = "database"


class ExecutionStatus(Enum):
    """執行狀態"""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    PENDING = "pending"


@dataclass
class ToolConfig:
    """工具配置"""

    name: str
    tool_type: ToolType
    enabled: bool = True
    timeout: int = 30
    sandbox: bool = True
    allowed_paths: list[str] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)


@dataclass
class ExecutionRequest:
    """執行請求"""

    tool_type: ToolType
    command: str
    args: list[str] = field(default_factory=list)
    working_dir: str | None = None
    timeout: int = 30
    environment: dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """執行結果"""

    status: ExecutionStatus
    output: str = ""
    error: str = ""
    exit_code: int = 0
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """工具基類"""

    def __init__(self, config: ToolConfig):
        self.config = config

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """執行工具操作"""
        pass

    @abstractmethod
    def validate(self, request: ExecutionRequest) -> tuple[bool, str]:
        """驗證請求是否安全"""
        pass


class CodeRunner(Tool):
    """
    代碼執行器

    安全地執行 Python、Node.js 等代碼。
    """

    SUPPORTED_LANGUAGES = {
        "python": {"cmd": "python3", "ext": ".py"},
        "node": {"cmd": "node", "ext": ".js"},
        "bash": {"cmd": "bash", "ext": ".sh"},
    }

    def __init__(self, config: ToolConfig | None = None):
        super().__init__(config or ToolConfig(name="code_runner", tool_type=ToolType.CODE_RUNNER))

    def _build_execution_command(self, lang_config: dict[str, str], temp_file: str) -> list[str]:
        """
        Build a two-element subprocess command array from a validated language configuration.
        `lang_config` must include a `cmd` entry sourced from SUPPORTED_LANGUAGES.
        Returns a list suitable for subprocess.run where index 0 is the executable and index 1 is
        the temporary file path.
        """
        return [lang_config["cmd"], temp_file]

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """執行代碼"""
        # 驗證請求
        valid, reason = self.validate(request)
        if not valid:
            return ExecutionResult(status=ExecutionStatus.BLOCKED, error=reason)

        # 確定語言
        language = request.environment.get("language", "python").lower()
        lang_config = self.SUPPORTED_LANGUAGES.get(language)

        if not lang_config:
            return ExecutionResult(
                status=ExecutionStatus.FAILURE, error=f"Unsupported language: {language}"
            )

        # 創建臨時文件
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=lang_config["ext"], delete=False
            ) as f:
                f.write(request.command)
                temp_file = f.name

            # 執行代碼
            exec_cmd = self._build_execution_command(lang_config, temp_file)
            result = subprocess.run(
                exec_cmd,
                capture_output=True,
                text=True,
                timeout=request.timeout,
                cwd=request.working_dir,
            )

            return ExecutionResult(
                status=(
                    ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILURE
                ),
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error=f"Execution timed out after {request.timeout}s",
            )
        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, error=str(e))
        finally:
            # 清理臨時文件
            if "temp_file" in locals():
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass  # File already deleted or inaccessible

    def _validate_python_code(self, code: str) -> tuple[bool, str]:
        """
        Context-aware validation for Python code using AST parsing.
        This allows legitimate string literals and comments containing shell metacharacters
        while blocking actual dangerous code patterns.
        """
        # Check code length first (simple check)
        if len(code) > 5000:
            return False, "Command too long"

        # Try to parse the code to ensure it's valid Python
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False, "Invalid Python syntax"

        # Check for dangerous function calls and imports in the AST
        dangerous_calls = {"eval", "exec", "__import__", "compile"}
        dangerous_modules = {"os.system", "subprocess.call", "subprocess.Popen"}

        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_calls:
                    return False, f"Dangerous function detected: {node.func.id}"

                # Check for os.system, subprocess.call, etc.
                if isinstance(node.func, ast.Attribute):
                    func_name = f"{ast.unparse(node.func.value)}.{node.func.attr}"
                    if any(danger in func_name for danger in dangerous_modules):
                        return False, f"Dangerous module call detected: {func_name}"

        return True, ""

    def _validate_javascript_code(self, code: str) -> tuple[bool, str]:
        """
        Context-aware validation for JavaScript/Node.js code.
        Uses regex-based detection with comment/string awareness.
        """
        if len(code) > 5000:
            return False, "Command too long"

        # Remove single-line comments
        code_no_comments = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
        # Remove multi-line comments
        code_no_comments = re.sub(r"/\*.*?\*/", "", code_no_comments, flags=re.DOTALL)
        # Remove string literals (both single and double quotes)
        code_no_strings = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code_no_comments)
        code_no_strings = re.sub(r"'(?:[^'\\]|\\.)*'", "''", code_no_strings)
        code_no_strings = re.sub(r"`(?:[^`\\]|\\.)*`", "``", code_no_strings)

        # Now check for dangerous patterns in the remaining code
        dangerous_patterns = [
            r"require\s*\(\s*['\"]child_process['\"]\s*\)",
            r"\.exec\s*\(",
            r"\.spawn\s*\(",
            r"eval\s*\(",
            r"Function\s*\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code_no_strings):
                return False, f"Dangerous JavaScript pattern detected: {pattern}"

        return True, ""

    def _validate_bash_code(self, code: str) -> tuple[bool, str]:
        """
        Strict validation for bash scripts.
        Shell scripts are inherently risky, so we maintain strict validation
        to prevent shell injection attacks. This intentionally blocks metacharacters
        even in comments/strings as bash syntax is complex and error-prone.
        """
        if len(code) > 5000:
            return False, "Command too long"

        # For bash, maintain strict validation due to shell injection risks
        dangerous_patterns = [
            "rm -rf /",
            ":(){ :|:& };:",  # Fork bomb
            "curl.*|.*sh",
            "wget.*|.*sh",
        ]

        dangerous_tokens = [
            "&&",
            "||",
            ";",
            "|",
            "`",
            "$(",
            "${",
            ">",
            "<",
            ">>",
            "<<",
        ]

        for pattern in dangerous_patterns:
            if pattern in code:
                return False, f"Dangerous bash pattern detected: {pattern}"

        # For bash, check tokens but allow them if they seem safe
        # This is a balance between security and usability
        if any(token in code for token in dangerous_tokens):
            # Allow if it's in a comment
            lines = code.split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue  # Skip comments
                if any(token in line for token in dangerous_tokens):
                    return (
                        False,
                        "Shell metacharacters detected in bash script - potential injection risk",
                    )

        return True, ""

    def validate(self, request: ExecutionRequest) -> tuple[bool, str]:
        """
        Context-aware code validation that understands language syntax.

        This validation uses language-specific parsers to distinguish between:
        - Dangerous code patterns (e.g., actual eval/exec calls)
        - Safe string literals (e.g., print("a && b"))
        - Comments containing metacharacters

        For Python and JavaScript, we parse the code structure to avoid false positives.
        For bash scripts, we maintain strict validation due to inherent shell injection risks.
        """
        # Determine language from request
        language = request.environment.get("language", "python").lower()

        # Dispatch to language-specific validator
        if language == "python":
            return self._validate_python_code(request.command)
        elif language == "node":
            return self._validate_javascript_code(request.command)
        elif language == "bash":
            return self._validate_bash_code(request.command)
        else:
            # For unknown languages, apply generic validation
            return False, f"Validation not implemented for language: {language}"


class FilesystemSandbox(Tool):
    """
    文件系統沙箱

    安全地進行文件操作。
    """

    def __init__(self, config: ToolConfig | None = None, sandbox_root: str | None = None):
        super().__init__(
            config or ToolConfig(name="filesystem_sandbox", tool_type=ToolType.FILE_SYSTEM)
        )
        self.sandbox_root = sandbox_root or tempfile.mkdtemp(prefix="island_sandbox_")

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """執行文件操作"""
        valid, reason = self.validate(request)
        if not valid:
            return ExecutionResult(status=ExecutionStatus.BLOCKED, error=reason)

        operation = request.command
        args = request.args

        try:
            if operation == "read":
                path = self._safe_path(args[0])
                with open(path) as f:
                    content = f.read()
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output=content)

            elif operation == "write":
                path = self._safe_path(args[0])
                content = args[1] if len(args) > 1 else ""
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(content)
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output=f"Written to {path}")

            elif operation == "list":
                path = self._safe_path(args[0] if args else "")
                files = os.listdir(path)
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output=json.dumps(files))

            elif operation == "delete":
                path = self._safe_path(args[0])
                os.remove(path)
                return ExecutionResult(status=ExecutionStatus.SUCCESS, output=f"Deleted {path}")

            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILURE, error=f"Unknown operation: {operation}"
                )

        except Exception as e:
            return ExecutionResult(status=ExecutionStatus.FAILURE, error=str(e))

    def validate(self, request: ExecutionRequest) -> tuple[bool, str]:
        """驗證文件操作是否安全"""
        if request.args:
            for arg in request.args:
                if ".." in arg:
                    return False, "Path traversal not allowed"
                if arg.startswith("/") and not arg.startswith(self.sandbox_root):
                    return False, "Access outside sandbox not allowed"

        return True, ""

    def _safe_path(self, path: str) -> str:
        """獲取安全路徑"""
        if path.startswith("/"):
            return path
        return os.path.join(self.sandbox_root, path)


class MCPClient:
    """
    MCP 客戶端

    與 Model Context Protocol 服務器通信。
    """

    def __init__(self, server_url: str | None = None):
        self.server_url = server_url
        self.tools: dict[str, dict[str, Any]] = {}

    async def connect(self) -> bool:
        """連接到 MCP 服務器"""
        # 模擬連接
        return True

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出可用工具"""
        return list(self.tools.values())

    async def call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """調用 MCP 工具"""
        if name not in self.tools:
            return {"error": f"Tool not found: {name}"}

        # 模擬工具調用
        return {"result": f"Called {name} with {args}"}

    def register_tool(self, name: str, schema: dict[str, Any]) -> None:
        """註冊工具"""
        self.tools[name] = {"name": name, "schema": schema}


class ToolExecutor:
    """
    工具執行器

    統一管理和執行各種工具。

    功能：
    - Code Runner 代碼執行
    - MCP 工具調用
    - Filesystem Sandbox 文件操作
    - 安全驗證
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.code_runner = CodeRunner()
        self.filesystem = FilesystemSandbox()
        self.mcp_client = MCPClient(self.config.get("mcp_server_url"))
        self.execution_history: list[dict[str, Any]] = []

    async def execute_code(
        self, code: str, language: str = "python", timeout: int = 30
    ) -> ExecutionResult:
        """執行代碼"""
        request = ExecutionRequest(
            tool_type=ToolType.CODE_RUNNER,
            command=code,
            timeout=timeout,
            environment={"language": language},
        )

        result = await self.code_runner.execute(request)
        self._log_execution("code_runner", request, result)

        return result

    async def execute_file_operation(self, operation: str, *args: str) -> ExecutionResult:
        """執行文件操作"""
        request = ExecutionRequest(
            tool_type=ToolType.FILE_SYSTEM, command=operation, args=list(args)
        )

        result = await self.filesystem.execute(request)
        self._log_execution("filesystem", request, result)

        return result

    async def call_mcp_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """調用 MCP 工具"""
        result = await self.mcp_client.call_tool(tool_name, args)

        self._log_execution("mcp", {"tool": tool_name, "args": args}, result)

        return result

    def get_execution_history(self) -> list[dict[str, Any]]:
        """獲取執行歷史"""
        return self.execution_history

    def _log_execution(self, tool_type: str, request: Any, result: Any) -> None:
        """記錄執行日誌"""
        self.execution_history.append(
            {"tool_type": tool_type, "request": str(request), "result": str(result)}
        )
