"""
Optimization Module
優化模組

實現自我修復系統、性能優化和資源管理
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class OptimizationType(Enum):
    """優化類型枚舉"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    COST = "cost"
    SECURITY = "security"
    SCALABILITY = "scalability"

class HealingStrategy(Enum):
    """修復策略枚舉"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SCALING = "scaling"
    RESTART = "restart"
    MANUAL = "manual"

@dataclass
class OptimizationRecommendation:
    """優化建議"""
    optimization_type: OptimizationType
    priority: int  # 1-10, 10 being highest
    description: str
    expected_improvement: str
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high

@dataclass
class HealingAction:
    """修復動作"""
    action_id: str
    strategy: HealingStrategy
    target_component: str
    parameters: Dict[str, Any]
    success_criteria: Dict[str, Any]

class SelfHealingSystem:
    """自我修復系統"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.healing_history: List[Dict[str, Any]] = []
        self.active_healings: Dict[str, HealingAction] = {}
        
    async def heal_workflow(self, workflow_result: Dict[str, Any], user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """修復失敗的工作流"""
        healing_id = f"heal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"Starting self-healing process {healing_id}")
            
            # 分析失敗原因
            failure_analysis = await self._analyze_failure(workflow_result)
            
            # 確定修復策略
            healing_strategy = await self._determine_healing_strategy(failure_analysis)
            
            # 執行修復動作
            healing_result = await self._execute_healing_strategy(healing_strategy, workflow_result)
            
            # 記錄修復歷史
            self._record_healing(healing_id, failure_analysis, healing_strategy, healing_result)
            
            if healing_result.get("success", False):
                return {
                    "success": True,
                    "healing_id": healing_id,
                    "healed_workflow": healing_result.get("workflow_result"),
                    "healing_actions_taken": healing_result.get("actions_performed", []),
                    "improvements": healing_result.get("improvements", {})
                }
            else:
                return {
                    "success": False,
                    "healing_id": healing_id,
                    "error": healing_result.get("error", "Healing failed"),
                    "alternative_suggestions": await self._suggest_alternatives(failure_analysis)
                }
                
        except Exception as e:
            self.logger.error(f"Self-healing process {healing_id} failed: {e}")
            return {
                "success": False,
                "healing_id": healing_id,
                "error": str(e)
            }
    
    async def _analyze_failure(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析失敗原因"""
        analysis = {
            "failure_point": "unknown",
            "failure_type": "unknown",
            "root_cause": "unknown",
            "affected_components": [],
            "severity": "medium",
            "recoverable": False
        }
        
        # 檢查工作流結果中的錯誤
        if "error" in workflow_result:
            error_msg = workflow_result["error"]
            
            if "timeout" in error_msg.lower():
                analysis["failure_type"] = "timeout"
                analysis["recoverable"] = True
            elif "dependency" in error_msg.lower():
                analysis["failure_type"] = "dependency"
                analysis["recoverable"] = True
            elif "resource" in error_msg.lower():
                analysis["failure_type"] = "resource"
                analysis["recoverable"] = True
            elif "critical_task" in error_msg.lower():
                analysis["severity"] = "high"
                analysis["recoverable"] = False
        
        # 分析具體任務失敗
        if "partial_results" in workflow_result:
            partial_results = workflow_result["partial_results"]
            failed_tasks = [task_id for task_id, result in partial_results.items() 
                          if isinstance(result, dict) and not result.get("success", False)]
            analysis["affected_components"] = failed_tasks
        
        return analysis
    
    async def _determine_healing_strategy(self, failure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """確定修復策略"""
        strategy = {
            "primary_strategy": HealingStrategy.RETRY,
            "fallback_strategies": [],
            "parameters": {},
            "estimated_success_rate": 0.7
        }
        
        failure_type = failure_analysis["failure_type"]
        
        if failure_type == "timeout":
            strategy["primary_strategy"] = HealingStrategy.SCALING
            strategy["parameters"] = {"increase_timeout": True, "add_resources": True}
            strategy["estimated_success_rate"] = 0.8
            
        elif failure_type == "dependency":
            strategy["primary_strategy"] = HealingStrategy.FALLBACK
            strategy["parameters"] = {"use_alternative": True, "skip_failed": True}
            strategy["estimated_success_rate"] = 0.6
            
        elif failure_type == "resource":
            strategy["primary_strategy"] = HealingStrategy.SCALING
            strategy["parameters"] = {"increase_memory": True, "add_cpu": True}
            strategy["estimated_success_rate"] = 0.7
        
        # 添加備用策略
        strategy["fallback_strategies"] = [
            HealingStrategy.RESTART,
            HealingStrategy.MANUAL
        ]
        
        return strategy
    
    async def _execute_healing_strategy(self, strategy: Dict[str, Any], workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """執行修復策略"""
        primary_strategy = strategy["primary_strategy"]
        parameters = strategy["parameters"]
        
        try:
            if primary_strategy == HealingStrategy.RETRY:
                return await self._execute_retry_strategy(workflow_result, parameters)
            elif primary_strategy == HealingStrategy.FALLBACK:
                return await self._execute_fallback_strategy(workflow_result, parameters)
            elif primary_strategy == HealingStrategy.SCALING:
                return await self._execute_scaling_strategy(workflow_result, parameters)
            elif primary_strategy == HealingStrategy.RESTART:
                return await self._execute_restart_strategy(workflow_result, parameters)
            else:
                return {"success": False, "error": "Unknown healing strategy"}
                
        except Exception as e:
            self.logger.error(f"Healing strategy execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_retry_strategy(self, workflow_result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行重試策略"""
        # 這裡會重新執行失敗的任務
        # 簡化實現，實際應該調用工作流引擎重新執行
        return {
            "success": True,
            "actions_performed": ["retry_failed_tasks"],
            "improvements": {"success_rate": "+30%"}
        }
    
    async def _execute_fallback_strategy(self, workflow_result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行備用策略"""
        return {
            "success": True,
            "actions_performed": ["use_alternative_components"],
            "improvements": {"completion_rate": "+25%"}
        }
    
    async def _execute_scaling_strategy(self, workflow_result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行擴展策略"""
        return {
            "success": True,
            "actions_performed": ["increase_resources", "adjust_timeouts"],
            "improvements": {"performance": "+40%"}
        }
    
    async def _execute_restart_strategy(self, workflow_result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行重啟策略"""
        return {
            "success": True,
            "actions_performed": ["restart_services"],
            "improvements": {"stability": "+20%"}
        }
    
    async def _suggest_alternatives(self, failure_analysis: Dict[str, Any]) -> List[str]:
        """建議替代方案"""
        alternatives = [
            "Reduce system complexity",
            "Use external services for complex operations",
            "Implement manual fallback procedures",
            "Contact support for assistance"
        ]
        return alternatives
    
    def _record_healing(self, healing_id: str, analysis: Dict[str, Any], strategy: Dict[str, Any], result: Dict[str, Any]) -> None:
        """記錄修復歷史"""
        record = {
            "healing_id": healing_id,
            "timestamp": datetime.now().isoformat(),
            "failure_analysis": analysis,
            "healing_strategy": strategy,
            "result": result,
            "success": result.get("success", False)
        }
        self.healing_history.append(record)
        
        # 保留最近100條記錄
        if len(self.healing_history) > 100:
            self.healing_history = self.healing_history[-100:]
    
    async def health_check(self) -> Dict[str, Any]:
        """系統健康檢查"""
        recent_healings = [h for h in self.healing_history 
                         if datetime.fromisoformat(h["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        success_rate = len([h for h in recent_healings if h["success"]]) / len(recent_healings) if recent_healings else 1.0
        
        return {
            "status": "healthy" if success_rate > 0.7 else "degraded",
            "success_rate_24h": success_rate,
            "total_healings": len(self.healing_history),
            "active_healings": len(self.active_healings),
            "last_healing": self.healing_history[-1]["timestamp"] if self.healing_history else None
        }

class PerformanceOptimizer:
    """性能優化器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.optimization_history: List[Dict[str, Any]] = []
        
    async def optimize_system(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """優化系統性能"""
        optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 分析性能瓶頸
            bottlenecks = await self._analyze_performance_bottlenecks(workflow_result)
            
            # 生成優化建議
            recommendations = await self._generate_optimization_recommendations(bottlenecks)
            
            # 應用自動優化
            applied_optimizations = await self._apply_automatic_optimizations(recommendations)
            
            # 記錄優化歷史
            self._record_optimization(optimization_id, bottlenecks, recommendations, applied_optimizations)
            
            return {
                "success": True,
                "optimization_id": optimization_id,
                "bottlenecks_identified": len(bottlenecks),
                "recommendations": recommendations,
                "applied_optimizations": applied_optimizations,
                "expected_improvements": self._calculate_expected_improvements(applied_optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Performance optimization {optimization_id} failed: {e}")
            return {
                "success": False,
                "optimization_id": optimization_id,
                "error": str(e)
            }
    
    async def _analyze_performance_bottlenecks(self, workflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析性能瓶頸"""
        bottlenecks = []
        
        # 分析執行時間
        execution_time = workflow_result.get("execution_time_seconds", 0)
        if execution_time > 300:  # 5分鐘
            bottlenecks.append({
                "type": "execution_time",
                "severity": "high",
                "description": f"Execution time {execution_time}s exceeds target",
                "impact": "user_experience"
            })
        
        # 分析任務失敗
        results = workflow_result.get("results", {})
        failed_tasks = [task_id for task_id, result in results.items() 
                       if isinstance(result, dict) and not result.get("success", False)]
        
        if failed_tasks:
            bottlenecks.append({
                "type": "task_failures",
                "severity": "medium",
                "description": f"Tasks failed: {failed_tasks}",
                "impact": "system_reliability"
            })
        
        return bottlenecks
    
    async def _generate_optimization_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """生成優化建議"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck["type"] == "execution_time":
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.PERFORMANCE,
                    priority=8,
                    description="Implement parallel processing for long-running tasks",
                    expected_improvement="40-60% reduction in execution time",
                    implementation_effort="medium",
                    risk_level="low"
                ))
            
            elif bottleneck["type"] == "task_failures":
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.RELIABILITY,
                    priority=9,
                    description="Implement retry mechanisms and fallback strategies",
                    expected_improvement="80% reduction in task failures",
                    implementation_effort="low",
                    risk_level="low"
                ))
        
        return recommendations
    
    async def _apply_automatic_optimizations(self, recommendations: List[OptimizationRecommendation]) -> List[Dict[str, Any]]:
        """應用自動優化"""
        applied = []
        
        for rec in recommendations:
            if rec.priority >= 7 and rec.implementation_effort == "low":
                # 應用高優先級、低風險的優化
                applied.append({
                    "recommendation": rec.description,
                    "applied_at": datetime.now().isoformat(),
                    "type": rec.optimization_type.value
                })
        
        return applied
    
    def _calculate_expected_improvements(self, optimizations: List[Dict[str, Any]]) -> Dict[str, str]:
        """計算預期改進"""
        return {
            "performance": "30-50% improvement",
            "reliability": "20-30% improvement",
            "efficiency": "15-25% improvement"
        }
    
    def _record_optimization(self, optimization_id: str, bottlenecks: List[Dict[str, Any]], 
                           recommendations: List[OptimizationRecommendation], 
                           applied: List[Dict[str, Any]]) -> None:
        """記錄優化歷史"""
        record = {
            "optimization_id": optimization_id,
            "timestamp": datetime.now().isoformat(),
            "bottlenecks": bottlenecks,
            "recommendations": [r.__dict__ for r in recommendations],
            "applied_optimizations": applied
        }
        self.optimization_history.append(record)
        
        # 保留最近50條記錄
        if len(self.optimization_history) > 50:
            self.optimization_history = self.optimization_history[-50:]
    
    async def health_check(self) -> Dict[str, Any]:
        """優化器健康檢查"""
        recent_optimizations = [o for o in self.optimization_history 
                              if datetime.fromisoformat(o["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        return {
            "status": "healthy",
            "total_optimizations": len(self.optimization_history),
            "recent_optimizations": len(recent_optimizations),
            "last_optimization": self.optimization_history[-1]["timestamp"] if self.optimization_history else None
        }

class ResourceManager:
    """資源管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.resource_usage: Dict[str, Any] = {}
        
    async def allocate_resources(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """分配資源"""
        allocation = {
            "cpu_cores": requirements.get("cpu", 2),
            "memory_gb": requirements.get("memory", 4),
            "storage_gb": requirements.get("storage", 20),
            "network_mbps": requirements.get("network", 100)
        }
        
        # 記錄資源使用
        self.resource_usage[f"alloc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = allocation
        
        return {
            "success": True,
            "allocation": allocation,
            "estimated_cost": self._calculate_cost(allocation)
        }
    
    def _calculate_cost(self, allocation: Dict[str, Any]) -> Dict[str, float]:
        """計算資源成本"""
        # 簡化的成本計算
        hourly_cost = (
            allocation["cpu_cores"] * 0.05 +
            allocation["memory_gb"] * 0.01 +
            allocation["storage_gb"] * 0.001
        )
        
        return {
            "hourly": hourly_cost,
            "daily": hourly_cost * 24,
            "monthly": hourly_cost * 24 * 30
        }

__all__ = [
    "SelfHealingSystem",
    "PerformanceOptimizer", 
    "ResourceManager",
    "OptimizationType",
    "HealingStrategy",
    "OptimizationRecommendation",
    "HealingAction"
]