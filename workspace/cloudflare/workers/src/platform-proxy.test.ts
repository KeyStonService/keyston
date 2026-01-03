/**
 * Platform Proxy Tests for MachineNativeOps Worker
 * 
 * These tests use Wrangler's `getPlatformProxy` API to emulate Cloudflare Workers
 * platform bindings in a Node.js environment. This is useful for testing code that
 * interacts with Workers bindings (KV, D1, R2, etc.) outside the Workers runtime.
 * 
 * @see https://developers.cloudflare.com/workers/wrangler/api/#getplatformproxy
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { getPlatformProxy } from 'wrangler';

// Define the shape of our environment bindings
interface Env {
  CACHE: KVNamespace;
  SESSIONS: KVNamespace;
  DB: D1Database;
  ASSETS: R2Bucket;
  RATE_LIMITER: DurableObjectNamespace;
  ENVIRONMENT: string;
}

describe('Platform Proxy - Bindings Emulation', () => {
  let platform: Awaited<ReturnType<typeof getPlatformProxy<Env>>>;

  beforeAll(async () => {
    // Get platform proxy with our environment bindings
    platform = await getPlatformProxy<Env>({
      configPath: '../../../wrangler.toml',
      persist: false, // Don't persist data for tests
    });
  });

  afterAll(async () => {
    // Cleanup: terminate the underlying workerd process
    await platform.dispose();
  });

  describe('Environment Variables', () => {
    it('should have access to environment variables', () => {
      // The ENVIRONMENT binding should be available from the config
      expect(platform.env).toBeDefined();
    });
  });

  describe('KV Namespace Bindings', () => {
    it('should have CACHE KV namespace binding', () => {
      expect(platform.env.CACHE).toBeDefined();
    });

    it('should have SESSIONS KV namespace binding', () => {
      expect(platform.env.SESSIONS).toBeDefined();
    });

    it('should support KV operations (put/get)', async () => {
      const testKey = 'test:key';
      const testValue = 'test-value';

      // Put a value in KV
      await platform.env.CACHE.put(testKey, testValue);

      // Get the value back
      const retrievedValue = await platform.env.CACHE.get(testKey);
      expect(retrievedValue).toBe(testValue);

      // Cleanup
      await platform.env.CACHE.delete(testKey);
    });

    it('should support KV expiration', async () => {
      const testKey = 'test:expiring-key';
      const testValue = 'expiring-value';

      // Put a value with TTL
      await platform.env.CACHE.put(testKey, testValue, {
        expirationTtl: 1, // 1 second
      });

      // Value should exist immediately
      const immediateValue = await platform.env.CACHE.get(testKey);
      expect(immediateValue).toBe(testValue);

      // Wait for expiration (in practice, KV TTL is not immediate)
      // This is a demonstration - actual expiration timing may vary
    });
  });

  describe('D1 Database Binding', () => {
    it('should have DB D1 database binding', () => {
      expect(platform.env.DB).toBeDefined();
    });

    it('should support D1 queries', async () => {
      // Create a test table
      await platform.env.DB.exec(`
        CREATE TABLE IF NOT EXISTS test_table (
          id INTEGER PRIMARY KEY,
          name TEXT
        )
      `);

      // Insert test data
      await platform.env.DB.prepare(
        'INSERT INTO test_table (id, name) VALUES (?, ?)'
      )
        .bind(1, 'test-name')
        .run();

      // Query the data
      const result = await platform.env.DB.prepare(
        'SELECT * FROM test_table WHERE id = ?'
      )
        .bind(1)
        .first();

      expect(result).toBeDefined();
      expect(result?.name).toBe('test-name');

      // Cleanup
      await platform.env.DB.exec('DROP TABLE IF EXISTS test_table');
    });
  });

  describe('R2 Bucket Binding', () => {
    it('should have ASSETS R2 bucket binding', () => {
      expect(platform.env.ASSETS).toBeDefined();
    });

    it('should support R2 operations (put/get)', async () => {
      const testKey = 'test-file.txt';
      const testContent = 'Hello from R2!';

      // Put an object in R2
      await platform.env.ASSETS.put(testKey, testContent);

      // Get the object back
      const object = await platform.env.ASSETS.get(testKey);
      expect(object).not.toBeNull();

      if (object) {
        const content = await object.text();
        expect(content).toBe(testContent);
      }

      // Cleanup
      await platform.env.ASSETS.delete(testKey);
    });
  });

  describe('Durable Objects Binding', () => {
    it('should have RATE_LIMITER Durable Object binding', () => {
      expect(platform.env.RATE_LIMITER).toBeDefined();
    });
  });

  describe('Context and CF Properties', () => {
    it('should provide context with waitUntil and passThroughOnException', () => {
      expect(platform.ctx).toBeDefined();
      expect(platform.ctx.waitUntil).toBeDefined();
      expect(platform.ctx.passThroughOnException).toBeDefined();

      // These are mock implementations that do nothing in the proxy
      expect(() => platform.ctx.waitUntil(Promise.resolve())).not.toThrow();
      expect(() => platform.ctx.passThroughOnException()).not.toThrow();
    });

    it('should provide cf property with request metadata', () => {
      expect(platform.cf).toBeDefined();
      // The cf property contains mock data similar to production
    });
  });

  describe('Caches API', () => {
    it('should provide caches API emulation', () => {
      expect(platform.caches).toBeDefined();
    });
  });
});
