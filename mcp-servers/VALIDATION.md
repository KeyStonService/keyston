# Validation System Documentation

## 概述

MachineNativeOps MCP Servers 實現了企業級的多層次驗證系統，確保程式碼品質、部署安全性、邏輯正確性和真實性。

## 驗證架構

```
┌─────────────────────────────────────────────┐
│     Comprehensive Validator (綜合驗證器)      │
│                                             │
│  ┌────────────┐  ┌────────────┐  ┌───────┐│
│  │ Deployment │  │   Logic    │  │ESLint ││
│  │ Validator  │  │ Validator  │  │Config ││
│  └────────────┘  └────────────┘  └───────┘│
└─────────────────────────────────────────────┘
```

## 驗證層級

### 1. 部署配置驗證 (Deployment Validation)

**目的：** 確保專案部署配置符合企業標準

**檢查項目：**

#### 必要文件檢查

- ✅ `package.json` - 專案配置
- ✅ `README.md` - 專案文檔
- ✅ `.gitignore` - 版本控制排除規則

#### Package.json 驗證

- 必要欄位檢查：
  - `name` - 專案名稱
  - `version` - 版本號（Semver 格式）
  - `description` - 專案描述
  - `main` - 進入點
  - `scripts` - 執行腳本
  - `license` - 授權條款
  - `engines` - 環境需求
  
- 必要腳本檢查：
  - `start` - 啟動命令
  - `test` - 測試命令

#### 安全配置檢查

- ✅ `.gitignore` 包含敏感文件模式
  - `node_modules` - 依賴套件
  - `.env` - 環境變數
  - `*.log` - 日誌文件
  
- ✅ 偵測不應提交的敏感文件
  - `.env` 文件
  - `secrets.json`
  - `credentials.json`
  - 私鑰文件 (`.key`, `.pem`, `.crt`)

#### 環境配置驗證

- `NODE_ENV` 設定檢查
- 支援值：`development`, `production`, `test`

#### Node.js 版本檢查

- 最低版本：Node.js 18.x
- 當前環境相容性驗證

**評分標準：**

- 100 分：所有檢查通過
- 每個錯誤扣 20 分
- 每個警告扣 5 分

---

### 2. 邏輯驗證 (Logic Validation)

**目的：** 驗證程式碼邏輯正確性、真實性和完整性

#### 2.1 真實性檢查 (Authenticity Checks)

**可疑模式偵測：**

```javascript
// ❌ 危險模式
eval('malicious code')           // 動態執行
Function('return ' + userInput)  // 動態函數
document.write(untrusted)        // DOM 注入
```

**程式碼混淆偵測：**

- Hex 轉義序列 (`\x[0-9a-f]{2}`)
- Unicode 轉義序列 (`\u[0-9a-f]{4}`)
- `String.fromCharCode` 使用
- 常見混淆變數名 (`_0x[a-f0-9]{4,}`)

**完整性驗證：**

- SHA-256 雜湊值計算
- 程式碼長度統計
- 行數統計

#### 2.2 邏輯正確性檢查

**不可達程式碼偵測：**

```javascript
// ❌ return 後的程式碼無法執行
function example() {
  return value;
  console.log('unreachable'); // 警告
}
```

**空白 catch 區塊偵測：**

```javascript
// ❌ 錯誤被靜默忽略
try {
  riskyOperation();
} catch (error) {
  // 空白 - 警告
}
```

**無限迴圈偵測：**

```javascript
// ❌ 沒有中斷條件的無限迴圈
while (true) {
  // 沒有 break 或 return - 錯誤
}
```

**相等性比較檢查：**

```javascript
// ⚠️ 鬆散相等
if (value == null) { }  // 建議使用 ===

// ✅ 嚴格相等
if (value === null) { }
```

**Promise 錯誤處理：**

```javascript
// ⚠️ 缺少錯誤處理
promise.then(handler);

// ✅ 包含錯誤處理
promise.then(handler).catch(errorHandler);
```

**變數遮蔽偵測：**

```javascript
// ⚠️ 變數遮蔽
let value = 1;
function example() {
  let value = 2; // 遮蔽外部變數
}
```

#### 2.3 一致性檢查 (Consistency Checks)

**縮排一致性：**

- 偵測縮排空格數的最大公約數
- 標準：2 或 4 個空格

**命名慣例：**

- camelCase 檢查
- snake_case 檢查
- 混合使用警告

**引號風格：**

- 單引號 (`'`)
- 雙引號 (`"`)
- 反引號 (`)
- 主要風格應佔 70% 以上

**分號使用：**

- 一致的分號使用模式
- 20-80% 使用率視為不一致

#### 2.4 設計模式驗證

**錯誤處理模式：**

- `try-catch` 區塊匹配
- 每個 `try` 應有對應的 `catch`

**異步模式：**

- `async` 函數應使用 `await`
- 偵測未使用的 `async` 關鍵字

**回調地獄偵測：**

- 深度巢狀回調函數
- 建議使用 async/await

**資源清理：**

- `setInterval` 應有 `clearInterval`
- `addEventListener` 應有 `removeEventListener`

#### 2.5 依賴分析

**Import 風格：**

```javascript
// ES6 Modules
import { something } from 'package';

// CommonJS
const something = require('package');
```

**相對路徑警告：**

- 超過 10 個相對引入建議使用模組別名

---

### 3. ESLint 配置

**嚴格規則：**

```json
{
  "rules": {
    "no-eval": "error",              // 禁用 eval
    "no-implied-eval": "error",      // 禁用隱式 eval
    "no-new-func": "error",          // 禁用 Function 建構子
    "require-await": "error",        // async 函數需使用 await
    "max-complexity": ["warn", 15],  // 複雜度上限 15
    "max-depth": ["warn", 4],        // 巢狀深度上限 4
    "max-nested-callbacks": ["warn", 3], // 回調巢狀上限 3
    "max-lines-per-function": ["warn", 100] // 函數長度上限 100 行
  }
}
```

---

### 4. 綜合驗證 (Comprehensive Validation)

**整合所有驗證器：**

1. 部署配置驗證
2. 所有 JavaScript 文件的邏輯驗證
3. 統計與評分

**評分計算：**

```
總分 = (部署分數 × 0.3) + (程式碼平均分 × 0.7)
```

**等級標準：**

- A+ : 95-100 分
- A  : 90-94 分
- A- : 85-89 分
- B+ : 80-84 分
- B  : 75-79 分
- C  : 70-74 分
- F  : < 70 分

---

## 使用方式

### 命令列執行

```bash
# 1. 部署配置驗證
npm run validate:deployment

# 2. 程式碼邏輯驗證
npm run validate:logic

# 3. 綜合驗證
npm run validate:comprehensive

# 4. ESLint 檢查
npm run lint

# 5. 完整嚴格檢查
npm run check:strict
```

### 程式化使用

```javascript
import { DeploymentValidator } from './deployment-validator.js';
import { LogicValidator } from './logic-validator.js';
import { ComprehensiveValidator } from './comprehensive-validator.js';

// 部署驗證
const deployValidator = new DeploymentValidator();
const deployResult = await deployValidator.validate();

// 邏輯驗證
const logicValidator = new LogicValidator();
const code = await readFile('example.js', 'utf-8');
const logicResult = logicValidator.validate(code);

// 綜合驗證
const compValidator = new ComprehensiveValidator();
const report = await compValidator.validate();
console.log(compValidator.formatReport(report));
```

---

## 驗證報告範例

```
═══════════════════════════════════════════════════════
          COMPREHENSIVE VALIDATION REPORT
═══════════════════════════════════════════════════════

Overall Status: ✓ PASSED
Overall Score: 95/100 (Grade: A)
Timestamp: 2025-11-21T21:00:00.000Z

─── SUMMARY ───
Total Files: 9
Validated Files: 9
Total Issues: 0
Critical Issues: 0
Warnings: 3

─── DEPLOYMENT VALIDATION ───
Status: ✓ PASSED
Score: 100/100
Errors: 0
Warnings: 0

─── CODE LOGIC VALIDATION ───
Total Files: 9
Valid Files: 9
Invalid Files: 0
Total Warnings: 3

Top Files by Warnings:
  ✓ code-analyzer.js - Score: 95/100, Warnings: 2
  ✓ test-generator.js - Score: 98/100, Warnings: 1
  ✓ doc-generator.js - Score: 100/100, Warnings: 0

─── RECOMMENDATIONS ───
[INFO] Status
  All validations passed successfully
  → Maintain current quality standards

[MEDIUM] Code Quality
  3 warnings detected across codebase
  → Address warnings to improve code quality

═══════════════════════════════════════════════════════
```

---

## 持續改進

### 當前狀態 (2025-11-21)

**評分：** B+ (81/100)

**待改進項目：**

- 95 個程式碼警告需要處理
- 主要來源：
  - 相等性比較（使用 `==` 而非 `===`）
  - 程式碼一致性（縮排、引號風格）
  - Promise 錯誤處理

### 改進計劃

1. **短期 (1 週)**
   - 修復所有嚴格相等性問題
   - 統一引號風格
   - 添加缺失的錯誤處理

2. **中期 (1 個月)**
   - 重構高複雜度函數
   - 改善測試覆蓋率
   - 文檔完整性

3. **長期 (3 個月)**
   - 達成 A 級評分 (90+)
   - 零關鍵問題
   - 警告數 < 10

---

## 最佳實踐

### ✅ DO（應該做）

```javascript
// 使用嚴格相等
if (value === null) { }

// 適當的錯誤處理
try {
  await operation();
} catch (error) {
  console.error('Operation failed:', error);
  throw error;
}

// Promise 錯誤處理
promise
  .then(handler)
  .catch(errorHandler);

// 資源清理
const timer = setInterval(work, 1000);
// ... 稍後
clearInterval(timer);
```

### ❌ DON'T（不應該做）

```javascript
// 使用 eval
eval(untrustedCode);

// 鬆散相等
if (value == null) { }

// 空白 catch
try {
  riskyOperation();
} catch (error) { }

// 無限迴圈無中斷
while (true) {
  // 沒有 break
}

// Promise 無錯誤處理
promise.then(handler);
```

---

## 安全考量

### 敏感文件防護

`.gitignore` 必須包含：

```gitignore
# 環境變數
.env
.env.local
.env.*.local

# 敏感數據
secrets.json
credentials.json
*.key
*.pem
*.crt

# 依賴
node_modules/

# 日誌
*.log
```

### 程式碼真實性

- 避免使用 `eval()` 和 `Function()` 建構子
- 不使用混淆程式碼
- 保持程式碼可讀性和可維護性
- 使用完整性雜湊驗證程式碼未被篡改

---

## 支援與貢獻

### 報告問題

- 在 GitHub Issues 中報告驗證器的問題
- 包含完整的驗證報告輸出

### 貢獻指南

- 遵循現有的程式碼風格
- 確保所有驗證通過
- 添加適當的測試案例
- 更新相關文檔

---

**版本：** 1.0.0  
**最後更新：** 2025-11-21  
**維護者：** MachineNativeOps Team
