"""
Context Understanding Engine (上下文理解引擎)

Phase 5 Component: Deep context understanding for accurate AI responses.

核心功能：
1. 深層上下文分析 - 理解用戶請求的真正意圖
2. 業務邏輯推理 - 根據業務邏輯判斷最佳方案
3. 歷史上下文記憶 - 記住之前的對話和決策
4. 多維度需求解析 - 從多個角度理解需求

Design Philosophy: "讓程式服務於人類，而非人類服務於程式"

研究顯示：62% 的開發者花費大量時間修復 AI 因誤解上下文而產生的錯誤
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import re


class ContextType(Enum):
    """Context types (上下文類型)"""
    TECHNICAL = "technical"       # 技術上下文
    BUSINESS = "business"         # 業務上下文
    USER = "user"                 # 用戶偏好上下文
    PROJECT = "project"           # 項目上下文
    CONVERSATION = "conversation" # 對話上下文
    DOMAIN = "domain"             # 領域知識上下文


class IntentCategory(Enum):
    """Intent categories (意圖類別)"""
    OPTIMIZATION = "optimization"     # 優化請求
    MIGRATION = "migration"           # 遷移請求
    DEBUGGING = "debugging"           # 調試請求
    REFACTORING = "refactoring"       # 重構請求
    NEW_FEATURE = "new_feature"       # 新功能請求
    SECURITY = "security"             # 安全相關
    DOCUMENTATION = "documentation"   # 文檔請求
    TESTING = "testing"               # 測試請求
    DEPLOYMENT = "deployment"         # 部署請求
    QUERY = "query"                   # 查詢請求


@dataclass
class ContextEntry:
    """A single context entry (單個上下文條目)"""
    context_id: str
    context_type: ContextType
    content: dict[str, Any]
    relevance_score: float = 1.0  # 相關性分數 0-1
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedIntent:
    """Parsed user intent (解析後的用戶意圖)"""
    primary_intent: IntentCategory
    secondary_intents: list[IntentCategory] = field(default_factory=list)
    confidence: float = 0.0
    entities: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    implicit_requirements: list[str] = field(default_factory=list)


@dataclass
class ContextAnalysis:
    """Full context analysis result (完整上下文分析結果)"""
    parsed_intent: ParsedIntent
    relevant_contexts: list[ContextEntry]
    understanding_confidence: float
    ambiguities: list[str] = field(default_factory=list)
    clarification_needed: list[str] = field(default_factory=list)
    recommended_approach: str = ""
    analyzed_at: datetime = field(default_factory=datetime.now)


class ContextUnderstandingEngine:
    """
    Context Understanding Engine (上下文理解引擎)
    
    解決 AI 「不理解上下文」的問題
    
    核心原則：
    1. 不假設用戶意圖，而是深入分析
    2. 識別隱含需求，而非僅處理顯式需求
    3. 保留歷史上下文，理解演進脈絡
    4. 多角度驗證理解的準確性
    """
    
    def __init__(self) -> None:
        self._contexts: dict[str, list[ContextEntry]] = {}  # user_id -> contexts
        self._conversation_history: dict[str, list[dict]] = {}
        self._context_counter = 0
        
        # 意圖關鍵詞映射
        self._intent_keywords = {
            IntentCategory.OPTIMIZATION: ["優化", "optimize", "improve", "faster", "performance", "效能", "加速"],
            IntentCategory.MIGRATION: ["遷移", "migrate", "transfer", "move", "搬遷", "同步", "sync"],
            IntentCategory.DEBUGGING: ["debug", "調試", "fix", "修復", "bug", "error", "錯誤", "問題"],
            IntentCategory.REFACTORING: ["重構", "refactor", "restructure", "clean", "整理"],
            IntentCategory.NEW_FEATURE: ["新增", "add", "create", "new", "implement", "建立", "功能"],
            IntentCategory.SECURITY: ["安全", "security", "secure", "vulnerability", "漏洞", "加密"],
            IntentCategory.DOCUMENTATION: ["文檔", "document", "readme", "說明", "註解", "comment"],
            IntentCategory.TESTING: ["測試", "test", "unit", "integration", "驗證"],
            IntentCategory.DEPLOYMENT: ["部署", "deploy", "release", "發布", "上線"],
            IntentCategory.QUERY: ["查詢", "query", "find", "search", "get", "查找", "獲取"],
        }
        
        # 隱含需求模式
        self._implicit_patterns = {
            "performance": ["大量數據", "high volume", "scalability", "concurrent", "並發"],
            "security": ["用戶資料", "user data", "password", "token", "敏感"],
            "reliability": ["生產環境", "production", "critical", "重要", "24/7"],
            "pagination": ["列表", "list", "all", "全部", "findMany"],
        }
    
    def analyze_request(
        self, 
        user_id: str, 
        request: str, 
        additional_context: Optional[dict] = None
    ) -> ContextAnalysis:
        """
        Analyze user request with full context understanding
        
        深度分析用戶請求，理解真正意圖
        
        Args:
            user_id: User identifier
            request: The user's request text
            additional_context: Optional additional context
            
        Returns:
            ContextAnalysis with full understanding
        """
        # 1. 解析顯式意圖
        parsed_intent = self._parse_intent(request)
        
        # 2. 獲取相關上下文
        relevant_contexts = self._get_relevant_contexts(user_id, request)
        
        # 3. 識別隱含需求
        implicit_requirements = self._identify_implicit_requirements(request, relevant_contexts)
        parsed_intent.implicit_requirements = implicit_requirements
        
        # 4. 檢測歧義
        ambiguities = self._detect_ambiguities(request, parsed_intent)
        
        # 5. 生成澄清問題
        clarification_needed = self._generate_clarifications(ambiguities, parsed_intent)
        
        # 6. 推薦方案
        recommended_approach = self._recommend_approach(parsed_intent, relevant_contexts)
        
        # 7. 計算理解置信度
        understanding_confidence = self._calculate_understanding_confidence(
            parsed_intent, ambiguities, clarification_needed
        )
        
        # 8. 記錄對話歷史
        self._record_conversation(user_id, request, parsed_intent)
        
        # 9. 更新上下文
        if additional_context:
            self._add_context(user_id, ContextType.CONVERSATION, additional_context)
        
        return ContextAnalysis(
            parsed_intent=parsed_intent,
            relevant_contexts=relevant_contexts,
            understanding_confidence=understanding_confidence,
            ambiguities=ambiguities,
            clarification_needed=clarification_needed,
            recommended_approach=recommended_approach,
        )
    
    def _parse_intent(self, request: str) -> ParsedIntent:
        """Parse the primary and secondary intents (解析主要和次要意圖)"""
        request_lower = request.lower()
        intent_scores: dict[IntentCategory, float] = {}
        
        # 計算每個意圖類別的匹配分數
        for intent, keywords in self._intent_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword.lower() in request_lower:
                    score += 1.0
            intent_scores[intent] = score
        
        # 排序找出主要和次要意圖
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_intent = sorted_intents[0][0] if sorted_intents[0][1] > 0 else IntentCategory.QUERY
        secondary_intents = [
            intent for intent, score in sorted_intents[1:4] 
            if score > 0
        ]
        
        # 計算置信度
        total_score = sum(intent_scores.values())
        confidence = sorted_intents[0][1] / max(total_score, 1.0) if total_score > 0 else 0.5
        
        # 提取實體
        entities = self._extract_entities(request)
        
        # 提取約束條件
        constraints = self._extract_constraints(request)
        
        # 提取優先級
        priorities = self._extract_priorities(request)
        
        return ParsedIntent(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            entities=entities,
            constraints=constraints,
            priorities=priorities,
        )
    
    def _extract_entities(self, request: str) -> dict[str, Any]:
        """Extract named entities from request (從請求中提取命名實體)"""
        entities: dict[str, Any] = {}
        
        # 提取系統/服務名稱
        system_pattern = r'(舊|新|老|source|target|from|to)\s*(系統|system|service|服務)'
        matches = re.findall(system_pattern, request, re.IGNORECASE)
        if matches:
            entities["systems"] = [f"{m[0]}_{m[1]}" for m in matches]
        
        # 提取數據類型
        data_pattern = r'(用戶|user|customer|訂單|order|產品|product|數據|data|資料)'
        matches = re.findall(data_pattern, request, re.IGNORECASE)
        if matches:
            entities["data_types"] = list(set(matches))
        
        # 提取數量相關
        quantity_pattern = r'(\d+)\s*(條|個|筆|records?|items?|rows?)'
        matches = re.findall(quantity_pattern, request, re.IGNORECASE)
        if matches:
            entities["quantities"] = [{"value": m[0], "unit": m[1]} for m in matches]
        
        # 提取時間相關
        time_pattern = r'(每\s*天|daily|每\s*小時|hourly|實時|real.?time|定期|scheduled)'
        matches = re.findall(time_pattern, request, re.IGNORECASE)
        if matches:
            entities["timing"] = list(set(matches))
        
        return entities
    
    def _extract_constraints(self, request: str) -> list[str]:
        """Extract constraints from request (提取約束條件)"""
        constraints = []
        
        constraint_patterns = [
            (r'不要.*?(丟失|lost|刪除|delete)', "data_preservation"),
            (r'必須.*?(快|fast|實時|real.?time)', "performance"),
            (r'不能.*?(停機|downtime|中斷)', "availability"),
            (r'需要.*?(驗證|validate|確認)', "validation"),
            (r'(?:零|zero|no)\s*(?:停機|downtime)', "zero_downtime"),
        ]
        
        for pattern, constraint_type in constraint_patterns:
            if re.search(pattern, request, re.IGNORECASE):
                constraints.append(constraint_type)
        
        return constraints
    
    def _extract_priorities(self, request: str) -> list[str]:
        """Extract priorities from request (提取優先級)"""
        priorities = []
        
        priority_patterns = [
            (r'最重要.*?(是|的)', "highest_priority"),
            (r'首先|first|優先', "high_priority"),
            (r'其次|然後|then', "secondary"),
            (r'可選|optional|如果可以', "optional"),
        ]
        
        for pattern, priority_type in priority_patterns:
            if re.search(pattern, request, re.IGNORECASE):
                priorities.append(priority_type)
        
        return priorities
    
    def _identify_implicit_requirements(
        self, 
        request: str, 
        contexts: list[ContextEntry]
    ) -> list[str]:
        """Identify implicit requirements not explicitly stated (識別隱含需求)"""
        implicit: list[str] = []
        request_lower = request.lower()
        
        for requirement, patterns in self._implicit_patterns.items():
            for pattern in patterns:
                if pattern.lower() in request_lower:
                    implicit.append(f"Implicit {requirement} requirement detected")
                    break
        
        # 基於上下文推斷
        for context in contexts:
            if context.context_type == ContextType.PROJECT:
                project_info = context.content
                if project_info.get("is_production"):
                    implicit.append("Production environment requires high reliability")
                if project_info.get("has_sensitive_data"):
                    implicit.append("Security measures required for sensitive data")
        
        # 基於意圖推斷
        if "遷移" in request or "migrate" in request_lower:
            implicit.append("Data validation needed before and after migration")
            implicit.append("Rollback plan should be prepared")
        
        if "優化" in request or "optimize" in request_lower:
            implicit.append("Benchmark before and after optimization")
            implicit.append("Consider impact on existing functionality")
        
        return implicit
    
    def _detect_ambiguities(self, request: str, parsed_intent: ParsedIntent) -> list[str]:
        """Detect ambiguities in the request (檢測請求中的歧義)"""
        ambiguities = []
        
        # 低置信度意圖
        if parsed_intent.confidence < 0.5:
            ambiguities.append("Intent is unclear - multiple possible interpretations")
        
        # 缺少具體細節
        if not parsed_intent.entities.get("systems"):
            ambiguities.append("Source and target systems not clearly specified")
        
        if not parsed_intent.entities.get("data_types"):
            ambiguities.append("Data type to be processed is not specified")
        
        # 模糊的時間要求
        if not parsed_intent.entities.get("timing"):
            if "遷移" in request or "同步" in request:
                ambiguities.append("Timing/frequency of operation not specified")
        
        # 衝突的約束
        if "fast" in parsed_intent.constraints and "validation" in parsed_intent.constraints:
            ambiguities.append("Speed vs validation trade-off needs clarification")
        
        return ambiguities
    
    def _generate_clarifications(
        self, 
        ambiguities: list[str], 
        parsed_intent: ParsedIntent
    ) -> list[str]:
        """Generate clarification questions (生成澄清問題)"""
        clarifications = []
        
        for ambiguity in ambiguities:
            if "systems not clearly specified" in ambiguity:
                clarifications.append("請問是從哪個系統遷移到哪個系統？/ Which systems are involved?")
            elif "Data type" in ambiguity:
                clarifications.append("請問需要處理什麼類型的數據？/ What type of data needs to be processed?")
            elif "Timing" in ambiguity:
                clarifications.append("這是一次性操作還是需要定期執行？/ Is this a one-time operation or scheduled?")
            elif "trade-off" in ambiguity:
                clarifications.append("在速度和數據驗證之間，哪個更優先？/ Which is more important: speed or validation?")
        
        return clarifications
    
    def _recommend_approach(
        self, 
        parsed_intent: ParsedIntent, 
        contexts: list[ContextEntry]
    ) -> str:
        """Recommend the best approach based on understanding (推薦最佳方案)"""
        intent = parsed_intent.primary_intent
        
        recommendations = {
            IntentCategory.MIGRATION: """
推薦方案 (Migration Approach):
1. 數據映射分析 - 確認源和目標數據結構
2. 增量遷移策略 - 避免一次性大量數據處理
3. 驗證檢查點 - 每批次完成後驗證數據完整性
4. 回滾計劃 - 準備快速回滾機制
5. 監控告警 - 設置遷移進度和錯誤監控
""",
            IntentCategory.OPTIMIZATION: """
推薦方案 (Optimization Approach):
1. 基準測試 - 先測量當前性能
2. 瓶頸分析 - 使用 profiler 識別熱點
3. 漸進優化 - 一次只改一處，驗證效果
4. 分頁處理 - 大數據集使用分頁
5. 緩存策略 - 考慮添加適當的緩存
""",
            IntentCategory.DEBUGGING: """
推薦方案 (Debugging Approach):
1. 重現問題 - 確保能穩定重現
2. 隔離範圍 - 縮小問題範圍
3. 日誌分析 - 檢查相關日誌
4. 單元測試 - 添加覆蓋此場景的測試
5. 根因分析 - 找到根本原因而非表面症狀
""",
        }
        
        base_recommendation = recommendations.get(intent, "分析需求後提供具體方案")
        
        # 根據隱含需求調整建議
        if parsed_intent.implicit_requirements:
            base_recommendation += "\n\n額外考慮事項 (Additional Considerations):\n"
            for req in parsed_intent.implicit_requirements:
                base_recommendation += f"- {req}\n"
        
        return base_recommendation.strip()
    
    def _calculate_understanding_confidence(
        self, 
        parsed_intent: ParsedIntent, 
        ambiguities: list[str], 
        clarifications: list[str]
    ) -> float:
        """Calculate confidence in understanding (計算理解置信度)"""
        base_confidence = parsed_intent.confidence
        
        # 每個歧義降低置信度
        ambiguity_penalty = len(ambiguities) * 0.1
        
        # 每個需要澄清的問題降低置信度
        clarification_penalty = len(clarifications) * 0.08
        
        # 有實體提取增加置信度
        entity_bonus = min(len(parsed_intent.entities) * 0.05, 0.2)
        
        # 有約束條件增加置信度
        constraint_bonus = min(len(parsed_intent.constraints) * 0.03, 0.1)
        
        confidence = base_confidence - ambiguity_penalty - clarification_penalty + entity_bonus + constraint_bonus
        
        return max(0.1, min(1.0, confidence))
    
    def _get_relevant_contexts(self, user_id: str, request: str) -> list[ContextEntry]:
        """Get relevant contexts for the request (獲取與請求相關的上下文)"""
        user_contexts = self._contexts.get(user_id, [])
        
        # 過濾過期的上下文
        now = datetime.now()
        valid_contexts = [
            c for c in user_contexts 
            if c.expires_at is None or c.expires_at > now
        ]
        
        # 按相關性排序
        # 這裡使用簡單的時間排序，實際可以使用更複雜的相關性計算
        valid_contexts.sort(key=lambda c: c.created_at, reverse=True)
        
        return valid_contexts[:10]  # 返回最近的 10 個上下文
    
    def _add_context(
        self, 
        user_id: str, 
        context_type: ContextType, 
        content: dict[str, Any],
        relevance_score: float = 1.0
    ) -> str:
        """Add a new context entry (添加新的上下文條目)"""
        self._context_counter += 1
        context_id = f"CTX-{self._context_counter:06d}"
        
        entry = ContextEntry(
            context_id=context_id,
            context_type=context_type,
            content=content,
            relevance_score=relevance_score,
        )
        
        if user_id not in self._contexts:
            self._contexts[user_id] = []
        
        self._contexts[user_id].append(entry)
        
        return context_id
    
    def _record_conversation(
        self, 
        user_id: str, 
        request: str, 
        parsed_intent: ParsedIntent
    ) -> None:
        """Record conversation for context memory (記錄對話用於上下文記憶)"""
        if user_id not in self._conversation_history:
            self._conversation_history[user_id] = []
        
        self._conversation_history[user_id].append({
            "request": request,
            "intent": parsed_intent.primary_intent.value,
            "timestamp": datetime.now().isoformat(),
        })
        
        # 保留最近 50 條對話
        if len(self._conversation_history[user_id]) > 50:
            self._conversation_history[user_id] = self._conversation_history[user_id][-50:]
    
    def add_project_context(
        self, 
        user_id: str, 
        project_info: dict[str, Any]
    ) -> str:
        """Add project context (添加項目上下文)"""
        return self._add_context(user_id, ContextType.PROJECT, project_info)
    
    def add_domain_context(
        self, 
        user_id: str, 
        domain_knowledge: dict[str, Any]
    ) -> str:
        """Add domain knowledge context (添加領域知識上下文)"""
        return self._add_context(user_id, ContextType.DOMAIN, domain_knowledge)
    
    def get_conversation_history(self, user_id: str) -> list[dict]:
        """Get conversation history (獲取對話歷史)"""
        return self._conversation_history.get(user_id, []).copy()
    
    def clear_user_context(self, user_id: str) -> None:
        """Clear all context for a user (清除用戶的所有上下文)"""
        self._contexts.pop(user_id, None)
        self._conversation_history.pop(user_id, None)
