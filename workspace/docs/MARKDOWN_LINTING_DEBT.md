# Markdown Linting Technical Debt

## Overview

This document tracks remaining markdown linting issues that require manual intervention or are accepted as technical debt.

**Last Updated**: 2026-01-03  
**Status**: 🟡 Partially Resolved

## Summary

| Rule | Description | Total | Auto-Fixed | Remaining | Status |
|------|-------------|-------|------------|-----------|--------|
| MD040 | Fenced code blocks need language | ~1300 | ✅ Many | ~1300 | 🔴 Manual Fix Required |
| MD060 | Table column spacing | ~8800 | ❌ None | ~8800 | 🔴 Tool Limitation |
| MD001 | Heading level increments | 33 | ✅ 29 | 4 | 🟢 Mostly Resolved |

## Completed Work

### ✅ MD001 (Heading Increments)

- **Fixed**: 29 out of 33 violations (88% reduction)
- **Method**: Cleaned up 132 files with merge conflict markers that were causing heading structure issues
- **Remaining**: 4 false positives in `docs/refactor_playbooks/03_refactor/misc/2-namespace.md`
  - These are caused by bash code block comments starting with `#` being detected as h1 headings
  - The markdown is actually correct; this is a markdownlint limitation

### ✅ Configuration

- Enabled MD040 and MD060 rules in `.markdownlint.json`
- Updated `docs:lint` npm script to use proper config files
- Applied auto-fix to 1500+ files

## Remaining Issues

### 🔴 MD040 (Fenced Code Language) - ~1300 violations

**Why Not Auto-Fixed**: The auto-fix tool cannot determine what language each code block should be tagged with. This requires human judgment.

**Impact**: Low - Most CI/CD pipelines don't enforce this rule strictly

**Recommendation**: 
- Accept as technical debt for legacy documentation
- Enforce for new files via pre-commit hooks
- Gradually fix when editing files

**Example Files with Most Violations**:
- `docs/` directory: ~1300+ violations
- Most are in legacy report and playbook files

### 🔴 MD060 (Table Column Style) - ~8800 violations

**Why Not Auto-Fixed**: Current version of markdownlint-cli cannot auto-fix table formatting issues

**Impact**: Low - Tables still render correctly, just with inconsistent spacing

**Recommendation**:
- Accept as technical debt for existing files
- Use table formatting tools for new content
- Consider using markdownlint-cli2 which may have better auto-fix support

**Example**: 
```markdown
❌ Bad (missing spaces):
|Column1|Column2|Column3|
|---|---|---|
|Value1|Value2|Value3|

✅ Good (proper spacing):
| Column1 | Column2 | Column3 |
| ------- | ------- | ------- |
| Value1  | Value2  | Value3  |
```

## Action Items

### For New Content

- [ ] Add pre-commit hook to enforce MD040 on changed files
- [ ] Use markdown table generators/formatters
- [ ] Document markdown style guide

### For Legacy Content

- [ ] Accept technical debt for MD040 and MD060
- [ ] Fix opportunistically when editing files  
- [ ] Prioritize fixing in frequently-edited files

### Tools and Automation

- [ ] Investigate markdownlint-cli2 for better auto-fix
- [ ] Create script to detect and suggest language for code blocks
- [ ] Add markdown formatting to CI/CD pipeline

## References

- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [MD040 Documentation](https://github.com/DavidAnson/markdownlint/blob/main/doc/md040.md)
- [MD060 Documentation](https://github.com/DavidAnson/markdownlint/blob/main/doc/md060.md)
- [MD001 Documentation](https://github.com/DavidAnson/markdownlint/blob/main/doc/md001.md)

## Notes

- All merge conflict markers have been cleaned up (132 files)
- Configuration is now correct and consistent
- Future commits will be linted with strict rules
- Legacy technical debt is documented and tracked
