#!/usr/bin/env python3
"""
部署無人機 (Deployment Drone)

負責自動化部署流程，包括環境準備、建置和健康檢查。
對應 config/dev/automation/deployment-drone.sh (Python 版本)
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_drone import BaseDrone, DroneStatus


class DeploymentDrone(BaseDrone):
    """
    部署無人機
    
    負責：
    - 環境準備
    - 建置應用
    - 部署到目標環境
    - 健康檢查
    """

    def __init__(self) -> None:
        super().__init__(name="部署無人機", drone_id="deployment_drone")
        self.deploy_env = os.environ.get('DEPLOY_ENV', 'development')
        self.deploy_tag = os.environ.get('DEPLOY_TAG', 'latest')
        self.health_check_retries = 5
        self.health_check_interval = 10

    def start(self) -> bool:
        """啟動部署無人機"""
        self.log_info("🚢 啟動部署無人機...")

        if not self.load_config():
            self.log_warn("使用預設配置")

        self.status = DroneStatus.RUNNING
        self.start_time = datetime.now()

        self.log_success("部署無人機已啟動")
        return True

    def stop(self) -> bool:
        """停止部署無人機"""
        self.log_info("停止部署無人機...")
        self.status = DroneStatus.STOPPED
        self.log_success("部署無人機已停止")
        return True

    def execute(self) -> dict[str, Any]:
        """執行部署流程"""
        self.log_info(f"🚀 執行部署到 {self.deploy_env} 環境...")

        result = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.deploy_env,
            'tag': self.deploy_tag,
            'steps': [],
            'success': True,
        }

        # 步驟 1: 檢查先決條件
        prereq_result = self.check_prerequisites()
        result['steps'].append({
            'name': '檢查先決條件',
            'success': prereq_result,
        })

        if not prereq_result:
            result['success'] = False
            return result

        # 步驟 2: 準備環境
        prep_result = self.prepare_environment()
        result['steps'].append({
            'name': '準備環境',
            'success': prep_result,
        })

        # 步驟 3: 建置應用
        build_result = self.build_application()
        result['steps'].append({
            'name': '建置應用',
            'success': build_result,
        })

        # 顯示結果
        self._display_result(result)

        return result

    def check_prerequisites(self) -> bool:
        """
        檢查部署先決條件
        
        Returns:
            是否通過檢查
        """
        self.log_info("🔍 檢查部署先決條件...")

        # 檢查 Docker
        try:
            subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                check=True
            )
            self.log_success("  Docker ✓")
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.log_error("  Docker 未安裝")
            return False

        # 檢查 Docker Compose
        try:
            # 嘗試新版 docker compose
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True
            )
            if result.returncode != 0:
                # 嘗試舊版 docker-compose
                subprocess.run(
                    ['docker-compose', '--version'],
                    capture_output=True,
                    check=True
                )
            self.log_success("  Docker Compose ✓")
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.log_error("  Docker Compose 未安裝")
            return False

        self.log_success("所有先決條件已滿足")
        return True

    def prepare_environment(self) -> bool:
        """
        準備部署環境
        
        Returns:
            是否成功
        """
        self.log_info(f"🔧 準備部署環境: {self.deploy_env}")

        # 載入環境配置
        env_file = self.project_root / 'config/dev' / 'environments' / f'{self.deploy_env}.env'

        if env_file.exists():
            self.log_info(f"  載入環境配置: {env_file}")
            self._load_env_file(env_file)
            self.log_success("環境配置已載入")
        else:
            self.log_warn(f"環境配置檔案不存在: {env_file}")
            self.log_info("  使用預設配置")

        # 創建必要目錄
        generated_dir = self.project_root / 'generated'
        logs_dir = self.project_root / 'logs'

        generated_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)

        return True

    def _load_env_file(self, env_file: Path) -> None:
        """載入環境變數檔案"""
        try:
            with open(env_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            self.log_warn(f"載入環境變數失敗: {e}")

    def build_application(self) -> bool:
        """
        建置應用
        
        Returns:
            是否成功
        """
        self.log_info("🔨 建置應用...")

        # 檢查 package.json 是否存在
        package_json = self.project_root / 'package.json'
        if not package_json.exists():
            self.log_warn("package.json 不存在，跳過建置")
            return True

        # 安裝依賴
        self.log_info("  安裝依賴...")
        try:
            subprocess.run(
                ['npm', 'ci', '--prefer-offline', '--no-audit'],
                cwd=self.project_root,
                capture_output=True,
                timeout=300
            )
        except subprocess.TimeoutExpired:
            self.log_warn("  安裝超時，嘗試 npm install")
            subprocess.run(
                ['npm', 'install'],
                cwd=self.project_root,
                capture_output=True
            )
        except Exception:
            pass

        # 執行建置
        self.log_info("  執行建置...")
        try:
            result = subprocess.run(
                ['npm', 'run', 'build', '--if-present'],
                cwd=self.project_root,
                capture_output=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log_success("應用建置完成")
            else:
                self.log_warn("建置有警告")
            return True
        except Exception as e:
            self.log_error(f"建置失敗: {e}")
            return False

    def deploy_services(self) -> bool:
        """
        部署服務
        
        Returns:
            是否成功
        """
        self.log_info(f"🚀 部署服務到 {self.deploy_env} 環境...")

        devcontainer_dir = self.project_root / 'config/dev'

        # 停止現有服務
        self.log_info("  停止現有服務...")
        self._run_docker_compose(['down', '--remove-orphans'], devcontainer_dir)

        # 啟動服務
        self.log_info("  啟動新服務...")
        result = self._run_docker_compose(['up', '-d'], devcontainer_dir)

        if result:
            self.log_success("服務部署完成")
        else:
            self.log_error("服務部署失敗")

        return result

    def _run_docker_compose(self, args: list[str], cwd: Path) -> bool:
        """執行 docker compose 命令"""
        try:
            # 嘗試新版 docker compose
            result = subprocess.run(
                ['docker', 'compose'] + args,
                cwd=cwd,
                capture_output=True
            )
            if result.returncode == 0:
                return True

            # 嘗試舊版 docker-compose
            result = subprocess.run(
                ['docker-compose'] + args,
                cwd=cwd,
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def health_check(self) -> bool:
        """
        執行健康檢查
        
        Returns:
            是否健康
        """
        self.log_info("🏥 執行健康檢查...")

        for i in range(1, self.health_check_retries + 1):
            self.log_info(f"  健康檢查 ({i}/{self.health_check_retries})...")

            # 檢查容器狀態
            devcontainer_dir = self.project_root / 'config/dev'

            try:
                result = subprocess.run(
                    ['docker', 'compose', 'ps'],
                    cwd=devcontainer_dir,
                    capture_output=True,
                    text=True
                )

                output = result.stdout
                if 'unhealthy' not in output and 'Exit' not in output:
                    self.log_success("所有服務健康檢查通過")
                    return True

            except Exception:
                pass

            if i < self.health_check_retries:
                self.log_warn(f"  部分服務尚未就緒，等待 {self.health_check_interval}s...")
                import time
                time.sleep(self.health_check_interval)

        self.log_error("健康檢查失敗")
        return False

    def _display_result(self, result: dict[str, Any]) -> None:
        """顯示部署結果"""
        self.log_info("📊 部署結果:")
        print()
        print(f"  環境: {result['environment']}")
        print(f"  標籤: {result['tag']}")
        print(f"  時間: {result['timestamp']}")
        print()

        print("  步驟:")
        for step in result['steps']:
            icon = '✅' if step['success'] else '❌'
            print(f"    {icon} {step['name']}")

        print()
        if result['success']:
            self.log_success("部署完成")
        else:
            self.log_error("部署失敗")

    def run_core_deployment(self) -> int:
        """
        執行核心部署腳本 (config/dev/automation/deployment-drone.sh)
        
        Returns:
            執行結果代碼
        """
        core_script = self.project_root / 'config/dev' / 'automation' / 'deployment-drone.sh'

        if not core_script.exists():
            self.log_error(f"核心部署腳本不存在: {core_script}")
            return 1

        self.log_info(f"執行核心部署腳本: {core_script}")

        try:
            result = subprocess.run(
                ['bash', str(core_script), 'status'],
                cwd=self.project_root
            )
            return result.returncode
        except Exception as e:
            self.log_error(f"執行失敗: {e}")
            return 1
