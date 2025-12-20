"""
Input Analysis Agent
輸入分析代理

負責解析用戶需求，提取關鍵信息，生成技術規格
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from . import BaseAgent, AgentTask, AgentResult, AgentType

class InputAnalysisAgent(BaseAgent):
    """輸入分析代理 - 第一階段處理"""
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        super().__init__(agent_type, config)
        self.analysis_patterns = {
            "requirements": r"(需求|requirement|需要|need)",
            "technology": r"(技術|technology|stack|框架|framework)",
            "timeline": r"(時間|timeline|deadline|截止|完成)",
            "budget": r"(預算|budget|成本|cost|費用)",
            "scale": r"(規模|scale|用戶|user|流量|traffic)"
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據格式"""
        required_fields = ["user_input", "context"]
        return all(field in input_data for field in required_fields)
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """處理輸入分析任務"""
        start_time = datetime.now()
        
        try:
            # 提取用戶輸入
            user_input = task.input_data.get("user_input", "")
            context = task.input_data.get("context", {})
            
            # 執行多層次分析
            analysis_result = await self._analyze_input(user_input, context)
            
            # 生成技術規格
            tech_specs = await self._generate_tech_specs(analysis_result)
            
            # 創建執行計劃
            execution_plan = await self._create_execution_plan(tech_specs)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=True,
                output_data={
                    "analysis": analysis_result,
                    "tech_specs": tech_specs,
                    "execution_plan": execution_plan,
                    "complexity_score": self._calculate_complexity(analysis_result),
                    "estimated_time": self._estimate_time(tech_specs)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Input analysis failed: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def _analyze_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """深度分析用戶輸入"""
        analysis = {
            "original_input": user_input,
            "extracted_info": {},
            "intent": "unknown",
            "domain": "general",
            "key_entities": [],
            "constraints": [],
            "success_criteria": []
        }
        
        # 提取關鍵信息
        for category, pattern in self.analysis_patterns.items():
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                analysis["extracted_info"][category] = matches
        
        # 意圖識別
        if any(word in user_input.lower() for word in ["網站", "website", "web"]):
            analysis["intent"] = "web_development"
            analysis["domain"] = "web"
        elif any(word in user_input.lower() for word in ["app", "應用", "mobile"]):
            analysis["intent"] = "mobile_development"
            analysis["domain"] = "mobile"
        elif any(word in user_input.lower() for word in ["api", "backend", "後端"]):
            analysis["intent"] = "backend_development"
            analysis["domain"] = "backend"
        
        # 提取關鍵實體
        analysis["key_entities"] = self._extract_entities(user_input)
        
        return analysis
    
    async def _generate_tech_specs(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成技術規格"""
        tech_specs = {
            "architecture": "microservices",
            "frontend": {
                "framework": "react",
                "styling": "tailwind",
                "state_management": "redux"
            },
            "backend": {
                "framework": "fastapi",
                "database": "postgresql",
                "cache": "redis"
            },
            "infrastructure": {
                "deployment": "docker",
                "orchestration": "kubernetes",
                "monitoring": "prometheus"
            },
            "integrations": [],
            "security": {
                "authentication": "jwt",
                "authorization": "rbac"
            }
        }
        
        # 根據分析結果調整技術規格
        if analysis["domain"] == "mobile":
            tech_specs["frontend"]["framework"] = "react_native"
        elif analysis["domain"] == "backend":
            tech_specs.pop("frontend", None)
        
        return tech_specs
    
    async def _create_execution_plan(self, tech_specs: Dict[str, Any]) -> Dict[str, Any]:
        """創建執行計劃"""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "架構設計",
                    "duration_minutes": 2,
                    "agents": ["architecture_design"],
                    "outputs": ["system_architecture", "api_design"]
                },
                {
                    "phase": 2,
                    "name": "代碼生成",
                    "duration_minutes": 4,
                    "agents": ["code_generation"],
                    "outputs": ["source_code", "configuration"]
                },
                {
                    "phase": 3,
                    "name": "測試與驗證",
                    "duration_minutes": 2,
                    "agents": ["testing"],
                    "outputs": ["test_results", "quality_report"]
                },
                {
                    "phase": 4,
                    "name": "部署與優化",
                    "duration_minutes": 2,
                    "agents": ["deployment", "optimization"],
                    "outputs": ["deployed_system", "performance_metrics"]
                }
            ],
            "total_duration_minutes": 10,
            "parallel_execution": True
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取關鍵實體"""
        # 簡化的實體提取邏輯
        entities = []
        patterns = [
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",  # 大寫開頭的詞組
            r"\b\w+\.com\b",  # 域名
            r"\b\d+\s*(?:用戶|用戶|users)\b"  # 用戶數量
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _calculate_complexity(self, analysis: Dict[str, Any]) -> int:
        """計算複雜度分數"""
        base_score = 1
        if len(analysis["extracted_info"]) > 3:
            base_score += 1
        if analysis["domain"] in ["mobile", "enterprise"]:
            base_score += 1
        return min(base_score, 5)  # 最高5分
    
    def _estimate_time(self, tech_specs: Dict[str, Any]) -> int:
        """估算執行時間（分鐘）"""
        base_time = 5
        if len(tech_specs.get("integrations", [])) > 0:
            base_time += 2
        return min(base_time, 10)

__all__ = ["InputAnalysisAgent"]