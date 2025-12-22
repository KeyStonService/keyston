/**
 * Rate Limiter Durable Object
 *
 * Provides distributed rate limiting using Cloudflare Durable Objects.
 * Implements a sliding window algorithm for accurate rate limiting.
 */

interface RateLimitConfig {
  windowMs: number;      // Time window in milliseconds
  maxRequests: number;   // Max requests per window
}

interface RequestRecord {
  timestamp: number;
  count: number;
}

export class RateLimiter {
  private state: DurableObjectState;
  private requests: RequestRecord[] = [];
  private config: RateLimitConfig = {
    windowMs: 60000,    // 1 minute window
    maxRequests: 100,   // 100 requests per minute
  };

  constructor(state: DurableObjectState, env: unknown) {
    this.state = state;

    // Load state from storage
    this.state.blockConcurrencyWhile(async () => {
      const stored = await this.state.storage.get<RequestRecord[]>('requests');
      if (stored) {
        this.requests = stored;
      }
    });
  }

  async fetch(request: Request): Promise<Response> {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    // Clean up old requests outside the window
    this.requests = this.requests.filter(r => r.timestamp > windowStart);

    // Count requests in the current window
    const totalRequests = this.requests.reduce((sum, r) => sum + r.count, 0);

    if (totalRequests >= this.config.maxRequests) {
      const oldestRequest = this.requests[0];
      const retryAfter = oldestRequest
        ? Math.ceil((oldestRequest.timestamp + this.config.windowMs - now) / 1000)
        : 60;

      return new Response(JSON.stringify({
        error: 'Rate limit exceeded',
        limit: this.config.maxRequests,
        window: this.config.windowMs / 1000,
        retry_after: retryAfter,
      }), {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'X-RateLimit-Limit': this.config.maxRequests.toString(),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': (Math.floor(now / 1000) + retryAfter).toString(),
          'Retry-After': retryAfter.toString(),
        },
      });
    }

    // Add new request
    this.requests.push({ timestamp: now, count: 1 });

    // Persist state
    await this.state.storage.put('requests', this.requests);

    const remaining = this.config.maxRequests - totalRequests - 1;

    return new Response(JSON.stringify({
      allowed: true,
      remaining,
      limit: this.config.maxRequests,
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'X-RateLimit-Limit': this.config.maxRequests.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
        'X-RateLimit-Reset': (Math.floor((now + this.config.windowMs) / 1000)).toString(),
      },
    });
  }

  /**
   * Handle alarm for cleanup
   */
  async alarm(): Promise<void> {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    this.requests = this.requests.filter(r => r.timestamp > windowStart);
    await this.state.storage.put('requests', this.requests);

    // Schedule next cleanup if there are still requests
    if (this.requests.length > 0) {
      const nextCleanup = this.requests[0].timestamp + this.config.windowMs;
      await this.state.storage.setAlarm(nextCleanup);
    }
  }
}
