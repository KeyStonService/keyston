# Wrangler API Integration - Quick Start Guide

This document provides quick setup instructions for using the Wrangler testing APIs.

## Prerequisites

- Node.js 18+ installed
- Wrangler 4.56+ installed (included in package.json)
- Cloudflare account (for deployment, not required for local testing)

## Installation

```bash
cd workspace/cloudflare/workers
npm install
```

## Running Tests

### All Tests

```bash
npm test
```

### Watch Mode

```bash
npm run test:watch
```

### Type Checking

```bash
npm run typecheck
```

## Configuration Notes

### Test Configuration

The tests use the root `wrangler.toml` configuration located at:
```
../../../wrangler.toml
```

### Bindings Setup (Optional)

Most tests will work without binding IDs configured. However, for full functionality:

1. **KV Namespaces**: Create test KV namespaces
   ```bash
   wrangler kv:namespace create CACHE --env development
   wrangler kv:namespace create SESSIONS --env development
   ```

2. **D1 Database**: Create test database
   ```bash
   wrangler d1 create machinenativeops-dev
   ```

3. **R2 Bucket**: Create test bucket
   ```bash
   wrangler r2 bucket create machinenativeops-assets-dev
   ```

4. Update `wrangler.toml` with the generated IDs

## Test Files Overview

- **`src/index.test.ts`**: Integration tests using `unstable_startWorker`
  - Recommended for new tests
  - Fast and reliable
  - Full Worker runtime simulation

- **`src/platform-proxy.test.ts`**: Platform proxy tests using `getPlatformProxy`
  - Tests binding interactions in Node.js
  - Useful for tooling and framework development
  - Emulates Workers platform

- **`src/unstable-dev.test.ts`**: Legacy API examples using `unstable_dev`
  - For backward compatibility
  - Being phased out
  - Use `unstable_startWorker` instead

- **`src/multi-worker.test.ts`**: Multi-worker testing patterns
  - Commented example code
  - Reference for service bindings
  - Demonstrates parent-child Worker communication

## Common Issues

### Issue: "Entry-point file not found"

**Solution**: The tests expect the worker code at the path specified in `wrangler.toml`. Make sure:
- The `main` field in `wrangler.toml` is correct
- The worker source file exists at that path
- Paths are relative to the project root

### Issue: "Binding is undefined"

**Solution**: Some bindings require configuration in `wrangler.toml`:
- Add binding IDs for KV, D1, R2
- Or mock the bindings in tests
- Or skip tests that require specific bindings

### Issue: "Node module not found"

**Solution**: Make sure you're using the Node.js environment for Wrangler API tests:
- Check `vitest.config.ts` has `environment: 'node'`
- Wrangler APIs don't work inside Workers runtime

## Next Steps

1. **Write Your Tests**: Use `src/index.test.ts` as a template
2. **Configure Bindings**: Set up KV, D1, R2 for full testing
3. **CI/CD Integration**: Add tests to your GitHub Actions workflow
4. **Coverage**: Run `npm test -- --coverage` to see coverage reports

## Resources

- [Wrangler API Docs](https://developers.cloudflare.com/workers/wrangler/api/)
- [Workers Testing Guide](https://developers.cloudflare.com/workers/testing/)
- [Vitest Documentation](https://vitest.dev/)

## Support

For issues or questions:
- Check the main [README.md](./README.md) for detailed documentation
- Review the Cloudflare Workers documentation
- Check existing test examples in this directory
