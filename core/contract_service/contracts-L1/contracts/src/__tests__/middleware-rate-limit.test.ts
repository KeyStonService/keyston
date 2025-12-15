/**
 * Rate Limiting Middleware Tests
 * Unit tests for express-rate-limit middleware configuration and behavior
 */

import request from 'supertest';
import express from 'express';
import rateLimit from 'express-rate-limit';
import { ErrorCode } from '../errors';

/**
 * Creates a test Express application with the rate limiter middleware configured
 * identically to the production routes.ts configuration.
 */
const createTestApp = () => {
  const app = express();
  app.use(express.json());

  // Create rate limiter with same configuration as routes.ts
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
    legacyHeaders: false, // Disable the `X-RateLimit-*` headers
    handler: (req, res) => {
      const traceId = (req as any).traceId || 'test-trace-id';
      res.status(429).json({
        error: {
          code: ErrorCode.RATE_LIMIT,
          message: 'Too many requests, please try again later.',
          status: 429,
          traceId,
          timestamp: new Date().toISOString(),
        },
      });
    },
  });

  // Test endpoint with rate limiting
  app.post('/api/test', limiter, (req, res) => {
    res.status(200).json({ success: true });
  });

  return app;
};

describe('Rate Limiting Middleware', () => {
  let app: express.Application;

  beforeEach(() => {
    app = createTestApp();
  });

  describe('Basic Rate Limiting Behavior', () => {
    it('should allow requests within the limit', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });

    it('should include rate limit headers in response', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.headers).toHaveProperty('ratelimit-limit');
      expect(response.headers).toHaveProperty('ratelimit-remaining');
      expect(response.headers).toHaveProperty('ratelimit-reset');
    });

    it('should set correct RateLimit-Limit header', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.headers['ratelimit-limit']).toBe('100');
    });

    it('should decrement RateLimit-Remaining header on each request', async () => {
      const response1 = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      const remaining1 = parseInt(response1.headers['ratelimit-remaining'], 10);

      const response2 = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      const remaining2 = parseInt(response2.headers['ratelimit-remaining'], 10);

      expect(remaining1).toBeGreaterThan(remaining2);
      expect(remaining1 - remaining2).toBe(1);
    });

    it('should include RateLimit-Reset timestamp', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      const resetTime = parseInt(response.headers['ratelimit-reset'], 10);
      // Reset time is in seconds and should be within the 15-minute window (900 seconds)
      expect(resetTime).toBeGreaterThan(0);
      expect(resetTime).toBeLessThanOrEqual(900);
    });
  });

  describe('Rate Limit Exceeded', () => {
    it('should return 429 when rate limit is exceeded', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
    });

    it('should return correct error response format when rate limited', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toMatchObject({
        code: ErrorCode.RATE_LIMIT,
        message: 'Too many requests, please try again later.',
        status: 429,
        traceId: expect.any(String),
        timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/),
      });
    });

    it('should include error code RATE_LIMIT in response', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
      expect(response.body.error.code).toBe(ErrorCode.RATE_LIMIT);
    });

    it('should include timestamp in rate limit error response', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      const beforeTime = Date.now();

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      const afterTime = Date.now();

      expect(response.status).toBe(429);
      const timestamp = new Date(response.body.error.timestamp).getTime();
      expect(timestamp).toBeGreaterThanOrEqual(beforeTime);
      expect(timestamp).toBeLessThanOrEqual(afterTime);
    });

    it('should include traceId in rate limit error response', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
      expect(response.body.error.traceId).toBeDefined();
      expect(typeof response.body.error.traceId).toBe('string');
      expect(response.body.error.traceId.length).toBeGreaterThan(0);
    });
  });

  describe('Rate Limit Headers', () => {
    it('should not include legacy X-RateLimit headers', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.headers).not.toHaveProperty('x-ratelimit-limit');
      expect(response.headers).not.toHaveProperty('x-ratelimit-remaining');
      expect(response.headers).not.toHaveProperty('x-ratelimit-reset');
    });

    it('should use standard RateLimit headers (lowercase)', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      // Headers are lowercase in Node.js HTTP
      expect(response.headers).toHaveProperty('ratelimit-limit');
      expect(response.headers).toHaveProperty('ratelimit-remaining');
      expect(response.headers).toHaveProperty('ratelimit-reset');
    });

    it('should show RateLimit-Remaining as 0 when limit is reached', async () => {
      // Make exactly 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      const responses = await Promise.all(promises);

      // The last successful request should show 0 remaining
      const lastSuccessful = responses[responses.length - 1];
      expect(lastSuccessful.status).toBe(200);
      expect(lastSuccessful.headers['ratelimit-remaining']).toBe('0');
    });
  });

  describe('IP-based Rate Limiting', () => {
    it('should track limits independently per test run', async () => {
      // Each test run has its own rate limiter instance
      // Make multiple requests and verify they are tracked
      const response1 = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      const remaining1 = parseInt(response1.headers['ratelimit-remaining'], 10);

      const response2 = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      const remaining2 = parseInt(response2.headers['ratelimit-remaining'], 10);

      // Second request should have fewer remaining requests
      expect(remaining1).toBeGreaterThan(remaining2);
      expect(remaining1 - remaining2).toBe(1);
    });
  });

  describe('Rate Limit Window Configuration', () => {
    it('should use 15-minute window (900000ms)', () => {
      // This is validated through the header values
      const response = request(app)
        .post('/api/test')
        .send({ data: 'test' });

      return response.then((res) => {
        expect(res.status).toBe(200);
        const resetTime = parseInt(res.headers['ratelimit-reset'], 10);

        // Reset time is in seconds until the window expires
        // Should be within 15 minutes (900 seconds)
        expect(resetTime).toBeGreaterThan(0);
        expect(resetTime).toBeLessThanOrEqual(900);
      });
    });

    it('should have maximum of 100 requests per window', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.headers['ratelimit-limit']).toBe('100');
    });
  });

  describe('Error Response Consistency', () => {
    it('should match standard error response format', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
      // Verify response structure matches standard error format
      expect(response.body).toEqual({
        error: {
          code: expect.any(String),
          message: expect.any(String),
          status: 429,
          traceId: expect.any(String),
          timestamp: expect.any(String),
        },
      });
    });

    it('should return JSON content-type for rate limit errors', async () => {
      // Make 100 requests to hit the limit
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          request(app)
            .post('/api/test')
            .send({ data: 'test' })
        );
      }
      await Promise.all(promises);

      // The 101st request should be rate limited
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(429);
      expect(response.headers['content-type']).toMatch(/application\/json/);
    });
  });

  describe('Sequential Request Behavior', () => {
    it('should correctly track remaining requests sequentially', async () => {
      const remainingCounts: number[] = [];

      // Make 5 sequential requests
      for (let i = 0; i < 5; i++) {
        const response = await request(app)
          .post('/api/test')
          .send({ data: 'test' });

        expect(response.status).toBe(200);
        remainingCounts.push(parseInt(response.headers['ratelimit-remaining'], 10));
      }

      // Verify counts decrease by 1 each time
      for (let i = 1; i < remainingCounts.length; i++) {
        expect(remainingCounts[i - 1] - remainingCounts[i]).toBe(1);
      }
    });

    it('should maintain consistent rate limit across multiple requests', async () => {
      const responses = [];

      for (let i = 0; i < 3; i++) {
        const response = await request(app)
          .post('/api/test')
          .send({ data: 'test' });
        responses.push(response);
      }

      // All responses should have the same limit
      responses.forEach((response) => {
        expect(response.status).toBe(200);
        expect(response.headers['ratelimit-limit']).toBe('100');
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle first request correctly', async () => {
      const response = await request(app)
        .post('/api/test')
        .send({ data: 'test' });

      expect(response.status).toBe(200);
      expect(response.headers['ratelimit-limit']).toBe('100');
      expect(parseInt(response.headers['ratelimit-remaining'], 10)).toBeLessThanOrEqual(100);
      expect(parseInt(response.headers['ratelimit-remaining'], 10)).toBeGreaterThanOrEqual(0);
    });

    it('should handle empty request body', async () => {
      const response = await request(app)
        .post('/api/test')
        .send();

      expect(response.status).toBe(200);
      expect(response.headers).toHaveProperty('ratelimit-limit');
      expect(response.headers).toHaveProperty('ratelimit-remaining');
    });

    it('should handle requests with different content types', async () => {
      const response = await request(app)
        .post('/api/test')
        .set('Content-Type', 'application/x-www-form-urlencoded')
        .send('data=test');

      expect(response.status).toBe(200);
      expect(response.headers).toHaveProperty('ratelimit-limit');
      expect(response.headers).toHaveProperty('ratelimit-remaining');
    });
  });
});
