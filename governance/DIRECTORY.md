# governance

## 目錄職責

此目錄為 MachineNativeOps 的**治理中心**，包含合規要求、政策規範和技術標準的定義與文檔。

## 子目錄說明

| 子目錄 | 職責 | 目前狀態 |
|--------|------|----------|
| `compliance/` | 法規合規要求（GDPR, HIPAA, SOC2） | 骨架（空文件） |
| `policies/` | 內部政策與流程規範 | 部分結構已建立 |
| `standards/` | 技術標準（API、編碼規範） | 骨架（空文件） |

## 目錄結構

```
governance/
├── compliance/           # 合規要求
│   ├── GDPR.md          # 歐盟資料保護條例
│   ├── HIPAA.md         # 醫療資訊隱私法
│   └── SOC2.md          # 服務組織控制標準
├── policies/             # 內部政策
│   ├── change-management/ # 變更管理流程
│   ├── exception/        # 例外處理政策
│   ├── gatekeeper/       # 閘門守衛（准入控制）
│   ├── migration/        # 遷移政策
│   ├── naming/           # 命名規範
│   ├── observability/    # 可觀測性政策
│   ├── security/         # 安全政策
│   └── validation/       # 驗證規則
└── standards/            # 技術標準
    ├── api-standards.md  # API 設計標準
    └── coding-standards.md # 編碼標準
```

## 職責分離說明

- **compliance/**：外部法規要求，由法務/合規團隊維護
- **policies/**：內部運作規範，由各領域負責人維護
- **standards/**：技術實踐標準，由架構團隊維護

## 與其他目錄的關係

- **config/governance/**：治理相關的配置文件
- **docs/governance/**：治理框架說明文檔
- **src/governance/**：治理系統的實作代碼

## 設計原則

1. **文檔即政策**：所有政策以 Markdown 格式維護，可版本控制
2. **可執行驗證**：政策應配合 `policies/validation/` 中的規則進行自動化檢查
3. **層級分離**：法規、政策、標準三層分開維護
