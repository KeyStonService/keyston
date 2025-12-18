"""
═══════════════════════════════════════════════════════════
        第三層：自適應指南 (Adaptive Guidelines)
        Layer 3: Adaptive Guidelines
═══════════════════════════════════════════════════════════

本模組定義 AI 可根據情境調整的彈性指南
這些指南會根據環境、使用者、任務類型動態調整

This module defines flexible guidelines that AI can adapt based on context
These guidelines dynamically adjust based on environment, user, and task type

自成閉環：本檔案完全獨立運作，支持動態學習和調整
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime
import hashlib


class GuidelineScope(Enum):
    """指南適用範圍"""
    GLOBAL = "global"           # 全局適用
    DOMAIN = "domain"           # 特定領域
    USER = "user"               # 特定使用者
    SESSION = "session"         # 特定會話
    TASK = "task"               # 特定任務


class AdaptationTrigger(Enum):
    """調整觸發條件"""
    USER_FEEDBACK = "user_feedback"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_PATTERN = "error_pattern"
    ENVIRONMENT_CHANGE = "environment_change"
    LEARNING_OUTCOME = "learning_outcome"
    TIME_BASED = "time_based"


@dataclass
class GuidelineAdjustment:
    """指南調整記錄"""
    guideline_id: str
    trigger: AdaptationTrigger
    old_value: Any
    new_value: Any
    reason: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reversible: bool = True


@dataclass
class GuidelineEvaluation:
    """指南評估結果"""
    guideline_id: str
    applicable: bool
    recommendation: str
    confidence: float
    context_factors: Dict[str, Any] = field(default_factory=dict)
    alternatives: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DomainGuideline:
    """
    領域指南
    Domain-specific Guidelines
    
    針對特定業務領域的行為指南
    """
    
    def __init__(self, domain: str):
        self.domain = domain
        self.guidelines: Dict[str, Dict[str, Any]] = {}
        self._adjustment_history: List[GuidelineAdjustment] = []
        self._evaluation_history: List[GuidelineEvaluation] = []
        
        # 初始化領域預設指南
        self._initialize_domain_defaults()
    
    def _initialize_domain_defaults(self):
        """初始化領域預設指南"""
        domain_defaults = {
            "software_development": {
                "code_review_depth": {
                    "value": "comprehensive",
                    "options": ["quick", "standard", "comprehensive", "exhaustive"],
                    "description": "代碼審查深度",
                },
                "test_coverage_target": {
                    "value": 80,
                    "min": 50,
                    "max": 100,
                    "description": "測試覆蓋率目標 (%)",
                },
                "documentation_level": {
                    "value": "detailed",
                    "options": ["minimal", "standard", "detailed", "comprehensive"],
                    "description": "文檔詳細程度",
                },
            },
            "data_processing": {
                "batch_size": {
                    "value": 1000,
                    "min": 100,
                    "max": 10000,
                    "description": "批次處理大小",
                },
                "validation_strictness": {
                    "value": "strict",
                    "options": ["lenient", "standard", "strict", "paranoid"],
                    "description": "數據驗證嚴格程度",
                },
                "error_handling": {
                    "value": "continue_with_log",
                    "options": ["fail_fast", "continue_with_log", "retry_then_fail"],
                    "description": "錯誤處理策略",
                },
            },
            "user_interaction": {
                "response_verbosity": {
                    "value": "balanced",
                    "options": ["concise", "balanced", "detailed", "comprehensive"],
                    "description": "回應詳細程度",
                },
                "clarification_threshold": {
                    "value": 0.7,
                    "min": 0.5,
                    "max": 0.95,
                    "description": "需要澄清的信心閾值",
                },
                "proactive_suggestions": {
                    "value": True,
                    "description": "是否主動提供建議",
                },
            },
            "system_operation": {
                "auto_scaling": {
                    "value": True,
                    "description": "是否自動擴展",
                },
                "resource_conservation": {
                    "value": "balanced",
                    "options": ["aggressive", "balanced", "performance_first"],
                    "description": "資源節約策略",
                },
                "backup_frequency": {
                    "value": "hourly",
                    "options": ["continuous", "hourly", "daily", "weekly"],
                    "description": "備份頻率",
                },
            },
        }
        
        self.guidelines = domain_defaults.get(self.domain, {})
    
    def get_guideline(self, key: str) -> Optional[Dict[str, Any]]:
        """獲取特定指南"""
        return self.guidelines.get(key)
    
    def set_guideline(self, key: str, value: Any, reason: str = "manual_update"):
        """設定指南值"""
        if key in self.guidelines:
            old_value = self.guidelines[key].get("value")
            self.guidelines[key]["value"] = value
            
            # 記錄調整
            self._adjustment_history.append(GuidelineAdjustment(
                guideline_id=f"{self.domain}.{key}",
                trigger=AdaptationTrigger.USER_FEEDBACK,
                old_value=old_value,
                new_value=value,
                reason=reason,
                confidence=1.0
            ))
    
    def evaluate(self, context: Dict[str, Any]) -> List[GuidelineEvaluation]:
        """評估所有指南在當前情境下的適用性"""
        evaluations = []
        
        for key, guideline in self.guidelines.items():
            evaluation = self._evaluate_single(key, guideline, context)
            evaluations.append(evaluation)
            self._evaluation_history.append(evaluation)
        
        return evaluations
    
    def _evaluate_single(
        self,
        key: str,
        guideline: Dict[str, Any],
        context: Dict[str, Any]
    ) -> GuidelineEvaluation:
        """評估單一指南"""
        applicable = True
        confidence = 0.9
        alternatives = []
        recommendation = guideline.get("value")
        
        # 根據情境調整建議
        if "urgency" in context:
            if context["urgency"] == "high" and key == "code_review_depth":
                recommendation = "quick"
                alternatives = ["standard"]
                confidence = 0.8
        
        if "resource_constrained" in context and context["resource_constrained"]:
            if key == "batch_size":
                recommendation = max(guideline.get("min", 100), guideline.get("value", 1000) // 2)
                confidence = 0.75
        
        return GuidelineEvaluation(
            guideline_id=f"{self.domain}.{key}",
            applicable=applicable,
            recommendation=str(recommendation),
            confidence=confidence,
            context_factors=context,
            alternatives=alternatives
        )
    
    def adapt(self, feedback: Dict[str, Any]) -> List[GuidelineAdjustment]:
        """根據反饋調整指南"""
        adjustments = []
        
        guideline_key = feedback.get("guideline_key")
        feedback_type = feedback.get("type")
        
        if guideline_key and guideline_key in self.guidelines:
            guideline = self.guidelines[guideline_key]
            old_value = guideline.get("value")
            new_value = old_value
            
            # 根據反饋類型調整
            if feedback_type == "too_strict":
                if "options" in guideline:
                    options = guideline["options"]
                    current_idx = options.index(old_value) if old_value in options else 0
                    if current_idx > 0:
                        new_value = options[current_idx - 1]
                elif isinstance(old_value, (int, float)):
                    new_value = old_value * 0.9
            
            elif feedback_type == "too_lenient":
                if "options" in guideline:
                    options = guideline["options"]
                    current_idx = options.index(old_value) if old_value in options else 0
                    if current_idx < len(options) - 1:
                        new_value = options[current_idx + 1]
                elif isinstance(old_value, (int, float)):
                    new_value = old_value * 1.1
            
            if new_value != old_value:
                self.guidelines[guideline_key]["value"] = new_value
                adjustment = GuidelineAdjustment(
                    guideline_id=f"{self.domain}.{guideline_key}",
                    trigger=AdaptationTrigger.USER_FEEDBACK,
                    old_value=old_value,
                    new_value=new_value,
                    reason=f"User feedback: {feedback_type}",
                    confidence=0.85
                )
                adjustments.append(adjustment)
                self._adjustment_history.append(adjustment)
        
        return adjustments
    
    def get_adjustment_history(self) -> List[GuidelineAdjustment]:
        """獲取調整歷史"""
        return self._adjustment_history.copy()


class ContextualGuideline:
    """
    情境指南
    Contextual Guidelines
    
    根據運行情境動態生成的指南
    """
    
    def __init__(self):
        self._context_rules: Dict[str, Dict[str, Any]] = {}
        self._active_guidelines: Dict[str, Any] = {}
        self._context_history: List[Dict[str, Any]] = []
    
    def register_context_rule(self, context_type: str, rule: Dict[str, Any]):
        """註冊情境規則"""
        self._context_rules[context_type] = rule
    
    def activate_for_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """根據情境激活相應指南"""
        activated = {}
        
        # 時間相關情境
        current_hour = datetime.utcnow().hour
        if 9 <= current_hour <= 17:
            activated["operation_mode"] = "business_hours"
            activated["response_priority"] = "high"
        else:
            activated["operation_mode"] = "off_hours"
            activated["response_priority"] = "normal"
        
        # 負載相關情境
        load = context.get("system_load", 0)
        if load > 80:
            activated["resource_mode"] = "conservation"
            activated["batch_processing"] = "reduced"
            activated["non_essential_tasks"] = "defer"
        elif load < 30:
            activated["resource_mode"] = "normal"
            activated["batch_processing"] = "full"
            activated["background_tasks"] = "allow"
        
        # 使用者相關情境
        user_type = context.get("user_type", "standard")
        if user_type == "admin":
            activated["access_level"] = "elevated"
            activated["audit_level"] = "detailed"
        elif user_type == "new_user":
            activated["guidance_level"] = "comprehensive"
            activated["validation_strictness"] = "helpful"
        
        # 任務相關情境
        task_type = context.get("task_type", "general")
        if task_type == "production_deployment":
            activated["verification_level"] = "exhaustive"
            activated["rollback_ready"] = True
            activated["notification_level"] = "all_stakeholders"
        elif task_type == "development":
            activated["verification_level"] = "standard"
            activated["experimentation_allowed"] = True
        
        self._active_guidelines = activated
        self._context_history.append({
            "context": context,
            "activated_guidelines": activated,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return activated
    
    def get_active_guideline(self, key: str) -> Optional[Any]:
        """獲取當前激活的指南"""
        return self._active_guidelines.get(key)
    
    def get_all_active_guidelines(self) -> Dict[str, Any]:
        """獲取所有激活的指南"""
        return self._active_guidelines.copy()
    
    def deactivate_all(self):
        """停用所有情境指南"""
        self._active_guidelines = {}


class LearningGuideline:
    """
    學習型指南
    Learning Guidelines
    
    從操作經驗中學習並自動調整的指南
    """
    
    def __init__(self):
        self._learning_data: Dict[str, List[Dict[str, Any]]] = {}
        self._learned_patterns: Dict[str, Dict[str, Any]] = {}
        self._adjustment_history: List[GuidelineAdjustment] = []
        self._confidence_threshold = 0.8
    
    def record_outcome(self, operation: Dict[str, Any], outcome: Dict[str, Any]):
        """記錄操作結果以供學習"""
        operation_type = operation.get("type", "unknown")
        
        if operation_type not in self._learning_data:
            self._learning_data[operation_type] = []
        
        self._learning_data[operation_type].append({
            "operation": operation,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 當數據足夠時觸發學習
        if len(self._learning_data[operation_type]) >= 10:
            self._learn_from_data(operation_type)
    
    def _learn_from_data(self, operation_type: str):
        """從數據中學習模式"""
        data = self._learning_data[operation_type]
        
        # 分析成功和失敗模式
        successes = [d for d in data if d["outcome"].get("success", False)]
        failures = [d for d in data if not d["outcome"].get("success", True)]
        
        success_rate = len(successes) / len(data) if data else 0
        
        # 分析成功案例的共同特徵
        if successes:
            success_params = self._extract_common_params(successes)
            
            pattern = {
                "operation_type": operation_type,
                "success_rate": success_rate,
                "recommended_params": success_params,
                "sample_size": len(data),
                "confidence": min(0.95, 0.5 + (len(data) / 100)),
                "learned_at": datetime.utcnow().isoformat()
            }
            
            self._learned_patterns[operation_type] = pattern
    
    def _extract_common_params(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取成功案例的共同參數"""
        common_params = {}
        
        # 簡化的參數提取邏輯
        if records:
            first_op = records[0].get("operation", {})
            for key, value in first_op.items():
                if key not in ["type", "timestamp", "id"]:
                    # 檢查此參數在所有成功案例中是否一致
                    consistent = all(
                        r.get("operation", {}).get(key) == value
                        for r in records
                    )
                    if consistent:
                        common_params[key] = value
        
        return common_params
    
    def get_recommendation(
        self,
        operation_type: str
    ) -> Optional[Dict[str, Any]]:
        """獲取學習到的建議"""
        pattern = self._learned_patterns.get(operation_type)
        
        if pattern and pattern.get("confidence", 0) >= self._confidence_threshold:
            return {
                "recommended_params": pattern.get("recommended_params", {}),
                "expected_success_rate": pattern.get("success_rate", 0),
                "confidence": pattern.get("confidence", 0),
                "based_on_samples": pattern.get("sample_size", 0),
            }
        
        return None
    
    def apply_learned_adjustments(
        self,
        operation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """應用學習到的調整"""
        operation_type = operation.get("type", "unknown")
        recommendation = self.get_recommendation(operation_type)
        
        if recommendation:
            adjusted_operation = operation.copy()
            for key, value in recommendation.get("recommended_params", {}).items():
                if key not in adjusted_operation or adjusted_operation[key] is None:
                    adjusted_operation[key] = value
            
            return adjusted_operation
        
        return operation
    
    def get_learned_patterns(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有學習到的模式"""
        return self._learned_patterns.copy()
    
    def reset_learning(self, operation_type: Optional[str] = None):
        """重置學習數據"""
        if operation_type:
            if operation_type in self._learning_data:
                del self._learning_data[operation_type]
            if operation_type in self._learned_patterns:
                del self._learned_patterns[operation_type]
        else:
            self._learning_data = {}
            self._learned_patterns = {}


class AdaptiveGuidelineEngine:
    """
    自適應指南引擎 - 整合所有自適應指南
    Adaptive Guideline Engine - Integrates all adaptive guidelines
    
    自成閉環：獨立管理所有自適應指南的評估和調整
    """
    
    def __init__(self):
        self._domain_guidelines: Dict[str, DomainGuideline] = {}
        self.contextual = ContextualGuideline()
        self.learning = LearningGuideline()
        
        # 初始化常用領域
        self._initialize_common_domains()
    
    def _initialize_common_domains(self):
        """初始化常用領域指南"""
        common_domains = [
            "software_development",
            "data_processing",
            "user_interaction",
            "system_operation",
        ]
        
        for domain in common_domains:
            self._domain_guidelines[domain] = DomainGuideline(domain)
    
    def get_domain_guideline(self, domain: str) -> DomainGuideline:
        """獲取或創建領域指南"""
        if domain not in self._domain_guidelines:
            self._domain_guidelines[domain] = DomainGuideline(domain)
        return self._domain_guidelines[domain]
    
    def evaluate_for_operation(
        self,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """評估操作的所有適用指南"""
        result = {
            "domain_guidelines": {},
            "contextual_guidelines": {},
            "learned_recommendations": {},
            "final_recommendations": {},
        }
        
        # 評估領域指南
        domain = operation.get("domain", "system_operation")
        domain_guideline = self.get_domain_guideline(domain)
        evaluations = domain_guideline.evaluate(context)
        
        for eval_result in evaluations:
            key = eval_result.guideline_id.split(".")[-1]
            result["domain_guidelines"][key] = {
                "recommendation": eval_result.recommendation,
                "confidence": eval_result.confidence,
                "alternatives": eval_result.alternatives,
            }
        
        # 激活情境指南
        contextual = self.contextual.activate_for_context(context)
        result["contextual_guidelines"] = contextual
        
        # 獲取學習建議
        operation_type = operation.get("type", "unknown")
        learned = self.learning.get_recommendation(operation_type)
        if learned:
            result["learned_recommendations"] = learned
        
        # 合併最終建議
        result["final_recommendations"] = self._merge_recommendations(
            result["domain_guidelines"],
            result["contextual_guidelines"],
            result["learned_recommendations"]
        )
        
        return result
    
    def _merge_recommendations(
        self,
        domain: Dict[str, Any],
        contextual: Dict[str, Any],
        learned: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合併所有來源的建議"""
        merged = {}
        
        # 優先級：學習 > 情境 > 領域
        # 先添加領域建議
        for key, value in domain.items():
            if isinstance(value, dict) and "recommendation" in value:
                merged[key] = value["recommendation"]
            else:
                merged[key] = value
        
        # 覆蓋情境建議
        merged.update(contextual)
        
        # 覆蓋學習建議（如果信心度足夠）
        if learned and learned.get("confidence", 0) > 0.8:
            for key, value in learned.get("recommended_params", {}).items():
                merged[key] = value
        
        return merged
    
    def record_operation_outcome(
        self,
        operation: Dict[str, Any],
        outcome: Dict[str, Any]
    ):
        """記錄操作結果供學習"""
        self.learning.record_outcome(operation, outcome)
    
    def adapt_from_feedback(
        self,
        domain: str,
        feedback: Dict[str, Any]
    ) -> List[GuidelineAdjustment]:
        """根據反饋調整指南"""
        domain_guideline = self.get_domain_guideline(domain)
        return domain_guideline.adapt(feedback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計資訊"""
        return {
            "domains": list(self._domain_guidelines.keys()),
            "learned_patterns": len(self.learning.get_learned_patterns()),
            "active_contextual_guidelines": len(
                self.contextual.get_all_active_guidelines()
            ),
        }


# 便捷類別別名
AdaptiveGuidelines = AdaptiveGuidelineEngine
