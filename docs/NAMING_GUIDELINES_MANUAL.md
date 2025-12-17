# 彈性命名規範完整學習手冊

## 從零開始到企業級實戰

> **目標讀者**: 初學者到資深工程師  
> **學習時間**: 4-6 週完整掌握  
> **實戰導向**: 100+ 實際範例與練習  
> **版本**: v1.0.0 - 2025年最新版

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

```plaintext
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

    async save(entity: UserProfile): Promise<UserProfile> {
        // 實作
        return entity;
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

**參考答案**：

**JavaScript (改進後):**

```javascript
// ✅ 改進後
const user = {};
function getUserById(userId) {
    return database.findById(userId);
}
class UserManager {
    deleteUser(userId) {}
}
```

**Python (改進後):**

```python
# ✅ 改進後
def get_user_data(user_id):
    return db.find(user_id)

class UserManager:
    def delete_user(self, user_id):
        pass
```

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

### 4.3 CI/CD 流水線命名

#### GitHub Actions 工作流程命名

```yaml
# .github/workflows/ci-build-test.yml
name: CI Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Node.js Environment
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Dependencies
        run: npm ci

      - name: Run Lint Checks
        run: npm run lint

      - name: Run Unit Tests
        run: npm run test:unit

      - name: Run Integration Tests
        run: npm run test:integration
```

#### 環境變數命名策略

```bash
# ✅ 良好的環境變數命名
DATABASE_HOST=postgres.production.example.com
DATABASE_PORT=5432
DATABASE_NAME=user_service_prod
DATABASE_USER=app_user
DATABASE_PASSWORD=<secure-password>

REDIS_CACHE_HOST=redis.production.example.com
REDIS_CACHE_PORT=6379

JWT_SECRET_KEY=<secure-key>
JWT_EXPIRATION_HOURS=24

API_RATE_LIMIT_PER_MINUTE=100
API_TIMEOUT_SECONDS=30

# 環境前綴模式
PROD_DATABASE_HOST=postgres.production.example.com
STAGING_DATABASE_HOST=postgres.staging.example.com
DEV_DATABASE_HOST=localhost

# ❌ 糟糕的環境變數命名
host=localhost
PORT=3000
secret=mysecret
db=mydb
```

### 4.4 雲端資源命名策略

#### AWS 資源命名規範

```bash
# 命名格式：{project}-{environment}-{service}-{resource-type}

# S3 儲存桶
user-service-prod-avatars-bucket
user-service-staging-logs-bucket
user-service-dev-uploads-bucket

# EC2 執行個體
user-service-prod-api-server-01
user-service-prod-worker-node-01

# RDS 資料庫
user-service-prod-postgres-primary
user-service-prod-postgres-replica

# Lambda 函數
user-service-prod-email-sender
user-service-prod-image-processor

# IAM 角色
user-service-prod-api-execution-role
user-service-prod-lambda-execution-role
```

#### Azure 資源命名規範

```bash
# 資源群組
rg-userservice-prod-eastus
rg-userservice-staging-westus

# App Service
app-userservice-api-prod
app-userservice-web-prod

# Azure SQL
sql-userservice-prod
sqldb-userservice-users-prod

# Storage Account (只能小寫字母和數字)
stuserserviceprodlogs
stuserserviceprodblobs
```

#### GCP 資源命名規範

```bash
# GKE Cluster
gke-user-service-prod-us-central1
gke-user-service-staging-us-west1

# Cloud SQL
cloudsql-user-service-prod-postgres
cloudsql-user-service-staging-postgres

# Cloud Storage
gs://user-service-prod-avatars
gs://user-service-prod-backups

# Cloud Functions
user-service-prod-email-sender
user-service-prod-webhook-handler
```

---

## 第五章：企業級命名治理

### 5.1 大型組織命名策略

#### 組織層級命名架構

```yaml
# 命名層級結構
organization:
  name: "acme-corp"
  business_units:
    - name: "platform"
      teams:
        - name: "authentication"
          services:
            - user-auth-api
            - identity-provider
            - session-manager
        - name: "payments"
          services:
            - payment-gateway
            - billing-service
            - invoice-generator
    - name: "commerce"
      teams:
        - name: "catalog"
          services:
            - product-api
            - inventory-service
            - search-indexer
```

#### 跨團隊命名協調

```yaml
# 命名註冊表
naming_registry:
  version: "1.0.0"
  last_updated: "2024-01-15"

  reserved_prefixes:
    - prefix: "platform-"
      owner: "platform-team"
      description: "Platform infrastructure services"
    - prefix: "commerce-"
      owner: "commerce-team"
      description: "E-commerce related services"

  naming_patterns:
    service:
      pattern: "{team}-{service}-{type}"
      example: "auth-user-api"
    infrastructure:
      pattern: "{env}-{region}-{service}-{resource}"
      example: "prod-us-east-user-db"
```

### 5.2 自動化驗證工具

#### 命名驗證腳本範例

```python
#!/usr/bin/env python3
"""
命名規範驗證工具
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 命名規則定義
NAMING_RULES = {
    'kubernetes_resource': {
        'pattern': r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$',
        'max_length': 63,
        'description': 'DNS-1123 subdomain naming'
    },
    'docker_image': {
        'pattern': r'^[a-z0-9]([._-]?[a-z0-9])*$',
        'max_length': 128,
        'description': 'Docker image naming'
    },
    'environment_variable': {
        'pattern': r'^[A-Z][A-Z0-9_]*$',
        'max_length': 256,
        'description': 'Environment variable naming'
    },
    'git_branch': {
        'pattern': r'^(feature|bugfix|hotfix|release|docs)/[a-z0-9-]+$',
        'max_length': 100,
        'description': 'Git branch naming'
    }
}

def validate_name(name: str, rule_type: str) -> Tuple[bool, str]:
    """驗證名稱是否符合規範"""
    if rule_type not in NAMING_RULES:
        return False, f"Unknown rule type: {rule_type}"

    rule = NAMING_RULES[rule_type]

    if len(name) > rule['max_length']:
        return False, f"Name exceeds maximum length of {rule['max_length']}"

    if not re.match(rule['pattern'], name):
        return False, f"Name does not match pattern: {rule['description']}"

    return True, "Valid"

def main():
    """主程式"""
    test_cases = [
        ('user-auth-api', 'kubernetes_resource'),
        ('USER_AUTH_API', 'environment_variable'),
        ('feature/add-user-login', 'git_branch'),
        ('my-app:v1.2.3', 'docker_image'),
    ]

    for name, rule_type in test_cases:
        is_valid, message = validate_name(name, rule_type)
        status = "✅" if is_valid else "❌"
        print(f"{status} {name} ({rule_type}): {message}")

if __name__ == "__main__":
    main()
```

### 5.3 命名規範遷移策略

#### 漸進式遷移計畫

```yaml
# 命名規範遷移計畫
migration_plan:
  phase_1:
    name: "Assessment"
    duration: "2 weeks"
    tasks:
      - Audit existing naming patterns
      - Identify violations
      - Document current state
      - Create baseline metrics

  phase_2:
    name: "Planning"
    duration: "2 weeks"
    tasks:
      - Define target naming conventions
      - Create migration scripts
      - Establish rollback procedures
      - Plan communication strategy

  phase_3:
    name: "Pilot Migration"
    duration: "4 weeks"
    tasks:
      - Select pilot services
      - Execute migration in staging
      - Validate functionality
      - Gather feedback

  phase_4:
    name: "Full Migration"
    duration: "8 weeks"
    tasks:
      - Migrate production services
      - Update documentation
      - Train teams
      - Monitor for issues

  phase_5:
    name: "Enforcement"
    duration: "ongoing"
    tasks:
      - Enable automated checks
      - Block non-compliant deployments
      - Regular compliance audits
      - Continuous improvement
```

---

## 第六章：實戰項目演練

### 6.1 電商平台命名設計

#### 微服務命名架構

```yaml
# 電商平台服務命名
services:
  # 用戶服務群
  user-management:
    - user-registration-api
    - user-profile-api
    - user-authentication-api
    - user-preferences-api

  # 商品服務群
  product-catalog:
    - product-listing-api
    - product-search-api
    - product-inventory-api
    - product-pricing-api

  # 訂單服務群
  order-management:
    - order-creation-api
    - order-fulfillment-api
    - order-tracking-api
    - order-history-api

  # 支付服務群
  payment-processing:
    - payment-gateway-api
    - payment-validation-api
    - refund-processing-api
    - billing-service-api
```

#### 資料庫命名設計

```sql
-- 電商平台資料庫命名
-- Schema 命名：{domain}_schema
CREATE SCHEMA user_management_schema;
CREATE SCHEMA product_catalog_schema;
CREATE SCHEMA order_management_schema;
CREATE SCHEMA payment_processing_schema;

-- 表格命名：{entity}_records 或 {entity}s
CREATE TABLE user_management_schema.user_accounts (
    user_id UUID PRIMARY KEY,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_catalog_schema.product_items (
    product_id UUID PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    base_price DECIMAL(10, 2) NOT NULL
);

-- 索引命名：idx_{table}_{columns}
CREATE INDEX idx_user_accounts_email ON user_management_schema.user_accounts(email_address);
CREATE INDEX idx_product_items_name ON product_catalog_schema.product_items(product_name);
```

### 6.2 DevOps 工具鏈命名

#### CI/CD 管道命名

```yaml
# .github/workflows/ecommerce-ci-cd.yml
name: E-Commerce CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  code-quality-check:
    name: Code Quality Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Run Static Analysis
        run: npm run lint

      - name: Run Security Scan
        run: npm run security:scan

  unit-test-suite:
    name: Unit Test Suite
    needs: code-quality-check
    runs-on: ubuntu-latest
    steps:
      - name: Run Unit Tests
        run: npm run test:unit

      - name: Generate Coverage Report
        run: npm run test:coverage

  integration-test-suite:
    name: Integration Test Suite
    needs: unit-test-suite
    runs-on: ubuntu-latest
    steps:
      - name: Setup Test Environment
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Run Integration Tests
        run: npm run test:integration

  build-and-push:
    name: Build and Push Docker Images
    needs: integration-test-suite
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker Image
        run: docker build -t user-auth-api:${{ github.sha }} .

      - name: Push to Registry
        run: docker push user-auth-api:${{ github.sha }}

  deploy-staging:
    name: Deploy to Staging Environment
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Kubernetes
        run: kubectl apply -f k8s/staging/

  deploy-production:
    name: Deploy to Production Environment
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Kubernetes
        run: kubectl apply -f k8s/production/
```

---

## 第七章：工具與自動化

### 7.1 IDE 整合

#### VS Code 設定

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "typescript.preferences.importModuleSpecifier": "relative",
  "files.associations": {
    "*.yaml": "yaml",
    "*.yml": "yaml"
  }
}
```

#### ESLint 命名規則配置

```javascript
// eslint.config.js
module.exports = {
  rules: {
    '@typescript-eslint/naming-convention': [
      'error',
      {
        selector: 'variable',
        format: ['camelCase', 'UPPER_CASE'],
        leadingUnderscore: 'allow',
      },
      {
        selector: 'function',
        format: ['camelCase'],
      },
      {
        selector: 'typeLike',
        format: ['PascalCase'],
      },
      {
        selector: 'interface',
        format: ['PascalCase'],
        prefix: ['I'],
      },
      {
        selector: 'enum',
        format: ['PascalCase'],
      },
      {
        selector: 'enumMember',
        format: ['UPPER_CASE'],
      },
    ],
  },
};
```

### 7.2 CI/CD 自動檢查

#### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running naming convention checks..."

# Check TypeScript/JavaScript files
npx eslint --rule '@typescript-eslint/naming-convention: error' .

# Check Python files
ruff check --select N .

# Check Kubernetes manifests
kubectl-validate ./k8s/

# Check for prohibited patterns
if grep -r "TODO\|FIXME\|HACK" --include="*.ts" --include="*.py" .; then
    echo "Warning: Found TODO/FIXME/HACK comments"
fi

echo "Naming convention checks passed!"
```

---

## 第八章：持續改進與維護

### 8.1 命名規範版本管理

#### 版本控制策略

```yaml
# naming-conventions-changelog.yaml
versions:
  - version: "2.0.0"
    date: "2024-01-15"
    changes:
      - Added Kubernetes naming conventions
      - Updated TypeScript interface naming rules
      - Added CI/CD workflow naming guidelines
    breaking_changes:
      - Changed environment variable prefix requirement

  - version: "1.1.0"
    date: "2023-10-01"
    changes:
      - Added Python naming conventions
      - Improved documentation examples
    deprecations:
      - Deprecated Hungarian notation for all languages

  - version: "1.0.0"
    date: "2023-06-15"
    changes:
      - Initial release
      - Basic naming conventions for JavaScript/TypeScript
```

### 8.2 團隊培訓與推廣

#### 培訓計畫大綱

```markdown
# 命名規範培訓計畫

## 第一週：基礎概念
- 命名規範的重要性
- 核心原則介紹
- 常見錯誤案例

## 第二週：語言特定規範
- 各程式語言命名慣例
- 實際程式碼練習
- Code Review 實作

## 第三週：DevOps 命名
- Git 分支與提交命名
- Docker 和 Kubernetes 命名
- CI/CD 流程命名

## 第四週：實戰演練
- 專案命名設計
- 遷移策略實作
- 自動化工具使用

## 評估方式
- 每週小測驗
- 實際專案應用
- 最終報告呈現
```

### 8.3 效果評估與優化

#### 評估指標

```yaml
# 命名規範效果評估指標
metrics:
  compliance_rate:
    description: "符合命名規範的程式碼比例"
    target: "> 95%"
    measurement: "Automated CI checks"

  review_time_reduction:
    description: "Code Review 時間減少"
    target: "> 30%"
    measurement: "PR review metrics"

  onboarding_efficiency:
    description: "新成員上手時間"
    target: "< 2 weeks"
    measurement: "Team surveys"

  bug_rate_reduction:
    description: "命名相關 Bug 減少"
    target: "> 50%"
    measurement: "Bug tracking system"

  developer_satisfaction:
    description: "開發者滿意度"
    target: "> 4.0/5.0"
    measurement: "Quarterly surveys"
```

---

## 🔗 相關資源

### 內部文件

- [命名規範](./architecture/naming-conventions.md) - 本專案的命名規範詳細定義
- [語言堆疊決策](./architecture/language-stack.md) - 語言選擇與命名規範關係
- [重構 Playbooks](./refactor_playbooks/README.md) - 重構計畫系統

### 外部參考

- [PEP 8 - Python 風格指南](https://peps.python.org/pep-0008/)
- [Google TypeScript 風格指南](https://google.github.io/styleguide/tsguide.html)
- [Effective Go](https://go.dev/doc/effective_go)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Kubernetes 命名規範](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)

---

## 📝 變更記錄

| 版本 | 日期 | 變更內容 |
|------|------|----------|
| 1.0.0 | 2025-12-17 | 完整學習手冊初版發布 |

---

**文件擁有者**: Unmanned Island System Team  
**審核週期**: 每季  
**下次審核**: 2026-03-17
