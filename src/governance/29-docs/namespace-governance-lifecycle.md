# Organizational Adoption & Governance Lifecycle for Naming (Summary)

## Purpose
- 提供組織層級命名治理的採用與生命週期指引。
- 對齊現有資產：`governance/34-config/naming/canonical-naming-machine-spec.yaml`、`governance/34-config/naming/namespace-mapping.yaml`、Conftest/Gatekeeper 命名政策。

## Lifecycle（規劃 → 試行 → 滾動 → 優化）
1) 規劃：定義標準/範疇、治理組織、例外門檻；輸出草案與決策批准。  
2) 試行：挑選核心模組試點；套用模板/版本命名；收集回饋迭代。  
3) 滾動：大規模導入；全域規範上線、指標監控、稽核報告、例外流程啟動。  
4) 優化：例外審核/回滾演練；成效復盤、年度優化、知識共創。

## Stakeholders（精簡）
- 決策層（董事會/CIO）：授權、資源配置、例外裁決。  
- 架構/技術負責人：標準審議、模板產出、CI/Policy 落地。  
- 資安/合規：審計報告、例外審核、控制對齊。  
- 業務窗口/產品：需求與場景輸入、溝通宣導。  
- 運維/自動化：工具部署、baseline/Conftest/Gatekeeper 管線。  
- 命名守門人委員會：規範維護、例外仲裁、培訓。

## Training（角色導向，摘錄）
- 守門人：進階命名規則、例外/RFC 撰寫、審計演練。  
- 技術負責人：命名生成工具、YAML/RegO/CI 集成。  
- 維運：回滾演練、配置核對、指標監測。  
- 一般用戶：基礎規則、常見錯誤案例、自助檢查。

## Controls & Templates（落地關聯）
- Machine-spec regex/labels：`canonical-naming-machine-spec.yaml` 為單一事實來源。  
- 映射：`namespace-mapping.yaml` 舊→canonical→URN/labels；遷移腳本據此套用。  
- 驗證：`governance/23-policies/conftest/naming_policy.rego` + Gatekeeper constraints（K8sNamingPattern / K8sRequiredLabels）。  
- 教學/範例：`namespace-from-zero.md`（基礎）、`namespace-advanced-playbook.md`（配額/RBAC/NetPol、遷移步驟）。

## Metrics & Audit（示例）
- 規則遵循率（regex/labels 通過率）、例外數量與老化時間、命名衝突/重複數、遷移完成率、審計發現整改週期。  
- 資料來源：CI conftest 報告、Gatekeeper PolicyReport、GitOps MR 檢查。

## Exception & Change Management
- 例外條件：合規/兼容性/客戶強制要求；需填寫用途、時效、回收計畫。  
- 流程：提交 → 守門人審核 → 時效性標註 → 定期復核/回收。  
- 變更：版本化規範，回滾策略（命名/標籤變更需同步 URN、GitOps manifest、監控標籤）。

## Adoption Checklist（精簡）
- [ ] 標準發布並與 machine-spec 對齊  
- [ ] 試點完成 & 回饋收斂  
- [ ] CI/Conftest & Gatekeeper 啟用  
- [ ] 映射與遷移腳本就緒並執行  
- [ ] 例外流程/審計報告通道上線  
- [ ] 指標儀表板與定期檢討節奏建立

## 附錄：組織採用策略與角色培訓（對應要求摘錄）
- 推行路徑：規劃→試行→滾動→優化，各階段輸出標準草案/試點模板/指標監控/例外與復盤。  
- 利害關係人：董事會/CIO（授權與資源）、架構/技術主管（標準審議與模板產出）、資安合規（稽核與例外審核）、業務窗口（需求輸入與宣導）、運維自動化（工具管線）、命名守門人委員會（規範維護與仲裁）。  
- 角色培訓：  
  - 守門人：進階命名規則、例外/RFC、審計演練。  
  - 技術負責人：名稱生成與模板、YAML/RegO/CI 集成。  
  - 維運：回滾演練、配置核對、指標監測。  
  - 一般用戶：基礎規則、錯誤案例、自助檢查。  
- 參考基礎文件（對齊本庫資產）：`canonical-naming-governance-v1.0.docx`、`naming-implementation-templates.v1.0.docx`、`naming-observability-validation-migration.v1.0.docx`（可對應本 repo 的 machine-spec、mapping、Conftest/Gatekeeper 範本與教學文件）。
