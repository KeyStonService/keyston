#!/usr/bin/env python3
"""
Controlplane 整合測試
驗證所有 controlplane 工具和庫的實際功能
"""

import sys
import os
import subprocess
import tempfile
import logging
from pathlib import Path

# 添加 lib 到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from controlplane import ControlplaneConfig, get_config, validate_name

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_test(name):
    print(f"\n{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")

def log_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def log_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def log_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")

class ControlplaneIntegrationTests:
    """Controlplane 整合測試套件"""
    
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def _find_repo_root(self) -> Path:
        """找到儲存庫根目錄"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def run_command(self, cmd, cwd=None):
        """運行命令並返回結果"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out after 30s: {cmd}", exc_info=True)
            return False, "", f"Timeout: {str(e)}"
        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Subprocess error running command '{cmd}': {e}", exc_info=True)
            return False, "", str(e)
    
    def assert_true(self, condition, message):
        """斷言為真"""
        self.total += 1
        if condition:
            self.passed += 1
            log_success(message)
            return True
        else:
            self.failed += 1
            log_error(message)
            return False
    
    def test_python_library(self):
        """測試 Python 配置庫"""
        log_test("Python Configuration Library")
        
        try:
            # 測試創建實例
            config = ControlplaneConfig()
            self.assert_true(True, "ControlplaneConfig instance created")
            
            # 測試獲取配置
            root_config = config.get_baseline_config("root.config.yaml")
            self.assert_true(
                'metadata' in root_config,
                "Root config loaded successfully"
            )
            
            # 測試命名驗證
            is_valid, _ = config.validate_name("my-file.yaml", "file")
            self.assert_true(is_valid, "Valid file name accepted")
            
            is_valid, _ = config.validate_name("MyFile.yaml", "file")
            self.assert_true(not is_valid, "Invalid file name rejected")
            
            # 測試獲取命名規則
            naming_rules = config.get_naming_rules()
            self.assert_true(
                len(naming_rules) > 0,
                "Naming rules loaded"
            )
            
            # 測試全局實例
            global_config = get_config()
            self.assert_true(
                global_config is not None,
                "Global config instance works"
            )
            
            # 測試便捷函數
            is_valid, _ = validate_name("test-file.yaml", "file")
            self.assert_true(is_valid, "Convenience function works")
            
        except (FileNotFoundError, RuntimeError, KeyError, AttributeError) as e:
            logger.error(f"Python library test failed with expected error: {e}", exc_info=True)
            self.assert_true(False, f"Python library test failed: {e}")
        except Exception as e:
            logger.error(f"Python library test failed with unexpected error: {e}", exc_info=True)
            raise  # Re-raise unexpected exceptions to avoid masking errors
    
    def test_cli_tool(self):
        """測試 CLI 工具"""
        log_test("CLI Tool (cp-cli)")
        
        cli_path = self.repo_root / "bin" / "cp-cli"
        
        # 測試 status 命令
        success, stdout, _ = self.run_command(f"{cli_path} status")
        self.assert_true(success, "cp-cli status command works")
        self.assert_true("Controlplane" in stdout, "Status output is correct")
        
        # 測試 check-name 命令
        success, _, _ = self.run_command(f"{cli_path} check-name my-file.yaml --type file")
        self.assert_true(success, "Valid name check passes")
        
        success, _, _ = self.run_command(f"{cli_path} check-name MyFile.yaml --type file")
        self.assert_true(not success, "Invalid name check fails")
        
        # 測試 synthesize 命令
        success, _, _ = self.run_command(f"{cli_path} synthesize")
        self.assert_true(success, "Synthesize command works")
        
        active_path = self.repo_root / "controlplane" / "active"
        self.assert_true(active_path.exists(), "Active directory created")
    
    def test_shell_library(self):
        """測試 Shell 庫"""
        log_test("Shell Library (controlplane.sh)")
        
        shell_lib = self.repo_root / "lib" / "controlplane.sh"
        
        # 測試載入庫 - 使用 bash 明確執行
        test_script = f"bash -c 'source {shell_lib} && cp_check_exists && echo EXISTS'"
        
        success, stdout, stderr = self.run_command(test_script)
        self.assert_true(success, "Shell library loads successfully")
        self.assert_true("EXISTS" in stdout, "cp_check_exists works")
        
        # 測試命名驗證
        test_script = f"bash -c 'source {shell_lib} && cp_validate_name my-file.yaml file && echo VALID'"
        
        success, stdout, stderr = self.run_command(test_script)
        self.assert_true("VALID" in stdout, "Shell name validation works")
    
    def test_validation_system(self):
        """測試驗證系統"""
        log_test("Validation System")
        
        validator = self.repo_root / "controlplane" / "baseline" / "validation" / "validate-root-specs.py"
        
        # 運行驗證
        success, stdout, _ = self.run_command(f"python3 {validator}")
        self.assert_true(success, "Validation script runs successfully")
        
        # 檢查報告生成
        report_json = self.repo_root / "controlplane" / "overlay" / "evidence" / "validation" / "validation.report.json"
        report_md = self.repo_root / "controlplane" / "overlay" / "evidence" / "validation" / "validation.report.md"
        
        self.assert_true(report_json.exists(), "JSON report generated")
        self.assert_true(report_md.exists(), "Markdown report generated")
    
    def test_naming_conventions(self):
        """測試命名規範"""
        log_test("Naming Conventions")
        
        config = ControlplaneConfig()
        
        # 測試文件名
        test_cases = [
            ("my-file.yaml", "file", True),
            ("MyFile.yaml", "file", False),
            ("my_file.yaml", "file", False),
            ("my-file.backup.yaml", "file", False),
            ("root.config.yaml", "file", True),
        ]
        
        for name, name_type, expected in test_cases:
            is_valid, _ = config.validate_name(name, name_type)
            self.assert_true(
                is_valid == expected,
                f"Name '{name}' validation: expected={expected}, got={is_valid}"
            )
        
        # 測試目錄名
        test_cases = [
            ("my-directory", "directory", True),
            ("MyDirectory", "directory", False),
            ("my_directory", "directory", False),
        ]
        
        for name, name_type, expected in test_cases:
            is_valid, _ = config.validate_name(name, name_type)
            self.assert_true(
                is_valid == expected,
                f"Directory '{name}' validation: expected={expected}, got={is_valid}"
            )
        
        # 測試命名空間
        test_cases = [
            ("my-namespace", "namespace", True),
            ("my.namespace", "namespace", False),
            ("MyNamespace", "namespace", False),
        ]
        
        for name, name_type, expected in test_cases:
            is_valid, _ = config.validate_name(name, name_type)
            self.assert_true(
                is_valid == expected,
                f"Namespace '{name}' validation: expected={expected}, got={is_valid}"
            )
    
    def test_configuration_access(self):
        """測試配置訪問"""
        log_test("Configuration Access")
        
        config = ControlplaneConfig()
        
        # 測試獲取各種配置
        try:
            root_config = config.get_baseline_config("root.config.yaml")
            self.assert_true(len(root_config) > 0, "Root config accessible")
            
            naming_policy = config.get_naming_rules()
            self.assert_true(len(naming_policy) > 0, "Naming policy accessible")
            
            governance = config.get_governance_policy()
            self.assert_true(len(governance) > 0, "Governance policy accessible")
            
            trust = config.get_trust_policy()
            self.assert_true(len(trust) > 0, "Trust policy accessible")
            
        except (FileNotFoundError, RuntimeError, KeyError, AttributeError) as e:
            logger.error(f"Configuration access failed with expected error: {e}", exc_info=True)
            self.assert_true(False, f"Configuration access failed: {e}")
        except Exception as e:
            logger.error(f"Configuration access failed with unexpected error: {e}", exc_info=True)
            raise  # Re-raise unexpected exceptions to avoid masking errors
    
    def test_overlay_extension(self):
        """測試 Overlay 擴展"""
        log_test("Overlay Extension")
        
        config = ControlplaneConfig()
        
        try:
            # 創建測試擴展
            extension_file = config.create_overlay_extension(
                name="test-extension",
                extends="baseline/config/root.config.yaml",
                config={"test_setting": "test_value"}
            )
            
            self.assert_true(
                extension_file.exists(),
                "Overlay extension created"
            )
            
            # 清理
            extension_file.unlink()
            
        except (FileNotFoundError, RuntimeError, OSError, AttributeError) as e:
            logger.error(f"Overlay extension test failed with expected error: {e}", exc_info=True)
            self.assert_true(False, f"Overlay extension test failed: {e}")
        except Exception as e:
            logger.error(f"Overlay extension test failed with unexpected error: {e}", exc_info=True)
            raise  # Re-raise unexpected exceptions to avoid masking errors
    
    def test_active_synthesis(self):
        """測試 Active 視圖合成"""
        log_test("Active View Synthesis")
        
        config = ControlplaneConfig()
        
        try:
            # 合成 active 視圖
            config.synthesize_active()
            
            active_path = config.active_path
            self.assert_true(active_path.exists(), "Active directory exists")
            
            # 檢查是否有配置文件
            active_configs = list(active_path.glob("*.yaml"))
            self.assert_true(len(active_configs) > 0, "Active configs synthesized")
            
        except (FileNotFoundError, RuntimeError, OSError, AttributeError) as e:
            logger.error(f"Active synthesis failed with expected error: {e}", exc_info=True)
            self.assert_true(False, f"Active synthesis failed: {e}")
        except Exception as e:
            logger.error(f"Active synthesis failed with unexpected error: {e}", exc_info=True)
            raise  # Re-raise unexpected exceptions to avoid masking errors
    
    def test_pre_commit_hook(self):
        """測試 Pre-commit Hook"""
        log_test("Pre-commit Hook")
        
        hook_path = self.repo_root / ".githooks" / "pre-commit"
        
        self.assert_true(hook_path.exists(), "Pre-commit hook exists")
        self.assert_true(os.access(hook_path, os.X_OK), "Pre-commit hook is executable")
    
    def test_github_actions_integration(self):
        """測試 GitHub Actions 整合"""
        log_test("GitHub Actions Integration")
        
        workflow_path = self.repo_root / ".github" / "workflows" / "controlplane-integration.yml"
        
        self.assert_true(workflow_path.exists(), "Integration workflow exists")
        
        # 檢查工作流程內容
        with open(workflow_path, 'r') as f:
            content = f.read()
            self.assert_true("controlplane" in content.lower(), "Workflow uses controlplane")
            self.assert_true("cp-cli" in content or "cp_" in content, "Workflow uses controlplane tools")
    
    def run_all_tests(self):
        """運行所有測試"""
        print("=" * 70)
        print(f"{Colors.BLUE}🧪 Controlplane Integration Tests{Colors.RESET}")
        print("=" * 70)
        
        # 運行所有測試
        self.test_python_library()
        self.test_cli_tool()
        self.test_shell_library()
        self.test_validation_system()
        self.test_naming_conventions()
        self.test_configuration_access()
        self.test_overlay_extension()
        self.test_active_synthesis()
        self.test_pre_commit_hook()
        self.test_github_actions_integration()
        
        # 顯示結果
        print("\n" + "=" * 70)
        print(f"{Colors.BLUE}📊 Test Results{Colors.RESET}")
        print("=" * 70)
        print(f"Total Tests: {self.total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✅ All tests passed!{Colors.RESET}")
            return 0
        else:
            print(f"\n{Colors.RED}❌ Some tests failed{Colors.RESET}")
            return 1

def main():
    """主函數"""
    tests = ControlplaneIntegrationTests()
    return tests.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())