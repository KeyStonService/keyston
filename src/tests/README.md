# Tests Directory

This directory contains all test files for SynergyMesh.

## Structure

```
tests/
├── e2e/          # End-to-end tests
├── integration/  # Integration tests
├── unit/         # Unit tests
├── performance/  # Performance tests
└── vectors/      # Test vectors
```

## Running Tests

### All Tests

```bash
npm test
```

### Specific Test Types

```bash
# Unit tests
cd tests/unit && npm test

# Integration tests
cd tests/integration && npm test

# E2E tests
cd tests/e2e && npm test
```

## Test Coverage

Target coverage: 80% minimum

## See Also

- [Migration Guide](../docs/MIGRATION.md)
- [Jest Configuration](../jest.config.js)
