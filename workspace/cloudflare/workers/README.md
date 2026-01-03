# Cloudflare Workers Testing with Wrangler APIs

This directory contains integration and unit tests for the MachineNativeOps Cloudflare Worker using Wrangler's programmatic testing APIs.

## 📚 Overview

We use three main Wrangler APIs for testing:

1. **`unstable_startWorker`** - Modern API for integration testing (recommended)
2. **`getPlatformProxy`** - Node.js emulation of Workers platform bindings
3. **`unstable_dev`** - Legacy API for integration testing (deprecated)

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

## 📖 Testing APIs

### 1. `unstable_startWorker` (Recommended)

**Use for**: Integration tests against a local Worker development server.

**Features**:
- Fast test execution
- Full Worker runtime simulation
- Access to bindings (KV, D1, R2, Durable Objects)
- Custom fetch interface

**Example**:

```typescript
import { unstable_startWorker } from 'wrangler';

const worker = await unstable_startWorker({
  config: 'wrangler.toml',
});

// Make requests to your worker
const response = await worker.fetch('http://example.com/api/test');

// Cleanup
await worker.dispose();
```

**See**: [`src/index.test.ts`](./src/index.test.ts)

### 2. `getPlatformProxy`

**Use for**: Testing code that uses Workers bindings in Node.js environment.

**Features**:
- Emulate Workers bindings in Node.js
- Test binding interactions outside Workers runtime
- Useful for framework development and tooling
- Access to KV, D1, R2, Durable Objects proxies

**Example**:

```typescript
import { getPlatformProxy } from 'wrangler';

const platform = await getPlatformProxy({
  configPath: 'wrangler.toml',
  persist: false,
});

// Access bindings
await platform.env.CACHE.put('key', 'value');
const value = await platform.env.CACHE.get('key');

// Use context helpers
platform.ctx.waitUntil(somePromise);

// Cleanup
await platform.dispose();
```

**See**: [`src/platform-proxy.test.ts`](./src/platform-proxy.test.ts)

### 3. `unstable_dev` (Legacy)

**Use for**: Backward compatibility with existing tests.

**Note**: This API is being phased out in favor of `unstable_startWorker`. New tests should use `unstable_startWorker`.

**Example**:

```typescript
import { unstable_dev } from 'wrangler';

const worker = await unstable_dev('src/index.ts', {
  config: 'wrangler.toml',
  experimental: { disableExperimentalWarning: true },
});

const response = await worker.fetch();

await worker.stop();
```

**See**: [`src/unstable-dev.test.ts`](./src/unstable-dev.test.ts)

## 🧪 Test Files

- **`examples.test.ts`** ⭐ **Start Here** - Minimal working examples
  - No binding configuration required
  - Demonstrates `getPlatformProxy` API
  - All tests pass out of the box
  - Best for learning the APIs

- **`index.test.ts`** - Main integration tests using `unstable_startWorker`
  - Health check endpoints
  - CORS handling
  - GitHub webhook integration
  - API routing
  - Asset handling

- **`platform-proxy.test.ts`** - Platform proxy tests using `getPlatformProxy`
  - KV namespace operations
  - D1 database queries
  - R2 bucket operations
  - Durable Objects access
  - Context and cf properties

- **`unstable-dev.test.ts`** - Legacy API examples using `unstable_dev`
  - Backward compatibility demonstrations
  - Migration reference

- **`multi-worker.test.ts`** - Multi-worker testing patterns
  - Service binding examples
  - Parent-child worker communication
  - Commented examples for reference

## 🏗️ Architecture

### Test Structure

```
workspace/cloudflare/workers/
├── src/
│   ├── index.ts                    # Main worker code
│   ├── index.test.ts               # Integration tests (unstable_startWorker)
│   ├── platform-proxy.test.ts      # Platform proxy tests (getPlatformProxy)
│   ├── unstable-dev.test.ts        # Legacy API tests (unstable_dev)
│   ├── multi-worker.test.ts        # Multi-worker examples
│   └── durable-objects/
│       └── rate-limiter.ts         # Durable Object implementation
├── vitest.config.ts                # Vitest configuration
├── tsconfig.json                   # TypeScript configuration
├── package.json                    # Dependencies and scripts
└── README.md                       # This file
```

### Configuration

Tests use the root `wrangler.toml` configuration located at:
```
../../../wrangler.toml
```

This configuration includes:
- Environment bindings (KV, D1, R2, Durable Objects)
- Development settings
- Environment-specific configurations (dev, staging, production)

## 🔧 Writing Tests

### Integration Test Pattern

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_startWorker } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('My Worker Tests', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    worker = await unstable_startWorker({
      config: 'wrangler.toml',
    });
  });

  afterAll(async () => {
    await worker.dispose();
  });

  it('should handle requests', async () => {
    const response = await worker.fetch('http://example.com/api/test');
    expect(response.status).toBe(200);
  });
});
```

### Platform Proxy Pattern

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { getPlatformProxy } from 'wrangler';

interface Env {
  CACHE: KVNamespace;
  DB: D1Database;
}

describe('Platform Proxy Tests', () => {
  let platform: Awaited<ReturnType<typeof getPlatformProxy<Env>>>;

  beforeAll(async () => {
    platform = await getPlatformProxy<Env>({
      configPath: 'wrangler.toml',
      persist: false,
    });
  });

  afterAll(async () => {
    await platform.dispose();
  });

  it('should test bindings', async () => {
    await platform.env.CACHE.put('test', 'value');
    const value = await platform.env.CACHE.get('test');
    expect(value).toBe('value');
  });
});
```

## 📚 Resources

- [Wrangler API Documentation](https://developers.cloudflare.com/workers/wrangler/api/)
- [Cloudflare Workers Testing Guide](https://developers.cloudflare.com/workers/testing/)
- [Vitest Workers Pool Documentation](https://developers.cloudflare.com/workers/testing/vitest-integration/)
- [Cloudflare Workers Runtime APIs](https://developers.cloudflare.com/workers/runtime-apis/)

## 🐛 Troubleshooting

### Tests Fail with "Worker not found"

Make sure the `wrangler.toml` path is correct relative to your test file:
```typescript
worker = await unstable_startWorker({
  config: '../../../wrangler.toml', // Adjust path as needed
});
```

### Bindings Not Available

Ensure bindings are defined in `wrangler.toml`:
```toml
[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-id"
```

For tests, you can use empty IDs or test-specific configurations.

### Platform Proxy Errors

Platform proxy requires `workerd` to be running. Make sure you have:
- Node.js 18+ installed
- Wrangler installed as a dev dependency
- Proper permissions to run `workerd`

### Multi-Worker Tests Fail

Ensure:
1. Child worker starts before parent worker
2. Child worker stops after parent worker
3. Service bindings are correctly configured
4. Both workers use compatible Wrangler configurations

## 🚦 CI/CD Integration

These tests can be integrated into GitHub Actions:

```yaml
- name: Install dependencies
  run: npm install

- name: Run Worker tests
  run: npm test
  working-directory: workspace/cloudflare/workers
```

## 📝 Best Practices

1. **Use `unstable_startWorker` for new tests** - It's faster and more reliable
2. **Cleanup resources** - Always call `dispose()` or `stop()` in `afterAll`
3. **Mock external dependencies** - Don't rely on external services in tests
4. **Test edge cases** - Cover error conditions and edge cases
5. **Use TypeScript** - Leverage type safety for better test reliability
6. **Keep tests isolated** - Each test should be independent
7. **Use descriptive test names** - Make test intent clear

## 🔐 Security

- Never commit real API keys or secrets to test files
- Use environment variables for sensitive configuration
- Use test-specific bindings separate from production
- Implement proper webhook signature verification in tests

## 📄 License

Part of the MachineNativeOps platform.
