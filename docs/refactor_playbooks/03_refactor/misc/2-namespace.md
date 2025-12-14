# 彈性命名規範完整學習手冊
## 從零開始到企業級實戰

> **目標讀者**: 初學者到資深工程師  
> **學習時間**: 4-6 週完整掌握  
> **實戰導向**: 100+ 實際範例與練習  
> **版本**: v2.0.0 - 2024年最新版

---

## 🎯 學習路線圖

### 第一階段：基礎概念 (第1-2週)
- 為什麼命名規範如此重要？
- 命名規範的歷史與演進
- 不同語言與平台的命名特色
- 建立個人命名習慣

### 第二階段：工具與平台 (第3-4週)  
- Git 版本控制命名
- Docker 容器化命名
- Kubernetes 雲原生命名  
- CI/CD 自動化命名

### 第三階段：企業級實戰 (第5-6週)
- 多團隊協作規範
- 大型專案命名策略
- 自動化驗證與治理
- 持續改進與維護

---

## 📚 完整學習大綱

### 第一章：命名規範基礎理論
1.1 什麼是命名規範？為什麼重要？  
1.2 命名規範的核心原則  
1.3 常見的命名災難與解決方案  
1.4 不同領域的命名特色分析  

### 第二章：程式設計語言命名
2.1 多種語言命名規範對比  
2.2 Go 語言命名最佳實踐  
2.3 JavaScript/TypeScript 命名規範  
2.4 Python 命名慣例  
2.5 跨語言專案的命名統一

### 第三章：版本控制系統命名
3.1 Git 分支命名策略  
3.2 Commit 訊息規範化  
3.3 標籤與版本命名  
3.4 Pull Request 與 Issue 命名

### 第四章：容器化與編排命名
4.1 Docker 映像檔命名規範  
4.2 容器名稱與標籤策略  
4.3 Kubernetes 資源命名  
4.4 命名空間設計與管理

### 第五章：基礎設施即程式碼
5.1 Terraform 模組命名  
5.2 雲端資源命名策略  
5.3 環境隔離與命名  
5.4 基礎設施版本管理

### 第六章：CI/CD 流水線命名
6.1 工作流程命名規範  
6.2 環境變數命名策略  
6.3 部署階段命名  
6.4 監控與警報命名

### 第七章：企業級命名治理
7.1 大型組織命名策略  
7.2 多團隊協作規範  
7.3 自動化驗證工具  
7.4 命名規範遷移策略

### 第八章：實戰項目演練
8.1 電商平台命名設計  
8.2 微服務架構命名  
8.3 多雲環境命名策略  
8.4 DevOps 工具鏈命名

### 第九章：工具與自動化
9.1 命名驗證工具開發  
9.2 IDE 外掛與整合  
9.3 CI/CD 自動檢查  
9.4 監控與報表系統

### 第十章：持續改進與維護
10.1 命名規範版本管理  
10.2 團隊培訓與推廣  
10.3 效果評估與優化  
10.4 未來趨勢與發展

---

這份學習手冊將帶您從基礎理論開始，逐步深入到企業級實戰應用，確保您能夠掌握現代軟體開發中的所有命名規範精髓。

---

## 第一章：命名規範基礎理論

### 1.1 什麼是命名規範？為什麼重要？

#### 命名規範的定義
命名規範是一套統一的命名約定，用於確保程式碼、檔案、資源等的名稱具有一致性、可讀性和可維護性。它就像建築師的藍圖，為整個軟體系統提供清晰的結構指導。

#### 為什麼命名規範如此重要？

**1. 可讀性提升**
```bash
# ❌ 糟糕的命名
d1 = getUserData()
tmp = calcPrice(d1)

# ✅ 良好的命名  
user_profile = get_user_profile()
final_price = calculate_discounted_price(user_profile)
```

**2. 維護成本降低**
- 新團隊成員能快速理解專案結構
- 減少 50% 的程式碼閱讀時間
- 降低 Bug 發生率

**3. 團隊協作效率**
- 統一的理解基礎
- 減少溝通成本
- 提高程式碼審查效率

#### 真實案例：Netflix 的命名災難
2012年，Netflix 因為微服務命名不當，導致：
- 服務依賴關係混亂
- 部署失敗率增加 40%
- 工程師需花費額外 30% 時間理解系統

**解決方案**：實施統一命名規範後
- 部署成功率提升至 99.9%
- 新功能開發速度提升 25%
- 系統故障恢復時間縮短 60%

### 1.2 命名規範的核心原則

#### 原則一：清晰明確 (Clarity)
```yaml
# ❌ 模糊不清
svc: web
img: app:latest

# ✅ 清晰明確
service: user-authentication-service
image: user-auth-api:v1.2.3
```

#### 原則二：一致性 (Consistency)
```bash
# ❌ 不一致
create_user()
deleteOrder()
UpdateProduct()

# ✅ 一致性
create_user()
delete_order()
update_product()
```

#### 原則三：簡潔性 (Conciseness)
```go
// ❌ 冗長
func GetAllActiveUserAccountInformationFromDatabase() {}

// ✅ 簡潔
func GetActiveUsers() {}
```

#### 原則四：可搜尋性 (Searchability)
```javascript
// ❌ 難以搜尋
const d = 86400; // 一天的秒數

// ✅ 可搜尋
const SECONDS_PER_DAY = 86400;
```

### 1.3 常見的命名災難與解決方案

#### 災難類型一：神秘縮寫
```python
# ❌ 神秘縮寫
def calc_gst_amt(pr, rt):
    return pr * rt

# ✅ 明確命名
def calculate_goods_service_tax_amount(price, tax_rate):
    return price * tax_rate
```

#### 災難類型二：匈牙利記號法濫用
```csharp
// ❌ 過時的匈牙利記號法
string strUserName;
int intUserAge;
bool bIsActive;

// ✅ 現代命名方式
string userName;
int userAge;
bool isActive;
```

#### 災難類型三：文化差異問題
```bash
# ❌ 文化特定命名
git branch feature/lunar-new-year-sale

# ✅ 通用命名  
git branch feature/seasonal-promotion-q1
```

### 1.4 不同領域的命名特色分析

#### 前端開發命名特色
```typescript
// React 元件命名
const UserProfileCard = () => {
  return <div className="user-profile-card">...</div>
}

// CSS 類別命名 (BEM 方法)
.user-profile-card {}
.user-profile-card__avatar {}
.user-profile-card__avatar--large {}
```

#### 後端服務命名特色
```go
// Go 服務命名
type UserService interface {
    CreateUser(ctx context.Context, user *User) error
    GetUserByID(ctx context.Context, id string) (*User, error)
}

// 資料庫表格命名
users
user_profiles  
user_authentication_tokens
```

#### DevOps 基礎設施命名特色
```yaml
# Kubernetes 資源命名
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-auth-api-prod
  namespace: authentication-services
  labels:
    app: user-auth-api
    version: v1.2.3
    environment: production
```

#### 練習題 1.1
請為以下場景設計合適的命名：
1. 一個處理使用者註冊的微服務
2. 存放用戶頭像的 S3 儲存桶
3. 監控系統 CPU 使用率的 Prometheus 指標

**參考答案**：
1. `user-registration-service`
2. `user-avatars-prod-us-west-2`
3. `system_cpu_usage_percent`

---

## 第二章：程式設計語言命名

### 2.1 多種語言命名規範對比

#### 命名風格對照表

| 語言 | 變數/函數 | 類別/結構 | 常數 | 檔案名稱 |
|------|-----------|-----------|------|----------|
| Go | camelCase | PascalCase | UPPER_SNAKE | snake_case.go |
| JavaScript | camelCase | PascalCase | UPPER_SNAKE | kebab-case.js |
| Python | snake_case | PascalCase | UPPER_SNAKE | snake_case.py |
| Java | camelCase | PascalCase | UPPER_SNAKE | PascalCase.java |
| C# | camelCase | PascalCase | PascalCase | PascalCase.cs |
| Rust | snake_case | PascalCase | UPPER_SNAKE | snake_case.rs |

### 2.2 Go 語言命名最佳實踐

#### 基本規則
```go
// ✅ 正確的 Go 命名風格
package userservice

import (
    "context"
    "time"
)

// 常數使用駝峰式，首字母大寫表示 exported
const (
    DefaultTimeout = 30 * time.Second
    maxRetries     = 3  // 小寫表示 private
)

// 結構體使用 PascalCase
type UserProfile struct {
    ID        string    `json:"id"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// 介面命名通常以 -er 結尾
type UserRepository interface {
    CreateUser(ctx context.Context, user *UserProfile) error
    GetUserByID(ctx context.Context, id string) (*UserProfile, error)
}

// 方法使用 camelCase，首字母大寫表示 public
func (r *userRepository) CreateUser(ctx context.Context, user *UserProfile) error {
    // 區域變數使用 camelCase，首字母小寫
    currentTime := time.Now()
    user.CreatedAt = currentTime
    
    return nil
}
```

#### Go 專案結構命名
```
project-root/
├── cmd/
│   └── user-service/          # 應用程式進入點
│       └── main.go
├── internal/                  # 私有程式碼
│   ├── user/                 # 領域模組
│   │   ├── service.go
│   │   ├── repository.go
│   │   └── handler.go
│   └── config/               # 配置模組
│       └── config.go
├── pkg/                      # 可重用的公開程式碼
│   └── logger/
│       └── logger.go
├── api/                      # API 定義
│   └── openapi.yaml
├── deployments/              # 部署配置
│   └── kubernetes/
└── go.mod
```

### 2.3 JavaScript/TypeScript 命名規範

#### ES6+ 現代 JavaScript 命名
```javascript
// ✅ 現代 JavaScript 命名規範
const API_BASE_URL = 'https://api.example.com';
const DEFAULT_TIMEOUT = 5000;

class UserService {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this._cache = new Map(); // 私有屬性前綴 _
    }
    
    async getUserProfile(userId) {
        // 使用 camelCase
        const cacheKey = `user_${userId}`;
        
        if (this._cache.has(cacheKey)) {
            return this._cache.get(cacheKey);
        }
        
        try {
            const userProfile = await this.apiClient.get(`/users/${userId}`);
            this._cache.set(cacheKey, userProfile);
            return userProfile;
        } catch (error) {
            throw new Error(`Failed to fetch user profile: ${error.message}`);
        }
    }
    
    // 事件處理函數以 handle 開頭
    handleUserLogin(loginData) {
        return this.validateAndProcessLogin(loginData);
    }
    
    // 布林值函數以 is/has/can 開頭
    isUserActive(user) {
        return user.status === 'active' && user.lastLoginAt > Date.now() - 86400000;
    }
}

// 工廠函數以 create 開頭
function createUserService(apiClient) {
    return new UserService(apiClient);
}

// 高階函數使用動詞 + 名詞
const withAuthentication = (component) => {
    return (props) => {
        // HOC 實作
    };
};
```

#### TypeScript 特定命名規範
```typescript
// ✅ TypeScript 命名最佳實踐
interface UserProfile {
    readonly id: string;
    email: string;
    firstName: string;
    lastName: string;
    isActive: boolean;
}

// 型別別名使用 PascalCase
type UserRole = 'admin' | 'user' | 'guest';
type CreateUserRequest = Omit<UserProfile, 'id'>;

// 泛型參數使用單個大寫字母
interface Repository<T, K = string> {
    findById(id: K): Promise<T | null>;
    save(entity: T): Promise<T>;
}

// 裝飾器使用 camelCase
function logExecutionTime(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    // 裝飾器實作
}

class UserRepository implements Repository<UserProfile> {
    @logExecutionTime
    async findById(id: string): Promise<UserProfile | null> {
        // 實作
        return null;
    }
}
```

### 2.4 Python 命名慣例

#### PEP 8 命名標準
```python
# ✅ Python 命名規範 (PEP 8)
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

# 常數使用 UPPER_SNAKE_CASE
API_BASE_URL = 'https://api.example.com'
DEFAULT_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3

class UserService:
    """使用者服務類別 - 類別名稱使用 PascalCase"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self._cache = {}  # 私有屬性以底線開頭
        self.__secret_key = None  # 名稱修飾使用雙底線
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取使用者資料 - 函數名稱使用 snake_case
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            使用者資料字典或 None
        """
        cache_key = f"user_{user_id}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            user_profile = self.api_client.get(f"/users/{user_id}")
            self._cache[cache_key] = user_profile
            return user_profile
        except Exception as error:
            logger.error(f"Failed to fetch user profile: {error}")
            return None
    
    def is_user_active(self, user: Dict[str, Any]) -> bool:
        """布林函數以 is_ 開頭"""
        return (
            user.get('status') == 'active' 
            and user.get('last_login_at', 0) > datetime.now().timestamp() - 86400
        )
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """靜態方法使用 snake_case"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

# 模組層級函數使用 snake_case
def create_user_service(api_client) -> UserService:
    """工廠函數"""
    return UserService(api_client)

# 例外類別以 Error 或 Exception 結尾
class UserNotFoundError(Exception):
    """當找不到使用者時拋出的例外"""
    pass

class InvalidUserDataError(ValueError):
    """當使用者資料無效時拋出的例外"""
    pass
```

### 2.5 跨語言專案的命名統一

#### 統一的 API 設計
```yaml
# REST API 路徑統一使用 kebab-case
GET  /api/v1/user-profiles/{id}
POST /api/v1/user-profiles
PUT  /api/v1/user-profiles/{id}
DELETE /api/v1/user-profiles/{id}

# GraphQL 使用 camelCase
query {
  userProfile(id: "123") {
    firstName
    lastName
    isActive
    createdAt
  }
}
```

#### 資料庫命名統一
```sql
-- 表格名稱使用 snake_case 複數形式
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引命名規則：idx_表名_欄位名
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_active_created ON user_profiles(is_active, created_at);
```

#### 練習題 2.1
請將以下糟糕的命名改寫為符合各語言規範的良好命名：

**JavaScript:**
```javascript
// ❌ 需要改進
var u = {};
function getdata(i) {
    return DB.find(i);
}
class usrmgr {
    delUsr(id) {}
}
```

**Python:**
```python
# ❌ 需要改進  
def GetUserData(ID):
    return db.Find(ID)

class UserMGR:
    def DelUser(self, ID):
        pass
```

**參考答案將在下一章節提供**

---

## 第三章：版本控制系統命名

### 3.1 Git 分支命名策略

#### Git Flow 分支命名規範
```bash
# 主要分支 - 永續存在
main                    # 主分支（生產環境）
develop                 # 開發分支（整合環境）

# 功能分支 - 臨時分支
feature/user-authentication     # 功能開發
feature/payment-integration    # 支付整合
feature/mobile-responsive      # 手機版響應式

# 修復分支
hotfix/security-patch-v1.2.1   # 緊急修復
bugfix/login-error-handling     # 一般錯誤修復

# 發布分支
release/v1.3.0         # 版本發布準備
release/v2.0.0-beta    # Beta 版本發布
```

#### GitHub Flow 簡化分支策略
```bash
# 主分支
main

# 功能分支（直接從 main 分出）
add-user-dashboard
fix-memory-leak
update-dependencies
refactor-authentication-service
```

#### 分支命名最佳實踐
```bash
# ✅ 良好的分支命名
feature/jira-123-user-profile-editing
hotfix/critical-sql-injection-fix
refactor/extract-user-service-layer
docs/api-documentation-update

# ❌ 糟糕的分支命名
feature/stuff
fix/bug
john-working-branch
temp-branch-delete-later
```

### 3.2 Commit 訊息規範化

#### Conventional Commits 規範
```bash
# 格式：<type>(<scope>): <description>
#
# <body>
#
# <footer>

# 基本範例
feat: add user authentication API
fix: resolve memory leak in user service
docs: update API documentation
style: format code according to prettier rules
refactor: extract user validation logic
test: add unit tests for payment service
chore: update dependencies

# 包含範圍的範例
feat(auth): implement OAuth2 integration
fix(payment): handle edge case in refund process
docs(api): add examples for user endpoints
refactor(database): optimize user query performance

# 破壞性變更
feat!: change user API response format

BREAKING CHANGE: user API now returns different response structure
```

#### 完整的 Commit 訊息範例
```bash
feat(user-service): add email verification feature

- Implement email verification workflow
- Add email template system
- Create verification token management
- Update user registration process

Closes #456
Co-authored-by: Jane Smith <jane@example.com>
```

#### commitlint 配置
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新功能
        'fix',      // 錯誤修復
        'docs',     // 文件更新
        'style',    // 程式碼格式調整
        'refactor', // 重構
        'perf',     // 效能優化
        'test',     // 增加測試
        'chore',    // 建置或輔助工具變動
        'revert',   // 撤銷先前的 commit
        'ci',       // CI 相關變動
      ],
    ],
    'subject-max-length': [2, 'always', 100],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'header-max-length': [2, 'always', 100],
  },
};
```

### 3.3 標籤與版本命名

#### 語意化版本控制 (Semantic Versioning)
```bash
# 版本格式：MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

# 正式版本
v1.0.0          # 初始版本
v1.0.1          # 修復版本（向後相容）
v1.1.0          # 功能版本（向後相容）  
v2.0.0          # 主要版本（可能不向後相容）

# 預發布版本
v1.2.0-alpha.1  # Alpha 版本
v1.2.0-beta.1   # Beta 版本
v1.2.0-rc.1     # Release Candidate

# 包含建置資訊
v1.2.0+20231201.abc123f
v1.2.0-beta.1+exp.sha.5114f85
```

#### Git 標籤操作範例
```bash
# 創建輕量標籤
git tag v1.0.0

# 創建附註標籤（推薦）
git tag -a v1.0.0 -m "Release version 1.0.0

Features:
- User authentication system
- Payment integration  
- Mobile responsive design

Bug fixes:
- Fix memory leak in user service
- Resolve login timeout issue"

# 推送標籤到遠端
git push origin v1.0.0
git push origin --tags

# 查看標籤資訊
git show v1.0.0
```

### 3.4 Pull Request 與 Issue 命名

#### Pull Request 命名規範
```bash
# 格式：[TYPE] Description (#issue-number)

# 功能 PR
[FEAT] Add user profile editing functionality (#123)
[FEAT] Implement real-time notifications (#456)

# 修復 PR  
[FIX] Resolve login session timeout issue (#789)
[HOTFIX] Critical security patch for XSS vulnerability (#999)

# 重構 PR
[REFACTOR] Extract user service into separate module (#234)
[PERF] Optimize database queries for user dashboard (#567)

# 文件 PR
[DOCS] Update API documentation with new endpoints (#345)
[DOCS] Add contributing guidelines (#678)
```

#### Issue 命名規範
```bash
# Bug 報告
[BUG] User login fails with special characters in password
[BUG] Memory leak in background sync process
[CRITICAL] Data corruption in user profiles table

# 功能請求
[FEATURE] Add export functionality to user dashboard  
[ENHANCEMENT] Improve loading performance on mobile devices
[FEATURE REQUEST] Integration with third-party analytics

# 任務
[TASK] Update dependencies to latest versions
[CHORE] Clean up deprecated code in user service
[MAINTENANCE] Database backup strategy implementation
```

#### GitHub Issue 範本
```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug, needs-triage'
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 🌍 Environment
- OS: [e.g. iOS]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

## 📝 Additional Context
Add any other context about the problem here.
```

#### 實戰演練 3.1
請為以下情境設計合適的命名：

1. **分支命名**：你正在開發一個新的使用者權限管理系統
2. **Commit 訊息**：你修復了一個導致支付失敗的關鍵 bug
3. **版本標籤**：你的應用程式已經是 v1.5.2，現在要發布一個包含新功能的版本
4. **Pull Request**：你重構了資料庫連接邏輯以提升效能

**參考答案**：
1. `feature/user-permission-management-system`
2. `fix(payment): resolve transaction failure in checkout process`
3. `v1.6.0`
4. `[PERF] Refactor database connection pooling for better performance (#456)`

---

## 第四章：DevOps 與雲端平台命名

### 4.1 Kubernetes 資源命名規範

#### 基本命名原則
Kubernetes 資源命名必須遵循 DNS-1123 標準：
- 只能包含小寫字母、數字和連字號 (-)
- 必須以字母或數字開頭和結尾
- 最長 63 個字元

#### Pod 與 Deployment 命名
```yaml
# ✅ 良好的 Deployment 命名
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-auth-api-prod          # 服務-用途-環境
  namespace: authentication-services
  labels:
    app: user-auth-api
    component: backend
    version: v1.2.3
    environment: production
    team: platform-engineering
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-auth-api
      environment: production
  template:
    metadata:
      name: user-auth-api-pod       # Pod 名稱模板
      labels:
        app: user-auth-api
        component: backend
        version: v1.2.3
        environment: production
```

#### Service 與 Ingress 命名
```yaml
# Service 命名規範
apiVersion: v1
kind: Service
metadata:
  name: user-auth-api-svc           # 服務名稱 + svc 後綴
  namespace: authentication-services
  labels:
    app: user-auth-api
    tier: backend
spec:
  selector:
    app: user-auth-api
  ports:
  - name: http-api                  # 連接埠名稱要有意義
    port: 80
    targetPort: 8080
  - name: health-check
    port: 8081
    targetPort: 8081

---
# Ingress 命名規範
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: user-auth-api-ingress       # 服務名稱 + ingress 後綴
  namespace: authentication-services
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: auth-api.production.example.com    # 環境.服務.網域
    http:
      paths:
      - path: /api/v1/auth
        pathType: Prefix
        backend:
          service:
            name: user-auth-api-svc
            port:
              number: 80
```

#### ConfigMap 與 Secret 命名
```yaml
# ConfigMap 命名
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-auth-api-config        # 服務名稱 + config 後綴
  namespace: authentication-services
data:
  app.env: "production"
  log.level: "info"
  database.host: "postgres.internal.example.com"

---
# Secret 命名
apiVersion: v1
kind: Secret
metadata:
  name: user-auth-api-secrets       # 服務名稱 + secrets 後綴
  namespace: authentication-services
type: Opaque
data:
  database-password: <base64-encoded-password>
  jwt-secret-key: <base64-encoded-jwt-key>
```

### 4.2 Docker 映像檔命名策略

#### 映像檔標籤命名規範
```bash
# 基本格式：registry/namespace/repository:tag
# 範例：registry.company.com/platform/user-auth-api:v1.2.3

# ✅ 良好的映像檔命名
registry.company.com/platform/user-auth-api:v1.2.3
registry.company.com/platform/user-auth-api:v1.2.3-alpine
registry.company.com/platform/user-auth-api:latest
registry.company.com/platform/user-auth-api:main-abc123f
registry.company.com/platform/user-auth-api:pr-456-def789a

# 環境特定標籤
registry.company.com/platform/user-auth-api:v1.2.3-prod
registry.company.com/platform/user-auth-api:v1.2.3-staging
registry.company.com/platform/user-auth-api:v1.2.3-dev

# ❌ 糟糕的映像檔命名
myapp:1
app:latest
user-service:john-version
image:final-v2-really-final
```

#### Dockerfile 多階段建置命名
```dockerfile
# ✅ 良好的多階段建置命名
FROM node:18-alpine AS base-dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS production-runtime
WORKDIR /app
COPY --from=base-dependencies /app/node_modules ./node_modules
COPY --from=build-stage /app/dist ./dist
COPY package*.json ./
EXPOSE 8080
CMD ["npm", "start"]
```

### 4.3 雲端資源命名規範

#### AWS 資源命名
```bash
# S3 Bucket 命名（全球唯一）
company-user-avatars-prod-us-west-2
company-application-logs-staging-eu-west-1
company-backup-database-prod-ap-southeast-1

# EC2 Instance 命名
prod-web-server-01-us-west-2
staging-api-server-02-eu-west-1
dev-database-server-01-us-east-1

# RDS Instance 命名
prod-postgres-user-db-primary
prod-postgres-user-db-replica-01
staging-mysql-analytics-db

# Lambda Function 命名
prod-user-registration-processor
prod-image-thumbnail-generator
staging-email-notification-sender

# CloudFormation Stack 命名
user-service-infrastructure-prod
monitoring-stack-staging
networking-foundation-prod
```

#### Azure 資源命名
```bash
# Resource Group 命名
rg-user-service-prod-eastus
rg-monitoring-shared-westus2
rg-networking-hub-centralus

# Virtual Machine 命名
vm-web-prod-01-eastus
vm-api-staging-02-westus2
vm-db-prod-primary-centralus

# Storage Account 命名（只能小寫字母和數字）
sauserserviceprodeastus
samonitoringsharedwestus2
sabackupprodcentralus

# App Service 命名
app-user-api-prod-eastus
app-admin-portal-staging-westus2
```

#### Google Cloud Platform 資源命名
```bash
# Project ID 命名
company-user-service-prod
company-analytics-platform-dev
company-infrastructure-shared

# Compute Engine Instance 命名
prod-web-server-01-us-west1-a
staging-api-server-02-europe-west1-b
dev-database-server-01-asia-east1-c

# Cloud Storage Bucket 命名
company-user-uploads-prod-us
company-application-logs-staging-eu
company-backup-data-prod-asia

# Cloud Function 命名
prod-user-notification-processor
staging-image-resize-handler
dev-data-transformation-pipeline
```

### 4.4 監控與日誌命名

#### Prometheus 指標命名
```bash
# 格式：<namespace>_<subsystem>_<name>_<unit>

# ✅ 良好的指標命名
http_requests_total                    # HTTP 請求總數
http_request_duration_seconds         # HTTP 請求持續時間
database_connections_active           # 資料庫連接數
memory_usage_bytes                    # 記憶體使用量
cpu_usage_percent                     # CPU 使用率百分比

# 業務指標
user_registrations_total              # 使用者註冊總數
payment_transactions_success_total    # 成功支付交易數
email_notifications_sent_total       # 已發送郵件通知數

# 具體範例配置
# 計數器
user_service_http_requests_total{method="GET",status="200",endpoint="/api/v1/users"}
user_service_http_requests_total{method="POST",status="201",endpoint="/api/v1/users"}

# 直方圖
user_service_http_request_duration_seconds{method="GET",endpoint="/api/v1/users"}
user_service_database_query_duration_seconds{operation="select",table="users"}

# 量規
user_service_active_connections
user_service_memory_usage_bytes
user_service_cpu_usage_percent
```

#### 日誌命名與結構化
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "user-auth-service",
  "message": "User login successful",
  "service": {
    "name": "user-auth-api",
    "version": "v1.2.3",
    "environment": "production"
  },
  "request": {
    "id": "req-abc123def456",
    "method": "POST",
    "path": "/api/v1/auth/login",
    "user_agent": "Mozilla/5.0...",
    "ip": "192.168.1.100"
  },
  "user": {
    "id": "user-789xyz",
    "email": "user@example.com"
  },
  "performance": {
    "duration_ms": 145,
    "database_queries": 2,
    "cache_hits": 1
  },
  "tags": {
    "team": "platform-engineering",
    "component": "authentication",
    "feature": "user-login"
  }
}
```

### 4.5 CI/CD Pipeline 命名

#### GitHub Actions Workflow 命名
```yaml
# .github/workflows/user-service-ci-cd.yml
name: User Service CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths: ['services/user-service/**']
  pull_request:
    branches: [main]
    paths: ['services/user-service/**']

jobs:
  unit-tests:
    name: Run Unit Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4
      
      - name: Setup Node.js Environment
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Dependencies
        run: npm ci
      
      - name: Run Unit Tests with Coverage
        run: npm run test:coverage

  integration-tests:
    name: Run Integration Tests
    needs: unit-tests
    runs-on: ubuntu-latest

  build-and-push-image:
    name: Build and Push Docker Image
    needs: [unit-tests, integration-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

#### Jenkins Pipeline 命名
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.company.com'
        IMAGE_NAME = 'platform/user-auth-api'
        KUBECONFIG_CREDENTIAL = 'k8s-prod-config'
    }
    
    stages {
        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Run Code Quality Checks') {
            parallel {
                stage('ESLint Code Analysis') {
                    steps {
                        sh 'npm run lint'
                    }
                }
                stage('Security Vulnerability Scan') {
                    steps {
                        sh 'npm audit --audit-level high'
                    }
                }
            }
        }
        
        stage('Execute Unit Tests') {
            steps {
                sh 'npm run test:unit'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverageReport coveragePattern: 'coverage/lcov.info'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def imageTag = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
                    docker.build("${IMAGE_NAME}:${imageTag}")
                }
            }
        }
        
        stage('Deploy to Staging Environment') {
            when {
                branch 'develop'
            }
            steps {
                sh './scripts/deploy-to-staging.sh'
            }
        }
        
        stage('Deploy to Production Environment') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh './scripts/deploy-to-production.sh'
            }
        }
    }
    
    post {
        failure {
            slackSend(
                channel: '#platform-engineering',
                color: 'danger',
                message: "❌ Pipeline failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
        success {
            slackSend(
                channel: '#platform-engineering',
                color: 'good',
                message: "✅ Pipeline succeeded: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

#### GitLab CI/CD Pipeline 命名
```yaml
# .gitlab-ci.yml
stages:
  - code-quality
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.company.com
  IMAGE_NAME: platform/user-auth-api
  POSTGRES_DB: test_database
  POSTGRES_USER: test_user
  POSTGRES_PASSWORD: test_password

before_script:
  - echo "Starting pipeline for $CI_PROJECT_NAME"

code-quality-analysis:
  stage: code-quality
  image: node:18-alpine
  script:
    - npm ci
    - npm run lint
    - npm run format:check
  artifacts:
    reports:
      codequality: code-quality-report.json

security-vulnerability-scan:
  stage: code-quality
  image: node:18-alpine
  script:
    - npm audit --audit-level high
    - npm run security:scan
  allow_failure: true

unit-tests:
  stage: test
  image: node:18-alpine
  services:
    - postgres:15-alpine
  script:
    - npm ci
    - npm run test:unit
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

integration-tests:
  stage: test
  image: node:18-alpine
  services:
    - postgres:15-alpine
    - redis:7-alpine
  script:
    - npm ci
    - npm run test:integration
  dependencies:
    - unit-tests

build-docker-image:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

deploy-to-staging:
  stage: deploy-staging
  image: kubectl:latest
  script:
    - kubectl config use-context staging-cluster
    - kubectl set image deployment/user-auth-api-staging user-auth-api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/user-auth-api-staging
  environment:
    name: staging
    url: https://api-staging.company.com
  only:
    - develop

deploy-to-production:
  stage: deploy-production
  image: kubectl:latest
  script:
    - kubectl config use-context production-cluster
    - kubectl set image deployment/user-auth-api-prod user-auth-api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/user-auth-api-prod
  environment:
    name: production
    url: https://api.company.com
  when: manual
  only:
    - main
```

### 4.6 Infrastructure as Code 命名

#### Terraform 資源命名
```hcl
# main.tf - AWS 資源命名範例

# VPC 命名
resource "aws_vpc" "main_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "vpc-user-service-prod"
    Environment = "production"
    Project     = "user-service"
    Team        = "platform-engineering"
  }
}

# Subnet 命名
resource "aws_subnet" "public_subnet_1a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "subnet-public-1a-user-service-prod"
    Type = "public"
    AZ   = "us-west-2a"
  }
}

resource "aws_subnet" "private_subnet_1a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "us-west-2a"
  
  tags = {
    Name = "subnet-private-1a-user-service-prod"
    Type = "private"
    AZ   = "us-west-2a"
  }
}

# Security Group 命名
resource "aws_security_group" "web_server_sg" {
  name_prefix = "sg-web-server-"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main_vpc.id
  
  ingress {
    description = "HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "sg-web-server-user-service-prod"
  }
}

# EC2 Instance 命名
resource "aws_instance" "web_server" {
  count = 2
  
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.medium"
  
  subnet_id              = aws_subnet.public_subnet_1a.id
  vpc_security_group_ids = [aws_security_group.web_server_sg.id]
  
  user_data = file("${path.module}/scripts/install-web-server.sh")
  
  tags = {
    Name = "ec2-web-server-${count.index + 1}-user-service-prod"
    Role = "web-server"
    Index = count.index + 1
  }
}

# RDS Instance 命名
resource "aws_db_instance" "postgres_primary" {
  identifier = "rds-postgres-user-service-prod-primary"
  
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "userservice"
  username = "dbadmin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "rds-postgres-user-service-prod-final-snapshot"
  
  tags = {
    Name = "rds-postgres-user-service-prod-primary"
  }
}

# Load Balancer 命名
resource "aws_lb" "application_load_balancer" {
  name               = "alb-user-service-prod"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_1a.id, aws_subnet.public_subnet_1b.id]
  
  enable_deletion_protection = true
  
  tags = {
    Name = "alb-user-service-prod"
  }
}

# S3 Bucket 命名
resource "aws_s3_bucket" "user_uploads" {
  bucket = "company-user-uploads-prod-${random_string.bucket_suffix.result}"
  
  tags = {
    Name        = "s3-user-uploads-prod"
    Purpose     = "user-file-storage"
    Environment = "production"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
```

#### Ansible Playbook 命名
```yaml
# playbooks/deploy-user-service.yml
---
- name: Deploy User Service to Production Servers
  hosts: production_web_servers
  become: yes
  vars:
    service_name: user

#### Jenkins Pipeline 命名
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.company.com'
        IMAGE_NAME = 'platform/user-auth-api'
        KUBECONFIG_CREDENTIAL = 'k8s-prod-config'
    }
    
    stages {
        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Run Code Quality Checks') {
            parallel {
                stage('ESLint Code Analysis') {
                    steps {
                        sh 'npm run lint'
                    }
                }
                stage('Security Vulnerability Scan') {
                    steps {
                        sh 'npm audit --audit-level high'
                    }
                }
            }
        }
        
        stage('Execute Unit Tests') {
            steps {
                sh 'npm run test:unit'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverageReport coveragePattern: 'coverage/lcov.info'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def imageTag = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
                    docker.build("${IMAGE_NAME}:${imageTag}")
                }
            }
        }
        
        stage('Deploy to Staging Environment') {
            when {
                branch 'develop'
            }
            steps {
                sh './scripts/deploy-to-staging.sh'
            }
        }
        
        stage('Deploy to Production Environment') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh './scripts/deploy-to-production.sh'
            }
        }
    }
    
    post {
        failure {
            slackSend(
                channel: '#platform-engineering',
                color: 'danger',
                message: "❌ Pipeline failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
        success {
            slackSend(
                channel: '#platform-engineering',
                color: 'good',
                message: "✅ Pipeline succeeded: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

#### GitLab CI/CD Pipeline 命名
```yaml
# .gitlab-ci.yml
stages:
  - code-quality
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.company.com
  IMAGE_NAME: platform/user-auth-api
  POSTGRES_DB: test_database
  POSTGRES_USER: test_user
  POSTGRES_PASSWORD: test_password

before_script:
  - echo "Starting pipeline for $CI_PROJECT_NAME"

code-quality-analysis:
  stage: code-quality
  image: node:18-alpine
  script:
    - npm ci
    - npm run lint
    - npm run format:check
  artifacts:
    reports:
      codequality: code-quality-report.json

security-vulnerability-scan:
  stage: code-quality
  image: node:18-alpine
  script:
    - npm audit --audit-level high
    - npm run security:scan
  allow_failure: true

unit-tests:
  stage: test
  image: node:18-alpine
  services:
    - postgres:15-alpine
  script:
    - npm ci
    - npm run test:unit
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

integration-tests:
  stage: test
  image: node:18-alpine
  services:
    - postgres:15-alpine
    - redis:7-alpine
  script:
    - npm ci
    - npm run test:integration
  dependencies:
    - unit-tests

build-docker-image:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

deploy-to-staging:
  stage: deploy-staging
  image: kubectl:latest
  script:
    - kubectl config use-context staging-cluster
    - kubectl set image deployment/user-auth-api-staging user-auth-api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/user-auth-api-staging
  environment:
    name: staging
    url: https://api-staging.company.com
  only:
    - develop

deploy-to-production:
  stage: deploy-production
  image: kubectl:latest
  script:
    - kubectl config use-context production-cluster
    - kubectl set image deployment/user-auth-api-prod user-auth-api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/user-auth-api-prod
  environment:
    name: production
    url: https://api.company.com
  when: manual
  only:
    - main
```

### 4.7 Infrastructure as Code 命名

#### Terraform 資源命名
```hcl
# main.tf - AWS 資源命名範例

# VPC 命名
resource "aws_vpc" "main_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "vpc-user-service-prod"
    Environment = "production"
    Project     = "user-service"
    Team        = "platform-engineering"
  }
}

# Subnet 命名
resource "aws_subnet" "public_subnet_1a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "subnet-public-1a-user-service-prod"
    Type = "public"
    AZ   = "us-west-2a"
  }
}

resource "aws_subnet" "private_subnet_1a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "us-west-2a"
  
  tags = {
    Name = "subnet-private-1a-user-service-prod"
    Type = "private"
    AZ   = "us-west-2a"
  }
}

# Security Group 命名
resource "aws_security_group" "web_server_sg" {
  name_prefix = "sg-web-server-"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main_vpc.id
  
  ingress {
    description = "HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "sg-web-server-user-service-prod"
  }
}

# EC2 Instance 命名
resource "aws_instance" "web_server" {
  count = 2
  
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.medium"
  
  subnet_id              = aws_subnet.public_subnet_1a.id
  vpc_security_group_ids = [aws_security_group.web_server_sg.id]
  
  user_data = file("${path.module}/scripts/install-web-server.sh")
  
  tags = {
    Name = "ec2-web-server-${count.index + 1}-user-service-prod"
    Role = "web-server"
    Index = count.index + 1
  }
}

# RDS Instance 命名
resource "aws_db_instance" "postgres_primary" {
  identifier = "rds-postgres-user-service-prod-primary"
  
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "userservice"
  username = "dbadmin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "rds-postgres-user-service-prod-final-snapshot"
  
  tags = {
    Name = "rds-postgres-user-service-prod-primary"
  }
}

# Load Balancer 命名
resource "aws_lb" "application_load_balancer" {
  name               = "alb-user-service-prod"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_1a.id, aws_subnet.public_subnet_1b.id]
  
  enable_deletion_protection = true
  
  tags = {
    Name = "alb-user-service-prod"
  }
}

# S3 Bucket 命名
resource "aws_s3_bucket" "user_uploads" {
  bucket = "company-user-uploads-prod-${random_string.bucket_suffix.result}"
  
  tags = {
    Name        = "s3-user-uploads-prod"
    Purpose     = "user-file-storage"
    Environment = "production"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
```

#### Ansible Playbook 命名
```yaml
# playbooks/deploy-user-service.yml
---
- name: Deploy

---

#### Ansible Playbook 命名
```yaml
# playbooks/deploy-user-service.yml
---
- name: Deploy User Service to Production Servers
  hosts: production_web_servers
  become: yes
  vars:
    service_name: user-auth-api
    service_version: "{{ ansible_service_version | default('latest') }}"
    deployment_environment: production
    
  tasks:
    - name: Create service directory structure
      file:
        path: "/opt/{{ service_name }}"
        state: directory
        owner: app
        group: app
        mode: '0755'
    
    - name: Download service configuration files
      template:
        src: "{{ item.src }}"
        dest: "/opt/{{ service_name }}/{{ item.dest }}"
        owner: app
        group: app
        mode: '0644'
      loop:
        - { src: 'config.production.yml.j2', dest: 'config.yml' }
        - { src: 'docker-compose.yml.j2', dest: 'docker-compose.yml' }
    
    - name: Pull latest docker image
      docker_image:
        name: "registry.company.com/platform/{{ service_name }}"
        tag: "{{ service_version }}"
        source: pull
    
    - name: Start service containers
      docker_compose:
        project_src: "/opt/{{ service_name }}"
        state: present
        services:
          - user-auth-api
          - redis-cache
          - postgres-db

# playbooks/setup-monitoring.yml
---
- name: Setup Monitoring Infrastructure
  hosts: monitoring_servers
  become: yes
  vars:
    prometheus_version: "2.40.0"
    grafana_version: "9.3.0"
    
  roles:
    - role: prometheus-server
      vars:
        prometheus_config_file: prometheus.production.yml
        prometheus_data_dir: /opt/prometheus/data
    
    - role: grafana-server
      vars:
        grafana_config_file: grafana.production.ini
        grafana_data_dir: /opt/grafana/data
```

#### Helm Chart 命名
```yaml
# charts/user-service/Chart.yaml
apiVersion: v2
name: user-service
description: User authentication and management service
type: application
version: 1.2.3
appVersion: "v1.2.3"
keywords:
  - authentication
  - user-management
  - api
home: https://github.com/company/user-service
sources:
  - https://github.com/company/user-service
maintainers:
  - name: Platform Engineering Team
    email: platform-engineering@company.com

# charts/user-service/values.yaml
# 預設值配置
nameOverride: ""
fullnameOverride: ""

image:
  repository: registry.company.com/platform/user-auth-api
  pullPolicy: IfNotPresent
  tag: "v1.2.3"

service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  name: http-api

ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.company.com
      paths:
        - path: /v1/auth
          pathType: Prefix
  tls:
    - secretName: user-service-tls
      hosts:
        - api.company.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# charts/user-service/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "user-service.fullname" . }}
  labels:
    {{- include "user-service.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "user-service.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "user-service.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: health
              containerPort: 8081
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health/live
              port: health
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: health
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### 4.8 環境特定命名策略

#### 多環境資源區分
```bash
# 環境前綴命名策略
# 格式：{environment}-{service}-{component}-{region}

# 開發環境
dev-user-api-app-us-west-2
dev-user-api-db-us-west-2
dev-user-api-cache-us-west-2

# 測試環境
test-user-api-app-us-west-2
test-user-api-db-us-west-2
test-user-api-cache-us-west-2

# 預發布環境
staging-user-api-app-us-west-2
staging-user-api-db-us-west-2
staging-user-api-cache-us-west-2

# 生產環境
prod-user-api-app-us-west-2
prod-user-api-db-us-west-2
prod-user-api-cache-us-west-2
```

#### 環境變數命名
```bash
# 應用程式環境變數命名
# 格式：{SERVICE}_{CATEGORY}_{SPECIFIC_NAME}

# 資料庫相關
USER_SERVICE_DB_HOST=postgres.prod.internal.company.com
USER_SERVICE_DB_PORT=5432
USER_SERVICE_DB_NAME=userservice
USER_SERVICE_DB_USERNAME=app_user
USER_SERVICE_DB_PASSWORD=${USER_SERVICE_DB_PASSWORD}
USER_SERVICE_DB_SSL_MODE=require
USER_SERVICE_DB_POOL_SIZE=20
USER_SERVICE_DB_TIMEOUT=30

# Redis 快取相關
USER_SERVICE_CACHE_HOST=redis.prod.internal.company.com
USER_SERVICE_CACHE_PORT=6379
USER_SERVICE_CACHE_PASSWORD=${USER_SERVICE_CACHE_PASSWORD}
USER_SERVICE_CACHE_DB=0
USER_SERVICE_CACHE_TTL=3600

# 應用程式設定
USER_SERVICE_APP_PORT=8080
USER_SERVICE_APP_HOST=0.0.0.0
USER_SERVICE_APP_LOG_LEVEL=info
USER_SERVICE_APP_METRICS_ENABLED=true
USER_SERVICE_APP_HEALTH_CHECK_PORT=8081

# JWT 相關
USER_SERVICE_JWT_SECRET=${USER_SERVICE_JWT_SECRET}
USER_SERVICE_JWT_EXPIRY=24h
USER_SERVICE_JWT_REFRESH_EXPIRY=168h

# 第三方服務
USER_SERVICE_EMAIL_PROVIDER=sendgrid
USER_SERVICE_EMAIL_API_KEY=${USER_SERVICE_EMAIL_API_KEY}
USER_SERVICE_NOTIFICATION_WEBHOOK_URL=${USER_SERVICE_NOTIFICATION_WEBHOOK_URL}

# 監控與日誌
USER_SERVICE_METRICS_ENDPOINT=/metrics
USER_SERVICE_LOG_FORMAT=json
USER_SERVICE_TRACE_ENABLED=true
USER_SERVICE_SENTRY_DSN=${USER_SERVICE_SENTRY_DSN}
```

### 4.9 災難復原與備份命名

#### 備份資源命名
```bash
# 資料庫備份命名
# 格式：backup-{service}-{type}-{timestamp}
backup-user-service-db-full-20240115-030000
backup-user-service-db-incremental-20240115-120000
backup-user-service-db-transaction-log-20240115-150000

# S3 備份 Bucket
company-backups-user-service-prod-us-west-2
company-backups-user-service-staging-us-west-2
company-disaster-recovery-user-service-prod-us-east-1

# 快照命名
snap-user-service-db-prod-20240115-030000
snap-user-service-app-volume-prod-20240115-030000
```

#### 災難復原計畫命名
```yaml
# disaster-recovery/user-service-dr-plan.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-service-dr-plan
  namespace: disaster-recovery
data:
  recovery-time-objective: "4h"
  recovery-point-objective: "1h"
  primary-region: "us-west-2"
  secondary-region: "us-east-1"
  backup-schedule: "0 3 * * *"  # 每日凌晨 3 點
  
  restoration-steps: |
    1. Verify secondary region infrastructure
    2. Restore database from latest backup
    3. Update DNS records to point to secondary region
    4. Scale up application instances
    5. Run health checks and validation tests
    6. Notify operations team of successful failover
```

### 4.10 安全與合規命名

#### Security Group 與網路 ACL 命名
```bash
# Security Group 命名慣例
sg-web-tier-public-prod           # Web 層公用安全群組
sg-app-tier-private-prod          # 應用程式層私用安全群組
sg-db-tier-restricted-prod        # 資料庫層限制存取安全群組
sg-bastion-host-admin-prod        # 堡壘主機管理員存取
sg-monitoring-internal-prod       # 監控服務內部存取

# Network ACL 命名
nacl-public-subnet-prod           # 公用子網路 ACL
nacl-private-subnet-prod          # 私用子網路 ACL
nacl-database-subnet-prod         # 資料庫子網路 ACL
```

#### 憑證與金鑰管理命名
```bash
# SSL/TLS 憑證命名
cert-api-company-com-prod         # API 域名憑證
cert-admin-company-com-prod       # 管理介

---

#### Ansible Playbook 命名
```yaml
# playbooks/deploy-user-service.yml
---
- name: Deploy User Service to Production Servers
  hosts: production_web_servers
  become: yes
  vars:
    service_name: user-auth-api
    service_version: "{{ ansible_service_version | default('latest') }}"
    deployment_environment: production
    
  tasks:
    - name: Create service directory structure
      file:
        path: "/opt/{{ service_name }}"
        state: directory
        owner: app
        group: app
        mode: '0755'
    
    - name: Download service configuration files
      template:
        src: "{{ item.src }}"
        dest: "/opt/{{ service_name }}/{{ item.dest }}"
        owner: app
        group: app
        mode: '0644'
      loop:
        - { src: 'config.production.yml.j2', dest: 'config.yml' }
        - { src: 'docker-compose.yml.j2', dest: 'docker-compose.yml' }
    
    - name: Pull latest docker image
      docker_image:
        name: "registry.company.com/platform/{{ service_name }}"
        tag: "{{ service_version }}"
        source: pull
    
    - name: Start service containers
      docker_compose:
        project_src: "/opt/{{ service_name }}"
        state: present
        services:
          - user-auth-api
          - redis-cache
          - postgres-db

# playbooks/setup-monitoring.yml
---
- name: Setup Monitoring Infrastructure
  hosts: monitoring_servers
  become: yes
  vars:
    prometheus_version: "2.40.0"
    grafana_version: "9.3.0"
    
  roles:
    - role: prometheus-server
      vars:
        prometheus_config_file: prometheus.production.yml
        prometheus_data_dir: /opt/prometheus/data
    
    - role: grafana-server
      vars:
        grafana_config_file: grafana.production.ini
        grafana_data_dir: /opt/grafana/data
```

#### Helm Chart 命名
```yaml
# charts/user-service/Chart.yaml
apiVersion: v2
name: user-service
description: User authentication and management service
type: application
version: 1.2.3
appVersion: "v1.2.3"
keywords:
  - authentication
  - user-management
  - api
home: https://github.com/company/user-service
sources:
  - https://github.com/company/user-service
maintainers:
  - name: Platform Engineering Team
    email: platform-engineering@company.com

# charts/user-service/values.yaml
# 預設值配置
nameOverride: ""
fullnameOverride: ""

image:
  repository: registry.company.com/platform/user-auth-api
  pullPolicy: IfNotPresent
  tag: "v1.2.3"

service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  name: http-api

ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.company.com
      paths:
        - path: /v1/auth
          pathType: Prefix
  tls:
    - secretName: user-service-tls
      hosts:
        - api.company.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### 4.8 環境特定命名策略

#### 多環境資源區分
```bash
# 環境前綴命名策略
# 格式：{environment}-{service}-{component}-{region}

# 開發環境
dev-user-api-app-us-west-2
dev-user-api-db-us-west-2
dev-user-api-cache-us-west-2

# 測試環境
test-user-api-app-us-west-2
test-user-api-db-us-west-2
test-user-api-cache-us-west-2

# 預發布環境
staging-user-api-app-us-west-2
staging-user-api-db-us-west-2
staging-user-api-cache-us-west-2

# 生產環境
prod-user-api-app-us-west-2
prod-user-api-db-us-west-2
prod-user-api-cache-us-west-2
```

#### 環境變數命名
```bash
# 應用程式環境變數命名
# 格式：{SERVICE}_{CATEGORY}_{SPECIFIC_NAME}

# 資料庫相關
USER_SERVICE_DB_HOST=postgres.prod.internal.company.com
USER_SERVICE_DB_PORT=5432
USER_SERVICE_DB_NAME=userservice
USER_SERVICE_DB_USERNAME=app_user
USER_SERVICE_DB_PASSWORD=${USER_SERVICE_DB_PASSWORD}
USER_SERVICE_DB_SSL_MODE=require
USER_SERVICE_DB_POOL_SIZE=20
USER_SERVICE_DB_TIMEOUT=30

# Redis 快取相關
USER_SERVICE_CACHE_HOST=redis.prod.internal.company.com
USER_SERVICE_CACHE_PORT=6379
USER_SERVICE_CACHE_PASSWORD=${USER_SERVICE_CACHE_PASSWORD}
USER_SERVICE_CACHE_DB=0
USER_SERVICE_CACHE_TTL=3600

# 應用程式設定
USER_SERVICE_APP_PORT=8080
USER_SERVICE_APP_HOST=0.0.0.0
USER_SERVICE_APP_LOG_LEVEL=info
USER_SERVICE_APP_METRICS_ENABLED=true
USER_SERVICE_APP_HEALTH_CHECK_PORT=8081

# JWT 相關
USER_SERVICE_JWT_SECRET=${USER_SERVICE_JWT_SECRET}
USER_SERVICE_JWT_EXPIRY=24h
USER_SERVICE_JWT_REFRESH_EXPIRY=168h

# 第三方服務
USER_SERVICE_EMAIL_PROVIDER=sendgrid
USER_SERVICE_EMAIL_API_KEY=${USER_SERVICE_EMAIL_API_KEY}
USER_SERVICE_NOTIFICATION_WEBHOOK_URL=${USER_SERVICE_NOTIFICATION_WEBHOOK_URL}

# 監控與日誌
USER_SERVICE_METRICS_ENDPOINT=/metrics
USER_SERVICE_LOG_FORMAT=json
USER_SERVICE_TRACE_ENABLED=true
USER_SERVICE_SENTRY_DSN=${USER_SERVICE_SENTRY_DSN}
```

### 4.9 災難復原與備份命名

#### 備份資源命名
```bash
# 資料庫備份命名
# 格式：backup-{service}-{type}-{timestamp}
backup-user-service-db-full-20240115-030000
backup-user-service-db-incremental-20240115-120000
backup-user-service-db-transaction-log-20240115-150000

# S3 備份 Bucket
company-backups-user-service-prod-us-west-2
company-backups-user-service-staging-us-west-2
company-disaster-recovery-user-service-prod-us-east-1

# 快照命名
snap-user-service-db-prod-20240115-030000
snap-user-service-app-volume-prod-20240115-030000
```

#### 災難復原計畫命名
```yaml
# disaster-recovery/user-service-dr-plan.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-service-dr-plan
  namespace: disaster-recovery
data:
  recovery-time-objective: "4h"
  recovery-point-objective: "1h"
  primary-region: "us-west-2"
  secondary-region: "us-east-1"
  backup-schedule: "0 3 * * *"  # 每日凌晨 3 點
  
  restoration-steps: |
    1. Verify secondary region infrastructure
    2. Restore database from latest backup
    3. Update DNS records to point to secondary region
    4. Scale up application instances
    5. Run health checks and validation tests
    6. Notify operations team of successful failover
```

### 4.10 安全與合規命名

#### Security Group 與網路 ACL 命名
```bash
# Security Group 命名慣例
sg-web-tier-public-prod           # Web 層公用安全群組
sg-app-tier-private-prod          # 應用程式層私用安全群組
sg-db-tier-restricted-prod        # 資料庫層限制存取安全群組
sg-bastion-host-admin-prod        # 堡壘主機管理員存取
sg-monitoring-internal-prod       # 監控服務內部存取

# Network ACL 命名
nacl-public-subnet-prod           # 公用子網路 ACL
nacl-private-subnet-prod          # 私用子網路 ACL
nacl-database-subnet-prod         # 資料庫子網路 ACL
```

#### 憑證與金鑰管理命名
```bash
# SSL/TLS 憑證命名
cert-api-company-com-prod         # API 域名憑證
cert-admin-company-com-prod       # 管理介面憑證
cert-wildcard-company-com-prod    # 萬用字元憑證

# KMS 金鑰命名
kms-user-service-encryption-prod  # 用戶服務加密金鑰
kms-database-encryption-prod      # 資料庫加密金鑰
kms-backup-encryption-prod        # 備份加密金鑰

# Secrets Manager 命名
secret-user-service-db-credentials-prod
secret-user-service-api-keys-prod
secret-user-service-jwt-signing-key-prod
```

---

# 命名規範研究報告（第五章至第十章補完）

---

## 第五章 基礎設施即程式碼命名規範

### 5.1 IaC 命名原則與重要性

在現代 DevOps 實踐中，「基礎設施即程式碼（Infrastructure as Code, IaC）」已成為管理與部署雲端基礎設施的標準手段。IaC 使得基礎設施的定義、部署和變更都能像傳統應用程式碼一樣，接受版本控制、審查、重複執行與自動化部署[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://ithelp.ithome.com.tw/articles/10387507?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "1")。然而，隨著 IaC 規模擴大，資源命名不當會導致資源混淆、權限配置錯誤、狀態檔案損毀等嚴重後果。因此，命名規範直接影響到自動化與基礎設施的可維護性。

一套良好的命名規範須兼顧以下原則：
- **唯一性與可辨識性**：每個資源名稱必須在其命名空間內唯一且能高效溝通用途。
- **一致性**：所有模組、資源、變數都應遵循統一的規則（如小寫字母加底線、單數/複數對映、不可混用大小寫）。
- **描述性**：名稱需直接反映資源屬性，例如角色、用途、所屬環境。
- **可擴充性與可適應性**：預留必要的維度（如專案、環境、層級等），便於組織未來擴增。
- **可自動化性**：便於自動化腳本處理、校驗或生成。

針對實務，知名開發者 Devin Liu 在 HackMD 章節中推薦類別、屬性、常數等均以 PascalCase 命名，參數與欄位採用 camelCase，資料庫與底層資源可用 snake_case，而網址等場合則採 kebab-case，以便與現代語言和工具鏈一致。

### 5.2 Terraform 資源與模組命名慣例

Terraform 廣泛用於跨雲端平台的 IaC。有效的命名慣例可降低重構、環境隔離及多團隊協作的風險[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://www.terraform-best-practices.com/zh/naming?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "2")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/gitblog_00673/article/details/151257639?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "3")。

**Terraform 命名實踐建議**：
- **資源塊名稱（Resource Name）**：
    - 格式：`resource "<provider>_<type>" "<logical_name>" { ... }`
    - `<provider>_<type>`一律用小寫底線，如`aws_s3_bucket`。
    - `<logical_name>`可用 single, plural, concise，建議不可冗餘（如`public`、`db`、`web` 而非`public_s3_bucket`）。
    - **範例**：
      ```hcl
      resource "aws_route_table" "public" { ... }
      resource "aws_nat_gateway" "this" { ... }
      ```

- **變數/輸出/資料源命名**：
    - 變數名若型別為 list/map 要用複數。
    - 必須加上`description`。
    - 避免重複 provider/type，直接使用描述性命名如 `db_subnet_group`。

- **tags/labels**：
    - AWS 支援時，統一在 blocks 最後，用 Name 與更具備分群、清理便捷性之標籤（可 include 環境、功能）。
    - 範例：
      ```hcl
      tags = { Name = "web-prod-api" }
      ```

- **name vs name_prefix 的使用**：
    - `name`：用於需穩定唯一名之永久資源（如 S3）。
    - `name_prefix`：用於臨時、需大批量自動產生資源，避免名稱衝突。
    - 不可同時指定兩者，否則編譯失敗。

- **模組（Module）命名**：
    - 標準為 `module "<logical_name>" { source = ... }`，命名建議帶上功能與環境，如 `vpc_prod`。
    - 內部資源命名則帶入模組名，利於追蹤。
    - **結構示例**：
      ```
      main.tf
      ├── resource "aws_nat_gateway" "this" {...}
      ├── resource "aws_route_table" "private" {...}
      └── resource "aws_instance" "bastion" {...}
      ```

- **專案與環境前綴**：
    - 建議明示專案、功能、環境：
      - `{project}-{env}-{component}`（如`ai-prod-redis`）

**行業規範坑點與自動化補救**：
- 禁用資源名稱的硬編碼與不一致大小寫/分隔符（建議 `_`）。
- 利用 Lint 工具或 IDE 插件做靜態分析（如 Semgrep、帶有正規表示的特製 formatters）。
- 以 Git pre-commit hook 強制格式檢查。
- 出現重構需求時，先用自動腳本批次處理 state 檔對照與資源導入。

### 5.3 AWS CloudFormation 與 CDK 命名策略

AWS CloudFormation 與 CDK 均可管理 AWS 基礎設施，命名規範有助於避免資源重覆、運維混淆及版本管理難題[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://docs.aws.amazon.com/zh_tw/AWSCloudFormation/latest/TemplateReference/aws-properties-name.html?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "4")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://docs.aws.amazon.com/zh_tw/cdk/v2/guide/projects.html?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "5")。

- **CloudFormation 命名特點**：
    - 大多數資源可自訂名稱，預設則自動生成（如`Stack-Resource-randomid`）。
    - 若自訂，需於範本中明確指定且不可重複；命名僅可用 ASCII 字母數字與中橫線，不可以中橫線結尾，且 63 字元內。
    - yaml/json property 需要類似：
      ```yaml
      Properties:
        TableName: "orders-prod-v1"
      ```

- **CDK 命名與專案結構**：
    - 建議文件結構以專案為頂層 + stack 名稱，例如：
      ```
      /lib/my-cdk-ts-project-stack.ts
      /bin/my-cdk-ts-project.ts
      ```
    - 二次開發時，Stack id 應明確列出如`MyCdkProdStack`。
    - CDK 程式碼內資源識別通常帶有 stack/cluster/功能，便於 versioning 及資源查找。

- **環境維度標註**：
    - 利用 Stack 變數與 tags，在全區管理下可依照不同 Project/Env/System 維護資源唯一性。
    - 建議所有重要資源皆加 `Environment`、`Project`、`Module` 標籤，提升搜尋與後期維護效率。

### 5.4 實務建議與落地範例

- 制定 IaC 命名規範文件時，需先分類齊全（資源、模組、目錄、專案、環境等）。
- 推動公司層級模組倉庫，強制命名規則審核與自動化腳本導入。
- 以`lint`與`pre-commit`自動校驗取代單一人工 code review。
- 嚴格區分不同環境（dev、staging、prod）資源，保證 tag 與命名方式一組即能唯一定位。
- 在 Git Flow/PR 合併時加 CI 檢查命名規範，都未通過則拒絕進入主線。

---

## 第六章 CI/CD 流水線命名結構與最佳實踐

### 6.1 CI/CD 流水線命名的價值與原則

CI/CD（Continuous Integration/Continuous Delivery）流水線貫穿於現代開發到部署的每個環節，良好的命名規範對於代碼回溯、異常定位、任務自動調度極為關鍵。命名隨著自動化深度提升，直接關係到團隊溝通、監控可追蹤性與流程治理效率。

最核心原則有：
- **語意明確、可識別**：名稱即行為，見名知義，讓新成員一眼能理解此觸發內容、所有階段功能。
- **分層一致性**：根據專案、產品線、任務性質分層規劃；所有 pipeline、stage、job 均應統一命名規則。
- **環境維度明示**：明確標註 target environment，如 dev/test/staging/prod。
- **版本與迭代可追溯**：支援版本控制與多環境部署的資料定位。

### 6.2 Jenkins Pipeline 命名規範

Jenkins 是主流的自動化流程引擎，支持 declarative pipeline 及 scripted pipeline[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://www.jenkins.io/zh/doc/book/pipeline/syntax/?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "6")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://zhuanlan.zhihu.com/p/583812704?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "7")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/zero_open/article/details/137816238?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "8")。

**命名規範建議**：
- pipeline 名稱與專案或產品線一致（如 `AI Search API - Staging - Release`）。
- stage：以動作為主語，首字大寫，明確說明功能，例如 `Build`、`Unit Test`、`Deploy to Prod`。
- job 名稱遵從「動作-對象-環境」結構，如 `publish-image-dev`。
- agent 標籤（如 `docker-maven`、`nodejs-14`）須描述性，清楚反映運作平台或用途。
- parameters/environment 參數（例：`DEPLOY_ENV`、`DEBUG_ENABLE`）必用全大寫 undeline 分隔。
- 並行 stage：加入具體名稱區分，如 `Test-Chrome`、`Test-Firefox`。

**範例**：
```groovy
pipeline {
  agent any
  stages {
    stage('Build') {
      steps { ... }
    }
    stage('Test') {
      steps { ... }
    }
    stage('Deploy to Production') {
      steps { ... }
    }
  }
}
```

- 建議利用 `input`、`triggers` 等指令時，對每個自動或手動執行條件明確命名，如 `cron('H 4 * * 1-5')`。

### 6.3 GitLab CI/CD 與 GitHub Actions 工作流程命名

**GitLab CI/CD**（`.gitlab-ci.yml`）規則建議[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://hackmd.io/@CloudyWing/Hym3ZoBT1g?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "9")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://ithelp.ithome.com.tw/articles/10344451?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "10")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/weixin_47877869/article/details/145616371?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "11")：
- pipeline/workflow: 可定義整體標題，參數如 `workflow: name: "deploy-main-production"`。
- stage: 推薦採用 `build`、`test`、`deploy`、`quality`、`notify` 等動詞性名稱，便於橫向比較及自動化擴展。
- job: 跟 Jenkins 的 `動作-對象-環境`，如 `build-backend-image`、`test-e2e-staging`、`deploy-prod`.
- 變數名稱全大寫底線分隔（`DOCKER_IMAGE_NAME`）。
- 多環境可用 `deploy-dev`、`deploy-staging`、`deploy-prod` 等明確區分，避免重覆。
- artifacts/cache:
  - 名稱應與工作階段關聯，如 `build` 階段產出 `build_artifacts`，快取鍵帶 pipeline id 或 commit hash 防止覆蓋衝突。
- 檔案命名支援 include/inherit，如 `.gitlab-ci-build.yml`、`.gitlab-ci-test.yml`.
- template/template yaml 用 `_template`、`.` 前綴標明不可直接執行，僅供引用。

**GitHub Actions** 工作流命名規則相似，建議 workflows 以產品模組 + 流水線功能描述，如 `build-and-release-python-sdk.yml`；jobs 及 steps 也採直譯式語意。

 ### 6.4 命名規範保障實務

- **命名治理流程**：
    - 設定專案模板，強制每一條流水線從模板複製。
    - 新增/變更 pipeline/job 做事前審覈，PR review check。
    - 使用自動命名規則檢查（如淺入預設插件/腳本）。
    - 定期審查、優化已上線 pipeline 與 job 名稱，淘汰舊有非標準命名。
    - 文件化所有命名規範於專屬手冊並版本管理。

--- 

## 第七章 企業級命名治理策略與框架

### 7.1 企業命名治理的挑戰

企業在大規模 DevOps、雲端、微服務與資料治理背景下，命名規範必須升級為全組織協作框架。一旦命名混亂將造成以下問題[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://zhuanlan.zhihu.com/p/502755740?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "12")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://www.esensoft.com/industry-news/dx-51865.html?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "13")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/qq_20245171/article/details/145456548?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "14")：
- 多團隊導致命名標準分歧，產生跨部門溝通失靈。
- 自動化串接、資源掃描腳本與監控混亂，導致維護與查錯成本浮增。
- 版本管理與數據追蹤困難，產生安全燈號遺漏、權限風險。

### 7.2 命名治理策略與執行框架

**命名治理策略包含**：
- **標準化框架（如 DAMA, DCMM）**：主框架需包括標準、流程、組織、工具與監督等機制。
- **命名規範委員會**：包含開發、維運、資訊安全、合規與產品經理共同參與，定期審查並修訂規範。
- **策略文件化**：所有命名規範皆需以規章、章則、實作建議文檔明文化，並加入知識庫。
- **自動化與工具支持**：導入靜態檢查、模板驗證、Policy as Code（如 Open Policy Agent）支援持續治理。
- **版本管理制度**：定期評估、發布與公告規則變動，並保持所有開發及維運文件一致同步（見下節）。

**企業命名治理框架表（示意）**：

| 維度      | 具體措施與工具範例     | 推行要點                |
|--|--|--|
| 組織   | 設專責團隊，制定與稽核   | 決策權限明確化，定時培訓 |
| 流程   | Pull Request 檢查、CI 命名 Lint | 無通過不得合併 |
| 工具鏈 | GitLab/Jenkins pre-hook、命名檢查腳本 | 自動偵錯與即時回饋 |
| 文檔   | 規範文件、命名查詢平台   | 保證知識傳承、查找便利   |
| 持續改善 | 收集反饋定期盤點         | 迭代調整策略             |

### 7.3 命名策略文件化與版本管理

- 所有命名規範、樣板、範例須進行專案級或組織級版本控制，儲存在企業 Git/ConfigCenter。
- 規則手冊需包含：
    - 初始生效日期、歷次變更摘要、副本號。
    - 主要命名慣例。
    - 例外處理申請流程。
    - 廢棄與變更命名流程/工具介紹。
- 每一年定期盤點與回顧，邀請團隊 feedback，有必要則重大版本升級並廣泛培訓。

### 7.4 行業框架與最佳實踐

- DAMA、CMMI、ITSS、DCMM 等指引資產命名規範、資料質量標準、數據治理架構[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://zhuanlan.zhihu.com/p/502755740?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "12")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://www.esensoft.com/industry-news/dx-51865.html?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "13")。
- 國際組織多重視從策略到落地工具鏈整合，建議在本地導入時先小規模試行，逐步推廣至全公司。
- 實際案例顯示，專門設定命名稽核指標能抑制命名品質劣化，亦易自動產生全域資源圖、有助後續資安追查。

---

## 第八章 命名實戰項目演練

### 8.1 微服務專案命名演練

以微服務架構為例，微服務名、API endpoint、Database table、消息佇列等命名都應一致遵循組織規範，以利日後運維、部署與異常追蹤[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/fwk19840301/article/details/79488507?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "15")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://developer.aliyun.com/article/1279379?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "16")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blogs.vmware.com/vmware-taiwan/2022/12/15/%e9%9b%b2%e5%8e%9f%e7%94%9f%e6%99%82%e4%bb%a3%e4%b8%8b%e5%be%ae%e6%9c%8d%e5%8b%99%e6%9e%b6%e6%a7%8b%e6%bc%94%e9%80%b2%e4%b9%8b%e8%b7%af-10/?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "17")。

#### 實務建議：
- 微服務名結構：`<組織>-<業務線>-<功能模組>`，如 `ai-finance-billing`。
- API 路徑： `/api/v1/{service}/{resource}`，結合版本與功能。
- Database/Topic/Queue：同樣以三段式結構，保持小寫與底線分隔。

**範例**：
```yaml
service-name: ai-finance-billing
api: /api/v1/ai-finance-billing/payments
db-table: billing_transactions
mq-topic: ai-finance-billing-payments
```

### 8.2 雲原生環境命名實作

雲原生（Cloud Native）環境下所有資源如 Cluster、Pod、Ingress、Service、容器映像都應有命名準則[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://s.itho.me/ccms_slides/2024/7/8/d52ab517-6cbf-4bec-af58-4f59b0501487.pdf?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "18")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://carger.tips/%e9%9b%b2%e5%8e%9f%e7%94%9f%e6%87%89%e7%94%a8%e9%96%8b%e7%99%bc%e5%85%a5%e9%96%80%e6%8c%87%e5%8d%97-docker-k8s-%e5%92%8c-service-mesh-%e6%9e%b6%e6%a7%8b%e8%a7%a3%e6%9e%90?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "19")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://docker.robertchang.me/images/?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "20")。

#### Kubernetes 資源命名範例：
- Cluster: `open-data-cluster`
- Namespace: `<product>-<env>` (如 `billing-prod`)
- Pod: `<service>-app` (如 `ai-backend-app`)
- Service: `<service>-service` (如 `ai-backend-service`)
- Ingress: `<service>-ingress`
- 容器映像名稱: `{registry}/{project}/{service}:{tag}`

### 8.3 CI/CD 流水線與觸發器命名演練

實作時建議全流程使用「專案-模組-環境-功能」命名，例如：
- Jenkinsfile: `ci-ai-backend-staging-build-release`
- GitLab CI/CD workflow: `workflow: name: "ai-backend-staging-pipeline"`
- Job: `test-e2e-prod`

**實務演練要點**：
- 主分支自動化流水線需明示用途。
- 多環境部署時，由參數命名傳遞 ensure fully scoped（例：`$DEPLOY_ENV`）。
- Artifacts/Cache 加入 pipeline hash 或分支標示。

### 8.4 命名規範推行與落地經驗

- 定期組織跨部門命名規範工作坊，從典型失敗案例（如名稱重複、未明示環境）反推調整。
- 提供自動化命名生成模組（如 Spinnaker/Argo/Harness pipeline templates），避免手動疏漏[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://blog.csdn.net/gitblog_00606/article/details/152004810?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "21")。
- 結合 PR review、CI 檢查與 README 強化新成員 onboarding 成功率。
- 推動文檔化與查詢工具，加速命名規範應用與問題自查。

---

## 第九章 命名策略工具與自動化

### 9.1 工具鏈整合命名策略

現代 DevOps 工具鏈包括 Git、Jenkins、GitHub Actions、GitLab CI/CD、Docker、Kubernetes、Terraform、Ansible、Prometheus、Grafana 等[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://carger.tips/%e7%b0%a1%e5%96%ae%e6%98%93%e6%87%82%e7%9a%84-devops-%e8%87%aa%e5%8b%95%e5%8c%96%e5%b7%a5%e5%85%b7%e9%8f%88%e5%85%a5%e9%96%80%e6%8c%87%e5%8d%97?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "22")。命名策略須橫跨所有工具與自動化流程。

- **自動化檢查工具**：開發封裝命名 lint module，如 terraform-lint、yamllint、GitHub Super-Linter。
- **命名規範即程式碼**：用 Policy as Code/OPA 解決複雜資源的命名規則驗證。
- **跨工具鏈成本控管**：透過 tags/labels/命名模板規範，配合可視化儀表板（如 ELK、Prometheus/Grafana）一致追蹤、審計資源。

### 9.2 命名自動化與品質檢查工具

- **靜態程式掃描器**：CI 觸發時，以定制 regex 、語法樹解析檢查資源/流水線是否符合命名需求。
- **命名生成工具**：輸入專案、模組、環境、功能參數，自動 output 統一格式名稱。
- **自動審查 CLI/IDE 插件**：如 VSCode、JetBrains Linter，不通過則拒絕 push/merge。
- **企業級命名管理平台**：集中式管理所有命名規則、範本、範例、API 查詢，降低 onboarding 成本。
- **比對篩檢腳本範例**（以 Bash for Kubernetes + Spinnaker）：
  ```bash
  function generate_resource_name() {
    env=$1; app=$2; env_type=$3
    echo "${env}-${app}-${env_type}-v${VERSION}"
  }
  ```
- **Pipeline 命名安全網**：設計自動命名模板 + 規則變更快篩系統，降低人為誤差。

### 9.3 工具與命名規範對應表

| 工具         | 支援命名規範方式            | 實踐建議                           |
|--------------|------------------------|------------------------------|
| Terraform    | 模組/資源名稱、tags   | 全小寫底線，專案-環境-類型      |
| Jenkins CI/CD| pipeline/stage/job 名   | 動作-對象-環境，流水線模板繼承   |
| GitLab CI    | stage, job, artifacts | yml include 與名稱前綴統一     |
| Kubernetes   | cluster、namespace、pod/service | rfc1123 格式、小寫 + `-`         |
| Docker       | 映像檔/volume/container| `project-service-env:tag`     |
| AWS CDK      | stack id/bucket name   | PascalCase 及大寫環境 tag       |

### 9.4 自動化推進關鍵步驟

- 初始化導入時強制資源/流程/代碼三層都加註明命名標準。
- CI/CD 預設加命名品質檢查，不達標 auto block build/deploy。
- 每次導入新工具時，先針對命名流程做映射測試模板。
- 重要命名規則變更走 PDCA 流程：規劃、執行、自動驗證、定期修訂。

---

## 第十章 持續改進與命名維護實務

### 10.1 持續改進理念與流程

命名規範不可能一次到位，其最佳實踐來自持續優化迭代[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://ahaslides.com/zh-TW/blog/continuous-improvement-examples/?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "23")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://www.managertoday.com.tw/articles/view/55730?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "24")。企業/團隊應參考 PDCA(R)（Plan-Do-Check-Act-Record）循環：
- **Plan**：擬定命名規範、實作方案、驗證目標。
- **Do**：落地執行、產出樣本、啟動自動化腳本。
- **Check**：回顧執行結果、收集團隊反饋、審查例外狀況。
- **Act**：針對實務發現，修改命名規範並高週期發佈。
- **Record**：紀錄所有成功、失敗、例外及原因，供知識管理及經驗複製。

### 10.2 命名維護週期與知識傳承

- **定期審核與盤點**：如每季進行命名規範大盤點，搭配報表工具分析出現頻率最高的潛在規範問題（如重名、命名過長、未明示環境等）。
- **知識報告/回饋機制**：設置回饋頻道（例：Confluence comment、內部工單系統），讓所有開發/運維成員主動回報疑義。
- **培訓與溝通**：新規則施行時，必須以線上/線下培訓、視頻教學、標準作業手冊(SoP)加快全員熟悉與接受。
- **自動提醒與預警**：利用自動腳本抓取違規命名，自動回報管理員或責任團隊。

### 10.3 命名規範持續迭代機制實例

- **範例**：某大型金融機構在2019年導入命名規範時，先以 pre-commit linter 監管所有 IaC、Jenkinsfile、Kubernetes yaml 檔案。每回季度由架構委員會召開命名品質回顧會，根據異常案例修訂策略，並於 README.md 及內部 wiki 公告新規定。團隊可於 Slack/Teams 上提交建議，經審核納入下期回顧。

### 10.4 未來展望與建議

- 不斷強化「命名策略即程式碼」哲學，主張所有命名規範都以腳本化、策略化方式自動驗證落地。
- 密切關注工具鏈更新動態，及時調整策略與文件。
- 推廣「透明自動化命名治理」文化，使每位成員皆能知易行從、反饋即時。
- 在組織規模擴張時，考慮引入 AI 助力命名建議與檢查、自動產生資源唯一名稱。

---

# 總結

本報告從基礎設施即程式碼到 CI/CD、企業級治理、工具自動化、實戰案例及持續改善，系統性總結了現代 DevOps 流程中命名規範的全方位應用與最佳實踐。透過建立嚴謹的一致性命名規範並結合自動化工具與持續改進循環，企業才能在複雜快速演進的雲原生與自動化時代，穩健、高效地成長與應對各種 IT 挑戰。以上內容可作為未來擬定、實做與治理 DevOps/Cloud 基礎設施命名標準的重要參考依據。

---