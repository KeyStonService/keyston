/**
 * Vitest Configuration for Cloudflare Workers
 * 
 * This configuration sets up two test environments:
 * 1. Node.js environment for Wrangler API tests (unstable_startWorker, getPlatformProxy)
 * 2. Workers environment for in-worker unit tests
 * 
 * @see https://developers.cloudflare.com/workers/testing/vitest-integration/
 */
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Use Node.js environment by default for Wrangler API tests
    environment: 'node',
    
    // Test file patterns
    include: ['**/*.test.ts', '**/*.spec.ts'],
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['**/*.test.ts', '**/*.spec.ts'],
    },
    
    // Increase timeout for worker startup
    testTimeout: 30000,
  },
});
