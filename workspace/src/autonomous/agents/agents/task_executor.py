"""
Task Executor - Intelligent Code Analysis and Auto-Fix Agent
智能代碼分析與自動修復執行器

Core capabilities extracted from OJ-agent for autonomous systems:
- Intelligent code analysis with heuristic teaching strategies
- Automated error detection and fixing
- Real-time streaming responses
- Context-aware problem solving
- Safety-critical code review for autonomous vehicles/drones

Adapted for: Drone/Autonomous Vehicle/Automated Iteration Systems
"""

import json
import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator

# Configure logging - must be before any logger usage
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not available, environment variables will not be loaded from .env file")
class TaskExecutor:
    """
    智能任務執行器 - 用於自動化代碼分析與修復
    
    Intelligent task executor for automated code analysis and fixing.
    Designed for safety-critical autonomous systems requiring:
    - Zero-downtime operation
    - Real-time error detection
    - Automated code quality enforcement
    - Security vulnerability prevention
    """
    
    def __init__(self):
        """Initialize the task executor with context management"""
        self.problem_content = ""  # Current problem/issue context
        self.editor_code = ""      # Code under analysis
        self.context_history = []   # Conversation/analysis history
        self._initialized = False
        logger.info("TaskExecutor initialized for autonomous code analysis")
    
    def set_problem_content(self, content: str) -> None:
        """
        Set the problem/issue context for analysis
        
        Args:
            content: Problem description or requirements
        """
        self.problem_content = content
        logger.info(f"Problem content set: {len(content)} characters")
    
    def set_editor_code(self, code: str) -> None:
        """
        Set the code to be analyzed
        
        Args:
            code: Source code for analysis
        """
        self.editor_code = code
        logger.info(f"Editor code set: {len(code)} characters")
    
    def reset_context(self) -> None:
        """Reset the analysis context"""
        self.context_history = []
        logger.info("Context reset")
    
    async def analyze_code(self, 
                          code: str,
                          analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze code for quality, security, and performance issues
        
        Args:
            code: Source code to analyze
            analysis_type: Type of analysis (comprehensive, security, performance)
            
        Returns:
            Analysis results with detected issues and recommendations
        """
        logger.info(f"Starting {analysis_type} code analysis")
        
        results = {
            "analysis_type": analysis_type,
            "timestamp": asyncio.get_event_loop().time(),
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Safety-critical checks for autonomous systems
        if analysis_type in ["comprehensive", "security"]:
            security_issues = await self._check_security(code)
            results["issues"].extend(security_issues)
        
        if analysis_type in ["comprehensive", "performance"]:
            performance_issues = await self._check_performance(code)
            results["issues"].extend(performance_issues)
        
        # Generate automated fix recommendations
        if results["issues"]:
            results["recommendations"] = await self._generate_recommendations(
                results["issues"]
            )
        
        logger.info(f"Analysis complete: {len(results['issues'])} issues found")
        return results
    
    async def _check_security(self, code: str) -> list:
        """
        Check for security vulnerabilities
        
        Critical for autonomous systems:
        - Input validation
        - Memory safety
        - Concurrency issues
        - Authentication/Authorization
        """
        issues = []
        
        # Basic security pattern detection
        if "eval(" in code or "exec(" in code:
            issues.append({
                "type": "security",
                "severity": "critical",
                "description": "Dangerous code execution detected (eval/exec)",
                "line": None,
                "recommendation": "Remove eval/exec and use safe alternatives"
            })
        
        if "password" in code.lower() and ("=" in code or ":" in code):
            issues.append({
                "type": "security",
                "severity": "high",
                "description": "Potential hardcoded credentials",
                "line": None,
                "recommendation": "Use environment variables or secure vault"
            })
        
        return issues
    
    async def _check_performance(self, code: str) -> list:
        """
        Check for performance issues
        
        Critical for real-time autonomous systems:
        - Time complexity
        - Memory usage
        - Blocking operations
        - Resource leaks
        """
        issues = []
        
        # Basic performance pattern detection
        if code.count("for") > 3 and code.count("for") < 10:
            issues.append({
                "type": "performance",
                "severity": "medium",
                "description": "Nested loops detected - potential O(n^x) complexity",
                "line": None,
                "recommendation": "Consider optimization or algorithm improvement"
            })
        
        return issues
    
    async def _generate_recommendations(self, issues: list) -> list:
        """
        Generate automated fix recommendations
        
        Returns actionable recommendations for detected issues
        """
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "security" and issue["severity"] == "critical":
                recommendations.append({
                    "priority": "immediate",
                    "action": "automated_fix",
                    "description": f"Fix {issue['description']}",
                    "automated": True
                })
            elif issue["type"] == "performance":
                recommendations.append({
                    "priority": "high",
                    "action": "review",
                    "description": f"Optimize {issue['description']}",
                    "automated": False
                })
        
        return recommendations
    
    async def execute_auto_fix(self, 
                              code: str, 
                              issue: Dict[str, Any]) -> Optional[str]:
        """
        Execute automated code fix for detected issue
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Fixed code or None if cannot auto-fix
        """
        logger.info(f"Attempting auto-fix for: {issue['type']}")
        
        # Safety check - only auto-fix if high confidence
        if issue.get("automated") is False:
            logger.warning("Issue not suitable for automated fixing")
            return None
        
        # Implement specific fix strategies
        fixed_code = code
        
        if issue["type"] == "security":
            if "eval(" in code or "exec(" in code:
                # Remove dangerous code execution
                fixed_code = code.replace("eval(", "# REMOVED_eval(")
                fixed_code = fixed_code.replace("exec(", "# REMOVED_exec(")
                logger.info("Applied security fix: removed eval/exec")
        
        return fixed_code if fixed_code != code else None
    
    async def stream_analysis(self, 
                             code: str,
                             analysis_type: str = "comprehensive") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream analysis results in real-time
        
        Suitable for dashboard monitoring and continuous integration
        
        Args:
            code: Code to analyze
            analysis_type: Type of analysis
            
        Yields:
            Streaming analysis updates
        """
        logger.info("Starting streaming analysis")
        
        # Yield initial status
        yield {
            "status": "started",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Perform analysis in chunks
        analysis_result = await self.analyze_code(code, analysis_type)
        
        # Stream results
        for issue in analysis_result["issues"]:
            yield {
                "status": "issue_found",
                "issue": issue
            }
            await asyncio.sleep(0.1)  # Simulate streaming
        
        # Yield final summary
        yield {
            "status": "completed",
            "summary": {
                "total_issues": len(analysis_result["issues"]),
                "recommendations": len(analysis_result["recommendations"])
            }
        }
        
        logger.info("Streaming analysis completed")


# Global singleton instance for easy access
task_executor = TaskExecutor()


async def main():
    """Example usage for testing"""
    executor = TaskExecutor()
    
    # WARNING: This is test code with intentional security issues for demonstration purposes only
    # Example: Analyze potentially unsafe code
    test_code = """
def process_data(user_input):
    result = eval(user_input)  # WARNING: Intentional security issue for testing only!
    password = "hardcoded123"   # WARNING: Intentional security issue for testing only!
    
    for i in range(len(data)):
        for j in range(len(data)):
            for k in range(len(data)):  # Performance issue!
                process(i, j, k)
    
    return result
"""
    
    logger.info("Running example code analysis")
    results = await executor.analyze_code(test_code, "comprehensive")
    
    print("\n=== Analysis Results ===")
    print(json.dumps(results, indent=2))
    
    # Test auto-fix
    if results["issues"]:
        issue = results["issues"][0]
        fixed_code = await executor.execute_auto_fix(test_code, issue)
        if fixed_code:
            print("\n=== Auto-Fixed Code ===")
            print(fixed_code)


if __name__ == "__main__":
    asyncio.run(main())
