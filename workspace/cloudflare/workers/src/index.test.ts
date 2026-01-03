/**
 * Integration Tests for MachineNativeOps Worker
 * 
 * These tests use Wrangler's `unstable_startWorker` API to run integration tests
 * against the Worker in a local development server.
 * 
 * @see https://developers.cloudflare.com/workers/wrangler/api/#unstable_startworker
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_startWorker } from 'wrangler';

describe('MachineNativeOps Worker - Integration Tests', () => {
  let worker: Awaited<ReturnType<typeof unstable_startWorker>>;

  beforeAll(async () => {
    // Start the worker with the root wrangler configuration
    worker = await unstable_startWorker({
      config: '../../../wrangler.toml',
    });
  });

  afterAll(async () => {
    // Cleanup: dispose of the worker instance
    await worker.dispose();
  });

  describe('Health Check Endpoint', () => {
    it('should return healthy status on /health', async () => {
      const response = await worker.fetch('http://example.com/health');
      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data).toHaveProperty('status', 'healthy');
      expect(data).toHaveProperty('environment');
      expect(data).toHaveProperty('timestamp');
    });

    it('should return healthy status on /healthz', async () => {
      const response = await worker.fetch('http://example.com/healthz');
      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data).toHaveProperty('status', 'healthy');
    });
  });

  describe('CORS Handling', () => {
    it('should handle OPTIONS preflight requests', async () => {
      const response = await worker.fetch('http://example.com/api/test', {
        method: 'OPTIONS',
      });
      
      expect(response.status).toBe(200);
      expect(response.headers.get('Access-Control-Allow-Origin')).toBeTruthy();
      expect(response.headers.get('Access-Control-Allow-Methods')).toBeTruthy();
    });
  });

  describe('API Routing', () => {
    it('should return 503 for API requests when backend not configured', async () => {
      const response = await worker.fetch('http://example.com/api/test');
      expect(response.status).toBe(503);
      
      const data = await response.json();
      expect(data).toHaveProperty('error', 'Backend not configured');
    });
  });

  describe('GitHub Webhook Endpoint', () => {
    it('should reject non-POST requests to webhook endpoint', async () => {
      const response = await worker.fetch('http://example.com/webhooks/github', {
        method: 'GET',
      });
      
      expect(response.status).toBe(405);
      const data = await response.json();
      expect(data).toHaveProperty('error', 'Method not allowed');
    });

    it('should reject webhook without event header', async () => {
      const response = await worker.fetch('http://example.com/webhooks/github', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ test: 'payload' }),
      });
      
      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error', 'Missing GitHub event header');
    });

    it('should accept valid webhook in development mode', async () => {
      const response = await worker.fetch('http://example.com/webhooks/github', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-GitHub-Event': 'push',
        },
        body: JSON.stringify({
          action: 'created',
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
      expect(data).toHaveProperty('received', true);
      expect(data).toHaveProperty('event_id');
      expect(data).toHaveProperty('event_type', 'push');
    });
  });

  describe('Asset Handling', () => {
    it('should return 404 for non-existent assets', async () => {
      const response = await worker.fetch('http://example.com/assets/non-existent.png');
      expect(response.status).toBe(404);
      
      const data = await response.json();
      expect(data).toHaveProperty('error', 'Asset not found');
    });
  });

  describe('404 Handling', () => {
    it('should return 404 for unknown routes', async () => {
      const response = await worker.fetch('http://example.com/unknown-route');
      expect(response.status).toBe(404);
      
      const data = await response.json();
      expect(data).toHaveProperty('error', 'Not Found');
    });
  });
});
