/**
 * Legacy unstable_dev API Example Tests
 * 
 * These tests demonstrate the use of Wrangler's `unstable_dev` API.
 * This API is being replaced by `unstable_startWorker`, but is shown here
 * for compatibility and migration purposes.
 * 
 * @see https://developers.cloudflare.com/workers/wrangler/api/#unstable_dev
 * @deprecated Use `unstable_startWorker` for new tests
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { Unstable_DevWorker } from 'wrangler';

describe('MachineNativeOps Worker - unstable_dev API (Legacy)', () => {
  let worker: Unstable_DevWorker;

  beforeAll(async () => {
    // Start the worker using unstable_dev (legacy API)
    // Note: This uses a relative path to the worker script
    worker = await unstable_dev('src/index.ts', {
      config: '../../../wrangler.toml',
      experimental: {
        disableExperimentalWarning: true,
      },
    });
  });

  afterAll(async () => {
    // Stop the dev server
    await worker.stop();
  });

  it('should return health check response', async () => {
    const response = await worker.fetch();
    // Without a specific path, it will hit the root route
    // which should return 404 per our worker logic
    expect(response.status).toBe(404);
  });

  it('should handle health endpoint', async () => {
    const response = await worker.fetch('http://localhost/health');
    expect(response.status).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });

  it('should handle GitHub webhook endpoint', async () => {
    const response = await worker.fetch('http://localhost/webhooks/github', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'push',
      },
      body: JSON.stringify({
        repository: {
          full_name: 'test/repo',
          html_url: 'https://github.com/test/repo',
        },
        sender: {
          login: 'testuser',
        },
      }),
    });
    
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.received).toBe(true);
  });
});
