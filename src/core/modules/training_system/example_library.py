"""
Example Library (示例庫)

Provides practical examples for AI learning including:
- Code examples with explanations
- Scenario-based learning examples
- Decision-making examples

參考：15 個實際 AI 代理示例展示如何自動化複雜任務 [4]
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExampleCategory(Enum):
    """Example categories for organization."""
    CODE_PATTERN = "code_pattern"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    REFACTORING = "refactoring"
    DECISION = "decision"
    WORKFLOW = "workflow"


@dataclass
class CodeExample:
    """
    A code example with before/after comparison.
    
    代碼示例：展示正確和錯誤的做法
    """
    id: str
    name: str
    category: ExampleCategory
    description: str

    # Code samples
    language: str  # python, typescript, sql, etc.
    bad_code: str = ""
    good_code: str = ""

    # Explanation
    why_bad: list[str] = field(default_factory=list)
    why_good: list[str] = field(default_factory=list)

    # Context
    scenario: str = ""
    common_mistakes: list[str] = field(default_factory=list)

    # Learning points
    key_takeaways: list[str] = field(default_factory=list)

    # Related
    related_concepts: list[str] = field(default_factory=list)
    related_practices: list[str] = field(default_factory=list)

    # Metadata
    difficulty: str = "intermediate"
    tags: list[str] = field(default_factory=list)


@dataclass
class ScenarioExample:
    """
    A scenario-based learning example.
    
    場景示例：在特定情境下的學習案例
    """
    id: str
    name: str
    category: ExampleCategory

    # Scenario description
    context: str
    problem_statement: str
    constraints: list[str] = field(default_factory=list)

    # Analysis process
    analysis_steps: list[str] = field(default_factory=list)
    considerations: list[str] = field(default_factory=list)

    # Solution
    recommended_solution: str = ""
    alternative_solutions: list[str] = field(default_factory=list)

    # Implementation
    implementation_steps: list[str] = field(default_factory=list)
    code_snippets: list[dict[str, str]] = field(default_factory=list)

    # Lessons
    lessons_learned: list[str] = field(default_factory=list)
    pitfalls_to_avoid: list[str] = field(default_factory=list)

    # Metadata
    difficulty: str = "intermediate"
    estimated_time_minutes: int = 30
    tags: list[str] = field(default_factory=list)


@dataclass
class DecisionExample:
    """
    A decision-making example for AI learning.
    
    決策示例：展示如何在複雜情況下做出決策
    """
    id: str
    name: str
    category: ExampleCategory

    # Decision context
    situation: str
    stakeholders: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    # Options
    options: list[dict[str, Any]] = field(default_factory=list)
    # Each option: {name, description, pros, cons, risks, costs}

    # Decision process
    evaluation_criteria: list[str] = field(default_factory=list)
    analysis_process: str = ""

    # Decision
    recommended_decision: str = ""
    rationale: str = ""

    # Impact
    expected_outcomes: list[str] = field(default_factory=list)
    monitoring_points: list[str] = field(default_factory=list)

    # Lessons
    decision_principles: list[str] = field(default_factory=list)

    # Metadata
    difficulty: str = "advanced"
    tags: list[str] = field(default_factory=list)


class ExampleLibrary:
    """
    Comprehensive Example Library for AI Learning.
    
    AI 示例庫：從示例中學習
    
    核心功能：
    1. 代碼示例管理 - Code example management
    2. 場景示例管理 - Scenario example management
    3. 決策示例管理 - Decision example management
    4. 示例搜索與推薦 - Example search and recommendations
    
    參考：示例驅動學習展示如何自動化複雜任務 [4]
    """

    def __init__(self):
        self.code_examples: dict[str, CodeExample] = {}
        self.scenario_examples: dict[str, ScenarioExample] = {}
        self.decision_examples: dict[str, DecisionExample] = {}

        # Initialize with built-in examples
        self._initialize_code_examples()
        self._initialize_scenario_examples()
        self._initialize_decision_examples()

    def _initialize_code_examples(self) -> None:
        """Initialize built-in code examples."""

        # N+1 Query Problem Example
        n_plus_one = CodeExample(
            id="ex_n_plus_one",
            name="N+1 Query Problem Solution",
            category=ExampleCategory.OPTIMIZATION,
            description="展示如何識別和解決 N+1 查詢問題",
            language="python",
            bad_code="""
# ❌ N+1 查詢問題
async def get_users_with_orders():
    users = await db.users.find_many()
    
    for user in users:
        # 每個用戶執行一次額外查詢
        user.orders = await db.orders.find_many(
            where={'user_id': user.id}
        )
    
    return users

# 如果有 100 個用戶，這將執行 101 次查詢！
# 1 次獲取所有用戶 + 100 次獲取每個用戶的訂單
""",
            good_code="""
# ✅ 使用預加載解決 N+1 問題
async def get_users_with_orders():
    # 一次查詢獲取所有數據
    users = await db.users.find_many(
        include={
            'orders': True  # 預加載訂單
        }
    )
    return users

# 或者使用 JOIN 查詢
async def get_users_with_orders_join():
    query = '''
    SELECT u.*, o.*
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    '''
    return await db.execute(query)

# 或者使用批量查詢
async def get_users_with_orders_batch():
    users = await db.users.find_many()
    user_ids = [u.id for u in users]
    
    # 一次查詢獲取所有訂單
    all_orders = await db.orders.find_many(
        where={'user_id': {'in': user_ids}}
    )
    
    # 在應用層組合數據
    orders_by_user = {}
    for order in all_orders:
        orders_by_user.setdefault(order.user_id, []).append(order)
    
    for user in users:
        user.orders = orders_by_user.get(user.id, [])
    
    return users
""",
            why_bad=[
                "查詢次數與數據量成正比",
                "數據庫連接被頻繁打開和關閉",
                "網絡往返時間累加",
                "數據庫負載增加",
            ],
            why_good=[
                "固定的查詢次數",
                "減少數據庫連接開銷",
                "更好的網絡效率",
                "可預測的性能",
            ],
            scenario="在顯示用戶列表及其訂單時，需要優化數據獲取",
            common_mistakes=[
                "在循環中調用數據庫",
                "沒有使用 ORM 的預加載功能",
                "忽略 EXPLAIN 分析結果",
            ],
            key_takeaways=[
                "總是使用預加載獲取關聯數據",
                "監控應用的 SQL 查詢日誌",
                "使用 EXPLAIN 分析查詢性能",
                "考慮使用 DataLoader 模式",
            ],
            related_concepts=["indexing", "eager_loading", "query_optimization"],
            difficulty="intermediate",
            tags=["performance", "database", "n+1", "optimization"],
        )
        self.code_examples[n_plus_one.id] = n_plus_one

        # SQL Injection Prevention Example
        sql_injection = CodeExample(
            id="ex_sql_injection",
            name="SQL Injection Prevention",
            category=ExampleCategory.SECURITY,
            description="展示如何防止 SQL 注入攻擊",
            language="python",
            bad_code="""
# ❌ SQL 注入漏洞
def get_user_by_email(email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)

# 攻擊者輸入: ' OR '1'='1' --
# 結果查詢: SELECT * FROM users WHERE email = '' OR '1'='1' --'
# 這將返回所有用戶！

def login(username: str, password: str):
    query = f\"\"\"
    SELECT * FROM users
    WHERE username = '{username}'
    AND password = '{password}'
    \"\"\"
    return db.execute(query)

# 攻擊者可以繞過登錄：
# username: admin' --
# password: anything
# 結果: SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything'
""",
            good_code="""
# ✅ 使用參數化查詢
def get_user_by_email(email: str):
    query = "SELECT * FROM users WHERE email = %s"
    return db.execute(query, (email,))

# ✅ 使用 ORM（推薦）
def get_user_by_email_orm(email: str):
    return db.users.find_first(where={'email': email})

# ✅ 安全的登錄實現
import bcrypt

def secure_login(username: str, password: str):
    # 使用參數化查詢
    user = db.users.find_first(where={'username': username})
    
    if user is None:
        return None
    
    # 密碼驗證使用 bcrypt
    if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return user
    
    return None

# ✅ 使用準備語句
def get_users_by_status(status: str):
    # 使用佔位符
    query = "SELECT * FROM users WHERE status = ?"
    return db.execute(query, [status])
""",
            why_bad=[
                "用戶輸入直接拼接到 SQL 中",
                "攻擊者可以執行任意 SQL",
                "可能洩露、修改或刪除數據",
                "可能獲得數據庫管理員權限",
            ],
            why_good=[
                "參數化查詢將數據與代碼分離",
                "數據庫驅動程序處理轉義",
                "防止惡意輸入被執行",
                "符合安全最佳實踐",
            ],
            scenario="實現用戶認證和數據查詢功能",
            key_takeaways=[
                "永遠使用參數化查詢",
                "使用 ORM 自動處理參數化",
                "永遠不要相信用戶輸入",
                "密碼應該哈希存儲，不是明文比較",
            ],
            difficulty="beginner",
            tags=["security", "sql", "injection", "authentication"],
        )
        self.code_examples[sql_injection.id] = sql_injection

        # Password Hashing Example
        password_hashing = CodeExample(
            id="ex_password_hashing",
            name="Secure Password Handling",
            category=ExampleCategory.SECURITY,
            description="展示如何安全地處理和存儲密碼",
            language="python",
            bad_code="""
# ❌ 不安全的密碼處理

# 問題 1：明文存儲
def create_user_insecure(email: str, password: str):
    db.users.create({
        'email': email,
        'password': password  # 💀 明文存儲！
    })

# 問題 2：使用弱哈希
import hashlib

def hash_password_weak(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # MD5 太弱了！

# 問題 3：沒有加鹽
def hash_password_no_salt(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
    # 相同密碼產生相同哈希，容易受彩虹表攻擊

# 問題 4：固定鹽
SALT = "my_secret_salt"
def hash_password_fixed_salt(password: str) -> str:
    return hashlib.sha256((password + SALT).encode()).hexdigest()
    # 固定鹽被發現後所有密碼都不安全
""",
            good_code="""
# ✅ 安全的密碼處理

import bcrypt
from argon2 import PasswordHasher
import secrets

# 方案 1：使用 bcrypt（推薦）
def hash_password_bcrypt(password: str) -> str:
    # bcrypt 自動生成隨機鹽並包含在哈希中
    # rounds=12 提供良好的安全性和性能平衡
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password_bcrypt(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# 方案 2：使用 Argon2（更現代，推薦用於新項目）
ph = PasswordHasher()

def hash_password_argon2(password: str) -> str:
    return ph.hash(password)

def verify_password_argon2(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except:
        return False

# 完整的用戶創建流程
class UserService:
    def __init__(self):
        self.ph = PasswordHasher()
    
    def create_user(self, email: str, password: str):
        # 1. 驗證密碼強度
        if not self._is_strong_password(password):
            raise ValueError("密碼不夠強")
        
        # 2. 哈希密碼
        password_hash = self.ph.hash(password)
        
        # 3. 創建用戶
        return db.users.create({
            'email': email,
            'password_hash': password_hash
        })
    
    def verify_login(self, email: str, password: str):
        user = db.users.find_first(where={'email': email})
        if user is None:
            return None
        
        try:
            if self.ph.verify(user.password_hash, password):
                return user
        except:
            pass
        
        return None
    
    def _is_strong_password(self, password: str) -> bool:
        # 至少 8 個字符，包含大小寫和數字
        return (
            len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password)
        )
""",
            why_bad=[
                "明文密碼洩露後用戶完全暴露",
                "弱哈希可以被快速破解",
                "沒有鹽容易受彩虹表攻擊",
                "固定鹽被發現後所有密碼不安全",
            ],
            why_good=[
                "強哈希算法（bcrypt/argon2）專為密碼設計",
                "每個密碼使用唯一的隨機鹽",
                "工作因子可調，抵抗硬件進步",
                "即使數據庫洩露，密碼仍然安全",
            ],
            key_takeaways=[
                "使用 bcrypt 或 argon2 哈希密碼",
                "永遠不要存儲明文密碼",
                "每個密碼使用唯一的隨機鹽",
                "驗證密碼強度",
            ],
            difficulty="intermediate",
            tags=["security", "password", "hashing", "bcrypt", "argon2"],
        )
        self.code_examples[password_hashing.id] = password_hashing

        # Transaction Usage Example
        transaction_example = CodeExample(
            id="ex_transaction",
            name="Database Transaction Usage",
            category=ExampleCategory.CODE_PATTERN,
            description="展示如何正確使用數據庫事務",
            language="python",
            bad_code="""
# ❌ 沒有使用事務

async def transfer_money(from_account: int, to_account: int, amount: float):
    # 從來源帳戶扣款
    await db.execute(
        "UPDATE accounts SET balance = balance - %s WHERE id = %s",
        (amount, from_account)
    )
    
    # ⚠️ 如果這裡發生錯誤，錢已經扣了但沒有轉入！
    
    # 轉入目標帳戶
    await db.execute(
        "UPDATE accounts SET balance = balance + %s WHERE id = %s",
        (amount, to_account)
    )

# 問題：如果在兩個操作之間發生錯誤或系統崩潰，
# 數據將處於不一致狀態！
""",
            good_code="""
# ✅ 使用事務確保一致性

async def transfer_money(from_account: int, to_account: int, amount: float):
    async with db.transaction() as tx:
        # 檢查餘額
        from_acc = await tx.accounts.find_first(where={'id': from_account})
        if from_acc.balance < amount:
            raise InsufficientFundsError("餘額不足")
        
        # 扣款
        await tx.accounts.update(
            where={'id': from_account},
            data={'balance': from_acc.balance - amount}
        )
        
        # 轉入
        to_acc = await tx.accounts.find_first(where={'id': to_account})
        await tx.accounts.update(
            where={'id': to_account},
            data={'balance': to_acc.balance + amount}
        )
        
        # 記錄交易
        await tx.transactions.create({
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount,
            'type': 'transfer'
        })
    
    # 事務結束後自動提交
    # 如果任何步驟失敗，所有更改都會回滾

# 使用 try-except 處理事務錯誤
async def safe_transfer(from_account: int, to_account: int, amount: float):
    try:
        async with db.transaction() as tx:
            # ... 執行轉賬操作
            pass
    except Exception as e:
        # 事務自動回滾
        logger.error(f"轉賬失敗: {e}")
        raise TransferFailedError(str(e))
""",
            why_bad=[
                "部分操作成功會導致數據不一致",
                "並發操作可能導致競態條件",
                "沒有錯誤恢復機制",
            ],
            why_good=[
                "ACID 特性保證數據一致性",
                "失敗時自動回滾所有更改",
                "隔離級別防止競態條件",
                "可預測的錯誤處理",
            ],
            scenario="實現金融交易或任何需要原子性操作的場景",
            key_takeaways=[
                "相關操作應該在同一個事務中",
                "使用 context manager 自動處理提交/回滾",
                "適當處理事務錯誤",
                "考慮事務隔離級別",
            ],
            difficulty="intermediate",
            tags=["database", "transaction", "consistency", "acid"],
        )
        self.code_examples[transaction_example.id] = transaction_example

    def _initialize_scenario_examples(self) -> None:
        """Initialize scenario-based examples."""

        # API Performance Optimization Scenario
        api_optimization = ScenarioExample(
            id="scenario_api_optimization",
            name="API Response Time Optimization",
            category=ExampleCategory.OPTIMIZATION,
            context="電商平台的商品列表 API 響應時間從原來的 200ms 增長到 2000ms",
            problem_statement="用戶抱怨頁面加載慢，需要優化商品列表 API 的性能",
            constraints=[
                "不能改變現有 API 格式",
                "數據必須實時準確",
                "需要在一週內完成",
            ],
            analysis_steps=[
                "1. 使用 APM 工具分析請求耗時分佈",
                "2. 檢查數據庫查詢日誌，找出慢查詢",
                "3. 使用 EXPLAIN 分析問題查詢",
                "4. 檢查是否存在 N+1 查詢問題",
                "5. 評估緩存策略",
            ],
            considerations=[
                "數據一致性 vs 性能",
                "實現複雜度 vs 效果",
                "短期修復 vs 長期架構改進",
            ],
            recommended_solution="實施多層優化策略：數據庫查詢優化 + 適當緩存 + 分頁",
            alternative_solutions=[
                "純緩存方案：Redis 緩存商品列表",
                "異步預計算：後台生成商品列表",
                "讀寫分離：使用只讀副本",
            ],
            implementation_steps=[
                "1. 為常用查詢字段添加複合索引",
                "2. 使用預加載解決 N+1 問題",
                "3. 實施遊標分頁替代 OFFSET",
                "4. 添加 Redis 緩存熱門商品",
                "5. 設置合理的緩存失效策略",
            ],
            code_snippets=[
                {
                    "title": "優化後的查詢",
                    "language": "python",
                    "code": """
async def get_products_optimized(cursor: str, limit: int = 20):
    # 使用遊標分頁
    products = await db.products.find_many(
        where={'id': {'gt': cursor}} if cursor else None,
        take=limit,
        include={
            'category': True,
            'images': {'take': 3},  # 只取前 3 張圖片
        },
        order_by={'id': 'asc'}
    )
    
    # 返回下一頁遊標
    next_cursor = products[-1].id if products else None
    return {'products': products, 'next_cursor': next_cursor}
""",
                },
            ],
            lessons_learned=[
                "性能問題需要數據支持，先測量再優化",
                "N+1 查詢是最常見的性能問題之一",
                "遊標分頁對大數據集更有效",
                "緩存需要仔細考慮失效策略",
            ],
            pitfalls_to_avoid=[
                "過早優化",
                "沒有測量就優化",
                "忽略緩存一致性",
                "一次性做太多改變",
            ],
            difficulty="intermediate",
            estimated_time_minutes=60,
            tags=["performance", "api", "optimization", "database"],
        )
        self.scenario_examples[api_optimization.id] = api_optimization

        # Security Incident Response Scenario
        security_incident = ScenarioExample(
            id="scenario_security_incident",
            name="Security Incident Response",
            category=ExampleCategory.SECURITY,
            context="安全團隊發現可疑的數據庫查詢活動，懷疑存在 SQL 注入攻擊",
            problem_statement="需要調查、修復漏洞並防止未來攻擊",
            constraints=[
                "必須盡快阻止攻擊",
                "需要保留證據用於調查",
                "不能中斷正常業務",
            ],
            analysis_steps=[
                "1. 隔離受影響的系統",
                "2. 收集和保存日誌證據",
                "3. 分析攻擊向量",
                "4. 識別受影響的數據",
                "5. 找出漏洞根源",
            ],
            recommended_solution="立即緩解 + 根本修復 + 長期改進",
            implementation_steps=[
                "1. 啟用 WAF 規則阻擋可疑請求",
                "2. 審計所有 SQL 查詢代碼",
                "3. 將所有查詢改為參數化",
                "4. 實施輸入驗證",
                "5. 添加安全監控警報",
            ],
            lessons_learned=[
                "永遠使用參數化查詢",
                "輸入驗證是第一道防線",
                "需要有事件響應計劃",
                "定期進行安全審計",
            ],
            difficulty="advanced",
            tags=["security", "incident", "sql_injection"],
        )
        self.scenario_examples[security_incident.id] = security_incident

    def _initialize_decision_examples(self) -> None:
        """Initialize decision-making examples."""

        # Microservices vs Monolith Decision
        architecture_decision = DecisionExample(
            id="decision_microservices",
            name="Microservices vs Monolith Architecture",
            category=ExampleCategory.ARCHITECTURE,
            situation="團隊正在規劃新項目，需要決定使用微服務還是單體架構",
            stakeholders=["開發團隊", "運維團隊", "產品經理", "管理層"],
            constraints=[
                "團隊規模 5 人",
                "預計用戶量初期較小",
                "需要快速上線",
                "預算有限",
            ],
            options=[
                {
                    "name": "單體架構",
                    "description": "傳統的單一部署單元架構",
                    "pros": [
                        "開發簡單",
                        "部署簡單",
                        "調試容易",
                        "低延遲（進程內調用）",
                    ],
                    "cons": [
                        "擴展性有限",
                        "技術棧固定",
                        "團隊擴展困難",
                    ],
                    "risks": ["技術債務累積", "未來重構成本"],
                    "costs": "低",
                },
                {
                    "name": "微服務架構",
                    "description": "分佈式的獨立服務架構",
                    "pros": [
                        "獨立擴展",
                        "技術多樣性",
                        "團隊自主",
                        "故障隔離",
                    ],
                    "cons": [
                        "複雜度高",
                        "運維困難",
                        "分佈式問題",
                        "網絡延遲",
                    ],
                    "risks": ["過度設計", "人員不足"],
                    "costs": "高",
                },
                {
                    "name": "模塊化單體",
                    "description": "內部模塊化但單一部署的架構",
                    "pros": [
                        "平衡複雜度和靈活性",
                        "未來可演進到微服務",
                        "開發和部署仍然簡單",
                    ],
                    "cons": [
                        "需要良好的模塊設計",
                        "仍然是單一部署單元",
                    ],
                    "risks": ["模塊邊界模糊"],
                    "costs": "中",
                },
            ],
            evaluation_criteria=[
                "團隊規模和經驗",
                "項目複雜度",
                "擴展需求",
                "上線時間壓力",
                "運維能力",
            ],
            analysis_process="""
1. 評估團隊能力：5 人團隊對微服務的運維經驗有限
2. 評估需求：初期用戶量小，不需要極端擴展性
3. 評估時間：需要快速上線，微服務會延長開發時間
4. 評估成本：預算有限，微服務需要更多基礎設施
5. 評估風險：微服務的複雜度風險高於單體的擴展風險
""",
            recommended_decision="模塊化單體架構",
            rationale="""
對於 5 人小團隊、初期用戶量小、需要快速上線的項目，
模塊化單體是最佳選擇。它提供了：
1. 快速開發和部署能力
2. 未來演進到微服務的可能性
3. 適合當前團隊規模的複雜度

等到產品驗證成功、團隊擴大、需求明確後，
再考慮將特定模塊拆分為微服務。
""",
            expected_outcomes=[
                "更快的初始上線時間",
                "較低的初始運維成本",
                "保留未來擴展的靈活性",
            ],
            monitoring_points=[
                "監控模塊間的耦合度",
                "追蹤性能瓶頸",
                "評估何時需要拆分",
            ],
            decision_principles=[
                "從簡單開始，按需演進",
                "避免過早優化",
                "考慮團隊實際能力",
                "保留選擇權",
            ],
            difficulty="advanced",
            tags=["architecture", "microservices", "monolith", "decision"],
        )
        self.decision_examples[architecture_decision.id] = architecture_decision

    # Query Methods

    def get_code_example(self, example_id: str) -> CodeExample | None:
        """Get a code example by ID."""
        return self.code_examples.get(example_id)

    def get_scenario_example(self, example_id: str) -> ScenarioExample | None:
        """Get a scenario example by ID."""
        return self.scenario_examples.get(example_id)

    def get_decision_example(self, example_id: str) -> DecisionExample | None:
        """Get a decision example by ID."""
        return self.decision_examples.get(example_id)

    def search_examples(
        self,
        query: str,
        category: ExampleCategory | None = None,
        max_results: int = 5
    ) -> dict[str, list[Any]]:
        """
        Search for relevant examples.
        
        搜索相關示例
        """
        query_lower = query.lower()
        results = {
            "code_examples": [],
            "scenario_examples": [],
            "decision_examples": [],
        }

        # Search code examples
        for example in self.code_examples.values():
            if category and example.category != category:
                continue

            score = self._calculate_relevance(
                query_lower,
                example.name,
                example.description,
                example.tags
            )
            if score > 0:
                results["code_examples"].append((example, score))

        results["code_examples"] = [
            e for e, _ in sorted(results["code_examples"], key=lambda x: x[1], reverse=True)[:max_results]
        ]

        # Search scenario examples
        for example in self.scenario_examples.values():
            if category and example.category != category:
                continue

            score = self._calculate_relevance(
                query_lower,
                example.name,
                example.problem_statement,
                example.tags
            )
            if score > 0:
                results["scenario_examples"].append((example, score))

        results["scenario_examples"] = [
            e for e, _ in sorted(results["scenario_examples"], key=lambda x: x[1], reverse=True)[:max_results]
        ]

        # Search decision examples
        for example in self.decision_examples.values():
            if category and example.category != category:
                continue

            score = self._calculate_relevance(
                query_lower,
                example.name,
                example.situation,
                example.tags
            )
            if score > 0:
                results["decision_examples"].append((example, score))

        results["decision_examples"] = [
            e for e, _ in sorted(results["decision_examples"], key=lambda x: x[1], reverse=True)[:max_results]
        ]

        return results

    def _calculate_relevance(
        self,
        query: str,
        name: str,
        description: str,
        tags: list[str]
    ) -> float:
        """Calculate relevance score."""
        score = 0.0
        query_words = set(query.split())

        for word in query_words:
            if word in name.lower():
                score += 3.0
            if word in description.lower():
                score += 1.0
            if word in [t.lower() for t in tags]:
                score += 2.0

        return score

    def get_examples_for_category(self, category: ExampleCategory) -> dict[str, list[Any]]:
        """Get all examples for a category."""
        return {
            "code_examples": [e for e in self.code_examples.values() if e.category == category],
            "scenario_examples": [e for e in self.scenario_examples.values() if e.category == category],
            "decision_examples": [e for e in self.decision_examples.values() if e.category == category],
        }

    def add_code_example(self, example: CodeExample) -> None:
        """Add a new code example."""
        self.code_examples[example.id] = example

    def add_scenario_example(self, example: ScenarioExample) -> None:
        """Add a new scenario example."""
        self.scenario_examples[example.id] = example

    def add_decision_example(self, example: DecisionExample) -> None:
        """Add a new decision example."""
        self.decision_examples[example.id] = example

    def get_stats(self) -> dict[str, int]:
        """Get example library statistics."""
        return {
            "code_examples": len(self.code_examples),
            "scenario_examples": len(self.scenario_examples),
            "decision_examples": len(self.decision_examples),
        }
