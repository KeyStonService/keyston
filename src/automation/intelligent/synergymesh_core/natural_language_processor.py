"""
Natural Language Processor - 自然語言處理器
零技術門檻界面 / Zero Technical Barrier Interface

This module enables non-engineers to interact with the system through natural
language, automatically translating business requirements into technical
implementations.

Core Capabilities:
- Natural language understanding and intent extraction
- Business requirement to technical specification conversion
- Context-aware conversation management
- Multi-language support (Traditional Chinese, English, etc.)

設計原則: 使用者無需理解底層技術細節，透過自然語言描述業務需求即可
"""

import logging
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Intent types for natural language processing"""
    DATA_MIGRATION = "data_migration"
    SYSTEM_INTEGRATION = "system_integration"
    CODE_ANALYSIS = "code_analysis"
    WORKFLOW_AUTOMATION = "workflow_automation"
    MONITORING_SETUP = "monitoring_setup"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Represents a parsed intent from natural language input"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    raw_query: str = ""
    language: str = "auto"
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TechnicalSpecification:
    """Technical specification generated from business requirements"""
    spec_id: str
    title: str
    description: str
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    estimated_complexity: str = "medium"
    dependencies: List[str] = field(default_factory=list)
    automation_level: str = "full"  # full, partial, manual
    generated_from: str = ""


class NaturalLanguageProcessor:
    """
    自然語言處理器 - 零技術門檻界面
    
    Natural Language Processor for zero-technical-barrier interface.
    Enables non-engineers to interact with the system through natural
    language and automatically translates business requirements into
    technical implementations.
    
    Features:
    - Intent recognition and classification
    - Entity extraction (systems, data types, actions)
    - Context management for multi-turn conversations
    - Technical specification generation
    - Multi-language support
    """
    
    # Language detection patterns
    CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        IntentType.DATA_MIGRATION: {
            "en": ["migrate", "sync", "transfer", "move data", "copy data", "import", "export"],
            "zh": ["遷移", "同步", "轉移", "移動資料", "匯入", "匯出", "資料同步"]
        },
        IntentType.SYSTEM_INTEGRATION: {
            "en": ["integrate", "connect", "link", "bridge", "api", "interface"],
            "zh": ["整合", "連接", "串接", "橋接", "介面", "對接"]
        },
        IntentType.CODE_ANALYSIS: {
            "en": ["analyze", "review", "check code", "scan", "inspect"],
            "zh": ["分析", "審查", "檢查代碼", "掃描", "檢視"]
        },
        IntentType.WORKFLOW_AUTOMATION: {
            "en": ["automate", "workflow", "schedule", "trigger", "pipeline"],
            "zh": ["自動化", "工作流", "排程", "觸發", "流程"]
        },
        IntentType.MONITORING_SETUP: {
            "en": ["monitor", "alert", "watch", "track", "observe"],
            "zh": ["監控", "警報", "追蹤", "觀測", "監視"]
        },
        IntentType.SECURITY_AUDIT: {
            "en": ["security", "audit", "vulnerability", "penetration", "secure"],
            "zh": ["安全", "審計", "漏洞", "滲透", "加固"]
        },
        IntentType.PERFORMANCE_OPTIMIZATION: {
            "en": ["optimize", "performance", "speed up", "faster", "efficiency"],
            "zh": ["優化", "性能", "加速", "效率", "提升"]
        },
        IntentType.DOCUMENTATION: {
            "en": ["document", "documentation", "explain", "describe", "wiki"],
            "zh": ["文檔", "說明", "解釋", "描述", "文件"]
        },
        IntentType.DEPLOYMENT: {
            "en": ["deploy", "release", "publish", "launch", "rollout"],
            "zh": ["部署", "發布", "上線", "發佈", "推出"]
        }
    }
    
    # Entity patterns
    SYSTEM_PATTERNS = {
        "en": [r"from\s+(\w+)\s+to\s+(\w+)", r"(\w+)\s+system", r"(\w+)\s+database"],
        "zh": [r"從\s*(\w+)\s*到\s*(\w+)", r"(\w+)\s*系統", r"(\w+)\s*資料庫"]
    }
    
    def __init__(self):
        """Initialize the Natural Language Processor"""
        self.conversation_context: Dict[str, List[ParsedIntent]] = {}
        self.session_count = 0
        logger.info("NaturalLanguageProcessor initialized - 自然語言處理器已初始化")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code ('zh' for Chinese, 'en' for English)
        """
        chinese_chars = len(self.CHINESE_PATTERN.findall(text))
        total_chars = len(text.replace(" ", ""))
        
        if total_chars == 0:
            return "en"
        
        # If more than 30% Chinese characters, consider it Chinese
        if chinese_chars / total_chars > 0.3:
            return "zh"
        return "en"
    
    def parse_intent(self, query: str, session_id: Optional[str] = None) -> ParsedIntent:
        """
        Parse user intent from natural language query
        
        解析使用者自然語言輸入，識別意圖
        
        Args:
            query: Natural language query from user
            session_id: Optional session ID for context management
            
        Returns:
            ParsedIntent with intent type, confidence, and extracted entities
        """
        logger.info(f"Parsing intent for query: {query[:100]}...")
        
        # Detect language
        language = self.detect_language(query)
        query_lower = query.lower()
        
        # Find best matching intent
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            lang_keywords = keywords.get(language, keywords.get("en", []))
            
            for keyword in lang_keywords:
                if keyword.lower() in query_lower:
                    # Calculate confidence based on keyword match
                    confidence = 0.7 + (len(keyword) / len(query_lower)) * 0.3
                    if confidence > best_confidence:
                        best_confidence = min(confidence, 0.95)
                        best_intent = intent_type
        
        # If no intent found, try general query
        if best_intent == IntentType.UNKNOWN:
            best_intent = IntentType.GENERAL_QUERY
            best_confidence = 0.5
        
        # Extract entities
        entities = self._extract_entities(query, language)
        
        # Get context from session
        context = {}
        if session_id and session_id in self.conversation_context:
            prev_intents = self.conversation_context[session_id]
            if prev_intents:
                context["previous_intent"] = prev_intents[-1].intent_type.value
                context["conversation_length"] = len(prev_intents)
        
        parsed = ParsedIntent(
            intent_type=best_intent,
            confidence=best_confidence,
            entities=entities,
            raw_query=query,
            language=language,
            context=context
        )
        
        # Store in session context
        if session_id:
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = []
            self.conversation_context[session_id].append(parsed)
        
        logger.info(f"Intent parsed: {best_intent.value} (confidence: {best_confidence:.2f})")
        return parsed
    
    def _extract_entities(self, query: str, language: str) -> Dict[str, Any]:
        """
        Extract entities from the query
        
        Args:
            query: User query
            language: Detected language
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract system names
        patterns = self.SYSTEM_PATTERNS.get(language, self.SYSTEM_PATTERNS["en"])
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    entities["source_system"] = matches[0][0]
                    if len(matches[0]) > 1:
                        entities["target_system"] = matches[0][1]
                else:
                    entities["system"] = matches[0]
        
        # Extract time-related entities
        time_patterns = {
            "en": [r"every\s+(\w+)", r"daily", r"weekly", r"monthly"],
            "zh": [r"每\s*(\w+)", r"每日", r"每週", r"每月"]
        }
        
        for pattern in time_patterns.get(language, []):
            if re.search(pattern, query, re.IGNORECASE):
                entities["schedule"] = pattern
        
        return entities
    
    async def translate_to_technical_spec(
        self,
        intent: ParsedIntent
    ) -> TechnicalSpecification:
        """
        Translate parsed intent into technical specification
        
        將業務需求自動翻譯為技術實現規格
        
        Args:
            intent: Parsed intent from natural language
            
        Returns:
            Technical specification with tasks and requirements
        """
        logger.info(f"Translating intent to technical spec: {intent.intent_type.value}")
        
        spec_id = f"SPEC-{self.session_count:04d}"
        self.session_count += 1
        
        # Generate tasks based on intent type
        tasks = await self._generate_tasks(intent)
        
        # Determine complexity
        complexity = self._estimate_complexity(intent, tasks)
        
        # Determine automation level
        automation_level = self._determine_automation_level(intent, tasks)
        
        # Generate dependencies
        dependencies = self._identify_dependencies(intent)
        
        # Create title based on intent
        title = self._generate_title(intent)
        
        # Create description
        description = self._generate_description(intent)
        
        spec = TechnicalSpecification(
            spec_id=spec_id,
            title=title,
            description=description,
            tasks=tasks,
            estimated_complexity=complexity,
            dependencies=dependencies,
            automation_level=automation_level,
            generated_from=intent.raw_query
        )
        
        logger.info(f"Technical spec generated: {spec_id} with {len(tasks)} tasks")
        return spec
    
    async def _generate_tasks(self, intent: ParsedIntent) -> List[Dict[str, Any]]:
        """Generate task list based on intent type"""
        tasks = []
        
        if intent.intent_type == IntentType.DATA_MIGRATION:
            tasks = [
                {
                    "id": "task-1",
                    "name": "Analyze Source System",
                    "description": "Analyze source system schema and data structure",
                    "automated": True,
                    "priority": 1
                },
                {
                    "id": "task-2",
                    "name": "Generate Migration Scripts",
                    "description": "Auto-generate migration scripts based on schema analysis",
                    "automated": True,
                    "priority": 2
                },
                {
                    "id": "task-3",
                    "name": "Execute Migration",
                    "description": "Execute migration with validation and rollback support",
                    "automated": True,
                    "priority": 3
                },
                {
                    "id": "task-4",
                    "name": "Verify Data Integrity",
                    "description": "Verify migrated data integrity and completeness",
                    "automated": True,
                    "priority": 4
                }
            ]
        elif intent.intent_type == IntentType.SYSTEM_INTEGRATION:
            tasks = [
                {
                    "id": "task-1",
                    "name": "Discover APIs",
                    "description": "Discover and document available APIs",
                    "automated": True,
                    "priority": 1
                },
                {
                    "id": "task-2",
                    "name": "Generate Integration Bridge",
                    "description": "Generate integration bridge code",
                    "automated": True,
                    "priority": 2
                },
                {
                    "id": "task-3",
                    "name": "Configure Authentication",
                    "description": "Configure authentication and authorization",
                    "automated": True,
                    "priority": 3
                },
                {
                    "id": "task-4",
                    "name": "Deploy Integration",
                    "description": "Deploy and test integration",
                    "automated": True,
                    "priority": 4
                }
            ]
        elif intent.intent_type == IntentType.CODE_ANALYSIS:
            tasks = [
                {
                    "id": "task-1",
                    "name": "Static Analysis",
                    "description": "Perform static code analysis",
                    "automated": True,
                    "priority": 1
                },
                {
                    "id": "task-2",
                    "name": "Security Scan",
                    "description": "Scan for security vulnerabilities",
                    "automated": True,
                    "priority": 2
                },
                {
                    "id": "task-3",
                    "name": "Generate Report",
                    "description": "Generate analysis report with recommendations",
                    "automated": True,
                    "priority": 3
                }
            ]
        elif intent.intent_type == IntentType.WORKFLOW_AUTOMATION:
            tasks = [
                {
                    "id": "task-1",
                    "name": "Analyze Workflow",
                    "description": "Analyze existing workflow and identify automation points",
                    "automated": True,
                    "priority": 1
                },
                {
                    "id": "task-2",
                    "name": "Generate Automation Scripts",
                    "description": "Generate workflow automation scripts",
                    "automated": True,
                    "priority": 2
                },
                {
                    "id": "task-3",
                    "name": "Configure Triggers",
                    "description": "Configure workflow triggers and schedules",
                    "automated": True,
                    "priority": 3
                }
            ]
        else:
            # Default task for general queries
            tasks = [
                {
                    "id": "task-1",
                    "name": "Process Request",
                    "description": "Process user request and determine action",
                    "automated": True,
                    "priority": 1
                }
            ]
        
        return tasks
    
    def _estimate_complexity(
        self,
        intent: ParsedIntent,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """Estimate complexity based on intent and tasks"""
        # Complexity heuristics
        if len(tasks) >= 4:
            return "high"
        elif len(tasks) >= 2:
            return "medium"
        return "low"
    
    def _determine_automation_level(
        self,
        intent: ParsedIntent,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """Determine automation level for the specification"""
        automated_count = sum(1 for t in tasks if t.get("automated", False))
        ratio = automated_count / len(tasks) if tasks else 0
        
        if ratio >= 0.9:
            return "full"
        elif ratio >= 0.5:
            return "partial"
        return "manual"
    
    def _identify_dependencies(self, intent: ParsedIntent) -> List[str]:
        """Identify dependencies based on intent type"""
        dependencies = []
        
        if intent.intent_type == IntentType.DATA_MIGRATION:
            dependencies = ["database_connector", "schema_analyzer", "migration_engine"]
        elif intent.intent_type == IntentType.SYSTEM_INTEGRATION:
            dependencies = ["api_gateway", "auth_service", "message_broker"]
        elif intent.intent_type == IntentType.CODE_ANALYSIS:
            dependencies = ["static_analyzer", "security_scanner", "report_generator"]
        elif intent.intent_type == IntentType.MONITORING_SETUP:
            dependencies = ["metrics_collector", "alert_manager", "dashboard_service"]
        
        return dependencies
    
    def _generate_title(self, intent: ParsedIntent) -> str:
        """Generate specification title"""
        titles = {
            IntentType.DATA_MIGRATION: "Data Migration Automation",
            IntentType.SYSTEM_INTEGRATION: "System Integration Bridge",
            IntentType.CODE_ANALYSIS: "Automated Code Analysis",
            IntentType.WORKFLOW_AUTOMATION: "Workflow Automation Pipeline",
            IntentType.MONITORING_SETUP: "Monitoring and Alerting Setup",
            IntentType.SECURITY_AUDIT: "Security Audit Automation",
            IntentType.PERFORMANCE_OPTIMIZATION: "Performance Optimization",
            IntentType.DOCUMENTATION: "Documentation Generation",
            IntentType.DEPLOYMENT: "Automated Deployment Pipeline",
            IntentType.GENERAL_QUERY: "Request Processing",
            IntentType.UNKNOWN: "Custom Request"
        }
        return titles.get(intent.intent_type, "Custom Request")
    
    def _generate_description(self, intent: ParsedIntent) -> str:
        """Generate specification description"""
        if intent.language == "zh":
            return f"根據使用者需求自動生成的技術規格：{intent.raw_query[:100]}"
        return f"Auto-generated technical specification from user request: {intent.raw_query[:100]}"
    
    async def process_natural_request(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process natural language request end-to-end
        
        完整處理自然語言請求，從解析到技術規格生成
        
        Args:
            query: Natural language query
            session_id: Optional session ID
            
        Returns:
            Complete processing result with intent and specification
        """
        logger.info(f"Processing natural request: {query[:50]}...")
        
        # Parse intent
        intent = self.parse_intent(query, session_id)
        
        # Generate technical specification
        spec = await self.translate_to_technical_spec(intent)
        
        result = {
            "status": "success",
            "intent": {
                "type": intent.intent_type.value,
                "confidence": intent.confidence,
                "language": intent.language,
                "entities": intent.entities
            },
            "specification": {
                "id": spec.spec_id,
                "title": spec.title,
                "description": spec.description,
                "tasks": spec.tasks,
                "complexity": spec.estimated_complexity,
                "automation_level": spec.automation_level,
                "dependencies": spec.dependencies
            },
            "message": self._generate_user_message(intent, spec)
        }
        
        logger.info(f"Natural request processed: {spec.spec_id}")
        return result
    
    def _generate_user_message(
        self,
        intent: ParsedIntent,
        spec: TechnicalSpecification
    ) -> str:
        """Generate user-friendly response message"""
        if intent.language == "zh":
            return (
                f"已理解您的需求：{spec.title}\n"
                f"系統將自動執行 {len(spec.tasks)} 個任務\n"
                f"自動化程度：{spec.automation_level}\n"
                f"預估複雜度：{spec.estimated_complexity}"
            )
        return (
            f"Understood your request: {spec.title}\n"
            f"System will automatically execute {len(spec.tasks)} tasks\n"
            f"Automation level: {spec.automation_level}\n"
            f"Estimated complexity: {spec.estimated_complexity}"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics"""
        total_sessions = len(self.conversation_context)
        total_intents = sum(len(intents) for intents in self.conversation_context.values())
        
        intent_counts = {}
        for intents in self.conversation_context.values():
            for intent in intents:
                intent_type = intent.intent_type.value
                intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "total_intents_processed": total_intents,
            "specs_generated": self.session_count,
            "intent_distribution": intent_counts
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear conversation context for a session"""
        if session_id in self.conversation_context:
            del self.conversation_context[session_id]
            logger.info(f"Session cleared: {session_id}")
            return True
        return False


# Example usage
if __name__ == "__main__":
    import json
    
    async def main():
        processor = NaturalLanguageProcessor()
        
        # Test cases in different languages
        test_queries = [
            "我需要將用戶資料從舊系統同步到新系統",  # Chinese - Data migration
            "I want to integrate the payment API with our backend",  # English - Integration
            "請分析這段代碼的性能問題",  # Chinese - Code analysis
            "Set up monitoring for the production servers",  # English - Monitoring
            "幫我自動化部署流程",  # Chinese - Deployment
        ]
        
        print("=== Natural Language Processor Test ===\n")
        
        for query in test_queries:
            print(f"Query: {query}")
            result = await processor.process_natural_request(query, session_id="test-session")
            print(f"Result:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
            print("-" * 50 + "\n")
        
        # Show statistics
        stats = processor.get_statistics()
        print("=== Statistics ===")
        print(json.dumps(stats, indent=2))
    
    asyncio.run(main())
