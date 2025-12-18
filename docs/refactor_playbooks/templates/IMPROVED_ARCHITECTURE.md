# 🏗️ MachineNativeOps 改进架构设计

## 核心问题分析

### 当前架构的单点故障

```
┌─────────────────────────────────────────┐
│     automation_launcher.py              │  ← 单点故障
│  (启动器、调度器、监控器合一)            │
├─────────────────────────────────────────┤
│     Master Orchestrator                 │  ← 次级单点
├─────────────────────────────────────────┤
│     引擎1   引擎2   引擎3   ...          │
└─────────────────────────────────────────┘
```

**问题**:

1. **单点故障**: Launcher失效 = 整个系统失控
2. **职责混乱**: 一个组件承担太多职责
3. **恢复困难**: 没有自动故障转移机制
4. **状态丢失**: 重启可能导致状态不一致

---

## 改进架构: 六层防御体系

基于你的AXIOM理念，采用**多层验证门 + 零信任原则**:

```
┌─────────────────────────────────────────────────────────────┐
│  L-A: Watchdog Layer (看门狗层)                              │
│  • 独立进程监控                                              │
│  • 自动故障恢复                                              │
│  • 心跳检测                                                  │
├─────────────────────────────────────────────────────────────┤
│  L-B: Control Plane (控制平面)                               │
│  • 主控调度器 (Primary Scheduler)                            │
│  • 备用调度器 (Standby Scheduler)                            │
│  • 状态同步                                                  │
├─────────────────────────────────────────────────────────────┤
│  L-C: Orchestration Layer (编排层)                           │
│  • Master Orchestrator (可多实例)                            │
│  • 分布式协调                                                │
│  • 任务分发                                                  │
├─────────────────────────────────────────────────────────────┤
│  L-D: Engine Layer (引擎层)                                  │
│  • 各类执行引擎                                              │
│  • 独立运行、可替换                                          │
│  • 健康上报                                                  │
├─────────────────────────────────────────────────────────────┤
│  L-E: State Management (状态管理层)                          │
│  • 分布式状态存储 (Redis/etcd)                               │
│  • 持久化日志                                                │
│  • 快照与回放                                                │
├─────────────────────────────────────────────────────────────┤
│  L-F: Monitoring & Observability (监控可观测层)              │
│  • 指标收集                                                  │
│  • 日志聚合                                                  │
│  • 告警系统                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer A: Watchdog Layer (看门狗层)

### 设计原则

- **独立性**: 与被监控系统完全分离
- **轻量级**: 最小依赖，极低资源占用
- **可靠性**: 自身具备自愈能力

### 实现方案

#### 1. 系统级Watchdog (systemd)

```ini
# /etc/systemd/system/machinenativeops-watchdog.service
[Unit]
Description=MachineNativeOps Watchdog Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/machinenativeops_watchdog
Restart=always
RestartSec=10
User=machinenativeops
StandardOutput=journal
StandardError=journal

# 健康检查
WatchdogSec=30
NotifyAccess=main

[Install]
WantedBy=multi-user.target
```

#### 2. 应用级Watchdog

```python
#!/usr/bin/env python3
"""
machinenativeops_watchdog.py - 看门狗守护进程

职责：
1. 监控所有关键进程（Launcher、Orchestrator、Engines）
2. 检测异常并自动恢复
3. 记录所有恢复操作
4. 向监控系统发送心跳
"""

import asyncio
import psutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
import json
import signal
import sys

class ProcessWatchdog:
    """进程看门狗"""
    
    def __init__(self, config_path: str = "/etc/machinenativeops/watchdog.json"):
        self.config = self._load_config(config_path)
        self.monitored_processes = {}
        self.recovery_count = {}
        self.running = False
        
        # 最大恢复尝试次数
        self.max_recovery_attempts = self.config.get("max_recovery_attempts", 3)
        self.recovery_window = self.config.get("recovery_window_seconds", 300)  # 5分钟
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置"""
        default_config = {
            "check_interval": 10,
            "processes": [
                {
                    "name": "automation_launcher",
                    "command": ["python", "automation_launcher.py", "start"],
                    "cwd": "/opt/machinenativeops",
                    "critical": True,
                    "restart_delay": 5
                },
                {
                    "name": "master_orchestrator",
                    "command": ["python", "-m", "master_orchestrator"],
                    "cwd": "/opt/machinenativeops/tools/automation",
                    "critical": True,
                    "restart_delay": 3
                }
            ],
            "alerting": {
                "enabled": True,
                "webhook_url": None,
                "email": None
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        except FileNotFoundError:
            print(f"⚠️  配置文件不存在，使用默认配置: {config_path}")
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
        
        return default_config
    
    def _check_process_health(self, process_name: str) -> tuple[bool, str]:
        """检查进程健康状态"""
        # 方法1: 检查进程是否存在
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if process_name in cmdline:
                    # 进程存在，检查是否响应
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        return False, f"进程 {process_name} 成为僵尸进程"
                    
                    # 检查CPU使用率（可选）
                    cpu_percent = proc.cpu_percent(interval=1)
                    if cpu_percent > 95:
                        return False, f"进程 {process_name} CPU使用率异常: {cpu_percent}%"
                    
                    return True, "健康"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False, f"进程 {process_name} 不存在"
    
    async def _recover_process(self, process_config: dict) -> bool:
        """恢复进程"""
        process_name = process_config["name"]
        
        # 检查恢复次数限制
        current_time = time.time()
        if process_name not in self.recovery_count:
            self.recovery_count[process_name] = []
        
        # 清理旧的恢复记录
        self.recovery_count[process_name] = [
            t for t in self.recovery_count[process_name]
            if current_time - t < self.recovery_window
        ]
        
        # 检查是否超过最大尝试次数
        if len(self.recovery_count[process_name]) >= self.max_recovery_attempts:
            print(f"❌ 进程 {process_name} 恢复次数超限，需要人工介入")
            await self._send_alert(
                f"CRITICAL: 进程 {process_name} 恢复失败超过 {self.max_recovery_attempts} 次",
                severity="critical"
            )
            return False
        
        print(f"🔄 尝试恢复进程: {process_name}")
        
        try:
            # 杀死可能存在的僵尸进程
            subprocess.run(["pkill", "-9", "-f", process_name], check=False)
            
            # 等待清理
            await asyncio.sleep(process_config.get("restart_delay", 5))
            
            # 启动进程
            cwd = process_config.get("cwd", ".")
            proc = subprocess.Popen(
                process_config["command"],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # 创建新会话组
            )
            
            # 等待启动
            await asyncio.sleep(3)
            
            # 验证启动
            if proc.poll() is None:  # 进程仍在运行
                print(f"✅ 进程 {process_name} 恢复成功, PID: {proc.pid}")
                self.recovery_count[process_name].append(current_time)
                self.monitored_processes[process_name] = proc
                return True
            else:
                print(f"❌ 进程 {process_name} 恢复失败，立即退出")
                return False
                
        except Exception as e:
            print(f"❌ 恢复进程 {process_name} 时出错: {e}")
            return False
    
    async def _send_alert(self, message: str, severity: str = "warning"):
        """发送告警"""
        if not self.config["alerting"]["enabled"]:
            return
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "source": "MachineNativeOps Watchdog"
        }
        
        print(f"🚨 告警: [{severity.upper()}] {message}")
        
        # Webhook通知
        webhook_url = self.config["alerting"].get("webhook_url")
        if webhook_url:
            try:
                import requests
                requests.post(webhook_url, json=alert_data, timeout=5)
            except Exception as e:
                print(f"⚠️  发送webhook告警失败: {e}")
        
        # Email通知（如果配置）
        # TODO: 实现email通知
    
    async def monitor_loop(self):
        """主监控循环"""
        check_interval = self.config.get("check_interval", 10)
        
        while self.running:
            for process_config in self.config["processes"]:
                process_name = process_config["name"]
                is_healthy, status_msg = self._check_process_health(process_name)
                
                if not is_healthy:
                    print(f"⚠️  检测到进程异常: {process_name} - {status_msg}")
                    
                    if process_config.get("critical", False):
                        # 关键进程，立即恢复
                        recovery_success = await self._recover_process(process_config)
                        
                        if not recovery_success:
                            await self._send_alert(
                                f"关键进程 {process_name} 恢复失败",
                                severity="critical"
                            )
                    else:
                        # 非关键进程，仅告警
                        await self._send_alert(
                            f"进程 {process_name} 异常: {status_msg}",
                            severity="warning"
                        )
            
            await asyncio.sleep(check_interval)
    
    async def start(self):
        """启动看门狗"""
        print("🐕 MachineNativeOps Watchdog 启动中...")
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        await self.monitor_loop()
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        print(f"🛑 收到信号 {signum}，准备停止...")
        self.running = False
    
    async def stop(self):
        """停止看门狗"""
        self.running = False
        print("🛑 Watchdog 已停止")

async def main():
    watchdog = ProcessWatchdog()
    await watchdog.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Layer B: Control Plane (控制平面)

### 主备调度器设计

```python
"""
scheduler_ha.py - 高可用调度器

实现主备模式：
- 主调度器处理所有请求
- 备用调度器实时同步状态
- 故障时自动切换
"""

import asyncio
import enum
from typing import Optional
import time

class SchedulerRole(enum.Enum):
    PRIMARY = "primary"
    STANDBY = "standby"
    UNKNOWN = "unknown"

class HAScheduler:
    """高可用调度器"""
    
    def __init__(self, node_id: str, peers: list[str]):
        self.node_id = node_id
        self.peers = peers
        self.role = SchedulerRole.UNKNOWN
        
        # 使用分布式锁选举
        self.lock_service = None  # Redis/etcd
        self.heartbeat_interval = 5
        self.election_timeout = 15
        
        self.last_heartbeat = time.time()
    
    async def start_election(self):
        """启动选举"""
        print(f"[{self.node_id}] 开始选举...")
        
        # 尝试获取分布式锁
        acquired = await self.lock_service.try_acquire(
            key="scheduler_primary_lock",
            ttl=self.election_timeout,
            node_id=self.node_id
        )
        
        if acquired:
            self.role = SchedulerRole.PRIMARY
            print(f"✅ [{self.node_id}] 成为主调度器")
            asyncio.create_task(self.primary_loop())
        else:
            self.role = SchedulerRole.STANDBY
            print(f"⏸️  [{self.node_id}] 成为备用调度器")
            asyncio.create_task(self.standby_loop())
    
    async def primary_loop(self):
        """主调度器循环"""
        while self.role == SchedulerRole.PRIMARY:
            try:
                # 续约锁
                await self.lock_service.renew_lock(
                    key="scheduler_primary_lock",
                    node_id=self.node_id
                )
                
                # 发送心跳
                await self.broadcast_heartbeat()
                
                # 执行调度任务
                await self.schedule_tasks()
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ 主调度器异常: {e}")
                # 释放锁，触发重新选举
                await self.lock_service.release_lock(
                    key="scheduler_primary_lock",
                    node_id=self.node_id
                )
                self.role = SchedulerRole.UNKNOWN
                await self.start_election()
    
    async def standby_loop(self):
        """备用调度器循环"""
        while self.role == SchedulerRole.STANDBY:
            try:
                # 监听主调度器心跳
                heartbeat_received = await self.check_primary_heartbeat()
                
                if not heartbeat_received:
                    print(f"⚠️  [{self.node_id}] 主调度器心跳超时，触发选举")
                    await self.start_election()
                    break
                
                # 同步状态（被动复制）
                await self.sync_state_from_primary()
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ 备用调度器异常: {e}")
    
    async def schedule_tasks(self):
        """调度任务（仅主调度器）"""
        # 实现任务调度逻辑
        pass
    
    async def broadcast_heartbeat(self):
        """广播心跳"""
        self.last_heartbeat = time.time()
        # 向所有peer发送心跳
        pass
    
    async def check_primary_heartbeat(self) -> bool:
        """检查主调度器心跳"""
        # 检查是否收到主调度器心跳
        time_since_heartbeat = time.time() - self.last_heartbeat
        return time_since_heartbeat < self.election_timeout
    
    async def sync_state_from_primary(self):
        """从主调度器同步状态"""
        # 实现状态同步
        pass
```

---

## Layer C: Orchestration Layer (编排层)

### 分布式Orchestrator

```python
"""
distributed_orchestrator.py - 分布式编排器

特性：
1. 可水平扩展（多实例）
2. 任务分片
3. 失败自动转移
"""

class DistributedOrchestrator:
    """分布式编排器"""
    
    def __init__(self, instance_id: str, cluster_config: dict):
        self.instance_id = instance_id
        self.cluster = cluster_config
        
        # 任务分片策略
        self.shard_count = cluster_config.get("shard_count", 16)
        self.my_shards = self._calculate_my_shards()
        
        # 引擎注册表（分布式）
        self.registry = DistributedRegistry(
            backend="redis",
            cluster_nodes=cluster_config["redis_nodes"]
        )
    
    def _calculate_my_shards(self) -> set[int]:
        """计算本实例负责的分片"""
        total_instances = len(self.cluster["instances"])
        instance_index = self.cluster["instances"].index(self.instance_id)
        
        shards = set()
        for shard_id in range(self.shard_count):
            if shard_id % total_instances == instance_index:
                shards.add(shard_id)
        
        return shards
    
    async def handle_engine_registration(self, engine_id: str, engine_info: dict):
        """处理引擎注册"""
        # 计算引擎所属分片
        shard_id = hash(engine_id) % self.shard_count
        
        if shard_id in self.my_shards:
            # 本实例负责此引擎
            await self.registry.register_engine(engine_id, engine_info)
            print(f"✅ [{self.instance_id}] 注册引擎: {engine_id} (shard {shard_id})")
        else:
            # 转发到负责的实例
            responsible_instance = self._get_responsible_instance(shard_id)
            await self._forward_registration(responsible_instance, engine_id, engine_info)
    
    def _get_responsible_instance(self, shard_id: int) -> str:
        """获取负责指定分片的实例"""
        total_instances = len(self.cluster["instances"])
        instance_index = shard_id % total_instances
        return self.cluster["instances"][instance_index]
    
    async def _forward_registration(self, target_instance: str, engine_id: str, engine_info: dict):
        """转发注册请求到其他实例"""
        # 实现跨实例通信
        pass
```

---

## Layer E: State Management (状态管理层)

### 分布式状态存储

```python
"""
state_manager.py - 分布式状态管理

使用Redis/etcd实现：
1. 状态持久化
2. 事件溯源
3. 快照与恢复
"""

class StateManager:
    """状态管理器"""
    
    def __init__(self, backend="redis", connection_config: dict = None):
        self.backend = backend
        
        if backend == "redis":
            import redis
            self.client = redis.Redis(**connection_config)
        elif backend == "etcd":
            import etcd3
            self.client = etcd3.client(**connection_config)
    
    async def save_state(self, key: str, state: dict):
        """保存状态"""
        # 序列化状态
        import json
        state_json = json.dumps(state)
        
        # 保存到后端
        self.client.set(key, state_json)
        
        # 记录事件日志（用于重放）
        event = {
            "timestamp": time.time(),
            "action": "state_update",
            "key": key,
            "state": state
        }
        self.client.lpush(f"events:{key}", json.dumps(event))
    
    async def load_state(self, key: str) -> Optional[dict]:
        """加载状态"""
        import json
        state_json = self.client.get(key)
        
        if state_json:
            return json.loads(state_json)
        return None
    
    async def replay_events(self, key: str, from_timestamp: float = 0):
        """重放事件（恢复状态）"""
        import json
        events = self.client.lrange(f"events:{key}", 0, -1)
        
        state = {}
        for event_json in events:
            event = json.loads(event_json)
            if event["timestamp"] >= from_timestamp:
                # 重放事件
                state.update(event["state"])
        
        return state
    
    async def create_snapshot(self, prefix: str = ""):
        """创建快照"""
        import json
        snapshot = {
            "timestamp": time.time(),
            "states": {}
        }
        
        # 获取所有状态
        keys = self.client.keys(f"{prefix}*")
        for key in keys:
            if not key.startswith(b"events:"):
                state_json = self.client.get(key)
                if state_json:
                    snapshot["states"][key.decode()] = json.loads(state_json)
        
        # 保存快照
        snapshot_key = f"snapshot:{prefix}:{time.time()}"
        self.client.set(snapshot_key, json.dumps(snapshot))
        
        print(f"📸 创建快照: {snapshot_key}")
        return snapshot_key
```

---

## 完整架构实现示例

### 启动脚本 (重构后)

```python
#!/usr/bin/env python3
"""
machinenativeops_cluster.py - 集群启动脚本

启动完整的高可用集群：
1. Watchdog
2. State Manager
3. HA Scheduler (主备)
4. Distributed Orchestrators
5. Engines
"""

import asyncio
import argparse
from typing import List

class MachineNativeOpsCluster:
    """MachineNativeOps 集群管理器"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.components = {}
    
    async def start_watchdog(self):
        """启动Watchdog"""
        from machinenativeops_watchdog import ProcessWatchdog
        
        watchdog = ProcessWatchdog(self.config["watchdog"])
        self.components["watchdog"] = watchdog
        
        asyncio.create_task(watchdog.start())
        print("✅ Watchdog 已启动")
    
    async def start_state_manager(self):
        """启动状态管理器"""
        from state_manager import StateManager
        
        state_mgr = StateManager(
            backend=self.config["state"]["backend"],
            connection_config=self.config["state"]["connection"]
        )
        self.components["state_manager"] = state_mgr
        
        print("✅ State Manager 已启动")
    
    async def start_schedulers(self):
        """启动HA调度器"""
        from scheduler_ha import HAScheduler
        
        node_id = self.config["scheduler"]["node_id"]
        peers = self.config["scheduler"]["peers"]
        
        scheduler = HAScheduler(node_id, peers)
        self.components["scheduler"] = scheduler
        
        await scheduler.start_election()
        print(f"✅ Scheduler 已启动 (node: {node_id})")
    
    async def start_orchestrators(self):
        """启动分布式Orchestrator"""
        from distributed_orchestrator import DistributedOrchestrator
        
        instance_id = self.config["orchestrator"]["instance_id"]
        cluster_config = self.config["orchestrator"]["cluster"]
        
        orchestrator = DistributedOrchestrator(instance_id, cluster_config)
        self.components["orchestrator"] = orchestrator
        
        await orchestrator.start()
        print(f"✅ Orchestrator 已启动 (instance: {instance_id})")
    
    async def start_all(self):
        """启动所有组件"""
        print("🚀 MachineNativeOps 集群启动中...")
        print("=" * 60)
        
        # 按顺序启动各层
        await self.start_watchdog()
        await self.start_state_manager()
        await self.start_schedulers()
        await self.start_orchestrators()
        
        print("=" * 60)
        print("🎉 MachineNativeOps 集群启动完成！")
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
                await self._health_check()
        except KeyboardInterrupt:
            await self.stop_all()
    
    async def _health_check(self):
        """集群健康检查"""
        # 实现健康检查逻辑
        pass
    
    async def stop_all(self):
        """停止所有组件"""
        print("\n🛑 停止集群...")
        
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                await component.stop()
                print(f"  ✓ {name} 已停止")

async def main():
    parser = argparse.ArgumentParser(description="MachineNativeOps 集群管理")
    parser.add_argument("--config", default="/etc/machinenativeops/cluster.json", help="配置文件路径")
    args = parser.parse_args()
    
    cluster = MachineNativeOpsCluster(args.config)
    await cluster.start_all()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 部署配置

### Docker Compose (高可用)

```yaml
version: '3.8'

services:
  # Redis - 状态存储
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Watchdog (主)
  watchdog-primary:
    build: .
    command: python machinenativeops_watchdog.py
    environment:
      - NODE_ID=watchdog-1
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  # Scheduler (主)
  scheduler-primary:
    build: .
    command: python scheduler_ha.py --role primary
    environment:
      - NODE_ID=scheduler-1
      - REDIS_URL=redis://redis:6379
      - PEERS=scheduler-2,scheduler-3
    depends_on:
      - redis
    restart: unless-stopped

  # Scheduler (备1)
  scheduler-standby-1:
    build: .
    command: python scheduler_ha.py --role standby
    environment:
      - NODE_ID=scheduler-2
      - REDIS_URL=redis://redis:6379
      - PEERS=scheduler-1,scheduler-3
    depends_on:
      - redis
    restart: unless-stopped

  # Orchestrator (实例1)
  orchestrator-1:
    build: .
    command: python distributed_orchestrator.py --instance-id orch-1
    environment:
      - INSTANCE_ID=orch-1
      - REDIS_URL=redis://redis:6379
      - CLUSTER_INSTANCES=orch-1,orch-2,orch-3
    depends_on:
      - redis
      - scheduler-primary
    restart: unless-stopped

  # Orchestrator (实例2)
  orchestrator-2:
    build: .
    command: python distributed_orchestrator.py --instance-id orch-2
    environment:
      - INSTANCE_ID=orch-2
      - REDIS_URL=redis://redis:6379
      - CLUSTER_INSTANCES=orch-1,orch-2,orch-3
    depends_on:
      - redis
      - scheduler-primary
    restart: unless-stopped

  # Orchestrator (实例3)
  orchestrator-3:
    build: .
    command: python distributed_orchestrator.py --instance-id orch-3
    environment:
      - INSTANCE_ID=orch-3
      - REDIS_URL=redis://redis:6379
      - CLUSTER_INSTANCES=orch-1,orch-2,orch-3
    depends_on:
      - redis
      - scheduler-primary
    restart: unless-stopped

  # Prometheus - 监控
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana - 可视化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  redis-data:
  prometheus-data:
  grafana-data:
```

---

## Kubernetes 部署 (生产级)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: machinenativeops-config
data:
  cluster.json: |
    {
      "watchdog": {
        "check_interval": 10,
        "max_recovery_attempts": 3
      },
      "scheduler": {
        "election_timeout": 15,
        "heartbeat_interval": 5
      },
      "orchestrator": {
        "shard_count": 16,
        "health_check_interval": 30
      },
      "state": {
        "backend": "redis",
        "connection": {
          "host": "redis-service",
          "port": 6379
        }
      }
    }

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: machinenativeops-scheduler
spec:
  serviceName: scheduler
  replicas: 3
  selector:
    matchLabels:
      app: machinenativeops-scheduler
  template:
    metadata:
      labels:
        app: machinenativeops-scheduler
    spec:
      containers:
      - name: scheduler
        image: machinenativeops/scheduler:latest
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        volumeMounts:
        - name: config
          mountPath: /etc/machinenativeops
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: machinenativeops-config

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: machinenativeops-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: machinenativeops-orchestrator
  template:
    metadata:
      labels:
        app: machinenativeops-orchestrator
    spec:
      containers:
      - name: orchestrator
        image: machinenativeops/orchestrator:latest
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: orchestrator-service
spec:
  selector:
    app: machinenativeops-orchestrator
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP
```

---

## 对比: 改进前 vs 改进后

| 特性 | 改进前 | 改进后 |
|------|--------|--------|
| **单点故障** | ❌ Launcher是单点 | ✅ 无单点，所有层都冗余 |
| **自动恢复** | ❌ 手动恢复 | ✅ Watchdog自动恢复 |
| **水平扩展** | ❌ 无法扩展 | ✅ Orchestrator可扩展 |
| **状态持久化** | ❌ 内存状态 | ✅ Redis/etcd持久化 |
| **故障转移** | ❌ 无 | ✅ 主备自动切换 |
| **监控告警** | ⚠️  基础日志 | ✅ Prometheus + Grafana |
| **部署复杂度** | 🟢 简单 | 🟡 中等（有工具支持） |
| **运维成本** | 🔴 高（需人工介入） | 🟢 低（自动化） |

---

## 实施路线图

### Phase 1: 应急措施 (立即)

- ✅ 部署 `emergency_recovery.py`
- ✅ 创建 `RECOVERY_PLAYBOOK.md`
- ✅ 建立监控告警

### Phase 2: Watchdog层 (1-2周)

- ⬜ 实现系统级Watchdog
- ⬜ 集成systemd服务
- ⬜ 测试自动恢复

### Phase 3: 控制平面 (2-3周)

- ⬜ 实现主备调度器
- ⬜ 分布式锁机制
- ⬜ 故障转移测试

### Phase 4: 分布式编排 (3-4周)

- ⬜ Orchestrator分片
- ⬜ 任务分发优化
- ⬜ 负载均衡

### Phase 5: 状态管理 (2周)

- ⬜ Redis/etcd集成
- ⬜ 事件溯源
- ⬜ 快照与恢复

### Phase 6: 生产部署 (1-2周)

- ⬜ Docker化
- ⬜ Kubernetes编排
- ⬜ 监控与可观测性

---

## 总结

**关键改进**:

1. **零单点故障**: 所有组件都有冗余
2. **自动故障恢复**: Watchdog + 主备切换
3. **水平可扩展**: Orchestrator可多实例运行
4. **状态持久化**: 不再依赖内存状态
5. **云原生**: 支持K8s部署

**立即可用**:

- `emergency_recovery.py` - 现在就可以用作应急方案
- `RECOVERY_PLAYBOOK.md` - 标准化恢复流程

**长期架构**:

- 六层防御体系
- 符合你的AXIOM系统理念
- 企业级可靠性

---

**下一步建议**:

1. 立即部署应急恢复脚本
2. 测试当前系统的恢复能力
3. 制定详细的迁移计划
4. 逐步实施架构改进

需要我详细展开任何一个部分吗?
