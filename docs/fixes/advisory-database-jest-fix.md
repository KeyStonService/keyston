# Advisory Database Jest Configuration Fix

**Date**: 2025-12-10  
**Component**: `@synergymesh/advisory-database`  
**Issue**: Deep Maintenance Project Fundamental Build Failure
(深度維修專案建置根本性失敗問題)

## Problem

The `@synergymesh/advisory-database` workspace was experiencing test failures
due to a missing `ts-node` dependency required by the Jest TypeScript
configuration file (`jest.config.ts`).

### Error Message

```
Error: Jest: Failed to parse the TypeScript config file jest.config.ts
  Error: Jest: 'ts-node' is required for the TypeScript configuration files.
  Error: Cannot find package 'ts-node' imported from jest-config
```

## Root Cause

Jest configuration file was written in TypeScript (`jest.config.ts`) but:

1. The required `ts-node` loader was not installed as a dependency
2. The package has `"type": "module"` in package.json, requiring CommonJS config
   to use `.cjs` extension

## Solution

### Changes Made

1. **Converted Jest config from TypeScript to CommonJS JavaScript**
   - Renamed: `jest.config.ts` → `jest.config.cjs`
   - Used `.cjs` extension because package.json has `"type": "module"`
   - Maintained all configuration options and functionality

2. **Added explicit ts-jest dependency**
   - Added `ts-jest: ^29.2.5` to devDependencies
   - This is a best practice even though it was being installed transitively

### Files Changed

- `core/advisory-database/jest.config.ts` →
  `core/advisory-database/jest.config.cjs`
- `core/advisory-database/package.json` (added ts-jest dependency)

## Validation

### Test Results

- Advisory Database: **60/60 tests passing** ✅
- Full Test Suite: **98/98 tests passing** ✅
- Build: **All workspaces build successfully** ✅
- Security Scan: **No issues detected** ✅

### Test Output

```
> @synergymesh/advisory-database@1.0.0 test
> jest --passWithNoTests

 PASS  src/__tests__/advisory.test.ts
  GHSA ID Utilities
    ✓ All tests passing
  AdvisoryValidator
    ✓ All tests passing
  AdvisoryService
    ✓ All tests passing
  AdvisoryBotEngine
    ✓ All tests passing
  InMemoryStorageAdapter
    ✓ All tests passing

Test Suites: 1 passed, 1 total
Tests:       60 passed, 60 total
```

## Implementation Notes

### Why `.cjs` instead of `.js`?

The package.json contains `"type": "module"`, which means:

- `.js` files are treated as ES modules
- Jest config uses `module.exports`, which is CommonJS
- `.cjs` explicitly marks the file as CommonJS

### Configuration Rationale

The `useESM: true` in ts-jest config is correct because:

- It's for handling ES modules in the TypeScript **source code**, not the config
  file
- The source files use ES module imports/exports
- The config file itself is CommonJS (`.cjs`)

## Related Issues

- PR #83: Similar fix (reference implementation)
- PR #84: This fix (current implementation)

## Lessons Learned

1. **Module System Awareness**: When a package uses `"type": "module"`, CommonJS
   files must use `.cjs` extension
2. **Minimal Dependencies**: Converting TypeScript config to JavaScript
   eliminates the need for `ts-node`
3. **Explicit Dependencies**: Adding `ts-jest` explicitly is better than relying
   on transitive dependencies
4. **Test First**: Always verify test infrastructure before making other changes

## Future Recommendations

1. Consider standardizing Jest config format across all workspaces
2. Document module system choices in workspace README files
3. Add pre-commit hooks to catch missing test dependencies early
