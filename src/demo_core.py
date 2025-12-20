"""
MachineNativeOps Core Demo
核心功能演示
"""

import asyncio
import sys
import os

# 添加路徑以便導入
sys.path.append(os.path.dirname(__file__))

from core.new import core
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_basic_functionality():
    """演示基本功能"""
    logger.info("🎬 開始 MachineNativeOps 核心功能演示...")
    
    # 1. 初始化核心
    logger.info("1️⃣ 初始化核心系統...")
    await core.initialize()
    
    # 2. 用戶認證演示
    logger.info("2️⃣ 用戶認證演示...")
    token = await core.authenticate("admin", "admin123")
    if token:
        logger.info(f"✅ 認證成功，令牌: {token[:10]}...")
    else:
        logger.error("❌ 認證失敗")
    
    # 3. 任務提交演示
    logger.info("3️⃣ 任務提交演示...")
    
    async def demo_task(message: str):
        """演示任務"""
        logger.info(f"📋 執行任務: {message}")
        return f"任務完成: {message}"
    
    task_id = await core.submit_task("demo_task", demo_task, {"message": "Hello MachineNativeOps!"})
    logger.info(f"✅ 任務已提交: {task_id}")
    
    # 4. 工作流創建演示
    logger.info("4️⃣ 工作流創建演示...")
    
    from core.new.automation.workflow_engine import WorkflowTask
    
    demo_tasks = [
        WorkflowTask(id="task1", name="初始化", config={"type": "init"}),
        WorkflowTask(id="task2", name="處理", config={"type": "process"}),
        WorkflowTask(id="task3", name="完成", config={"type": "complete"})
    ]
    
    workflow = await core.create_workflow(
        "demo_workflow", 
        "演示工作流",
        demo_tasks
    )
    logger.info(f"✅ 工作流已創建: {workflow.id}")
    
    # 等待一下讓任務執行
    await asyncio.sleep(1)
    
    # 5. 關閉系統
    logger.info("5️⃣ 關閉系統...")
    await core.shutdown()
    
    logger.info("🎉 演示完成！")

if __name__ == "__main__":
    asyncio.run(demo_basic_functionality())