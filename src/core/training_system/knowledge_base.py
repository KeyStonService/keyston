"""
Knowledge Base System (知識庫系統)

Provides comprehensive domain knowledge for AI agents including:
- Domain-specific concepts and definitions
- Best practices and anti-patterns
- Technical references and examples

參考：AI 知識庫提供全面、最新的資源 [2]
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import uuid


class KnowledgeCategory(Enum):
    """Knowledge categories for organization."""
    DATABASE = "database"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    DEPLOYMENT = "deployment"
    PERFORMANCE = "performance"
    TESTING = "testing"
    CODE_QUALITY = "code_quality"
    API_DESIGN = "api_design"
    DATA_MODELING = "data_modeling"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    DEVOPS = "devops"


@dataclass
class ConceptDefinition:
    """
    Defines a technical concept with comprehensive details.
    
    概念定義：技術概念的完整定義
    """
    id: str
    name: str
    category: KnowledgeCategory
    definition: str
    description: str
    
    # Detailed information
    key_points: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    
    # Usage guidance
    when_to_use: List[str] = field(default_factory=list)
    when_not_to_use: List[str] = field(default_factory=list)
    
    # Examples
    code_examples: List[Dict[str, str]] = field(default_factory=list)
    real_world_examples: List[str] = field(default_factory=list)
    
    # Metadata
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced, expert
    tags: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class BestPractice:
    """
    Defines a best practice with reasoning and examples.
    
    最佳實踐：為什麼這樣做是正確的
    """
    id: str
    name: str
    category: KnowledgeCategory
    
    # Core content
    principle: str
    rationale: str
    benefits: List[str]
    
    # Implementation
    implementation_steps: List[str] = field(default_factory=list)
    code_example_correct: str = ""
    code_example_incorrect: str = ""
    
    # Context
    applicable_scenarios: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    
    # Impact
    impact_areas: List[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high, critical
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_practices: List[str] = field(default_factory=list)


@dataclass
class AntiPattern:
    """
    Defines an anti-pattern to avoid with alternatives.
    
    反模式：應該避免的做法以及原因
    """
    id: str
    name: str
    category: KnowledgeCategory
    
    # Core content
    description: str
    why_its_bad: str
    symptoms: List[str]
    consequences: List[str]
    
    # Examples
    bad_code_example: str = ""
    good_code_example: str = ""
    
    # Solution
    solution: str = ""
    alternative_approaches: List[str] = field(default_factory=list)
    refactoring_steps: List[str] = field(default_factory=list)
    
    # Detection
    detection_patterns: List[str] = field(default_factory=list)
    common_causes: List[str] = field(default_factory=list)
    
    # Metadata
    severity: str = "medium"  # low, medium, high, critical
    tags: List[str] = field(default_factory=list)


@dataclass
class DomainKnowledge:
    """
    Complete domain knowledge collection.
    
    領域知識：特定技術領域的完整知識集合
    """
    domain: KnowledgeCategory
    name: str
    description: str
    
    # Knowledge content
    concepts: Dict[str, ConceptDefinition] = field(default_factory=dict)
    best_practices: Dict[str, BestPractice] = field(default_factory=dict)
    anti_patterns: Dict[str, AntiPattern] = field(default_factory=dict)
    
    # Quick references
    terminology: Dict[str, str] = field(default_factory=dict)
    common_mistakes: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    
    # Learning path
    prerequisites: List[str] = field(default_factory=list)
    learning_order: List[str] = field(default_factory=list)


class KnowledgeBase:
    """
    Comprehensive AI Knowledge Base System.
    
    AI 知識庫：所有 AI 智能體的知識來源
    
    核心功能：
    1. 領域知識管理 - Domain knowledge management
    2. 概念查詢 - Concept lookup
    3. 最佳實踐推薦 - Best practice recommendations
    4. 反模式檢測 - Anti-pattern detection
    5. 知識關聯分析 - Knowledge relationship analysis
    """
    
    def __init__(self):
        self.domains: Dict[KnowledgeCategory, DomainKnowledge] = {}
        self.concepts: Dict[str, ConceptDefinition] = {}
        self.best_practices: Dict[str, BestPractice] = {}
        self.anti_patterns: Dict[str, AntiPattern] = {}
        self._concept_index: Dict[str, Set[str]] = {}  # tag -> concept_ids
        
        # Initialize with built-in knowledge
        self._initialize_database_knowledge()
        self._initialize_security_knowledge()
        self._initialize_architecture_knowledge()
        self._initialize_performance_knowledge()
    
    def _initialize_database_knowledge(self) -> None:
        """Initialize database domain knowledge."""
        domain = DomainKnowledge(
            domain=KnowledgeCategory.DATABASE,
            name="Database Knowledge",
            description="數據庫設計、優化和最佳實踐的完整知識",
            terminology={
                "index": "索引是提高數據庫查詢性能的數據結構",
                "normalization": "將數據組織成多個相關表以減少冗餘",
                "denormalization": "有意增加冗餘以提高查詢性能",
                "transaction": "一組必須完全成功或完全失敗的操作",
                "ACID": "原子性、一致性、隔離性、持久性",
                "N+1 query": "由於循環中的單獨查詢導致的性能問題",
            },
            common_mistakes=[
                "在循環中執行數據庫查詢（N+1 問題）",
                "沒有為常用查詢字段建立索引",
                "過度使用 SELECT *",
                "忽略事務處理",
                "沒有考慮數據一致性",
            ],
            tips=[
                "總是使用參數化查詢防止 SQL 注入",
                "監控慢查詢日誌",
                "為外鍵建立索引",
                "考慮使用連接池",
                "定期分析和優化查詢",
            ]
        )
        
        # Add indexing concept
        indexing_concept = ConceptDefinition(
            id="db_indexing",
            name="Database Indexing",
            category=KnowledgeCategory.DATABASE,
            definition="索引是提高數據庫查詢性能的數據結構",
            description="索引類似於書籍的目錄，允許快速查找特定數據而無需掃描整個表",
            key_points=[
                "B-Tree 索引最適合範圍查詢",
                "Hash 索引最適合等值查詢",
                "覆蓋索引可以避免回表查詢",
                "索引會增加寫入開銷",
            ],
            when_to_use=[
                "經常用於 WHERE 子句的列",
                "用於 JOIN 的列",
                "用於 ORDER BY 的列",
            ],
            when_not_to_use=[
                "很少查詢的列",
                "經常更新的列",
                "數據分佈非常不均勻的列",
            ],
            code_examples=[
                {
                    "title": "創建 B-Tree 索引",
                    "language": "sql",
                    "code": "CREATE INDEX idx_users_email ON users(email);",
                    "explanation": "為 email 列創建索引以加速查詢",
                },
                {
                    "title": "複合索引",
                    "language": "sql",
                    "code": "CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);",
                    "explanation": "複合索引遵循最左前綴原則",
                },
            ],
            tags=["indexing", "performance", "optimization"],
        )
        domain.concepts["indexing"] = indexing_concept
        self.concepts["db_indexing"] = indexing_concept
        
        # Add N+1 query anti-pattern
        n_plus_one = AntiPattern(
            id="n_plus_one_query",
            name="N+1 Query Problem",
            category=KnowledgeCategory.DATABASE,
            description="在循環中執行數據庫查詢，導致 N+1 次查詢",
            why_its_bad="每次循環迭代都會發起一次數據庫請求，嚴重影響性能",
            symptoms=[
                "響應時間隨數據量線性增長",
                "數據庫連接池耗盡",
                "高數據庫 CPU 使用率",
            ],
            consequences=[
                "應用程序變慢",
                "數據庫負載過高",
                "用戶體驗差",
            ],
            bad_code_example="""
# ❌ N+1 查詢問題
users = db.users.find_many()
for user in users:
    orders = db.orders.find_many(where={'user_id': user.id})  # 每個用戶一次查詢！
""",
            good_code_example="""
# ✅ 使用 JOIN 或預加載
users = db.users.find_many(include={'orders': True})  # 一次查詢獲取所有數據
# 或使用 JOIN
SELECT u.*, o.* FROM users u LEFT JOIN orders o ON u.id = o.user_id
""",
            solution="使用 JOIN、預加載（eager loading）或批量查詢",
            alternative_approaches=[
                "使用 ORM 的 include/eager loading 功能",
                "使用 JOIN 查詢",
                "使用 IN 子句批量查詢",
                "使用 DataLoader 模式",
            ],
            detection_patterns=[
                "循環內的數據庫調用",
                "響應時間與數據量成正比",
            ],
            severity="high",
            tags=["performance", "database", "query"],
        )
        domain.anti_patterns["n_plus_one"] = n_plus_one
        self.anti_patterns["n_plus_one_query"] = n_plus_one
        
        # Add transaction best practice
        transaction_practice = BestPractice(
            id="use_transactions",
            name="Always Use Transactions for Related Operations",
            category=KnowledgeCategory.DATABASE,
            principle="相關的數據庫操作應該在事務中執行",
            rationale="事務確保數據一致性，防止部分更新導致的數據損壞",
            benefits=[
                "數據一致性保證",
                "失敗時自動回滾",
                "並發控制",
            ],
            implementation_steps=[
                "開始事務",
                "執行所有相關操作",
                "如果成功，提交事務",
                "如果失敗，回滾事務",
            ],
            code_example_correct="""
# ✅ 使用事務
async with db.transaction():
    user = await db.users.create(data={'email': email})
    await db.accounts.create(data={'user_id': user.id, 'balance': 0})
    await db.audit_log.create(data={'action': 'user_created', 'user_id': user.id})
""",
            code_example_incorrect="""
# ❌ 沒有使用事務
user = await db.users.create(data={'email': email})
await db.accounts.create(data={'user_id': user.id, 'balance': 0})  # 如果失敗，用戶已創建但沒有賬戶！
await db.audit_log.create(data={'action': 'user_created', 'user_id': user.id})
""",
            applicable_scenarios=[
                "創建相關聯的多條記錄",
                "轉賬等金融操作",
                "任何需要原子性的操作",
            ],
            priority="critical",
            tags=["transaction", "consistency", "reliability"],
        )
        domain.best_practices["use_transactions"] = transaction_practice
        self.best_practices["use_transactions"] = transaction_practice
        
        self.domains[KnowledgeCategory.DATABASE] = domain
    
    def _initialize_security_knowledge(self) -> None:
        """Initialize security domain knowledge."""
        domain = DomainKnowledge(
            domain=KnowledgeCategory.SECURITY,
            name="Security Knowledge",
            description="應用程序安全、認證和數據保護的最佳實踐",
            terminology={
                "authentication": "驗證用戶身份的過程",
                "authorization": "確定用戶權限的過程",
                "encryption": "將數據轉換為不可讀格式以保護隱私",
                "hashing": "單向轉換，用於密碼存儲",
                "SQL injection": "通過惡意 SQL 代碼攻擊數據庫",
                "XSS": "跨站腳本攻擊",
                "CSRF": "跨站請求偽造",
            },
            common_mistakes=[
                "明文存儲密碼",
                "沒有使用參數化查詢",
                "沒有驗證用戶輸入",
                "硬編碼敏感信息",
                "使用弱加密算法",
            ],
            tips=[
                "永遠不要信任用戶輸入",
                "使用 bcrypt 或 argon2 哈希密碼",
                "實施速率限制",
                "定期更新依賴",
                "使用 HTTPS",
            ]
        )
        
        # Password handling best practice
        password_practice = BestPractice(
            id="secure_password_handling",
            name="Secure Password Handling",
            category=KnowledgeCategory.SECURITY,
            principle="密碼必須使用強哈希算法存儲，永不明文",
            rationale="密碼洩露是最常見的安全事件之一，正確的哈希可以保護用戶",
            benefits=[
                "即使數據庫洩露，密碼也是安全的",
                "防止彩虹表攻擊",
                "符合安全標準和法規",
            ],
            implementation_steps=[
                "使用 bcrypt、argon2 或 scrypt",
                "設置適當的工作因子/成本",
                "自動加鹽（這些算法會自動處理）",
                "驗證時使用時間常數比較",
            ],
            code_example_correct="""
# ✅ 安全的密碼處理
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
""",
            code_example_incorrect="""
# ❌ 不安全的密碼處理
def save_user(email: str, password: str):
    # 明文存儲密碼！
    db.users.create({'email': email, 'password': password})
    
# ❌ 使用弱哈希
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()  # MD5 太弱了！
""",
            priority="critical",
            tags=["password", "authentication", "hashing"],
        )
        domain.best_practices["secure_password"] = password_practice
        self.best_practices["secure_password_handling"] = password_practice
        
        # SQL injection anti-pattern
        sql_injection = AntiPattern(
            id="sql_injection_vulnerability",
            name="SQL Injection Vulnerability",
            category=KnowledgeCategory.SECURITY,
            description="直接將用戶輸入拼接到 SQL 查詢中",
            why_its_bad="攻擊者可以執行任意 SQL 命令，竊取或破壞數據",
            symptoms=[
                "字符串拼接構建 SQL",
                "沒有輸入驗證",
                "使用 format() 或 f-string 構建查詢",
            ],
            consequences=[
                "數據洩露",
                "數據被刪除或修改",
                "服務器被入侵",
            ],
            bad_code_example="""
# ❌ SQL 注入漏洞
def get_user(email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)
# 攻擊者輸入: ' OR '1'='1
""",
            good_code_example="""
# ✅ 使用參數化查詢
def get_user(email: str):
    query = "SELECT * FROM users WHERE email = %s"
    return db.execute(query, (email,))
# 或使用 ORM
user = db.users.find_first(where={'email': email})
""",
            solution="永遠使用參數化查詢或 ORM",
            severity="critical",
            tags=["security", "sql", "injection"],
        )
        domain.anti_patterns["sql_injection"] = sql_injection
        self.anti_patterns["sql_injection_vulnerability"] = sql_injection
        
        self.domains[KnowledgeCategory.SECURITY] = domain
    
    def _initialize_architecture_knowledge(self) -> None:
        """Initialize architecture domain knowledge."""
        domain = DomainKnowledge(
            domain=KnowledgeCategory.ARCHITECTURE,
            name="Architecture Knowledge",
            description="系統架構設計、模式和原則",
            terminology={
                "microservices": "將應用分解為小型獨立服務",
                "monolith": "單一部署單元的應用",
                "API gateway": "管理 API 流量的入口點",
                "service mesh": "管理服務間通信的基礎設施層",
                "event-driven": "基於事件的異步架構",
                "CQRS": "命令查詢責任分離",
            },
            common_mistakes=[
                "過早微服務化",
                "緊耦合的服務",
                "沒有定義清晰的邊界",
                "忽略非功能需求",
            ],
            tips=[
                "從簡單開始，按需演進",
                "明確服務邊界",
                "設計時考慮失敗",
                "監控和可觀測性優先",
            ]
        )
        
        self.domains[KnowledgeCategory.ARCHITECTURE] = domain
    
    def _initialize_performance_knowledge(self) -> None:
        """Initialize performance domain knowledge."""
        domain = DomainKnowledge(
            domain=KnowledgeCategory.PERFORMANCE,
            name="Performance Knowledge",
            description="性能優化、緩存和擴展策略",
            terminology={
                "caching": "存儲計算結果以避免重複計算",
                "CDN": "內容分發網絡，加速靜態資源",
                "load balancing": "在多個服務器間分配流量",
                "connection pooling": "重用數據庫連接",
                "lazy loading": "延遲加載數據直到需要",
            },
            common_mistakes=[
                "過早優化",
                "沒有測量就優化",
                "忽略緩存失效",
                "過度使用同步操作",
            ],
            tips=[
                "測量優先，優化其次",
                "關注關鍵路徑",
                "使用適當的緩存策略",
                "考慮異步處理",
            ]
        )
        
        self.domains[KnowledgeCategory.PERFORMANCE] = domain
    
    # Query Methods
    
    def get_concept(self, concept_id: str) -> Optional[ConceptDefinition]:
        """Get a specific concept by ID."""
        return self.concepts.get(concept_id)
    
    def search_concepts(self, query: str, category: Optional[KnowledgeCategory] = None) -> List[ConceptDefinition]:
        """Search concepts by keyword."""
        query_lower = query.lower()
        results = []
        
        for concept in self.concepts.values():
            if category and concept.category != category:
                continue
            
            if (query_lower in concept.name.lower() or
                query_lower in concept.definition.lower() or
                any(query_lower in tag.lower() for tag in concept.tags)):
                results.append(concept)
        
        return results
    
    def get_best_practice(self, practice_id: str) -> Optional[BestPractice]:
        """Get a specific best practice by ID."""
        return self.best_practices.get(practice_id)
    
    def get_best_practices_for_category(self, category: KnowledgeCategory) -> List[BestPractice]:
        """Get all best practices for a category."""
        return [
            practice for practice in self.best_practices.values()
            if practice.category == category
        ]
    
    def get_anti_pattern(self, pattern_id: str) -> Optional[AntiPattern]:
        """Get a specific anti-pattern by ID."""
        return self.anti_patterns.get(pattern_id)
    
    def get_anti_patterns_for_category(self, category: KnowledgeCategory) -> List[AntiPattern]:
        """Get all anti-patterns for a category."""
        return [
            pattern for pattern in self.anti_patterns.values()
            if pattern.category == category
        ]
    
    def get_domain_knowledge(self, category: KnowledgeCategory) -> Optional[DomainKnowledge]:
        """Get complete domain knowledge."""
        return self.domains.get(category)
    
    def add_concept(self, concept: ConceptDefinition) -> None:
        """Add a new concept to the knowledge base."""
        self.concepts[concept.id] = concept
        
        # Update domain if exists
        if concept.category in self.domains:
            self.domains[concept.category].concepts[concept.id] = concept
        
        # Update tag index
        for tag in concept.tags:
            if tag not in self._concept_index:
                self._concept_index[tag] = set()
            self._concept_index[tag].add(concept.id)
    
    def add_best_practice(self, practice: BestPractice) -> None:
        """Add a new best practice."""
        self.best_practices[practice.id] = practice
        
        if practice.category in self.domains:
            self.domains[practice.category].best_practices[practice.id] = practice
    
    def add_anti_pattern(self, pattern: AntiPattern) -> None:
        """Add a new anti-pattern."""
        self.anti_patterns[pattern.id] = pattern
        
        if pattern.category in self.domains:
            self.domains[pattern.category].anti_patterns[pattern.id] = pattern
    
    def get_relevant_knowledge(self, context: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Get relevant knowledge based on context.
        
        根據上下文獲取相關知識
        """
        context_lower = context.lower()
        
        relevant = {
            "concepts": [],
            "best_practices": [],
            "anti_patterns": [],
            "tips": [],
        }
        
        # Find relevant concepts
        for concept in self.concepts.values():
            score = self._calculate_relevance(context_lower, concept.name, concept.definition, concept.tags)
            if score > 0:
                relevant["concepts"].append((concept, score))
        
        relevant["concepts"] = [
            c for c, _ in sorted(relevant["concepts"], key=lambda x: x[1], reverse=True)[:max_results]
        ]
        
        # Find relevant best practices
        for practice in self.best_practices.values():
            score = self._calculate_relevance(context_lower, practice.name, practice.principle, practice.tags)
            if score > 0:
                relevant["best_practices"].append((practice, score))
        
        relevant["best_practices"] = [
            p for p, _ in sorted(relevant["best_practices"], key=lambda x: x[1], reverse=True)[:max_results]
        ]
        
        # Find relevant anti-patterns
        for pattern in self.anti_patterns.values():
            score = self._calculate_relevance(context_lower, pattern.name, pattern.description, pattern.tags)
            if score > 0:
                relevant["anti_patterns"].append((pattern, score))
        
        relevant["anti_patterns"] = [
            p for p, _ in sorted(relevant["anti_patterns"], key=lambda x: x[1], reverse=True)[:max_results]
        ]
        
        # Collect tips from relevant domains
        for domain in self.domains.values():
            for tip in domain.tips:
                if any(word in tip.lower() for word in context_lower.split()):
                    relevant["tips"].append(tip)
        
        return relevant
    
    def _calculate_relevance(self, context: str, name: str, description: str, tags: List[str]) -> float:
        """Calculate relevance score for knowledge item."""
        score = 0.0
        context_words = set(context.split())
        
        # Name matching (high weight)
        name_lower = name.lower()
        for word in context_words:
            if word in name_lower:
                score += 3.0
        
        # Description matching (medium weight)
        description_lower = description.lower()
        for word in context_words:
            if word in description_lower:
                score += 1.0
        
        # Tag matching (high weight)
        tags_lower = [t.lower() for t in tags]
        for word in context_words:
            if word in tags_lower:
                score += 2.0
        
        return score
    
    def get_stats(self) -> Dict[str, int]:
        """Get knowledge base statistics."""
        return {
            "domains": len(self.domains),
            "concepts": len(self.concepts),
            "best_practices": len(self.best_practices),
            "anti_patterns": len(self.anti_patterns),
        }
