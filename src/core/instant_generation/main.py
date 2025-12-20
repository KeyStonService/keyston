"""
Instant Generation Main System
即時生成主系統

革命性架構的主要入口點，繞過沙箱服務限制
實現10分鐘內完整系統生成
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .workflows import InstantGenerationWorkflow
from .optimization import SelfHealingSystem, PerformanceOptimizer
from .monitoring import RealTimeMonitor, PerformanceTracker

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class InstantGenerationSystem:
    """即時生成系統主類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # 初始化核心組件
        self.workflow_engine = InstantGenerationWorkflow(self.config)
        self.self_healing = SelfHealingSystem(self.config)
        self.optimizer = PerformanceOptimizer(self.config)
        self.monitor = RealTimeMonitor(self.config)
        self.tracker = PerformanceTracker()
        
        # 系統狀態
        self.is_running = False
        self.start_time = None
        self.stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_time": 0.0,
            "last_generation_time": None
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "target_time_minutes": 10,
            "max_parallel_agents": 6,
            "self_healing_enabled": True,
            "bypass_sandbox": True,
            "optimization_enabled": True,
            "monitoring_enabled": True,
            "timeout_per_task": 300,  # 5分鐘
            "retry_attempts": 3,
            "quality_threshold": 80.0
        }
    
    async def generate_system(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成完整系統 - 主要入口方法"""
        generation_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting instant generation {generation_id}")
            self.logger.info(f"User input: {user_input[:100]}...")
            
            # 更新系統狀態
            self.is_running = True
            self.start_time = datetime.now()
            
            # 開始監控
            if self.config["monitoring_enabled"]:
                await self.monitor.start_monitoring(generation_id)
            
            # 執行生成工作流
            workflow_result = await self.workflow_engine.execute_instant_generation(
                user_input, context or {}
            )
            
            # 執行自我修復（如果需要）
            if not workflow_result.get("success", False) and self.config["self_healing_enabled"]:
                self.logger.info("Attempting self-healing...")
                healing_result = await self.self_healing.heal_workflow(
                    workflow_result, user_input, context
                )
                if healing_result.get("success", False):
                    workflow_result = healing_result
            
            # 性能優化
            if workflow_result.get("success", False) and self.config["optimization_enabled"]:
                self.logger.info("Optimizing generated system...")
                optimization_result = await self.optimizer.optimize_system(workflow_result)
                workflow_result["optimization"] = optimization_result
            
            # 生成最終輸出
            final_output = await self._generate_final_output(workflow_result, generation_id)
            
            # 更新統計
            execution_time = time.time() - start_time
            self._update_stats(True, execution_time)
            
            # 記錄性能指標
            await self.tracker.record_generation(generation_id, {
                "execution_time": execution_time,
                "success": workflow_result.get("success", False),
                "input_length": len(user_input),
                "output_size": len(str(final_output))
            })
            
            self.logger.info(f"Generation {generation_id} completed in {execution_time:.2f}s")
            
            return {
                "success": True,
                "generation_id": generation_id,
                "execution_time_seconds": execution_time,
                "target_time_met": execution_time <= (self.config["target_time_minutes"] * 60),
                "output": final_output,
                "workflow_result": workflow_result
            }
            
        except Exception as e:
            self.logger.error(f"Generation {generation_id} failed: {e}")
            execution_time = time.time() - start_time
            self._update_stats(False, execution_time)
            
            return {
                "success": False,
                "generation_id": generation_id,
                "execution_time_seconds": execution_time,
                "error": str(e),
                "debug_info": {
                    "config": self.config,
                    "system_status": self.get_system_status()
                }
            }
            
        finally:
            self.is_running = False
            if self.config["monitoring_enabled"]:
                await self.monitor.stop_monitoring(generation_id)
    
    async def _generate_final_output(self, workflow_result: Dict[str, Any], generation_id: str) -> Dict[str, Any]:
        """生成最終輸出"""
        results = workflow_result.get("results", {})
        
        # 提取各階段結果
        analysis_result = results.get("input_analysis", {})
        code_result = results.get("code_generation", {})
        deployment_result = results.get("deployment", {})
        optimization_result = results.get("optimization", {})
        
        final_output = {
            "generation_id": generation_id,
            "timestamp": datetime.now().isoformat(),
            "system_overview": {
                "name": f"Generated System {generation_id}",
                "type": analysis_result.get("output_data", {}).get("analysis", {}).get("domain", "web"),
                "complexity": analysis_result.get("output_data", {}).get("complexity_score", "medium"),
                "generated_files": code_result.get("output_data", {}).get("generated_files", 0)
            },
            "generated_components": {
                "source_code": code_result.get("output_data", {}).get("code_components", {}),
                "configuration": code_result.get("output_data", {}).get("config_files", {}),
                "documentation": code_result.get("output_data", {}).get("documentation", {})
            },
            "deployment_info": {
                "manifest": code_result.get("output_data", {}).get("deployment_manifest", {}),
                "deployment_status": deployment_result.get("output_data", {}).get("deployment_status", "ready"),
                "access_urls": deployment_result.get("output_data", {}).get("access_urls", [])
            },
            "performance_metrics": {
                "code_quality": code_result.get("output_data", {}).get("code_quality_score", 0),
                "optimization_applied": optimization_result.get("success", False),
                "performance_improvements": optimization_result.get("improvements", [])
            },
            "next_steps": [
                "Review generated code and documentation",
                "Run local tests to verify functionality",
                "Deploy to staging environment",
                "Configure production settings"
            ]
        }
        
        return final_output
    
    def _update_stats(self, success: bool, execution_time: float) -> None:
        """更新系統統計"""
        self.stats["total_generations"] += 1
        
        if success:
            self.stats["successful_generations"] += 1
        else:
            self.stats["failed_generations"] += 1
        
        # 更新平均時間
        total_successful = self.stats["successful_generations"]
        if total_successful > 0:
            current_avg = self.stats["average_time"]
            self.stats["average_time"] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
        
        self.stats["last_generation_time"] = datetime.now().isoformat()
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "statistics": self.stats.copy(),
            "workflow_stats": self.workflow_engine.get_stats(),
            "config": self.config
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """系統健康檢查"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # 檢查工作流引擎
            if hasattr(self.workflow_engine, "health_check"):
                workflow_health_func = self.workflow_engine.health_check
                if asyncio.iscoroutinefunction(workflow_health_func):
                    workflow_health = await workflow_health_func()
                else:
                    workflow_health = workflow_health_func()
            else:
                workflow_health = {
                    "status": "unknown",
                    "details": "workflow_engine does not implement health_check"
                }
            health_status["components"]["workflow_engine"] = workflow_health
            
            # 檢查自我修復系統
            healing_health = await self.self_healing.health_check()
            health_status["components"]["self_healing"] = healing_health
            
            # 檢查優化器
            optimizer_health = await self.optimizer.health_check()
            health_status["components"]["optimizer"] = optimizer_health
            
            # 檢查監控系統
            monitor_health = await self.monitor.health_check()
            health_status["components"]["monitor"] = monitor_health
            
            # 綜合健康狀態
            all_healthy = all(
                component.get("status") == "healthy" 
                for component in health_status["components"].values()
            )
            
            health_status["status"] = "healthy" if all_healthy else "degraded"
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def save_output(self, output: Dict[str, Any], output_dir: str = "output") -> str:
        """保存生成結果到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        generation_id = output.get("generation_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存主要輸出
        main_file = output_path / f"{generation_id}_{timestamp}.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        # 保存代碼文件
        if "output" in output and "generated_components" in output["output"]:
            code_dir = output_path / f"{generation_id}_{timestamp}_code"
            code_dir.mkdir(exist_ok=True)
            await self._save_code_files(output["output"]["generated_components"], code_dir)
        
        self.logger.info(f"Output saved to {main_file}")
        return str(main_file)
    
    async def _save_code_files(self, components: Dict[str, Any], base_dir: Path) -> None:
        """保存代碼文件到目錄結構"""
        import os
        
        def save_recursive(data: Dict[str, Any], current_path: Path) -> None:
            for key, value in data.items():
                if isinstance(value, dict):
                    # 創建子目錄
                    sub_path = current_path / key
                    sub_path.mkdir(exist_ok=True)
                    save_recursive(value, sub_path)
                elif isinstance(value, str):
                    # 保存文件
                    file_path = current_path / key
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(value)
        
        save_recursive(components, base_dir)

# 全局系統實例
_instant_generation_system = None

def get_system(config: Dict[str, Any] = None) -> InstantGenerationSystem:
    """獲取全局系統實例"""
    global _instant_generation_system
    if _instant_generation_system is None:
        _instant_generation_system = InstantGenerationSystem(config)
    return _instant_generation_system

# 便捷函數
async def generate_system(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """便捷函數：生成系統"""
    system = get_system()
    return await system.generate_system(user_input, context)

async def quick_generate(user_input: str) -> str:
    """超快速生成 - 返回結果摘要"""
    result = await generate_system(user_input)
    
    if result["success"]:
        return f"""
✅ 系統生成成功！
🆔 生成ID: {result['generation_id']}
⏱️ 執行時間: {result['execution_time_seconds']:.2f}秒
🎯 目標達成: {'是' if result['target_time_met'] else '否'}
📁 生成文件: {result['output']['system_overview']['generated_files']}個
📊 代碼質量: {result['output']['performance_metrics']['code_quality']:.1f}分
        """
    else:
        return f"""
❌ 生成失敗
🆔 生成ID: {result['generation_id']}
⏱️ 執行時間: {result['execution_time_seconds']:.2f}秒
🚨 錯誤: {result['error']}
        """

if __name__ == "__main__":
    # 命令行測試
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print('Usage: python main.py "<user_input>"')
            return
        
        user_input = " ".join(sys.argv[1:])
        result = await quick_generate(user_input)
        print(result)
    
    asyncio.run(main())