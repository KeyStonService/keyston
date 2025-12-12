# 🚀 Governance Directory Quickstart | 治理目錄快速開始

> Begin the **phased refactor** of the `governance/` directory while preserving the layered (00-80) architecture and recently consolidated paths (`23-policies/`, `31-schemas/`, `35-scripts/`).

## 🧭 TL;DR

1. **Phase 0 - Snapshot**: Capture the current tree for diffing  
   ```bash
   tree -L 2 governance
   ```
2. **Phase 1 - Baseline hygiene**: Keep root docs aligned (README, QUICKSTART, IMPLEMENTATION-ROADMAP) and confirm required dimensions exist (00-14, 10-policy).  
3. **Phase 2 - Path normalization**: Migrate any old references to the new numbered locations per [RESTRUCTURING_GUIDE.md](./RESTRUCTURING_GUIDE.md).  
4. **Phase 3 - Validation**: Run the lightweight governance check:  
   ```bash
   python -m pytest governance/28-tests/unit/test_governance.py -q
   ```
5. **Phase 4 - Rollout**: Update downstream configs/workflows after validation.

## 🔗 Key References 參考

- Layered architecture: [GOVERNANCE_INTEGRATION_ARCHITECTURE.md](./GOVERNANCE_INTEGRATION_ARCHITECTURE.md)
- Restructuring playbook: [RESTRUCTURING_GUIDE.md](./RESTRUCTURING_GUIDE.md)
- Phased delivery plan: [IMPLEMENTATION-ROADMAP.md](./IMPLEMENTATION-ROADMAP.md)
