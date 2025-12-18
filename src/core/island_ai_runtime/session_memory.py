#!/usr/bin/env python3
"""
Session Memory - 會話記憶
Short-term Memory, Context Management, and Planning

管理 AI 會話上下文和任務規劃
"""

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(Enum):
    """記憶類型"""

    SHORT_TERM = "short_term"  # 短期記憶（會話內）
    WORKING = "working"  # 工作記憶（當前任務）
    EPISODIC = "episodic"  # 情節記憶（事件序列）


class MessageRole(Enum):
    """訊息角色"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """會話訊息"""

    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanStep:
    """計劃步驟"""

    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class Plan:
    """任務計劃"""

    id: str
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    status: str = "created"  # created, executing, completed, failed
    created_at: float = field(default_factory=time.time)


@dataclass
class ContextWindow:
    """上下文窗口"""

    max_tokens: int
    current_tokens: int = 0
    messages: list[Message] = field(default_factory=list)


class ShortTermMemory:
    """
    短期記憶

    管理會話內的即時記憶。
    """

    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self.messages: deque[Message] = deque(maxlen=max_messages)

    def add(self, message: Message) -> None:
        """添加訊息"""
        self.messages.append(message)

    def get_recent(self, n: int = 10) -> list[Message]:
        """獲取最近的訊息"""
        return list(self.messages)[-n:]

    def search(self, query: str) -> list[Message]:
        """搜索訊息"""
        results = []
        query_lower = query.lower()
        for msg in self.messages:
            if query_lower in msg.content.lower():
                results.append(msg)
        return results

    def clear(self) -> None:
        """清空記憶"""
        self.messages.clear()

    def to_messages(self) -> list[dict[str, str]]:
        """轉換為 LLM 訊息格式"""
        return [{"role": msg.role.value, "content": msg.content} for msg in self.messages]


class WorkingMemory:
    """
    工作記憶

    管理當前任務的臨時信息。
    """

    def __init__(self):
        self.data: dict[str, Any] = {}
        self.focus: str | None = None

    def set(self, key: str, value: Any) -> None:
        """設置數據"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """獲取數據"""
        return self.data.get(key, default)

    def remove(self, key: str) -> None:
        """移除數據"""
        self.data.pop(key, None)

    def set_focus(self, focus: str) -> None:
        """設置焦點"""
        self.focus = focus

    def get_focus(self) -> str | None:
        """獲取焦點"""
        return self.focus

    def clear(self) -> None:
        """清空工作記憶"""
        self.data.clear()
        self.focus = None


class Planner:
    """
    任務規劃器

    創建和管理任務計劃。
    """

    def __init__(self):
        self.plans: dict[str, Plan] = {}
        self.current_plan: Plan | None = None

    def create_plan(self, goal: str, steps: list[dict[str, Any]]) -> Plan:
        """創建計劃"""
        plan_id = f"plan_{int(time.time())}"

        plan_steps = [
            PlanStep(
                id=f"step_{i}",
                description=step.get("description", ""),
                dependencies=step.get("dependencies", []),
            )
            for i, step in enumerate(steps)
        ]

        plan = Plan(id=plan_id, goal=goal, steps=plan_steps)

        self.plans[plan_id] = plan
        self.current_plan = plan

        return plan

    def get_next_step(self) -> PlanStep | None:
        """獲取下一個待執行的步驟"""
        if not self.current_plan:
            return None

        for step in self.current_plan.steps:
            if step.status == "pending":
                # 檢查依賴是否完成
                dependencies_met = all(
                    self._get_step(dep).status == "completed"
                    for dep in step.dependencies
                    if self._get_step(dep)
                )
                if dependencies_met:
                    return step

        return None

    def update_step(self, step_id: str, status: str, result: Any = None) -> None:
        """更新步驟狀態"""
        if not self.current_plan:
            return

        for step in self.current_plan.steps:
            if step.id == step_id:
                step.status = status
                step.result = result
                break

        # 檢查計劃是否完成
        all_completed = all(s.status == "completed" for s in self.current_plan.steps)
        any_failed = any(s.status == "failed" for s in self.current_plan.steps)

        if all_completed:
            self.current_plan.status = "completed"
        elif any_failed:
            self.current_plan.status = "failed"

    def _get_step(self, step_id: str) -> PlanStep | None:
        """獲取步驟"""
        if not self.current_plan:
            return None

        for step in self.current_plan.steps:
            if step.id == step_id:
                return step
        return None


class SessionMemory:
    """
    會話記憶

    整合短期記憶、工作記憶和規劃器。

    功能：
    - Short-term Memory 短期記憶
    - Working Memory 工作記憶
    - Context Management 上下文管理
    - Task Planning 任務規劃
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.short_term = ShortTermMemory(max_messages=self.config.get("max_messages", 100))
        self.working = WorkingMemory()
        self.planner = Planner()
        self.context_window = ContextWindow(max_tokens=self.config.get("max_tokens", 128000))

    def add_message(
        self, role: str | MessageRole, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """添加訊息到記憶"""
        if isinstance(role, str):
            role = MessageRole(role)

        message = Message(role=role, content=content, metadata=metadata or {})

        self.short_term.add(message)
        self.context_window.messages.append(message)

    def get_context(self, max_messages: int | None = None) -> list[dict[str, str]]:
        """獲取上下文"""
        messages = self.short_term.to_messages()
        if max_messages:
            messages = messages[-max_messages:]
        return messages

    def set_working_data(self, key: str, value: Any) -> None:
        """設置工作記憶數據"""
        self.working.set(key, value)

    def get_working_data(self, key: str, default: Any = None) -> Any:
        """獲取工作記憶數據"""
        return self.working.get(key, default)

    def create_plan(self, goal: str, steps: list[dict[str, Any]]) -> Plan:
        """創建任務計劃"""
        return self.planner.create_plan(goal, steps)

    def get_current_plan(self) -> Plan | None:
        """獲取當前計劃"""
        return self.planner.current_plan

    def update_plan_step(self, step_id: str, status: str, result: Any = None) -> None:
        """更新計劃步驟"""
        self.planner.update_step(step_id, status, result)

    def summarize(self) -> dict[str, Any]:
        """生成記憶摘要"""
        return {
            "short_term": {
                "message_count": len(self.short_term.messages),
                "recent_topics": self._extract_topics(),
            },
            "working": {"focus": self.working.focus, "data_keys": list(self.working.data.keys())},
            "planning": {
                "current_plan": (
                    self.planner.current_plan.goal if self.planner.current_plan else None
                ),
                "plan_count": len(self.planner.plans),
            },
        }

    def _extract_topics(self) -> list[str]:
        """提取最近話題（簡化版）"""
        topics = []
        recent = self.short_term.get_recent(5)
        for msg in recent:
            # 簡單提取：取每個訊息的前幾個詞
            words = msg.content.split()[:3]
            if words:
                topics.append(" ".join(words))
        return topics

    def clear(self) -> None:
        """清空所有記憶"""
        self.short_term.clear()
        self.working.clear()
        self.planner.plans.clear()
        self.planner.current_plan = None
        self.context_window.messages.clear()
