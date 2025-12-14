# 🚨 SynergyMesh 应急恢复手册

## 快速决策树

```
Launcher启动失败？
├── 是 → 执行应急恢复流程
│   ├── Step 1: 运行 emergency_recovery.py
│   ├── Step 2: 检查恢复日志
│   └── Step 3: 验证系统健康
│
└── 引擎启动失败？
    ├── 单个引擎故障 → 隔离并重启
    ├── 多个引擎故障 → 全系统重启
    └── Orchestrator故障 → 手动接管
```

## 应急响应等级

### 🟢 Level 0: 正常运行
- **状态**: 所有组件健康
- **操作**: 无需介入

### 🟡 Level 1: 部分降级
- **状态**: 单个引擎故障
- **操作**: 
  ```bash
  # 重启特定引擎
  python automation_launcher.py start-engine <engine_id>
  ```

### 🟠 Level 2: 主控故障
- **状态**: MasterOrchestrator无响应
- **操作**:
  ```bash
  # 1. 尝试优雅重启
  python automation_launcher.py stop
  python automation_launcher.py start
  
  # 2. 如果失败，使用应急脚本
  python emergency_recovery.py
  ```

### 🔴 Level 3: Launcher故障
- **状态**: automation_launcher.py完全失效
- **操作**:
  ```bash
  # 直接运行应急恢复
  python emergency_recovery.py
  ```

### ⚫ Level 4: 灾难性故障
- **状态**: 所有自动化失效
- **操作**: 执行手动恢复（见下方）

---

## 详细恢复步骤

### Scenario 1: Launcher启动引擎功能失效

#### 症状识别
- ✗ `python automation_launcher.py start-engine <id>` 失败
- ✗ 引擎无法通过launcher启动
- ✓ MasterOrchestrator可能仍在运行

#### 恢复步骤

**Step 1: 验证问题**
```bash
# 检查launcher自身状态
python automation_launcher.py status

# 检查orchestrator进程
ps aux | grep master_orchestrator
```

**Step 2: 绕过launcher直接操作**
```bash
# 方案A: 使用应急脚本
python emergency_recovery.py

# 方案B: 直接调用orchestrator API
cd tools/automation
python -c "
from master_orchestrator import MasterOrchestrator
import asyncio

async def direct_start():
    orch = MasterOrchestrator(config)
    await orch.start_engine('engine_id')

asyncio.run(direct_start())
"
```

**Step 3: 临时修复launcher**
```bash
# 备份当前版本
cp automation_launcher.py automation_launcher.py.broken

# 恢复最后已知良好版本
git checkout HEAD~1 automation_launcher.py

# 或使用应急版本
cp automation_launcher_backup.py automation_launcher.py
```

### Scenario 2: 完全无法启动

#### 手动恢复流程

**1. 杀死所有相关进程**
```bash
# 找出所有相关进程
ps aux | grep -E "(automation|orchestrator|engine)" | grep -v grep

# 优雅停止
pkill -SIGTERM -f "master_orchestrator"
pkill -SIGTERM -f "automation_launcher"

# 强制停止（如果需要）
pkill -SIGKILL -f "master_orchestrator"
```

**2. 清理状态文件**
```bash
# 清除可能损坏的状态
rm -f .orchestrator_status
rm -f .launcher_state
rm -f /tmp/synergymesh_*
```

**3. 验证环境**
```bash
# 检查Python环境
python --version
python -c "import asyncio; print('✓ asyncio')"

# 检查依赖
pip list | grep -E "(pyyaml|asyncio)"
```

**4. 重新启动**
```bash
# 使用应急恢复脚本
python emergency_recovery.py
```

---

## 手动接管指南

当所有自动化失效时，手动启动核心组件：

### 1. 直接启动MasterOrchestrator

创建临时启动脚本 `manual_start.py`:
```python
#!/usr/bin/env python3
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "tools" / "automation"))

from master_orchestrator import MasterOrchestrator, OrchestratorConfig

async def manual_start():
    config = OrchestratorConfig(
        name="SynergyMesh",
        version="1.0.0",
        auto_discover=True,
        auto_start_engines=True,
        engines_paths=["./tools/automation/engines"]
    )
    
    orch = MasterOrchestrator(config)
    success = await orch.start()
    
    if success:
        print("✅ 手动启动成功")
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
                status = orch.get_status()
                print(f"Status: {status}")
        except KeyboardInterrupt:
            await orch.stop()
    else:
        print("❌ 启动失败")

if __name__ == "__main__":
    asyncio.run(manual_start())
```

运行：
```bash
python manual_start.py
```

### 2. 单独启动引擎

如果需要逐个启动引擎：

```python
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "tools" / "automation" / "engines"))

# 导入特定引擎
from your_engine import YourEngine

async def start_single_engine():
    engine = YourEngine(config={
        "name": "manual_engine",
        # 其他配置...
    })
    
    await engine.initialize()
    await engine.start()
    
    print(f"✅ 引擎 {engine.name} 已启动")
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(start_single_engine())
```

---

## 故障诊断检查清单

### ✓ 环境检查
- [ ] Python版本正确 (3.8+)
- [ ] 虚拟环境已激活
- [ ] 所有依赖已安装
- [ ] 必要目录存在且可写

### ✓ 进程检查
- [ ] 没有僵尸进程
- [ ] 端口没有被占用
- [ ] 系统资源充足（CPU、内存）

### ✓ 配置检查
- [ ] 配置文件完整
- [ ] 路径设置正确
- [ ] 权限设置正确

### ✓ 日志检查
- [ ] 查看最新错误日志
- [ ] 检查堆栈跟踪
- [ ] 识别根本原因

---

## 预防性措施

### 1. 定期备份
```bash
# 每日备份脚本
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

cp automation_launcher.py "$BACKUP_DIR/"
cp -r tools/automation "$BACKUP_DIR/"
cp -r config "$BACKUP_DIR/"

echo "✅ 备份完成: $BACKUP_DIR"
```

### 2. 健康监控
```bash
# 添加到crontab
*/5 * * * * /path/to/health_check.sh
```

### 3. 配置版本控制
```bash
# 提交所有配置到Git
git add config/ tools/
git commit -m "Config snapshot $(date +%Y%m%d_%H%M%S)"
```

---

## 联系与升级

### 何时升级到人工介入
- ⚠️ 应急恢复脚本连续失败3次
- ⚠️ 数据损坏或丢失风险
- ⚠️ 安全事件（未授权访问）
- ⚠️ 不明原因的系统行为

### 记录和报告
每次恢复操作后，请记录：
1. 故障时间和持续时间
2. 故障现象和错误消息
3. 执行的恢复步骤
4. 最终解决方案
5. 建议的预防措施

使用模板：
```markdown
## 故障报告 - [YYYY-MM-DD HH:MM]

**故障等级**: Level X
**影响范围**: [影响的组件]
**检测时间**: [时间]
**恢复时间**: [时间]
**停机时长**: [分钟]

### 症状
- [描述观察到的问题]

### 根本原因
- [分析后确定的原因]

### 恢复步骤
1. [步骤1]
2. [步骤2]
...

### 预防措施
- [建议的改进]
```

---

## 快速命令参考

```bash
# 快速状态检查
python automation_launcher.py status

# 应急恢复
python emergency_recovery.py

# 查看日志
tail -f logs/latest.log

# 进程管理
ps aux | grep orchestrator
pkill -SIGTERM -f orchestrator

# 环境验证
python -c "import sys; print(sys.version)"
pip list

# 清理和重启
rm -f .orchestrator_status && python emergency_recovery.py
```

---

**最后更新**: 2025-12-09
**版本**: 1.0.0
**维护者**: SynergyMesh Team
