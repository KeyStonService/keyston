"""
Visualization Agent - Intelligent Explanation and Concept Visualization
可視化智能體 - 智能解釋與概念可視化

Core capabilities for autonomous systems:
- Generate intuitive explanations for complex algorithms
- Use analogies and metaphors for better understanding
- Support real-time streaming explanations
- Context-aware explanation generation

Adapted for: Training and debugging autonomous systems
"""

import logging
from typing import Dict, Any, AsyncGenerator
import asyncio

# Configure logging
logger = logging.getLogger(__name__)


class VisualizationAgent:
    """
    可視化智能體 - 生成易懂的概念解釋
    
    Visualization agent for generating intuitive explanations.
    Designed for:
    - Algorithm explanation
    - Concept clarification
    - Debugging assistance
    - Knowledge transfer
    """
    
    def __init__(self):
        """Initialize visualization agent"""
        self.explanation_history = []
        logger.info("VisualizationAgent initialized")
    
    async def generate_explanation(self,
                                   query: str,
                                   problem_content: str = "",
                                   editor_code: str = "") -> Dict[str, Any]:
        """
        Generate intuitive explanation for query
        
        Args:
            query: Question or concept to explain
            problem_content: Problem context
            editor_code: Code context
            
        Returns:
            Explanation with analogies and examples
        """
        logger.info(f"Generating explanation for: {query[:100]}...")
        
        # Analyze query topic
        topic = self._identify_topic(query)
        
        # Generate explanation
        explanation = await self._create_explanation(topic, query)
        
        # Generate follow-up questions
        follow_ups = self._generate_follow_up_questions(topic, query)
        
        result = {
            "query": query,
            "topic": topic,
            "explanation": explanation,
            "follow_up_questions": follow_ups,
            "has_context": {
                "problem": bool(problem_content),
                "code": bool(editor_code)
            }
        }
        
        # Store in history
        self.explanation_history.append(result)
        
        logger.info(f"Explanation generated for topic: {topic}")
        return result
    
    def _identify_topic(self, query: str) -> str:
        """
        Identify the main topic of the query
        
        Args:
            query: User query
            
        Returns:
            Identified topic category
        """
        query_lower = query.lower()
        
        # Algorithm topics
        if any(keyword in query_lower for keyword in 
               ["sort", "search", "algorithm", "complexity", "遞歸", "recursion"]):
            return "algorithm"
        
        # Data structure topics
        if any(keyword in query_lower for keyword in
               ["array", "list", "tree", "graph", "stack", "queue", "hash"]):
            return "data_structure"
        
        # Performance topics
        if any(keyword in query_lower for keyword in
               ["performance", "optimization", "efficiency", "性能", "優化"]):
            return "performance"
        
        # Concurrency topics
        if any(keyword in query_lower for keyword in
               ["thread", "async", "concurrent", "parallel", "並發", "異步"]):
            return "concurrency"
        
        # Safety topics (critical for autonomous systems)
        if any(keyword in query_lower for keyword in
               ["safety", "reliability", "fault", "error", "安全", "可靠"]):
            return "safety"
        
        return "general"
    
    async def _create_explanation(self, topic: str, query: str) -> Dict[str, Any]:
        """
        Create detailed explanation with analogies
        
        Args:
            topic: Topic category
            query: Original query
            
        Returns:
            Structured explanation
        """
        # Base explanation structure
        explanation = {
            "summary": "",
            "analogy": "",
            "key_points": [],
            "practical_example": ""
        }
        
        if topic == "algorithm":
            explanation["summary"] = "算法是解決問題的步驟方法"
            explanation["analogy"] = "就像烹飪食譜一樣，提供按順序執行的明確步驟"
            explanation["key_points"] = [
                "明確的輸入和輸出",
                "有限的步驟數量",
                "每步驟都是可執行的",
                "最終能解決特定問題"
            ]
            explanation["practical_example"] = "在自動駕駛中，路徑規劃算法決定車輛行駛路線"
        
        elif topic == "data_structure":
            explanation["summary"] = "數據結構是組織和存儲數據的方式"
            explanation["analogy"] = "就像圖書館的分類系統，不同的組織方式適合不同的查找需求"
            explanation["key_points"] = [
                "選擇合適的數據結構影響效率",
                "不同操作有不同的時間複雜度",
                "空間和時間需要權衡",
                "根據使用場景選擇"
            ]
            explanation["practical_example"] = "無人機使用樹結構管理傳感器數據層次"
        
        elif topic == "performance":
            explanation["summary"] = "性能優化關注程序執行效率"
            explanation["analogy"] = "就像調整車輛引擎，找出瓶頸並優化關鍵部分"
            explanation["key_points"] = [
                "先測量後優化",
                "關注熱點代碼路徑",
                "權衡可讀性和效率",
                "考慮實時性要求"
            ]
            explanation["practical_example"] = "自動駕駛系統需要在毫秒級做出決策"
        
        elif topic == "concurrency":
            explanation["summary"] = "並發處理多個任務同時進行"
            explanation["analogy"] = "就像餐廳廚房，多個廚師同時準備不同菜品"
            explanation["key_points"] = [
                "提高系統吞吐量",
                "需要處理同步問題",
                "避免競態條件",
                "合理使用鎖機制"
            ]
            explanation["practical_example"] = "無人機同時處理導航、避障、通訊等任務"
        
        elif topic == "safety":
            explanation["summary"] = "安全性確保系統可靠運行"
            explanation["analogy"] = "就像飛機的多重安全系統，層層保護防止故障"
            explanation["key_points"] = [
                "輸入驗證和邊界檢查",
                "錯誤處理和恢復",
                "冗餘和備份機制",
                "持續監控和告警"
            ]
            explanation["practical_example"] = "自動駕駛車輛需要多重傳感器驗證決策"
        
        else:
            explanation["summary"] = "通用編程概念說明"
            explanation["analogy"] = "具體問題具體分析"
            explanation["key_points"] = ["理解問題本質", "選擇合適工具", "測試驗證"]
            explanation["practical_example"] = "根據實際需求選擇最佳解決方案"
        
        return explanation
    
    def _generate_follow_up_questions(self, topic: str, query: str) -> list:
        """
        Generate relevant follow-up questions
        
        Args:
            topic: Topic category
            query: Original query
            
        Returns:
            List of follow-up questions
        """
        base_questions = {
            "algorithm": [
                "這個算法的時間複雜度是多少？",
                "有沒有更高效的算法？",
                "在什麼情況下應該使用這個算法？"
            ],
            "data_structure": [
                "這個數據結構的主要操作時間複雜度是？",
                "它相比其他數據結構有什麼優勢？",
                "在實際應用中如何選擇合適的數據結構？"
            ],
            "performance": [
                "如何測量當前系統的性能瓶頸？",
                "有哪些常見的性能優化策略？",
                "優化後如何驗證改進效果？"
            ],
            "concurrency": [
                "如何避免並發問題？",
                "什麼時候應該使用異步處理？",
                "如何處理競態條件？"
            ],
            "safety": [
                "如何設計容錯機制？",
                "怎樣處理異常情況？",
                "如何驗證系統的安全性？"
            ],
            "general": [
                "這個概念的實際應用場景？",
                "有哪些最佳實踐？",
                "常見的錯誤是什麼？"
            ]
        }
        
        return base_questions.get(topic, base_questions["general"])
    
    async def stream_explanation(self,
                                query: str,
                                problem_content: str = "",
                                editor_code: str = "") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream explanation in real-time
        
        Args:
            query: Question to explain
            problem_content: Problem context
            editor_code: Code context
            
        Yields:
            Streaming explanation chunks
        """
        logger.info("Starting streaming explanation")
        
        # Yield start
        yield {
            "type": "start",
            "query": query
        }
        
        # Generate explanation
        result = await self.generate_explanation(query, problem_content, editor_code)
        
        # Stream summary
        yield {
            "type": "summary",
            "data": result["explanation"]["summary"]
        }
        await asyncio.sleep(0.1)
        
        # Stream analogy
        yield {
            "type": "analogy",
            "data": result["explanation"]["analogy"]
        }
        await asyncio.sleep(0.1)
        
        # Stream key points
        for point in result["explanation"]["key_points"]:
            yield {
                "type": "key_point",
                "data": point
            }
            await asyncio.sleep(0.1)
        
        # Stream example
        yield {
            "type": "example",
            "data": result["explanation"]["practical_example"]
        }
        
        # Stream follow-up questions
        yield {
            "type": "follow_up",
            "data": result["follow_up_questions"]
        }
        
        # Complete
        yield {
            "type": "complete",
            "data": {"topic": result["topic"]}
        }
        
        logger.info("Streaming explanation completed")


# Example usage
async def main():
    """Test visualization agent"""
    agent = VisualizationAgent()
    
    test_queries = [
        "什麼是遞歸？",
        "如何優化算法性能？",
        "並發編程的注意事項",
        "自動駕駛系統如何保證安全性？"
    ]
    
    print("=== Visualization Agent Test ===\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        result = await agent.generate_explanation(query)
        print(f"\nTopic: {result['topic']}")
        print(f"Summary: {result['explanation']['summary']}")
        print(f"Analogy: {result['explanation']['analogy']}")
        print(f"Key Points: {result['explanation']['key_points']}")
        print(f"Example: {result['explanation']['practical_example']}")
        print(f"Follow-up: {result['follow_up_questions'][:2]}")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
