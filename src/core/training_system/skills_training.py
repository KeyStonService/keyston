"""
Skills Training System (技能訓練系統)

Provides structured training and skill development for AI agents including:
- Skill definitions and levels
- Training modules and sessions
- Skill assessment and certification
- Learning paths

參考：AI 代理需要根本不同的訓練方法 [3]
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid
import asyncio


class SkillLevel(Enum):
    """Skill proficiency levels."""
    NOVICE = "novice"           # 新手 - Basic awareness
    BEGINNER = "beginner"       # 初學者 - Can perform with guidance
    INTERMEDIATE = "intermediate"  # 中級 - Can perform independently
    ADVANCED = "advanced"       # 高級 - Can handle complex scenarios
    EXPERT = "expert"           # 專家 - Can teach others and innovate


class SkillCategory(Enum):
    """Skill categories for organization."""
    TECHNICAL = "technical"
    PROBLEM_SOLVING = "problem_solving"
    DECISION_MAKING = "decision_making"
    COMMUNICATION = "communication"
    DOMAIN_SPECIFIC = "domain_specific"


@dataclass
class Skill:
    """
    Defines a learnable skill with progression criteria.
    
    技能定義：可學習的技能及其進階標準
    """
    id: str
    name: str
    category: SkillCategory
    description: str
    
    # Progression criteria for each level
    level_criteria: Dict[SkillLevel, List[str]] = field(default_factory=dict)
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)
    
    # Associated knowledge
    related_concepts: List[str] = field(default_factory=list)
    related_practices: List[str] = field(default_factory=list)
    
    # Metadata
    difficulty: str = "intermediate"
    estimated_learning_hours: int = 10
    tags: List[str] = field(default_factory=list)


@dataclass
class TrainingModule:
    """
    A training module containing learning content and exercises.
    
    訓練模組：包含學習內容和練習的模組
    """
    id: str
    name: str
    skill_id: str
    target_level: SkillLevel
    
    # Content
    learning_objectives: List[str] = field(default_factory=list)
    theory_content: str = ""
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Exercises
    exercises: List[Dict[str, Any]] = field(default_factory=list)
    
    # Assessment
    assessment_criteria: List[str] = field(default_factory=list)
    passing_score: float = 0.7
    
    # Metadata
    duration_minutes: int = 60
    prerequisites_modules: List[str] = field(default_factory=list)


@dataclass
class TrainingSession:
    """
    A training session instance for an AI agent.
    
    訓練課程：AI 智能體的訓練課程實例
    """
    id: str
    agent_id: str
    module_id: str
    
    # Progress
    status: str = "not_started"  # not_started, in_progress, completed, failed
    progress_percentage: float = 0.0
    current_exercise: int = 0
    
    # Results
    exercise_results: List[Dict[str, Any]] = field(default_factory=list)
    assessment_score: Optional[float] = None
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Feedback
    feedback: List[str] = field(default_factory=list)


@dataclass
class SkillAssessment:
    """
    Assessment result for a skill.
    
    技能評估：技能評估結果
    """
    id: str
    agent_id: str
    skill_id: str
    
    # Assessment details
    assessed_level: SkillLevel = SkillLevel.NOVICE
    score: float = 0.0
    confidence: float = 0.0
    
    # Evidence
    evidence: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    
    # Recommendations
    recommended_modules: List[str] = field(default_factory=list)
    next_level_requirements: List[str] = field(default_factory=list)
    
    # Metadata
    assessed_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningPath:
    """
    A structured learning path for skill development.
    
    學習路徑：技能發展的結構化學習路徑
    """
    id: str
    name: str
    description: str
    target_role: str  # e.g., "database_expert", "security_specialist"
    
    # Path structure
    skills: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Progression
    estimated_duration_hours: int = 40
    
    # Metadata
    difficulty: str = "intermediate"
    prerequisites: List[str] = field(default_factory=list)


class SkillsTrainingSystem:
    """
    Comprehensive Skills Training System for AI Agents.
    
    AI 技能訓練系統：教導 AI 如何執行任務和做決策
    
    核心功能：
    1. 技能定義與管理 - Skill definition and management
    2. 訓練模組執行 - Training module execution
    3. 技能評估 - Skill assessment
    4. 學習路徑規劃 - Learning path planning
    5. 進度追蹤 - Progress tracking
    
    參考：AI 代理需要根本不同的訓練數據 - 不是教模式識別，而是教如何執行任務 [3]
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.modules: Dict[str, TrainingModule] = {}
        self.sessions: Dict[str, TrainingSession] = {}
        self.assessments: Dict[str, List[SkillAssessment]] = {}
        self.learning_paths: Dict[str, LearningPath] = {}
        self.agent_skills: Dict[str, Dict[str, SkillLevel]] = {}  # agent_id -> skill_id -> level
        
        # Exercise handlers
        self._exercise_handlers: Dict[str, Callable] = {}
        
        # Initialize built-in skills and modules
        self._initialize_core_skills()
        self._initialize_training_modules()
        self._initialize_learning_paths()
    
    def _initialize_core_skills(self) -> None:
        """Initialize core skills for AI agents."""
        
        # Database Query Optimization Skill
        db_optimization = Skill(
            id="skill_db_optimization",
            name="Database Query Optimization",
            category=SkillCategory.TECHNICAL,
            description="優化數據庫查詢以提高性能",
            level_criteria={
                SkillLevel.NOVICE: [
                    "了解索引的基本概念",
                    "能識別簡單的慢查詢",
                ],
                SkillLevel.BEGINNER: [
                    "能為常見查詢添加適當的索引",
                    "了解 EXPLAIN 分析",
                ],
                SkillLevel.INTERMEDIATE: [
                    "能優化複雜的 JOIN 查詢",
                    "能識別並解決 N+1 問題",
                    "了解分頁策略",
                ],
                SkillLevel.ADVANCED: [
                    "能設計高效的數據庫架構",
                    "能處理大規模數據優化",
                    "了解分區和分片策略",
                ],
                SkillLevel.EXPERT: [
                    "能設計和評估複雜的索引策略",
                    "能進行數據庫性能調優",
                    "能教導其他人數據庫優化",
                ],
            },
            prerequisites=[],
            related_concepts=["db_indexing", "query_optimization"],
            related_practices=["use_transactions"],
            estimated_learning_hours=20,
            tags=["database", "performance", "optimization"],
        )
        self.skills[db_optimization.id] = db_optimization
        
        # Secure Coding Skill
        secure_coding = Skill(
            id="skill_secure_coding",
            name="Secure Coding Practices",
            category=SkillCategory.TECHNICAL,
            description="編寫安全的代碼，防止常見漏洞",
            level_criteria={
                SkillLevel.NOVICE: [
                    "了解常見安全漏洞類型",
                    "了解密碼應該哈希存儲",
                ],
                SkillLevel.BEGINNER: [
                    "能使用參數化查詢防止 SQL 注入",
                    "能正確處理用戶輸入驗證",
                ],
                SkillLevel.INTERMEDIATE: [
                    "能實施完整的認證系統",
                    "能處理 XSS 和 CSRF 防護",
                    "了解安全標頭配置",
                ],
                SkillLevel.ADVANCED: [
                    "能設計安全的 API 架構",
                    "能進行安全代碼審查",
                    "了解加密和密鑰管理",
                ],
                SkillLevel.EXPERT: [
                    "能設計企業級安全架構",
                    "能評估和修復複雜安全漏洞",
                    "能培訓團隊安全意識",
                ],
            },
            prerequisites=[],
            related_concepts=["authentication", "authorization"],
            related_practices=["secure_password_handling"],
            estimated_learning_hours=30,
            tags=["security", "coding", "best_practices"],
        )
        self.skills[secure_coding.id] = secure_coding
        
        # Problem Analysis Skill
        problem_analysis = Skill(
            id="skill_problem_analysis",
            name="Problem Analysis and Root Cause Identification",
            category=SkillCategory.PROBLEM_SOLVING,
            description="分析問題並識別根本原因",
            level_criteria={
                SkillLevel.NOVICE: [
                    "能描述問題現象",
                    "能收集基本錯誤信息",
                ],
                SkillLevel.BEGINNER: [
                    "能區分症狀和原因",
                    "能使用日誌進行基本診斷",
                ],
                SkillLevel.INTERMEDIATE: [
                    "能進行系統性的問題分析",
                    "能識別多個可能的原因",
                    "能制定測試假設的計劃",
                ],
                SkillLevel.ADVANCED: [
                    "能分析複雜的分佈式系統問題",
                    "能識別隱藏的依賴關係",
                    "能預測問題的連鎖反應",
                ],
                SkillLevel.EXPERT: [
                    "能建立問題分析框架",
                    "能教導問題分析方法論",
                    "能在壓力下快速定位問題",
                ],
            },
            prerequisites=[],
            estimated_learning_hours=25,
            tags=["problem_solving", "debugging", "analysis"],
        )
        self.skills[problem_analysis.id] = problem_analysis
        
        # Decision Making Skill
        decision_making = Skill(
            id="skill_decision_making",
            name="Technical Decision Making",
            category=SkillCategory.DECISION_MAKING,
            description="在技術場景中做出明智的決策",
            level_criteria={
                SkillLevel.NOVICE: [
                    "能識別需要決策的情況",
                    "能列出可能的選項",
                ],
                SkillLevel.BEGINNER: [
                    "能比較不同選項的優缺點",
                    "能考慮基本的約束條件",
                ],
                SkillLevel.INTERMEDIATE: [
                    "能進行風險評估",
                    "能考慮長期影響",
                    "能權衡技術債務",
                ],
                SkillLevel.ADVANCED: [
                    "能在不確定性下做決策",
                    "能評估多維度的影響",
                    "能制定決策框架",
                ],
                SkillLevel.EXPERT: [
                    "能做戰略性技術決策",
                    "能建立決策支持系統",
                    "能培養團隊決策能力",
                ],
            },
            prerequisites=[],
            estimated_learning_hours=20,
            tags=["decision_making", "strategy", "trade_offs"],
        )
        self.skills[decision_making.id] = decision_making
    
    def _initialize_training_modules(self) -> None:
        """Initialize training modules."""
        
        # Database Optimization Module - Beginner
        db_module_beginner = TrainingModule(
            id="module_db_opt_beginner",
            name="Database Optimization Fundamentals",
            skill_id="skill_db_optimization",
            target_level=SkillLevel.BEGINNER,
            learning_objectives=[
                "理解索引的工作原理",
                "學會使用 EXPLAIN 分析查詢",
                "能為簡單查詢添加索引",
            ],
            theory_content="""
# 數據庫索引基礎

## 什麼是索引？
索引是數據庫中用於加速數據檢索的數據結構。就像書籍的目錄一樣，
索引允許數據庫快速定位數據，而無需掃描整個表。

## 索引類型
1. **B-Tree 索引**：最常見的索引類型，適用於範圍查詢和排序
2. **Hash 索引**：適用於等值查詢
3. **全文索引**：適用於文本搜索

## 何時使用索引
- 經常用於 WHERE 子句的列
- 用於 JOIN 的列
- 用於 ORDER BY 的列

## 索引的代價
- 增加存儲空間
- 降低寫入性能
- 需要維護

## EXPLAIN 分析
使用 EXPLAIN 可以查看查詢的執行計劃，識別潛在的性能問題。
""",
            examples=[
                {
                    "title": "創建索引示例",
                    "description": "為用戶表的 email 列創建索引",
                    "code": """
-- 創建索引
CREATE INDEX idx_users_email ON users(email);

-- 驗證索引生效
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
""",
                    "expected_outcome": "查詢應該使用 idx_users_email 索引",
                },
            ],
            exercises=[
                {
                    "id": "ex_1",
                    "type": "analysis",
                    "question": "分析以下查詢，判斷是否需要索引：SELECT * FROM orders WHERE user_id = 123 AND status = 'pending'",
                    "expected_answer": "需要為 (user_id, status) 創建複合索引",
                    "hints": ["考慮查詢的 WHERE 條件", "複合索引遵循最左前綴原則"],
                },
                {
                    "id": "ex_2",
                    "type": "code_fix",
                    "question": "這個查詢很慢：SELECT * FROM products ORDER BY created_at DESC LIMIT 10",
                    "expected_answer": "CREATE INDEX idx_products_created_at ON products(created_at DESC);",
                    "hints": ["ORDER BY 子句也可以使用索引"],
                },
            ],
            assessment_criteria=[
                "能正確識別需要索引的列",
                "能使用 EXPLAIN 分析查詢",
                "能創建適當的索引",
            ],
            passing_score=0.7,
            duration_minutes=90,
        )
        self.modules[db_module_beginner.id] = db_module_beginner
        
        # Database Optimization Module - Intermediate
        db_module_intermediate = TrainingModule(
            id="module_db_opt_intermediate",
            name="Advanced Query Optimization",
            skill_id="skill_db_optimization",
            target_level=SkillLevel.INTERMEDIATE,
            learning_objectives=[
                "識別並解決 N+1 查詢問題",
                "優化複雜的 JOIN 查詢",
                "實施有效的分頁策略",
            ],
            theory_content="""
# 進階查詢優化

## N+1 查詢問題
N+1 查詢是指在循環中執行額外的查詢，導致查詢次數與數據量成正比。

### 問題示例
```python
users = db.users.find_many()  # 1 次查詢
for user in users:
    orders = db.orders.find_many(where={'user_id': user.id})  # N 次查詢
```

### 解決方案
1. 使用 JOIN
2. 使用預加載（Eager Loading）
3. 使用批量查詢

## 高效分頁
傳統的 OFFSET 分頁在大數據量時性能很差。

### 遊標分頁
```sql
SELECT * FROM products 
WHERE id > :last_id 
ORDER BY id 
LIMIT 20;
```
""",
            exercises=[
                {
                    "id": "ex_1",
                    "type": "code_refactor",
                    "question": """
修復這段代碼的 N+1 問題：
users = db.users.find_many()
for user in users:
    user.orders = db.orders.find_many(where={'user_id': user.id})
""",
                    "expected_answer": "users = db.users.find_many(include={'orders': True})",
                    "hints": ["使用 ORM 的 include/eager loading 功能"],
                },
            ],
            assessment_criteria=[
                "能識別 N+1 查詢問題",
                "能使用預加載解決 N+1",
                "能實施遊標分頁",
            ],
            passing_score=0.75,
            duration_minutes=120,
            prerequisites_modules=["module_db_opt_beginner"],
        )
        self.modules[db_module_intermediate.id] = db_module_intermediate
        
        # Secure Coding Module - Beginner
        security_module_beginner = TrainingModule(
            id="module_security_beginner",
            name="Secure Coding Fundamentals",
            skill_id="skill_secure_coding",
            target_level=SkillLevel.BEGINNER,
            learning_objectives=[
                "了解常見安全漏洞",
                "學會使用參數化查詢",
                "正確處理密碼存儲",
            ],
            theory_content="""
# 安全編碼基礎

## 最重要的安全原則
**永遠不要信任用戶輸入**

## 常見安全漏洞

### 1. SQL 注入
攻擊者通過輸入惡意 SQL 代碼來操縱數據庫查詢。

❌ 不安全：
```python
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

✅ 安全：
```python
query = "SELECT * FROM users WHERE email = %s"
db.execute(query, (user_input,))
```

### 2. 密碼存儲
密碼必須使用強哈希算法存儲，永不明文。

❌ 不安全：
```python
db.users.create({'password': plain_password})
```

✅ 安全：
```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
db.users.create({'password': hashed})
```

## 輸入驗證
所有用戶輸入都必須驗證和清理。
""",
            exercises=[
                {
                    "id": "ex_1",
                    "type": "vulnerability_fix",
                    "question": """
修復這段代碼的安全漏洞：
def login(email, password):
    query = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
    user = db.execute(query)
    return user
""",
                    "expected_answer": """
def login(email, password):
    query = "SELECT * FROM users WHERE email = %s"
    user = db.execute(query, (email,))
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None
""",
                    "hints": ["使用參數化查詢", "密碼應該哈希存儲"],
                },
            ],
            assessment_criteria=[
                "能識別 SQL 注入漏洞",
                "能使用參數化查詢",
                "能正確處理密碼哈希",
            ],
            passing_score=0.8,  # Security requires higher passing score
            duration_minutes=90,
        )
        self.modules[security_module_beginner.id] = security_module_beginner
    
    def _initialize_learning_paths(self) -> None:
        """Initialize learning paths."""
        
        # Database Expert Path
        db_expert_path = LearningPath(
            id="path_database_expert",
            name="Database Expert Path",
            description="成為數據庫優化和設計專家的學習路徑",
            target_role="database_expert",
            skills=[
                "skill_db_optimization",
            ],
            modules=[
                "module_db_opt_beginner",
                "module_db_opt_intermediate",
            ],
            milestones=[
                {
                    "name": "基礎完成",
                    "requirements": ["module_db_opt_beginner"],
                    "level": SkillLevel.BEGINNER.value,
                },
                {
                    "name": "進階完成",
                    "requirements": ["module_db_opt_intermediate"],
                    "level": SkillLevel.INTERMEDIATE.value,
                },
            ],
            estimated_duration_hours=20,
            difficulty="intermediate",
        )
        self.learning_paths[db_expert_path.id] = db_expert_path
        
        # Security Specialist Path
        security_path = LearningPath(
            id="path_security_specialist",
            name="Security Specialist Path",
            description="成為應用安全專家的學習路徑",
            target_role="security_specialist",
            skills=[
                "skill_secure_coding",
            ],
            modules=[
                "module_security_beginner",
            ],
            milestones=[
                {
                    "name": "安全基礎完成",
                    "requirements": ["module_security_beginner"],
                    "level": SkillLevel.BEGINNER.value,
                },
            ],
            estimated_duration_hours=30,
            difficulty="intermediate",
        )
        self.learning_paths[security_path.id] = security_path
    
    # Training Methods
    
    def start_training_session(self, agent_id: str, module_id: str) -> TrainingSession:
        """
        Start a new training session for an agent.
        
        開始訓練課程
        """
        if module_id not in self.modules:
            raise ValueError(f"Module not found: {module_id}")
        
        module = self.modules[module_id]
        
        # Check prerequisites
        for prereq_id in module.prerequisites_modules:
            if not self._has_completed_module(agent_id, prereq_id):
                raise ValueError(f"Prerequisite not completed: {prereq_id}")
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = TrainingSession(
            id=session_id,
            agent_id=agent_id,
            module_id=module_id,
            status="in_progress",
            started_at=datetime.now(),
        )
        
        self.sessions[session_id] = session
        return session
    
    def _has_completed_module(self, agent_id: str, module_id: str) -> bool:
        """Check if an agent has completed a module."""
        for session in self.sessions.values():
            if (session.agent_id == agent_id and 
                session.module_id == module_id and 
                session.status == "completed"):
                return True
        return False
    
    async def submit_exercise_answer(
        self, 
        session_id: str, 
        exercise_id: str, 
        answer: str
    ) -> Dict[str, Any]:
        """
        Submit an answer for an exercise.
        
        提交練習答案
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.sessions[session_id]
        module = self.modules[session.module_id]
        
        # Find the exercise
        exercise = None
        for ex in module.exercises:
            if ex["id"] == exercise_id:
                exercise = ex
                break
        
        if not exercise:
            raise ValueError(f"Exercise not found: {exercise_id}")
        
        # Evaluate the answer
        result = self._evaluate_answer(answer, exercise)
        
        session.exercise_results.append({
            "exercise_id": exercise_id,
            "answer": answer,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Update progress
        total_exercises = len(module.exercises)
        completed_exercises = len(session.exercise_results)
        session.progress_percentage = (completed_exercises / total_exercises) * 100
        session.current_exercise = completed_exercises
        
        return result
    
    def _evaluate_answer(self, answer: str, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an exercise answer."""
        expected = exercise.get("expected_answer", "")
        exercise_type = exercise.get("type", "")
        
        # Simple evaluation (in real system, this would be more sophisticated)
        answer_lower = answer.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Check for key concepts
        key_concepts = self._extract_key_concepts(expected_lower)
        matched_concepts = sum(1 for concept in key_concepts if concept in answer_lower)
        
        score = matched_concepts / len(key_concepts) if key_concepts else 0.0
        is_correct = score >= 0.7
        
        feedback = []
        if is_correct:
            feedback.append("答案正確！展示了對概念的良好理解。")
        else:
            feedback.append("答案需要改進。")
            for concept in key_concepts:
                if concept not in answer_lower:
                    feedback.append(f"建議包含：{concept}")
        
        return {
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "hints": exercise.get("hints", []) if not is_correct else [],
        }
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from expected answer."""
        # Simple keyword extraction
        keywords = [
            "index", "索引", "join", "eager", "loading", "預加載",
            "transaction", "事務", "bcrypt", "hash", "哈希",
            "parameterized", "參數化", "n+1",
        ]
        return [k for k in keywords if k in text]
    
    def complete_session(self, session_id: str) -> SkillAssessment:
        """
        Complete a training session and assess skill level.
        
        完成訓練課程並評估技能等級
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.sessions[session_id]
        module = self.modules[session.module_id]
        
        # Calculate overall score
        total_score = 0.0
        for result in session.exercise_results:
            total_score += result["result"]["score"]
        
        avg_score = total_score / len(session.exercise_results) if session.exercise_results else 0.0
        session.assessment_score = avg_score
        
        # Determine if passed
        if avg_score >= module.passing_score:
            session.status = "completed"
            # Update agent skill level
            skill_id = module.skill_id
            if session.agent_id not in self.agent_skills:
                self.agent_skills[session.agent_id] = {}
            self.agent_skills[session.agent_id][skill_id] = module.target_level
        else:
            session.status = "failed"
        
        session.completed_at = datetime.now()
        
        # Create assessment
        assessment = SkillAssessment(
            id=f"assess_{uuid.uuid4().hex[:8]}",
            agent_id=session.agent_id,
            skill_id=module.skill_id,
            assessed_level=module.target_level if session.status == "completed" else SkillLevel.NOVICE,
            score=avg_score,
            confidence=0.8 if len(session.exercise_results) >= 3 else 0.5,
            evidence=[f"完成練習 {len(session.exercise_results)} 個"],
            strengths=[],
            areas_for_improvement=self._identify_improvement_areas(session),
        )
        
        # Store assessment
        if session.agent_id not in self.assessments:
            self.assessments[session.agent_id] = []
        self.assessments[session.agent_id].append(assessment)
        
        return assessment
    
    def _identify_improvement_areas(self, session: TrainingSession) -> List[str]:
        """Identify areas needing improvement based on session results."""
        areas = []
        for result in session.exercise_results:
            if not result["result"]["is_correct"]:
                areas.extend(result["result"]["feedback"][1:])  # Skip the first "needs improvement" message
        return areas[:5]  # Limit to top 5
    
    def get_agent_skill_level(self, agent_id: str, skill_id: str) -> SkillLevel:
        """Get an agent's current skill level."""
        if agent_id in self.agent_skills:
            return self.agent_skills[agent_id].get(skill_id, SkillLevel.NOVICE)
        return SkillLevel.NOVICE
    
    def get_recommended_modules(self, agent_id: str, skill_id: str) -> List[TrainingModule]:
        """Get recommended training modules for an agent."""
        current_level = self.get_agent_skill_level(agent_id, skill_id)
        
        # Find modules at or above current level
        recommended = []
        for module in self.modules.values():
            if module.skill_id == skill_id:
                # Check if module is appropriate for current level
                level_order = list(SkillLevel)
                current_idx = level_order.index(current_level)
                module_idx = level_order.index(module.target_level)
                
                if module_idx == current_idx + 1:  # Next level
                    recommended.append(module)
        
        return recommended
    
    def get_learning_path_progress(self, agent_id: str, path_id: str) -> Dict[str, Any]:
        """Get an agent's progress on a learning path."""
        if path_id not in self.learning_paths:
            raise ValueError(f"Learning path not found: {path_id}")
        
        path = self.learning_paths[path_id]
        
        completed_modules = []
        for module_id in path.modules:
            if self._has_completed_module(agent_id, module_id):
                completed_modules.append(module_id)
        
        progress = len(completed_modules) / len(path.modules) * 100 if path.modules else 0
        
        return {
            "path_id": path_id,
            "path_name": path.name,
            "total_modules": len(path.modules),
            "completed_modules": len(completed_modules),
            "progress_percentage": progress,
            "next_module": self._get_next_module(agent_id, path),
            "milestones_achieved": self._get_achieved_milestones(agent_id, path),
        }
    
    def _get_next_module(self, agent_id: str, path: LearningPath) -> Optional[str]:
        """Get the next module to complete in a path."""
        for module_id in path.modules:
            if not self._has_completed_module(agent_id, module_id):
                return module_id
        return None
    
    def _get_achieved_milestones(self, agent_id: str, path: LearningPath) -> List[str]:
        """Get milestones achieved by an agent."""
        achieved = []
        for milestone in path.milestones:
            requirements = milestone.get("requirements", [])
            if all(self._has_completed_module(agent_id, req) for req in requirements):
                achieved.append(milestone["name"])
        return achieved
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill definition."""
        return self.skills.get(skill_id)
    
    def get_module(self, module_id: str) -> Optional[TrainingModule]:
        """Get a training module."""
        return self.modules.get(module_id)
    
    def get_learning_path(self, path_id: str) -> Optional[LearningPath]:
        """Get a learning path."""
        return self.learning_paths.get(path_id)
    
    def get_stats(self) -> Dict[str, int]:
        """Get training system statistics."""
        return {
            "skills": len(self.skills),
            "modules": len(self.modules),
            "learning_paths": len(self.learning_paths),
            "total_sessions": len(self.sessions),
            "active_agents": len(self.agent_skills),
        }
