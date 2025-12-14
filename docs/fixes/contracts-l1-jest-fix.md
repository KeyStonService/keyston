# Contracts L1 Jest Configuration Fix

**Date**: 2025-12-10  
**Component**: `@synergymesh/contracts-l1`  
**Issue**: Missing test infrastructure dependencies (Part of Deep Maintenance Project Build Failure scan)

## Problem

The `@synergymesh/contracts-l1` workspace had missing Jest dependencies:
1. `ts-jest` was not installed (required for TypeScript test execution)
2. `supertest` was not installed (required for API testing)
3. Jest config was in TypeScript format (`jest.config.ts`)

### Error Messages

```
sh: 1: jest: not found
```

```
Cannot find module 'supertest' from 'src/__tests__/assignment.test.ts'
```

## Root Cause

The workspace had:
- TypeScript Jest configuration file (`jest.config.ts`)
- Missing `ts-jest` dependency in package.json devDependencies
- Missing `supertest` dependency (used by multiple test files)

## Solution

### Changes Made

1. **Converted Jest config from TypeScript to CommonJS JavaScript**
   - Renamed: `jest.config.ts` → `jest.config.cjs`
   - Used `.cjs` extension for consistency with advisory-database fix
   - Maintained all configuration options and functionality

2. **Added missing test dependencies**
   - Added `ts-jest: ^29.2.5` to devDependencies
   - Added `supertest: ^6.3.4` to devDependencies (for API testing)

### Files Changed

- `core/contract_service/contracts-L1/contracts/jest.config.ts` → `jest.config.cjs`
- `core/contract_service/contracts-L1/contracts/package.json` (added ts-jest and supertest)

## Validation

### Test Infrastructure
- ✅ Jest can now find and execute tests
- ✅ TypeScript test files compile and run
- ✅ API tests can import supertest
- ⚠️  Some tests have pre-existing failures unrelated to jest config (test logic issues)

### Configuration
```javascript
/** @type {import('jest').Config} */
const config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.ts'],
  transform: { '^.+\\.ts$': 'ts-jest' },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts'
  ]
};

module.exports = config;
```

## Implementation Notes

### Why `.cjs` extension?

For consistency with the advisory-database fix and to avoid potential module resolution issues:
- Explicit CommonJS syntax with `module.exports`
- Works reliably across all Node.js module configurations
- Standard approach for Jest configs in modern projects

### Test Infrastructure Dependencies

This fix reveals the importance of:
1. **Explicit test dependencies**: Always declare test runners and assertion libraries
2. **Complete test tooling**: Include all testing utilities (supertest, etc.)
3. **Consistent configuration**: Use same config format across workspaces

## Related Fixes

- PR #84: Advisory database Jest fix (original fix)
- This fix: Contracts L1 Jest fix (discovered during project-wide scan)

## Lessons Learned

1. **Scan Entire Project**: After fixing one workspace, scan all workspaces for similar issues
2. **Missing Dependencies**: Jest config may parse but tests fail if test utilities missing
3. **Pre-existing Issues**: Distinguish between config fixes and pre-existing test failures
4. **Consistent Approach**: Apply same fix pattern across all affected workspaces

## Future Recommendations

1. Add dependency validation to pre-commit hooks
2. Standardize Jest configuration format across all workspaces
3. Document required test dependencies in workspace README files
4. Consider creating shared Jest config preset for monorepo consistency
