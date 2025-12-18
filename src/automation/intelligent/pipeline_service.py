"""
Pipeline Service - Orchestration Service for Intelligent Automation
管線服務 - 智能自動化編排服務

Orchestrates multiple AI agents for autonomous code analysis and fixing.
Designed for: Unmanned systems requiring zero-human-intervention operations

Core capabilities:
- Multi-agent coordination
- Real-time streaming responses
- Context-aware routing
- Safety-critical validation
- Auto environment upgrade (自動環境升級)
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Auto-upgrade environment if needed
# 自動升級環境（如果需要）
try:
    from auto_upgrade_env import AutoUpgradeEnvironment
    _upgrader = AutoUpgradeEnvironment(auto_install=True)
    _upgrade_results = _upgrader.check_and_upgrade(['dotenv', 'loguru'])
    if _upgrader.installed_deps:
        logger.info(f"已自動升級環境 Auto-upgraded: {', '.join(_upgrader.installed_deps)}")
except Exception as e:
    logger.warning(f"環境升級檢查跳過 Auto-upgrade skipped: {e}")

# Import agents
try:
    from agents.task_executor import task_executor
    from agents.recognition_server import RecognitionServer
    from agents.visualization_agent import VisualizationAgent
except ImportError:
    logger.warning("Running in standalone mode - agents not available")
    task_executor = None
    RecognitionServer = None
    VisualizationAgent = None


class PipelineService:
    """
    管線服務 - 智能代理編排器
    
    Pipeline service for orchestrating intelligent agents.
    Handles:
    - Request routing
    - Agent coordination
    - Response aggregation
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize pipeline service with all agents"""
        self.recognition_server = RecognitionServer() if RecognitionServer else None
        self.task_executor = task_executor
        self.visualization_agent = VisualizationAgent() if VisualizationAgent else None
        self.request_count = 0
        logger.info("PipelineService initialized")
    
    async def process_request(self,
                             query: str,
                             problem_content: str = "",
                             editor_code: str = "",
                             analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Process request through intelligent pipeline
        
        Args:
            query: User query/request
            problem_content: Problem or issue description
            editor_code: Code to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Processing result with routed response
        """
        self.request_count += 1
        request_id = f"req_{self.request_count}"
        
        logger.info(f"[{request_id}] Processing request: {query[:100]}...")
        
        try:
            # Step 1: Set context for task executor
            if self.task_executor:
                self.task_executor.set_problem_content(problem_content)
                self.task_executor.set_editor_code(editor_code)
            
            # Step 2: Intent recognition and routing
            if self.recognition_server:
                intent_result = self.recognition_server.process_request(
                    query=query,
                    problem_content=problem_content,
                    editor_code=editor_code
                )
                
                if intent_result["status"] == "blocked":
                    logger.warning(f"[{request_id}] Request blocked for security")
                    return {
                        "request_id": request_id,
                        "status": "blocked",
                        "message": "Request blocked due to security concerns",
                        "details": intent_result
                    }
                
                action = intent_result["action"]
                logger.info(f"[{request_id}] Routed to action: {action}")
            else:
                action = "proceed"  # Default action
            
            # Step 3: Route to appropriate handler
            if action == "visualize":
                result = await self._handle_visualization(query, problem_content, editor_code)
            elif action == "generate_diagram":
                result = await self._handle_diagram_generation(query, problem_content, editor_code)
            else:  # proceed
                result = await self._handle_code_analysis(query, editor_code, analysis_type)
            
            return {
                "request_id": request_id,
                "status": "success",
                "action": action,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing request: {str(e)}")
            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
    
    async def _handle_code_analysis(self,
                                    query: str,
                                    code: str,
                                    analysis_type: str) -> Dict[str, Any]:
        """
        Handle code analysis request
        
        Args:
            query: User query
            code: Code to analyze
            analysis_type: Type of analysis
            
        Returns:
            Analysis result
        """
        if not self.task_executor:
            return {"error": "Task executor not available"}
        
        logger.info(f"Performing {analysis_type} code analysis")
        
        # Analyze code
        analysis_result = await self.task_executor.analyze_code(code, analysis_type)
        
        # Attempt auto-fix for critical issues
        fixed_code = None
        if analysis_result["issues"]:
            critical_issues = [
                issue for issue in analysis_result["issues"]
                if issue.get("severity") == "critical"
            ]
            
            if critical_issues:
                logger.info(f"Found {len(critical_issues)} critical issues, attempting auto-fix")
                fixed_code = await self.task_executor.execute_auto_fix(
                    code, 
                    critical_issues[0]
                )
        
        return {
            "type": "code_analysis",
            "analysis": analysis_result,
            "auto_fix_applied": fixed_code is not None,
            "fixed_code": fixed_code,
            "recommendations": analysis_result.get("recommendations", [])
        }
    
    async def _handle_visualization(self,
                                   query: str,
                                   problem_content: str,
                                   editor_code: str) -> Dict[str, Any]:
        """
        Handle visualization/explanation request
        
        Args:
            query: User query
            problem_content: Problem context
            editor_code: Code context
            
        Returns:
            Explanation result
        """
        if not self.visualization_agent:
            return {"error": "Visualization agent not available"}
        
        logger.info("Generating explanation")
        
        explanation = await self.visualization_agent.generate_explanation(
            query,
            problem_content,
            editor_code
        )
        
        return {
            "type": "explanation",
            "explanation": explanation
        }
    
    async def _handle_diagram_generation(self,
                                        query: str,
                                        problem_content: str,
                                        editor_code: str) -> Dict[str, Any]:
        """
        Handle diagram generation request
        
        Args:
            query: User query
            problem_content: Problem context
            editor_code: Code context
            
        Returns:
            Diagram generation result
        """
        logger.info("Diagram generation requested")
        
        # Placeholder for diagram generation
        # In production, integrate with mermaid_agent
        return {
            "type": "diagram",
            "message": "Diagram generation capability available",
            "note": "Integrate with mermaid_agent for full functionality"
        }
    
    async def stream_process(self,
                           query: str,
                           problem_content: str = "",
                           editor_code: str = "",
                           analysis_type: str = "comprehensive"):
        """
        Process request with streaming response
        
        Args:
            query: User query
            problem_content: Problem context
            editor_code: Code to analyze
            analysis_type: Type of analysis
            
        Yields:
            Streaming processing updates
        """
        request_id = f"req_{self.request_count + 1}"
        
        logger.info(f"[{request_id}] Starting streaming process")
        
        # Yield initial status
        yield {
            "type": "status",
            "data": {"status": "started", "request_id": request_id}
        }
        
        # Intent recognition
        if self.recognition_server:
            async for chunk in self.recognition_server.process_request_stream(
                query, problem_content, editor_code
            ):
                yield chunk
        
        # Main processing
        result = await self.process_request(
            query, problem_content, editor_code, analysis_type
        )
        
        # Yield result
        yield {
            "type": "result",
            "data": result
        }
        
        # Complete
        yield {
            "type": "complete",
            "data": {"status": "completed", "request_id": request_id}
        }
        
        logger.info(f"[{request_id}] Streaming process completed")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics
        
        Returns:
            Pipeline statistics and metrics
        """
        stats = {
            "total_requests": self.request_count,
            "agents_available": {
                "recognition_server": self.recognition_server is not None,
                "task_executor": self.task_executor is not None,
                "visualization_agent": self.visualization_agent is not None
            }
        }
        
        # Add recognition server stats
        if self.recognition_server:
            stats["recognition_stats"] = self.recognition_server.get_statistics()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all agents
        
        Returns:
            Health status of pipeline and agents
        """
        return {
            "status": "healthy",
            "agents": {
                "recognition_server": "available" if self.recognition_server else "unavailable",
                "task_executor": "available" if self.task_executor else "unavailable",
                "visualization_agent": "available" if self.visualization_agent else "unavailable"
            },
            "total_requests_processed": self.request_count
        }


# Global singleton instance
pipeline_service = PipelineService()


async def main():
    """Example usage and testing"""
    service = PipelineService()
    
    print("=== Pipeline Service Test ===\n")
    
    # Health check
    health = service.health_check()
    print(f"Health Check: {json.dumps(health, indent=2)}\n")
    
    # Test code analysis
    test_code = """
def unsafe_function(user_input):
    # Security issue: eval
    result = eval(user_input)
    
    # Performance issue: nested loops
    for i in range(100):
        for j in range(100):
            for k in range(100):
                process(i, j, k)
    
    return result
"""
    
    print("Test 1: Code Analysis")
    result = await service.process_request(
        query="分析這段代碼",
        editor_code=test_code,
        analysis_type="comprehensive"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")
    
    # Test explanation
    print("Test 2: Explanation Request")
    result = await service.process_request(
        query="什麼是時間複雜度？"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")
    
    # Get statistics
    stats = service.get_statistics()
    print("Statistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
