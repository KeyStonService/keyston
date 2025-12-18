"""
Natural Language Interaction Layer - 自然語言交互層
Phase 2: Multi-modal Interface Support

This module provides the Natural Language Interaction (NLI) layer for SynergyMesh,
enabling non-technical users to interact with the system through multiple modalities.

Supported Interfaces:
- Text conversation (文字對話)
- Voice interface (語音接口) - stub for integration
- Visual drag-drop (視覺拖拉) - configuration interface
- Gesture control (手勢控制) - stub for integration

設計原則: 使用者無需理解底層技術細節，透過自然語言描述業務需求即可
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """Supported interaction modes"""
    TEXT = "text"
    VOICE = "voice"
    VISUAL = "visual"
    GESTURE = "gesture"
    MULTIMODAL = "multimodal"


class UserIntent(Enum):
    """User intent categories"""
    QUERY = "query"
    COMMAND = "command"
    CONFIGURATION = "configuration"
    FEEDBACK = "feedback"
    HELP = "help"
    CANCEL = "cancel"


@dataclass
class InteractionContext:
    """Context for a user interaction session"""
    session_id: str
    user_id: str = "anonymous"
    mode: InteractionMode = InteractionMode.TEXT
    language: str = "auto"
    history: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class InteractionResult:
    """Result of processing a user interaction"""
    result_id: str
    success: bool
    intent: UserIntent
    response_text: str
    response_data: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processing_time_ms: float = 0.0


@dataclass
class VisualComponent:
    """Visual drag-drop component definition"""
    component_id: str
    component_type: str
    label: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)
    position: Dict[str, float] = field(default_factory=dict)


class NaturalLanguageInteractionLayer:
    """
    自然語言交互層 - 零技術門檻人機接口
    
    Natural Language Interaction Layer providing multi-modal interface
    for zero-technical-barrier system interaction.
    
    Features:
    - 文字對話: Text-based conversation interface
    - 語音接口: Voice recognition and synthesis (stub)
    - 視覺拖拉: Visual drag-drop configuration
    - 手勢控制: Gesture-based control (stub)
    
    設計目標:
    - 零學習成本: No learning curve for users
    - 多模態支援: Support multiple interaction modes
    - 上下文理解: Context-aware conversation
    - 智能推薦: Intelligent action suggestions
    """
    
    # Response templates by language
    RESPONSE_TEMPLATES = {
        "zh": {
            "greeting": "您好！我是 SynergyMesh 智能助手，請問有什麼需要幫助？",
            "understanding": "我理解您想要 {action}。",
            "processing": "正在處理您的請求...",
            "completed": "已完成 {action}。",
            "clarification": "請問您是指 {options}？",
            "error": "抱歉，處理時發生錯誤：{error}",
            "help": "您可以嘗試以下操作：{suggestions}"
        },
        "en": {
            "greeting": "Hello! I'm SynergyMesh assistant. How can I help you?",
            "understanding": "I understand you want to {action}.",
            "processing": "Processing your request...",
            "completed": "Completed {action}.",
            "clarification": "Do you mean {options}?",
            "error": "Sorry, an error occurred: {error}",
            "help": "You can try: {suggestions}"
        }
    }
    
    def __init__(self):
        """Initialize the Natural Language Interaction Layer"""
        self.sessions: Dict[str, InteractionContext] = {}
        self.visual_components: Dict[str, VisualComponent] = {}
        self.interaction_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        
        # Statistics
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "mode_usage": {mode.value: 0 for mode in InteractionMode}
        }
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.info("NaturalLanguageInteractionLayer initialized - 自然語言交互層已初始化")
    
    def _register_default_handlers(self) -> None:
        """Register default interaction handlers"""
        self.interaction_handlers["help"] = self._handle_help
        self.interaction_handlers["status"] = self._handle_status
        self.interaction_handlers["cancel"] = self._handle_cancel
    
    def create_session(
        self,
        user_id: str = "anonymous",
        mode: InteractionMode = InteractionMode.TEXT,
        language: str = "auto",
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new interaction session
        
        創建新的互動會話
        
        Args:
            user_id: User identifier
            mode: Interaction mode
            language: Preferred language
            preferences: User preferences
            
        Returns:
            Session ID
        """
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        
        context = InteractionContext(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            language=language,
            preferences=preferences or {}
        )
        
        self.sessions[session_id] = context
        logger.info(f"Session created: {session_id} (mode: {mode.value})")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[InteractionContext]:
        """Get session context by ID"""
        return self.sessions.get(session_id)
    
    async def process_text_input(
        self,
        session_id: str,
        text: str
    ) -> InteractionResult:
        """
        Process text input from user
        
        處理使用者文字輸入
        
        Args:
            session_id: Session identifier
            text: User input text
            
        Returns:
            Interaction result with response
        """
        start_time = datetime.now()
        result_id = f"result-{uuid.uuid4().hex[:8]}"
        
        # Get or create session
        context = self.sessions.get(session_id)
        if not context:
            session_id = self.create_session()
            context = self.sessions[session_id]
        
        # Update statistics
        self.stats["total_interactions"] += 1
        self.stats["mode_usage"][InteractionMode.TEXT.value] += 1
        
        # Detect language
        language = self._detect_language(text) if context.language == "auto" else context.language
        
        # Analyze intent
        intent, confidence = self._analyze_intent(text, language)
        
        # Generate response
        response_text, response_data, suggestions = await self._generate_response(
            text, intent, language, context
        )
        
        # Record in history
        context.history.append({
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "intent": intent.value,
            "response": response_text
        })
        context.last_activity = datetime.now()
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        self.stats["successful_interactions"] += 1
        
        return InteractionResult(
            result_id=result_id,
            success=True,
            intent=intent,
            response_text=response_text,
            response_data=response_data,
            suggested_actions=suggestions,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        import re
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
        chinese_chars = len(chinese_pattern.findall(text))
        total_chars = len(text.replace(" ", ""))
        
        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            return "zh"
        return "en"
    
    def _analyze_intent(self, text: str, language: str) -> tuple:
        """Analyze user intent from text"""
        text_lower = text.lower()
        
        # Help intent
        help_keywords = ["help", "幫助", "怎麼", "如何", "什麼是"]
        if any(kw in text_lower for kw in help_keywords):
            return UserIntent.HELP, 0.9
        
        # Cancel intent
        cancel_keywords = ["cancel", "取消", "停止", "不要"]
        if any(kw in text_lower for kw in cancel_keywords):
            return UserIntent.CANCEL, 0.9
        
        # Query intent
        query_keywords = ["show", "list", "get", "顯示", "列出", "查詢", "查看"]
        if any(kw in text_lower for kw in query_keywords):
            return UserIntent.QUERY, 0.8
        
        # Command intent (default for action requests)
        command_keywords = ["create", "migrate", "deploy", "sync", "建立", "遷移", "部署", "同步"]
        if any(kw in text_lower for kw in command_keywords):
            return UserIntent.COMMAND, 0.85
        
        # Configuration intent
        config_keywords = ["config", "setting", "configure", "設定", "配置"]
        if any(kw in text_lower for kw in config_keywords):
            return UserIntent.CONFIGURATION, 0.8
        
        # Default to query
        return UserIntent.QUERY, 0.5
    
    async def _generate_response(
        self,
        text: str,
        intent: UserIntent,
        language: str,
        context: InteractionContext
    ) -> tuple:
        """Generate response based on intent"""
        templates = self.RESPONSE_TEMPLATES.get(language, self.RESPONSE_TEMPLATES["en"])
        
        response_data = {
            "intent": intent.value,
            "language": language,
            "session_id": context.session_id
        }
        suggestions = []
        
        if intent == UserIntent.HELP:
            suggestions = [
                "查看系統狀態" if language == "zh" else "Check system status",
                "創建新任務" if language == "zh" else "Create new task",
                "數據遷移" if language == "zh" else "Data migration"
            ]
            response_text = templates["help"].format(suggestions=", ".join(suggestions))
            
        elif intent == UserIntent.CANCEL:
            response_text = "已取消操作。" if language == "zh" else "Operation cancelled."
            
        elif intent == UserIntent.COMMAND:
            # Extract action from text
            action = self._extract_action(text, language)
            response_text = templates["understanding"].format(action=action)
            response_data["action"] = action
            suggestions = [
                "確認執行" if language == "zh" else "Confirm execution",
                "查看詳情" if language == "zh" else "View details",
                "取消" if language == "zh" else "Cancel"
            ]
            
        elif intent == UserIntent.QUERY:
            response_text = "正在查詢相關信息..." if language == "zh" else "Querying information..."
            
        else:
            response_text = templates["greeting"]
        
        return response_text, response_data, suggestions
    
    def _extract_action(self, text: str, language: str) -> str:
        """Extract action description from text"""
        # Simplified action extraction
        action_patterns = {
            "zh": {
                "遷移": "數據遷移",
                "同步": "數據同步",
                "部署": "系統部署",
                "建立": "創建資源",
                "分析": "數據分析"
            },
            "en": {
                "migrate": "data migration",
                "sync": "data synchronization",
                "deploy": "system deployment",
                "create": "resource creation",
                "analyze": "data analysis"
            }
        }
        
        patterns = action_patterns.get(language, action_patterns["en"])
        text_lower = text.lower()
        
        for keyword, action in patterns.items():
            if keyword in text_lower:
                return action
        
        return text[:50] if len(text) > 50 else text
    
    async def _handle_help(self, context: InteractionContext) -> Dict[str, Any]:
        """Handle help request"""
        return {
            "available_commands": [
                "create", "migrate", "deploy", "sync", "analyze",
                "建立", "遷移", "部署", "同步", "分析"
            ],
            "examples": [
                "我需要將用戶資料從舊系統同步到新系統",
                "I want to migrate data from MySQL to PostgreSQL"
            ]
        }
    
    async def _handle_status(self, context: InteractionContext) -> Dict[str, Any]:
        """Handle status request"""
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "history_length": len(context.history),
            "mode": context.mode.value
        }
    
    async def _handle_cancel(self, context: InteractionContext) -> Dict[str, Any]:
        """Handle cancel request"""
        return {"cancelled": True}
    
    # Visual Drag-Drop Interface Methods
    
    def register_visual_component(
        self,
        component_type: str,
        label: str,
        description: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a visual component for drag-drop interface
        
        註冊可拖拉的視覺組件
        
        Args:
            component_type: Type of component
            label: Display label
            description: Component description
            properties: Default properties
            
        Returns:
            Component ID
        """
        component_id = f"comp-{uuid.uuid4().hex[:8]}"
        
        component = VisualComponent(
            component_id=component_id,
            component_type=component_type,
            label=label,
            description=description,
            properties=properties or {}
        )
        
        self.visual_components[component_id] = component
        logger.info(f"Visual component registered: {label} ({component_type})")
        
        return component_id
    
    def get_available_components(self) -> List[Dict[str, Any]]:
        """
        Get all available visual components
        
        獲取所有可用的視覺組件
        """
        return [
            {
                "id": comp.component_id,
                "type": comp.component_type,
                "label": comp.label,
                "description": comp.description,
                "properties": comp.properties
            }
            for comp in self.visual_components.values()
        ]
    
    def create_visual_workflow(
        self,
        name: str,
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a workflow from visual components
        
        從視覺組件創建工作流
        
        Args:
            name: Workflow name
            components: List of component configurations
            
        Returns:
            Workflow definition
        """
        workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"
        
        workflow = {
            "workflow_id": workflow_id,
            "name": name,
            "components": components,
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        logger.info(f"Visual workflow created: {name} ({workflow_id})")
        return workflow
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get interaction layer statistics"""
        return {
            "total_interactions": self.stats["total_interactions"],
            "successful_interactions": self.stats["successful_interactions"],
            "success_rate": round(
                self.stats["successful_interactions"] / max(self.stats["total_interactions"], 1) * 100, 2
            ),
            "mode_usage": self.stats["mode_usage"],
            "active_sessions": len(self.sessions),
            "registered_components": len(self.visual_components)
        }
    
    def close_session(self, session_id: str) -> bool:
        """Close an interaction session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session closed: {session_id}")
            return True
        return False


# Example usage
if __name__ == "__main__":
    import json
    
    async def main():
        nli = NaturalLanguageInteractionLayer()
        
        print("=== Natural Language Interaction Layer Test ===\n")
        
        # Create session
        session_id = nli.create_session(user_id="test-user", language="auto")
        print(f"Session created: {session_id}")
        
        # Test interactions
        test_inputs = [
            "我需要將用戶資料從舊系統同步到新系統",
            "How can I migrate data?",
            "幫助",
            "取消"
        ]
        
        for text in test_inputs:
            print(f"\nInput: {text}")
            result = await nli.process_text_input(session_id, text)
            print(f"Response: {result.response_text}")
            print(f"Intent: {result.intent.value}, Confidence: {result.confidence}")
        
        # Register visual components
        print("\n=== Visual Components ===")
        nli.register_visual_component("source", "數據源", "Data source connection")
        nli.register_visual_component("transform", "數據轉換", "Data transformation")
        nli.register_visual_component("target", "目標", "Target destination")
        
        components = nli.get_available_components()
        print(f"Registered {len(components)} components")
        
        # Get statistics
        print("\n=== Statistics ===")
        stats = nli.get_statistics()
        print(json.dumps(stats, indent=2))
        
        # Close session
        nli.close_session(session_id)
    
    asyncio.run(main())
