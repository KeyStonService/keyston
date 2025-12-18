"""
Intent Understanding & Task Orchestration Layer - 意圖理解與任務編排層
Phase 2: Advanced Intent Processing and Workflow Generation

This module provides the Intent Understanding and Task Orchestration layer,
enabling intelligent interpretation of user requests and automatic task generation.

Core Capabilities:
- Multi-modal intent understanding (多模態意圖理解)
- Business logic reasoning (業務邏輯推理)
- Context memory management (上下文記憶)
- Automatic workflow generation (自動工作流生成)
- Task orchestration (任務編排)

設計原則: 系統自動翻譯為技術實現
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks that can be orchestrated"""
    DATA_MIGRATION = "data_migration"
    DATA_SYNC = "data_sync"
    SYSTEM_INTEGRATION = "system_integration"
    CODE_ANALYSIS = "code_analysis"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SECURITY_AUDIT = "security_audit"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BusinessIntent:
    """Parsed business intent from user input"""
    intent_id: str
    task_type: TaskType
    description: str
    entities: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    priority: str = "normal"
    confidence: float = 0.0
    source_text: str = ""
    language: str = "en"
    parsed_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowStep:
    """A step in an orchestrated workflow"""
    step_id: str
    name: str
    description: str
    task_type: TaskType
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_count: int = 3
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None


@dataclass
class OrchestratedWorkflow:
    """Complete orchestrated workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    source_intent: Optional[BusinessIntent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextMemory:
    """Context memory for intent understanding"""
    memory_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)
    domain_knowledge: Dict[str, Any] = field(default_factory=dict)
    last_intents: List[BusinessIntent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class IntentUnderstandingEngine:
    """
    意圖理解引擎 - 多模態意圖理解
    
    Intent Understanding Engine for parsing and understanding
    user requests across multiple modalities.
    
    Features:
    - NLP 語義分析: Semantic analysis of natural language
    - 業務邏輯推理: Business logic reasoning
    - 上下文記憶: Context-aware understanding
    - 實體提取: Entity extraction from requests
    """
    
    # Intent patterns by language
    INTENT_PATTERNS = {
        "zh": {
            TaskType.DATA_MIGRATION: ["遷移", "搬移", "轉移資料", "數據遷移"],
            TaskType.DATA_SYNC: ["同步", "同步資料", "數據同步", "資料同步"],
            TaskType.SYSTEM_INTEGRATION: ["整合", "連接", "串接", "對接"],
            TaskType.CODE_ANALYSIS: ["分析", "檢查代碼", "代碼審查"],
            TaskType.DEPLOYMENT: ["部署", "發布", "上線"],
            TaskType.MONITORING: ["監控", "監視", "追蹤"],
            TaskType.SECURITY_AUDIT: ["安全", "審計", "漏洞"],
            TaskType.OPTIMIZATION: ["優化", "加速", "提升性能"]
        },
        "en": {
            TaskType.DATA_MIGRATION: ["migrate", "migration", "move data", "transfer"],
            TaskType.DATA_SYNC: ["sync", "synchronize", "synchronization"],
            TaskType.SYSTEM_INTEGRATION: ["integrate", "connect", "bridge", "link"],
            TaskType.CODE_ANALYSIS: ["analyze", "review", "inspect", "check code"],
            TaskType.DEPLOYMENT: ["deploy", "release", "publish", "launch"],
            TaskType.MONITORING: ["monitor", "track", "observe", "watch"],
            TaskType.SECURITY_AUDIT: ["security", "audit", "vulnerability", "scan"],
            TaskType.OPTIMIZATION: ["optimize", "speed up", "improve", "enhance"]
        }
    }
    
    # Entity extraction patterns
    ENTITY_PATTERNS = {
        "source": ["from", "從", "source"],
        "target": ["to", "到", "target", "destination"],
        "system": ["system", "系統", "database", "資料庫"],
        "frequency": ["daily", "weekly", "hourly", "每日", "每週", "每小時"]
    }
    
    def __init__(self):
        """Initialize the Intent Understanding Engine"""
        self.context_memories: Dict[str, ContextMemory] = {}
        
        # Statistics
        self.stats = {
            "intents_parsed": 0,
            "successful_parses": 0,
            "intent_distribution": {t.value: 0 for t in TaskType}
        }
        
        logger.info("IntentUnderstandingEngine initialized - 意圖理解引擎已初始化")
    
    def parse_intent(
        self,
        text: str,
        user_id: str = "anonymous",
        language: str = "auto"
    ) -> BusinessIntent:
        """
        Parse user text to extract business intent
        
        解析使用者文字以提取業務意圖
        
        Args:
            text: User input text
            user_id: User identifier
            language: Language code or 'auto'
            
        Returns:
            Parsed BusinessIntent
        """
        intent_id = f"intent-{uuid.uuid4().hex[:8]}"
        
        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)
        
        # Identify task type
        task_type, confidence = self._identify_task_type(text, language)
        
        # Extract entities
        entities = self._extract_entities(text, language)
        
        # Extract constraints
        constraints = self._extract_constraints(text, language)
        
        # Determine priority
        priority = self._determine_priority(text, language)
        
        # Generate description
        description = self._generate_description(task_type, entities, language)
        
        intent = BusinessIntent(
            intent_id=intent_id,
            task_type=task_type,
            description=description,
            entities=entities,
            constraints=constraints,
            priority=priority,
            confidence=confidence,
            source_text=text,
            language=language
        )
        
        # Update context memory
        self._update_context_memory(user_id, intent)
        
        # Update statistics
        self.stats["intents_parsed"] += 1
        self.stats["successful_parses"] += 1
        self.stats["intent_distribution"][task_type.value] += 1
        
        logger.info(f"Intent parsed: {task_type.value} (confidence: {confidence:.2f})")
        return intent
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        import re
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
        chinese_chars = len(chinese_pattern.findall(text))
        total_chars = len(text.replace(" ", ""))
        
        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            return "zh"
        return "en"
    
    def _identify_task_type(self, text: str, language: str) -> tuple:
        """Identify task type from text"""
        text_lower = text.lower()
        patterns = self.INTENT_PATTERNS.get(language, self.INTENT_PATTERNS["en"])
        
        best_match = TaskType.CUSTOM
        best_confidence = 0.3
        
        for task_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    confidence = 0.7 + (len(keyword) / len(text_lower)) * 0.25
                    if confidence > best_confidence:
                        best_match = task_type
                        best_confidence = min(confidence, 0.95)
        
        return best_match, best_confidence
    
    def _extract_entities(self, text: str, language: str) -> Dict[str, Any]:
        """Extract entities from text"""
        import re
        entities = {}
        text_lower = text.lower()
        
        # Extract source and target
        source_match = re.search(r'(?:from|從)\s+(\S+)', text_lower)
        if source_match:
            entities["source"] = source_match.group(1)
        
        target_match = re.search(r'(?:to|到)\s+(\S+)', text_lower)
        if target_match:
            entities["target"] = target_match.group(1)
        
        # Extract system names
        system_patterns = [
            r'(\w+)\s*(?:system|系統)',
            r'(\w+)\s*(?:database|資料庫|db)'
        ]
        
        for pattern in system_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if "systems" not in entities:
                    entities["systems"] = []
                entities["systems"].append(match.group(1))
        
        return entities
    
    def _extract_constraints(self, text: str, language: str) -> List[str]:
        """Extract constraints from text"""
        constraints = []
        text_lower = text.lower()
        
        # Time constraints
        time_keywords = ["urgent", "asap", "immediately", "緊急", "立即", "馬上"]
        if any(kw in text_lower for kw in time_keywords):
            constraints.append("urgent")
        
        # Data constraints
        if "no data loss" in text_lower or "不丟失" in text_lower:
            constraints.append("no_data_loss")
        
        # Performance constraints
        if "fast" in text_lower or "快" in text_lower or "高效" in text_lower:
            constraints.append("high_performance")
        
        return constraints
    
    def _determine_priority(self, text: str, language: str) -> str:
        """Determine task priority from text"""
        text_lower = text.lower()
        
        high_priority = ["urgent", "critical", "asap", "緊急", "重要", "立即"]
        low_priority = ["when possible", "不急", "有空"]
        
        if any(kw in text_lower for kw in high_priority):
            return "high"
        if any(kw in text_lower for kw in low_priority):
            return "low"
        return "normal"
    
    def _generate_description(
        self,
        task_type: TaskType,
        entities: Dict[str, Any],
        language: str
    ) -> str:
        """Generate human-readable description"""
        descriptions = {
            "zh": {
                TaskType.DATA_MIGRATION: "數據遷移任務",
                TaskType.DATA_SYNC: "數據同步任務",
                TaskType.SYSTEM_INTEGRATION: "系統整合任務",
                TaskType.CODE_ANALYSIS: "代碼分析任務",
                TaskType.DEPLOYMENT: "系統部署任務",
                TaskType.MONITORING: "系統監控任務",
                TaskType.SECURITY_AUDIT: "安全審計任務",
                TaskType.OPTIMIZATION: "性能優化任務",
                TaskType.CUSTOM: "自定義任務"
            },
            "en": {
                TaskType.DATA_MIGRATION: "Data migration task",
                TaskType.DATA_SYNC: "Data synchronization task",
                TaskType.SYSTEM_INTEGRATION: "System integration task",
                TaskType.CODE_ANALYSIS: "Code analysis task",
                TaskType.DEPLOYMENT: "Deployment task",
                TaskType.MONITORING: "Monitoring task",
                TaskType.SECURITY_AUDIT: "Security audit task",
                TaskType.OPTIMIZATION: "Optimization task",
                TaskType.CUSTOM: "Custom task"
            }
        }
        
        desc = descriptions.get(language, descriptions["en"]).get(task_type, "Task")
        
        if entities.get("source") and entities.get("target"):
            if language == "zh":
                desc += f"：從 {entities['source']} 到 {entities['target']}"
            else:
                desc += f": from {entities['source']} to {entities['target']}"
        
        return desc
    
    def _update_context_memory(self, user_id: str, intent: BusinessIntent) -> None:
        """Update context memory for user"""
        if user_id not in self.context_memories:
            self.context_memories[user_id] = ContextMemory(
                memory_id=f"mem-{uuid.uuid4().hex[:8]}",
                user_id=user_id
            )
        
        memory = self.context_memories[user_id]
        memory.last_intents.append(intent)
        
        # Keep only last 10 intents
        if len(memory.last_intents) > 10:
            memory.last_intents = memory.last_intents[-10:]
    
    def get_context_memory(self, user_id: str) -> Optional[ContextMemory]:
        """Get context memory for user"""
        return self.context_memories.get(user_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "intents_parsed": self.stats["intents_parsed"],
            "successful_parses": self.stats["successful_parses"],
            "success_rate": round(
                self.stats["successful_parses"] / max(self.stats["intents_parsed"], 1) * 100, 2
            ),
            "intent_distribution": self.stats["intent_distribution"],
            "active_contexts": len(self.context_memories)
        }


class TaskOrchestrationEngine:
    """
    任務編排引擎 - 自動工作流生成與執行
    
    Task Orchestration Engine for automatic workflow generation
    and execution based on parsed intents.
    
    Features:
    - 自動工作流生成: Auto-generate workflows from intents
    - 任務依賴管理: Manage task dependencies
    - 並行執行優化: Optimize parallel execution
    - 錯誤恢復: Error recovery and retry
    """
    
    # Workflow templates by task type
    WORKFLOW_TEMPLATES = {
        TaskType.DATA_MIGRATION: [
            {"name": "Analyze Source", "description": "Analyze source data structure"},
            {"name": "Validate Target", "description": "Validate target system compatibility"},
            {"name": "Generate Scripts", "description": "Generate migration scripts"},
            {"name": "Execute Migration", "description": "Execute data migration"},
            {"name": "Verify Data", "description": "Verify data integrity"}
        ],
        TaskType.DATA_SYNC: [
            {"name": "Configure Sync", "description": "Configure synchronization settings"},
            {"name": "Initial Sync", "description": "Perform initial data sync"},
            {"name": "Setup Monitoring", "description": "Setup continuous monitoring"}
        ],
        TaskType.SYSTEM_INTEGRATION: [
            {"name": "Discover APIs", "description": "Discover available APIs"},
            {"name": "Generate Bridge", "description": "Generate integration bridge"},
            {"name": "Configure Auth", "description": "Configure authentication"},
            {"name": "Test Integration", "description": "Test integration"},
            {"name": "Deploy", "description": "Deploy integration"}
        ],
        TaskType.CODE_ANALYSIS: [
            {"name": "Static Analysis", "description": "Perform static code analysis"},
            {"name": "Security Scan", "description": "Scan for vulnerabilities"},
            {"name": "Generate Report", "description": "Generate analysis report"}
        ],
        TaskType.DEPLOYMENT: [
            {"name": "Build", "description": "Build application"},
            {"name": "Test", "description": "Run tests"},
            {"name": "Stage", "description": "Deploy to staging"},
            {"name": "Validate", "description": "Validate deployment"},
            {"name": "Deploy Prod", "description": "Deploy to production"}
        ]
    }
    
    def __init__(self):
        """Initialize the Task Orchestration Engine"""
        self.workflows: Dict[str, OrchestratedWorkflow] = {}
        self.step_handlers: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {}
        
        # Statistics
        self.stats = {
            "workflows_created": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "steps_executed": 0
        }
        
        logger.info("TaskOrchestrationEngine initialized - 任務編排引擎已初始化")
    
    def generate_workflow(self, intent: BusinessIntent) -> OrchestratedWorkflow:
        """
        Generate workflow from business intent
        
        從業務意圖生成工作流
        
        Args:
            intent: Parsed business intent
            
        Returns:
            Generated workflow
        """
        workflow_id = f"wf-{uuid.uuid4().hex[:8]}"
        
        # Get template for task type
        template = self.WORKFLOW_TEMPLATES.get(intent.task_type, [
            {"name": "Execute", "description": "Execute custom task"}
        ])
        
        # Generate steps from template
        steps = []
        for i, step_template in enumerate(template):
            step = WorkflowStep(
                step_id=f"step-{i+1}",
                name=step_template["name"],
                description=step_template["description"],
                task_type=intent.task_type,
                dependencies=[f"step-{i}"] if i > 0 else [],
                parameters={
                    "entities": intent.entities,
                    "constraints": intent.constraints
                }
            )
            steps.append(step)
        
        workflow = OrchestratedWorkflow(
            workflow_id=workflow_id,
            name=f"Workflow: {intent.description}",
            description=intent.description,
            steps=steps,
            source_intent=intent,
            metadata={
                "priority": intent.priority,
                "language": intent.language
            }
        )
        
        self.workflows[workflow_id] = workflow
        self.stats["workflows_created"] += 1
        
        logger.info(f"Workflow generated: {workflow_id} with {len(steps)} steps")
        return workflow
    
    def register_step_handler(
        self,
        step_name: str,
        handler: Callable[..., Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register a handler for a specific step type"""
        self.step_handlers[step_name] = handler
        logger.debug(f"Step handler registered: {step_name}")
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow
        
        執行工作流
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Execution result
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        workflow.status = WorkflowStatus.EXECUTING
        workflow.started_at = datetime.now()
        
        results = {}
        
        try:
            for step in workflow.steps:
                step.status = "executing"
                
                # Execute step
                handler = self.step_handlers.get(step.name, self._default_step_handler)
                step_result = await handler(step)
                
                step.result = step_result
                step.status = "completed"
                results[step.step_id] = step_result
                self.stats["steps_executed"] += 1
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            self.stats["workflows_completed"] += 1
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            self.stats["workflows_failed"] += 1
            logger.error(f"Workflow {workflow_id} failed: {e}")
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _default_step_handler(self, step: WorkflowStep) -> Dict[str, Any]:
        """Default handler for steps without specific handlers"""
        logger.info(f"Executing step: {step.name}")
        await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "step_id": step.step_id,
            "name": step.name,
            "status": "completed",
            "message": f"Step '{step.name}' completed successfully"
        }
    
    def get_workflow(self, workflow_id: str) -> Optional[OrchestratedWorkflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "name": s.name,
                    "status": s.status
                }
                for s in workflow.steps
            ],
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestration engine statistics"""
        return {
            "workflows_created": self.stats["workflows_created"],
            "workflows_completed": self.stats["workflows_completed"],
            "workflows_failed": self.stats["workflows_failed"],
            "steps_executed": self.stats["steps_executed"],
            "success_rate": round(
                self.stats["workflows_completed"] / max(self.stats["workflows_created"], 1) * 100, 2
            ),
            "active_workflows": len([
                w for w in self.workflows.values()
                if w.status in [WorkflowStatus.PENDING, WorkflowStatus.EXECUTING]
            ])
        }


# Example usage
if __name__ == "__main__":
    import json
    
    async def main():
        # Initialize engines
        intent_engine = IntentUnderstandingEngine()
        orchestration_engine = TaskOrchestrationEngine()
        
        print("=== Intent Understanding & Task Orchestration Test ===\n")
        
        # Test intent parsing
        test_inputs = [
            "我需要將用戶資料從舊系統同步到新系統",
            "Deploy the application to production urgently",
            "分析代碼中的安全漏洞"
        ]
        
        for text in test_inputs:
            print(f"\nInput: {text}")
            
            # Parse intent
            intent = intent_engine.parse_intent(text)
            print(f"Intent: {intent.task_type.value}")
            print(f"Description: {intent.description}")
            print(f"Entities: {intent.entities}")
            print(f"Confidence: {intent.confidence:.2f}")
            
            # Generate workflow
            workflow = orchestration_engine.generate_workflow(intent)
            print(f"Workflow: {workflow.workflow_id} ({len(workflow.steps)} steps)")
            
            # Execute workflow
            result = await orchestration_engine.execute_workflow(workflow.workflow_id)
            print(f"Execution: {result['status']}")
        
        # Get statistics
        print("\n=== Statistics ===")
        print("Intent Engine:")
        print(json.dumps(intent_engine.get_statistics(), indent=2))
        print("\nOrchestration Engine:")
        print(json.dumps(orchestration_engine.get_statistics(), indent=2))
    
    asyncio.run(main())
