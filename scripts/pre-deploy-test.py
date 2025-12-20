#!/usr/bin/env python3
"""
MachineNativeOps Pre-deployment Test Script
部署前測試腳本
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PreDeployTester:
    """部署前測試器"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_test(self, test_name: str, test_func):
        """運行單個測試"""
        self.total_tests += 1
        logger.info(f"🧪 運行測試: {test_name}")
        
        try:
            result = test_func()
            if result:
                logger.info(f"✅ 測試通過: {test_name}")
                self.passed_tests += 1
                self.test_results.append({"name": test_name, "status": "PASS"})
            else:
                logger.error(f"❌ 測試失敗: {test_name}")
                self.test_results.append({"name": test_name, "status": "FAIL", "reason": "Test returned False"})
        except Exception as e:
            logger.error(f"❌ 測試異常: {test_name} - {str(e)}")
            self.test_results.append({"name": test_name, "status": "ERROR", "reason": str(e)})
    
    def test_core_imports(self):
        """測試核心模組導入"""
        try:
            from src.new import core
            from src.new.governance import policy_engine
            from src.new.security import auth
            from src.new.automation import workflow_engine
            return True
        except ImportError as e:
            logger.error(f"導入失敗: {e}")
            return False
    
    def test_business_imports(self):
        """測試業務模組導入"""
        try:
            from src.business import services, workflows, models, api
            return True
        except ImportError as e:
            logger.error(f"業務模組導入失敗: {e}")
            return False
    
    def test_data_models(self):
        """測試數據模型"""
        try:
            from src.business.models import (
                Project, Task, Resource, WorkflowExecution,
                BusinessMetrics, CreateProjectRequest, CreateTaskRequest
            )
            from datetime import datetime
            
            # 測試項目模型
            project = Project(
                id="test-123",
                name="Test Project",
                owner="admin"
            )
            
            # 測試任務模型
            task = Task(
                id="task-123",
                project_id="test-123",
                name="Test Task"
            )
            
            # 測試業務指標
            metrics = BusinessMetrics(
                total_projects=1,
                active_projects=1,
                total_tasks=1
            )
            
            return (project.id == "test-123" and 
                   task.project_id == "test-123" and
                   metrics.total_projects == 1)
        except Exception as e:
            logger.error(f"數據模型測試失敗: {e}")
            return False
    
    def test_api_endpoints(self):
        """測試 API 端點"""
        try:
            from src.business.api import BusinessAPI
            
            # 創建 API 實例
            api = BusinessAPI()
            
            # 檢查應用實例
            return api.app is not None
        except Exception as e:
            logger.error(f"API 端點測試失敗: {e}")
            return False
    
    def test_configuration(self):
        """測試配置文件"""
        try:
            # 檢查配置文件是否存在
            config_files = [
                "config/prod/config.yaml",
                "docker-compose.prod.yml",
                "Dockerfile",
                "requirements-prod.txt",
                ".env.example"
            ]
            
            missing_files = []
            for file_path in config_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                logger.error(f"缺少配置文件: {missing_files}")
                return False
            
            # 測試配置加載
            import yaml
            with open("config/prod/config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            
            return config is not None and 'app' in config
        except Exception as e:
            logger.error(f"配置測試失敗: {e}")
            return False
    
    def test_docker_files(self):
        """測試 Docker 文件"""
        try:
            # 檢查 Dockerfile 語法
            with open("Dockerfile", 'r') as f:
                dockerfile_content = f.read()
            
            # 基本 Dockerfile 檢查
            required_keywords = ["FROM", "WORKDIR", "COPY", "EXPOSE", "CMD"]
            for keyword in required_keywords:
                if keyword not in dockerfile_content:
                    logger.error(f"Dockerfile 缺少必要指令: {keyword}")
                    return False
            
            # 檢查 docker-compose 文件
            import yaml
            with open("docker-compose.prod.yml", 'r') as f:
                compose_config = yaml.safe_load(f)
            
            return ('services' in compose_config and 
                   'mno-business' in compose_config['services'])
        except Exception as e:
            logger.error(f"Docker 文件測試失敗: {e}")
            return False
    
    def test_scripts_permissions(self):
        """測試腳本權限"""
        try:
            scripts = [
                "scripts/deploy.sh",
                "scripts/migrate.py"
            ]
            
            for script in scripts:
                if not os.access(script, os.X_OK):
                    logger.error(f"腳本缺少執行權限: {script}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"腳本權限測試失敗: {e}")
            return False
    
    def test_dependencies(self):
        """測試依賴文件"""
        try:
            # 檢查 requirements-prod.txt
            with open("requirements-prod.txt", 'r') as f:
                requirements = f.read()
            
            required_packages = ["fastapi", "uvicorn", "pydantic", "asyncpg", "redis"]
            for package in required_packages:
                if package not in requirements:
                    logger.error(f"缺少必要依賴: {package}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"依賴測試失敗: {e}")
            return False
    
    def test_directory_structure(self):
        """測試目錄結構"""
        try:
            required_dirs = [
                "src/business",
                "src/core/new",
                "config/prod",
                "scripts"
            ]
            
            # 檢查業務文件是否存在
            required_files = [
                "src/business/services.py",
                "src/business/workflows.py", 
                "src/business/models.py",
                "src/business/api.py"
            ]
            
            missing_dirs = []
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    missing_dirs.append(dir_path)
            
            missing_files = []
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_dirs:
                logger.error(f"缺少必要目錄: {missing_dirs}")
                return False
            
            if missing_files:
                logger.error(f"缺少必要文件: {missing_files}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"目錄結構測試失敗: {e}")
            return False
    
    def test_demo_core_execution(self):
        """測試 demo_core.py 執行"""
        try:
            # 檢查 demo_core.py 文件是否存在
            if not os.path.exists("src/demo_core.py"):
                logger.error("demo_core.py 文件不存在")
                return False
            
            # 檢查文件內容是否包含必要的函數
            with open("src/demo_core.py", 'r') as f:
                content = f.read()
            
            required_functions = ["demo_basic_functionality", "core.initialize"]
            for func in required_functions:
                if func not in content:
                    logger.error(f"demo_core.py 缺少必要函數: {func}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"demo_core.py 測試失敗: {e}")
            return False
    
    def generate_report(self):
        """生成測試報告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
            },
            "results": self.test_results
        }
        
        # 保存報告到文件
        report_file = "test-results.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_all_tests(self):
        """運行所有測試"""
        logger.info("🚀 開始部署前測試...")
        logger.info("=" * 60)
        
        # 運行所有測試
        tests = [
            ("核心模組導入測試", self.test_core_imports),
            ("業務模組導入測試", self.test_business_imports),
            ("數據模型測試", self.test_data_models),
            ("API 端點測試", self.test_api_endpoints),
            ("配置文件測試", self.test_configuration),
            ("Docker 文件測試", self.test_docker_files),
            ("腳本權限測試", self.test_scripts_permissions),
            ("依賴文件測試", self.test_dependencies),
            ("目錄結構測試", self.test_directory_structure),
            ("Demo Core 測試", self.test_demo_core_execution)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        logger.info("=" * 60)
        
        # 生成報告
        report = self.generate_report()
        
        # 顯示結果
        success_rate = report["summary"]["success_rate"]
        if success_rate >= 90:
            logger.info(f"🎉 測試完成！成功率: {success_rate:.1f}%")
            logger.info("✅ 系統準備就緒，可以進行部署")
        elif success_rate >= 70:
            logger.warning(f"⚠️  測試完成！成功率: {success_rate:.1f}%")
            logger.warning("⚠️  存在一些問題，建議修復後再部署")
        else:
            logger.error(f"❌ 測試完成！成功率: {success_rate:.1f}%")
            logger.error("❌ 存在嚴重問題，不建議部署")
        
        # 顯示失敗的測試
        failed_tests = [r for r in self.test_results if r["status"] != "PASS"]
        if failed_tests:
            logger.error("失敗的測試:")
            for test in failed_tests:
                logger.error(f"  ❌ {test['name']}: {test.get('reason', 'Unknown error')}")
        
        logger.info(f"📊 詳細報告已保存到: test-results.json")
        
        return success_rate >= 90


def main():
    """主函數"""
    tester = PreDeployTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎯 下一步:")
        logger.info("1. 複製 .env.example 到 .env 並配置環境變量")
        logger.info("2. 運行部署腳本: ./scripts/deploy.sh")
        logger.info("3. 監控部署日誌: docker-compose -f docker-compose.prod.yml logs -f")
        sys.exit(0)
    else:
        logger.error("\n🛠️  請修復失敗的測試後重新運行")
        sys.exit(1)


if __name__ == "__main__":
    main()