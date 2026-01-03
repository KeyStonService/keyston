/**
 * Multi-Worker Integration Tests
 * 
 * This example demonstrates testing multiple Workers that communicate with each other.
 * It shows how to set up parent-child Worker relationships for testing service bindings.
 * 
 * @see https://developers.cloudflare.com/workers/wrangler/api/#multi-worker-example
 */
import { describe } from 'vitest';

/**
 * Note: This is a demonstration test that would work if you have:
 * 1. A child worker (e.g., child-worker.ts)
 * 2. A parent worker that calls the child worker via service binding
 * 3. Separate wrangler.toml configs for each worker
 * 
 * For the MachineNativeOps platform, this pattern could be used for:
 * - API Gateway (parent) -> Auth Service (child)
 * - Main Worker (parent) -> Rate Limiter Worker (child)
 * - Router (parent) -> Multiple Backend Workers (children)
 */
describe.skip('Multi-Worker Testing Example', () => {
  // Example test structure - uncomment and adapt when implementing multi-worker setup
  
  /*
  let childWorker: Awaited<ReturnType<typeof unstable_dev>>;
  let parentWorker: Awaited<ReturnType<typeof unstable_dev>>;

  beforeAll(async () => {
    // Start child worker first
    childWorker = await unstable_dev('src/child-worker.ts', {
      config: 'src/child-wrangler.toml',
      experimental: { disableExperimentalWarning: true },
    });

    // Start parent worker second
    // The parent worker's wrangler.toml should have a service binding to the child
    parentWorker = await unstable_dev('src/parent-worker.ts', {
      config: 'src/parent-wrangler.toml',
      experimental: { disableExperimentalWarning: true },
    });
  });

  afterAll(async () => {
    // Important: Stop child worker AFTER parent worker
    // If you stop the child first, parent worker won't be able to reach it
    await parentWorker.stop();
    await childWorker.stop();
  });

  it('should test child worker independently', async () => {
    // Test that child worker works on its own
    const response = await childWorker.fetch();
    const text = await response.text();
    expect(text).toBe('Hello from Child Worker!');
  });

  it('should test parent worker calling child worker', async () => {
    // Test that parent worker can successfully call child worker
    const response = await parentWorker.fetch();
    const text = await response.text();
    expect(text).toBe('Parent worker sees: Hello from Child Worker!');
  });
  */
});

/**
 * Example Child Worker Implementation
 * 
 * Save as: src/child-worker.ts
 * 
 * ```typescript
 * export default {
 *   async fetch(request: Request): Promise<Response> {
 *     return new Response('Hello from Child Worker!');
 *   },
 * };
 * ```
 */

/**
 * Example Parent Worker Implementation
 * 
 * Save as: src/parent-worker.ts
 * 
 * ```typescript
 * interface Env {
 *   CHILD_WORKER: Fetcher;
 * }
 * 
 * export default {
 *   async fetch(request: Request, env: Env): Promise<Response> {
 *     const response = await env.CHILD_WORKER.fetch(request);
 *     const text = await response.text();
 *     return new Response(`Parent worker sees: ${text}`);
 *   },
 * };
 * ```
 */

/**
 * Example Child Worker Configuration
 * 
 * Save as: src/child-wrangler.toml
 * 
 * ```toml
 * name = "child-worker"
 * main = "src/child-worker.ts"
 * compatibility_date = "2025-12-01"
 * ```
 */

/**
 * Example Parent Worker Configuration
 * 
 * Save as: src/parent-wrangler.toml
 * 
 * ```toml
 * name = "parent-worker"
 * main = "src/parent-worker.ts"
 * compatibility_date = "2025-12-01"
 * 
 * [[services]]
 * binding = "CHILD_WORKER"
 * service = "child-worker"
 * ```
 */
