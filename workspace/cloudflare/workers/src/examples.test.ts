/**
 * Minimal Working Example Tests
 * 
 * These tests demonstrate the Wrangler APIs without requiring configured bindings.
 * They show the basic structure and API usage.
 */
import { describe, it, expect } from 'vitest';
import { getPlatformProxy } from 'wrangler';

describe('Wrangler API Examples - Minimal', () => {
  describe('getPlatformProxy - Basic Usage', () => {
    it('should create platform proxy successfully', async () => {
      const platform = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      // Platform proxy should be created
      expect(platform).toBeDefined();
      expect(platform.env).toBeDefined();
      expect(platform.ctx).toBeDefined();
      expect(platform.cf).toBeDefined();
      expect(platform.caches).toBeDefined();

      // Cleanup
      await platform.dispose();
    });

    it('should provide context helpers', async () => {
      const platform = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      // Context should have waitUntil and passThroughOnException
      expect(typeof platform.ctx.waitUntil).toBe('function');
      expect(typeof platform.ctx.passThroughOnException).toBe('function');

      // These are mock implementations that don't throw
      expect(() => platform.ctx.waitUntil(Promise.resolve())).not.toThrow();
      expect(() => platform.ctx.passThroughOnException()).not.toThrow();

      // Cleanup
      await platform.dispose();
    });

    it('should provide cf request properties', async () => {
      const platform = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      // CF properties should be available (mock data)
      expect(platform.cf).toBeDefined();
      expect(typeof platform.cf).toBe('object');

      // Cleanup
      await platform.dispose();
    });

    it('should provide caches API', async () => {
      const platform = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      // Caches API should be available
      expect(platform.caches).toBeDefined();
      expect(typeof platform.caches).toBe('object');

      // Cleanup
      await platform.dispose();
    });

    it('should allow multiple platform proxy instances', async () => {
      const platform1 = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      const platform2 = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      expect(platform1).toBeDefined();
      expect(platform2).toBeDefined();

      // Both should work independently
      expect(platform1.env).toBeDefined();
      expect(platform2.env).toBeDefined();

      // Cleanup both
      await platform1.dispose();
      await platform2.dispose();
    });
  });

  describe('API Documentation Examples', () => {
    it('demonstrates basic getPlatformProxy usage from docs', async () => {
      // Example from Cloudflare docs
      const { env, dispose } = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
      });

      // Access environment (bindings would be here if configured)
      expect(env).toBeDefined();

      // Cleanup
      await dispose();
    });

    it('demonstrates persist option', async () => {
      // With persist: false, no data is written to filesystem
      const platform1 = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: false,
      });

      expect(platform1).toBeDefined();
      await platform1.dispose();

      // With persist: true, data would be persisted
      // (defaults to same location as Wrangler)
      const platform2 = await getPlatformProxy({
        configPath: '../../../wrangler.toml',
        persist: true,
      });

      expect(platform2).toBeDefined();
      await platform2.dispose();
    });
  });
});
