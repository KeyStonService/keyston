"""
Domain Experts (領域專家)

Specialized virtual expert implementations for different domains.

參考：AI 代理需要專業化分工 [1]
"""

from typing import Dict, List, Optional, Any

try:
    from .expert_base import (
        VirtualExpert,
        ExpertPersonality,
        ExpertKnowledge,
        WorkStyle,
        CommunicationStyle,
        ExpertiseLevel,
    )
except ImportError:
    from expert_base import (
        VirtualExpert,
        ExpertPersonality,
        ExpertKnowledge,
        WorkStyle,
        CommunicationStyle,
        ExpertiseLevel,
    )


# ============ Factory Functions for Domain Experts ============

def DrAlexChen() -> VirtualExpert:
    """
    Create Dr. Alex Chen - AI 架構師
    
    首席 AI 決策引擎架構師，專注於構建智能系統。
    """
    expert = VirtualExpert(
        id="expert_alex_chen",
        name="Dr. Alex Chen",
        title="首席 AI 決策引擎架構師",
        avatar="🧠",
        role="AI Architect",
        department="Core AI Team",
        personality=ExpertPersonality(
            traits=["analytical", "perfectionist", "innovative", "data-driven"],
            motto="Building intelligent systems that think ahead",
            approach="用數學和數據說話，追求算法的優雅與效率",
            strengths=[
                "算法設計與優化",
                "系統架構規劃",
                "性能調優",
                "複雜問題分解",
            ],
            working_preferences=[
                "先理論後實踐",
                "數據驅動決策",
                "迭代式優化",
            ]
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "ai-decision-engine",
                "machine-learning",
                "algorithm-optimization",
            ],
            secondary_domains=[
                "data-science",
                "system-architecture",
                "performance-engineering",
            ],
            specializations=[
                "決策樹算法優化",
                "神經網絡架構設計",
                "實時推理引擎",
                "模型性能調優",
            ],
            years_of_experience=15,
            certifications=[
                "PhD in Computer Science",
                "AWS Machine Learning Specialty",
            ],
            tools_expertise={
                "TensorFlow": ExpertiseLevel.MASTER,
                "PyTorch": ExpertiseLevel.MASTER,
                "scikit-learn": ExpertiseLevel.EXPERT,
                "ONNX": ExpertiseLevel.EXPERT,
            },
            methodologies=["MLOps", "AutoML", "Experiment Tracking"]
        ),
        work_style=WorkStyle(
            methodology="data-driven",
            pace="methodical",
            attention_to_detail="high",
            risk_tolerance="medium",
            collaboration_style="mentoring",
            decision_making="analytical",
        ),
        communication_style=CommunicationStyle(
            tone="professional",
            verbosity="detailed",
            explanation_style="technical",
            feedback_style="constructive",
            preferred_format="structured",
        ),
    )
    
    # Add custom methods
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "AI Architecture",
        }
        
        topic_lower = topic.lower()
        
        if "decision" in topic_lower:
            guidance.update({
                "guidance": """
決策引擎設計的關鍵原則：

1. **明確決策邊界**
   - 定義清楚什麼情況下系統可以自主決策
   - 設置適當的信心閾值

2. **多因素評估**
   - 不要依賴單一指標
   - 使用加權評分系統

3. **可解釋性**
   - 每個決策都要能夠解釋
   - 記錄決策過程和依據

4. **回饋學習**
   - 追蹤決策結果
   - 持續優化決策模型
""",
                "recommendations": [
                    "使用規則引擎 + ML 的混合方法",
                    "實施 A/B 測試驗證決策效果",
                    "建立決策審計日誌",
                ],
                "best_practices": [
                    "決策閾值應該可配置",
                    "高風險決策需要多重驗證",
                    "保留人工覆蓋的能力",
                ],
            })
        
        elif "model" in topic_lower or "performance" in topic_lower:
            guidance.update({
                "guidance": """
模型性能優化策略：

1. **數據優化**
   - 特徵工程是最重要的
   - 數據質量 > 數據數量

2. **模型選擇**
   - 從簡單模型開始
   - 只有在需要時才增加複雜度

3. **推理優化**
   - 模型量化
   - 批處理推理
   - 模型蒸餾
""",
                "recommendations": [
                    "使用模型基準測試",
                    "監控推理延遲分佈",
                    "考慮邊緣計算場景",
                ],
            })
        
        return guidance
    
    def review_code(code: str, language: str) -> Dict[str, Any]:
        issues = []
        suggestions = []
        
        code_lower = code.lower()
        
        if "predict" in code_lower and "try" not in code_lower:
            issues.append({
                "severity": "medium",
                "type": "error_handling",
                "message": "模型預測應該有錯誤處理",
            })
        
        if "model.fit" in code_lower and "validation" not in code_lower:
            issues.append({
                "severity": "medium",
                "type": "validation",
                "message": "建議使用驗證集監控訓練過程",
            })
        
        if "random" in code_lower and "seed" not in code_lower:
            suggestions.append({
                "type": "reproducibility",
                "message": "設置隨機種子以確保結果可重現",
            })
        
        return {
            "expert": expert.name,
            "language": language,
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": 1.0 - (len(issues) * 0.1),
        }
    
    # Attach methods
    expert.provide_guidance = provide_guidance
    expert.review_code = review_code
    
    return expert


def SarahWong() -> VirtualExpert:
    """
    Create Sarah Wong - 自然語言處理專家
    
    NLP 專家，專注於讓系統理解人類語言。
    """
    expert = VirtualExpert(
        id="expert_sarah_wong",
        name="Sarah Wong",
        title="首席 NLP 工程師",
        avatar="💬",
        role="NLP Expert",
        department="Core AI Team",
        personality=ExpertPersonality(
            traits=["creative", "empathetic", "detail-oriented", "curious"],
            motto="Teaching machines to understand humanity",
            approach="從用戶角度思考，讓機器更懂人類",
            strengths=[
                "意圖識別",
                "語義分析",
                "多語言處理",
                "對話系統設計",
            ],
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "natural-language-processing",
                "text-analysis",
                "conversational-ai",
            ],
            secondary_domains=[
                "machine-learning",
                "user-experience",
            ],
            specializations=[
                "意圖分類",
                "實體識別",
                "情感分析",
                "多語言 NLP",
            ],
            years_of_experience=12,
            tools_expertise={
                "spaCy": ExpertiseLevel.MASTER,
                "Hugging Face": ExpertiseLevel.MASTER,
                "NLTK": ExpertiseLevel.EXPERT,
            },
        ),
        work_style=WorkStyle(
            methodology="user-centered",
            collaboration_style="team-oriented",
        ),
        communication_style=CommunicationStyle(
            tone="friendly",
            explanation_style="example-based",
        ),
    )
    
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "NLP",
        }
        
        topic_lower = topic.lower()
        
        if "intent" in topic_lower or "意圖" in topic:
            guidance.update({
                "guidance": """
意圖識別最佳實踐：

1. **定義清晰的意圖分類**
   - 意圖應該互斥
   - 避免過於細粒度的分類

2. **收集多樣化的訓練數據**
   - 包含不同的表達方式
   - 考慮打字錯誤和口語

3. **處理邊界情況**
   - 設置「未知」意圖
   - 使用信心閾值

4. **多語言支持**
   - 考慮中英文混合
   - 處理翻譯差異
""",
                "recommendations": [
                    "使用預訓練模型作為基礎",
                    "實施主動學習收集難例",
                    "建立意圖混淆矩陣",
                ],
            })
        
        return guidance
    
    expert.provide_guidance = provide_guidance
    
    return expert


def MarcusJohnson() -> VirtualExpert:
    """
    Create Marcus Johnson - 安全架構師
    
    資深安全專家，專注於應用程序安全。
    """
    expert = VirtualExpert(
        id="expert_marcus_johnson",
        name="Marcus Johnson",
        title="首席安全架構師",
        avatar="🔐",
        role="Security Architect",
        department="Security Team",
        personality=ExpertPersonality(
            traits=["vigilant", "methodical", "skeptical", "thorough"],
            motto="Security is not a feature, it's a mindset",
            approach="假設一切都可能被攻擊，防禦深度優先",
            strengths=[
                "威脅建模",
                "滲透測試",
                "安全審計",
                "事件響應",
            ],
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "application-security",
                "authentication",
                "cryptography",
            ],
            secondary_domains=[
                "network-security",
                "compliance",
            ],
            specializations=[
                "OWASP Top 10",
                "安全編碼",
                "密鑰管理",
                "零信任架構",
            ],
            years_of_experience=18,
            certifications=[
                "CISSP",
                "CEH",
                "OSCP",
            ],
        ),
        work_style=WorkStyle(
            methodology="defense-in-depth",
            risk_tolerance="low",
            attention_to_detail="high",
        ),
        communication_style=CommunicationStyle(
            tone="professional",
            feedback_style="direct",
        ),
    )
    
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "Security",
        }
        
        topic_lower = topic.lower()
        
        if "password" in topic_lower or "密碼" in topic:
            guidance.update({
                "guidance": """
密碼安全最佳實踐：

⚠️ **絕對不要**：
- 明文存儲密碼
- 使用 MD5 或 SHA1
- 使用相同的鹽

✅ **必須做到**：
- 使用 bcrypt 或 Argon2
- 每個密碼使用唯一的隨機鹽
- 設置適當的工作因子

**代碼示例**：
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(), 
        bcrypt.gensalt(rounds=12)
    ).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode(), 
        hashed.encode()
    )
```
""",
                "warnings": [
                    "密碼洩露是最常見的安全事件",
                    "弱哈希可以被彩虹表破解",
                ],
            })
        
        elif "injection" in topic_lower or "注入" in topic:
            guidance.update({
                "guidance": """
防止注入攻擊：

1. **SQL 注入防護**
   - 永遠使用參數化查詢
   - 使用 ORM
   - 輸入驗證

2. **命令注入防護**
   - 避免使用 shell 執行
   - 白名單驗證輸入
   - 使用安全的 API

3. **XSS 防護**
   - 輸出編碼
   - Content-Security-Policy
   - HttpOnly cookies
""",
                "warnings": [
                    "注入攻擊是 OWASP Top 10 第一名",
                    "一個漏洞可能導致整個數據庫洩露",
                ],
            })
        
        return guidance
    
    def review_code(code: str, language: str) -> Dict[str, Any]:
        issues = []
        
        code_lower = code.lower()
        
        if "password" in code_lower:
            if "md5" in code_lower or "sha1" in code_lower:
                issues.append({
                    "severity": "critical",
                    "type": "weak_hashing",
                    "message": "使用弱哈希算法處理密碼！使用 bcrypt 或 argon2",
                })
            
            if "= password" in code_lower or "=password" in code_lower:
                issues.append({
                    "severity": "critical",
                    "type": "plaintext_password",
                    "message": "可能存在明文密碼存儲",
                })
        
        if "execute" in code_lower or "query" in code_lower:
            if "f'" in code or 'f"' in code or ".format" in code:
                issues.append({
                    "severity": "critical",
                    "type": "sql_injection",
                    "message": "可能存在 SQL 注入漏洞！使用參數化查詢",
                })
        
        if "eval(" in code_lower or "exec(" in code_lower:
            issues.append({
                "severity": "critical",
                "type": "code_injection",
                "message": "使用 eval/exec 可能導致代碼注入",
            })
        
        return {
            "expert": expert.name,
            "language": language,
            "issues": issues,
            "suggestions": [],
            "quality_score": 1.0 - (len(issues) * 0.2),
        }
    
    expert.provide_guidance = provide_guidance
    expert.review_code = review_code
    
    return expert


def LiWei() -> VirtualExpert:
    """
    Create Li Wei - 數據庫專家
    
    資深 DBA，專注於數據庫設計和優化。
    """
    expert = VirtualExpert(
        id="expert_li_wei",
        name="Li Wei",
        title="首席數據庫架構師",
        avatar="🗄️",
        role="Database Expert",
        department="Database Team",
        personality=ExpertPersonality(
            traits=["meticulous", "patient", "systematic", "performance-focused"],
            motto="Data is the foundation, performance is the key",
            approach="從數據模型開始，優化到每一毫秒",
            strengths=[
                "數據庫設計",
                "查詢優化",
                "索引策略",
                "分佈式數據庫",
            ],
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "database-design",
                "query-optimization",
                "data-modeling",
            ],
            secondary_domains=[
                "distributed-systems",
                "caching",
            ],
            specializations=[
                "索引優化",
                "N+1 問題解決",
                "事務處理",
                "分區策略",
            ],
            years_of_experience=16,
            tools_expertise={
                "PostgreSQL": ExpertiseLevel.MASTER,
                "MySQL": ExpertiseLevel.MASTER,
                "Redis": ExpertiseLevel.EXPERT,
                "MongoDB": ExpertiseLevel.PROFICIENT,
            },
        ),
        work_style=WorkStyle(
            methodology="measurement-first",
            attention_to_detail="high",
        ),
    )
    
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "Database",
        }
        
        topic_lower = topic.lower()
        
        if "n+1" in topic_lower or "query" in topic_lower:
            guidance.update({
                "guidance": """
N+1 查詢問題解決方案：

**問題識別**：
- 監控 SQL 日誌
- 查看查詢次數與數據量的關係

**解決方案**：

1. **預加載 (Eager Loading)**
```python
users = db.users.find_many(include={'orders': True})
```

2. **批量查詢**
```python
user_ids = [u.id for u in users]
orders = db.orders.find_many(where={'user_id': {'in': user_ids}})
```

3. **JOIN 查詢**
```sql
SELECT u.*, o.* 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id
```
""",
                "best_practices": [
                    "總是檢查 ORM 生成的 SQL",
                    "使用 EXPLAIN 分析查詢",
                    "設置查詢日誌監控",
                ],
            })
        
        elif "index" in topic_lower or "索引" in topic:
            guidance.update({
                "guidance": """
索引設計原則：

1. **選擇正確的列**
   - WHERE 子句中的列
   - JOIN 條件列
   - ORDER BY 列

2. **複合索引設計**
   - 遵循最左前綴原則
   - 選擇性高的列放前面

3. **避免過度索引**
   - 索引會降低寫入性能
   - 定期檢查未使用的索引

4. **覆蓋索引**
   - 包含查詢所需的所有列
   - 避免回表查詢
""",
            })
        
        return guidance
    
    expert.provide_guidance = provide_guidance
    
    return expert


def EmmaThompson() -> VirtualExpert:
    """
    Create Emma Thompson - DevOps 專家
    
    資深 DevOps 工程師，專注於自動化和可靠性。
    """
    expert = VirtualExpert(
        id="expert_emma_thompson",
        name="Emma Thompson",
        title="首席 DevOps 工程師",
        avatar="🚀",
        role="DevOps Expert",
        department="DevOps Team",
        personality=ExpertPersonality(
            traits=["automation-focused", "pragmatic", "resilient", "collaborative"],
            motto="Automate everything, monitor relentlessly",
            approach="如果需要做兩次，就應該自動化",
            strengths=[
                "CI/CD 流程設計",
                "基礎設施即代碼",
                "監控和告警",
                "故障排除",
            ],
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "ci-cd",
                "infrastructure-as-code",
                "containerization",
            ],
            secondary_domains=[
                "cloud-platforms",
                "monitoring",
            ],
            specializations=[
                "Kubernetes",
                "Docker",
                "Terraform",
                "GitHub Actions",
            ],
            years_of_experience=12,
            tools_expertise={
                "Kubernetes": ExpertiseLevel.MASTER,
                "Docker": ExpertiseLevel.MASTER,
                "Terraform": ExpertiseLevel.EXPERT,
                "Prometheus": ExpertiseLevel.EXPERT,
            },
        ),
        work_style=WorkStyle(
            methodology="automation-first",
            collaboration_style="team-oriented",
        ),
    )
    
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "DevOps",
        }
        
        topic_lower = topic.lower()
        
        if "deploy" in topic_lower or "部署" in topic:
            guidance.update({
                "guidance": """
部署最佳實踐：

1. **部署策略選擇**
   - **Rolling**: 漸進式更新，適合大多數情況
   - **Blue-Green**: 零停機，快速回滾
   - **Canary**: 漸進式驗證，降低風險

2. **自動化部署流程**
   - 使用 CI/CD 流水線
   - 自動化測試
   - 自動化回滾

3. **監控和告警**
   - 部署後監控關鍵指標
   - 設置異常告警
   - 準備回滾計劃
""",
                "recommendations": [
                    "使用 GitOps 方法",
                    "實施漸進式發布",
                    "自動化冒煙測試",
                ],
            })
        
        return guidance
    
    expert.provide_guidance = provide_guidance
    
    return expert


def JamesMiller() -> VirtualExpert:
    """
    Create James Miller - 系統架構師
    
    資深架構師，專注於系統設計和可擴展性。
    """
    expert = VirtualExpert(
        id="expert_james_miller",
        name="James Miller",
        title="首席系統架構師",
        avatar="🏗️",
        role="System Architect",
        department="Architecture Team",
        personality=ExpertPersonality(
            traits=["strategic", "big-picture", "pragmatic", "experienced"],
            motto="Architecture is the art of making trade-offs",
            approach="從業務需求出發，平衡複雜度和價值",
            strengths=[
                "系統設計",
                "技術決策",
                "架構評估",
                "技術債務管理",
            ],
        ),
        knowledge=ExpertKnowledge(
            primary_domains=[
                "system-architecture",
                "design-patterns",
                "scalability",
            ],
            secondary_domains=[
                "microservices",
                "event-driven-architecture",
            ],
            specializations=[
                "領域驅動設計",
                "微服務架構",
                "事件驅動架構",
                "CQRS/Event Sourcing",
            ],
            years_of_experience=20,
        ),
        work_style=WorkStyle(
            methodology="domain-driven",
            decision_making="analytical",
        ),
    )
    
    def provide_guidance(topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        guidance = {
            "expert": expert.name,
            "topic": topic,
            "perspective": "Architecture",
        }
        
        topic_lower = topic.lower()
        
        if "microservice" in topic_lower or "微服務" in topic:
            guidance.update({
                "guidance": """
微服務架構決策：

**何時使用微服務**：
- 團隊規模大（20+人）
- 需要獨立擴展不同組件
- 技術棧需要多樣化

**何時不使用**：
- 小團隊（<10人）
- 早期產品驗證階段
- 簡單的業務邏輯

**建議**：
從模塊化單體開始，按需演進到微服務。
""",
                "recommendations": [
                    "先定義清晰的領域邊界",
                    "使用 API 合約優先設計",
                    "考慮運維複雜度",
                ],
            })
        
        return guidance
    
    expert.provide_guidance = provide_guidance
    
    return expert
