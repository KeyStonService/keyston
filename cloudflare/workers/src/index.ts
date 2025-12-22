/**
 * MachineNativeOps - Cloudflare Worker Entry Point
 *
 * This worker serves as the edge gateway for the MachineNativeOps platform,
 * providing API routing, caching, rate limiting, and GitHub integration.
 *
 * @module machinenativeops-worker
 */

import { RateLimiter } from './durable-objects/rate-limiter';

export { RateLimiter };

// ============================================================================
// Type Definitions
// ============================================================================

interface Env {
  // KV Namespaces
  CACHE: KVNamespace;
  SESSIONS: KVNamespace;

  // D1 Database
  DB: D1Database;

  // R2 Bucket
  ASSETS: R2Bucket;

  // Durable Objects
  RATE_LIMITER: DurableObjectNamespace;

  // Environment Variables
  ENVIRONMENT: string;
  GITHUB_TOKEN?: string;
  GITHUB_WEBHOOK_SECRET?: string;
  API_BACKEND_URL?: string;

  // Optional AI binding
  AI?: Ai;
}

interface GitHubWebhookPayload {
  action?: string;
  repository?: {
    full_name: string;
    html_url: string;
  };
  sender?: {
    login: string;
  };
  [key: string]: unknown;
}

// ============================================================================
// Constants
// ============================================================================

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-GitHub-Event, X-Hub-Signature-256',
  'Access-Control-Max-Age': '86400',
};

// ============================================================================
// Main Worker
// ============================================================================

export default {
  /**
   * Main fetch handler for incoming requests
   */
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    try {
      // Route requests
      return await routeRequest(request, env, ctx, url);
    } catch (error) {
      console.error('Worker error:', error);
      return createErrorResponse(error as Error);
    }
  },

  /**
   * Scheduled event handler (Cron Triggers)
   */
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log(`Cron trigger: ${event.cron}`);

    // Perform scheduled tasks
    switch (event.cron) {
      case '0 * * * *': // Every hour
        await cleanupExpiredCache(env);
        break;
      case '0 0 * * *': // Daily at midnight
        await generateDailyReport(env);
        break;
    }
  },

  /**
   * Queue message handler
   */
  async queue(batch: MessageBatch<unknown>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      console.log('Processing queue message:', message.body);
      // Process queue messages
      message.ack();
    }
  },
};

// ============================================================================
// Request Router
// ============================================================================

async function routeRequest(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
  url: URL
): Promise<Response> {
  const path = url.pathname;

  // Health check endpoint
  if (path === '/health' || path === '/healthz') {
    return createJsonResponse({
      status: 'healthy',
      environment: env.ENVIRONMENT,
      timestamp: new Date().toISOString()
    });
  }

  // GitHub webhook endpoint
  if (path === '/webhooks/github') {
    return await handleGitHubWebhook(request, env);
  }

  // GitHub API proxy endpoints
  if (path.startsWith('/api/github/')) {
    return await handleGitHubAPI(request, env, url);
  }

  // Rate limit check
  const rateLimitResult = await checkRateLimit(request, env);
  if (rateLimitResult) {
    return rateLimitResult;
  }

  // API routes
  if (path.startsWith('/api/')) {
    return await handleAPIRequest(request, env, ctx, url);
  }

  // Static assets from R2
  if (path.startsWith('/assets/')) {
    return await handleAssetRequest(request, env, url);
  }

  // Cache-first response for other routes
  const cacheKey = new Request(url.toString(), request);
  const cache = caches.default;

  let response = await cache.match(cacheKey);
  if (response) {
    return response;
  }

  // Fallback: proxy to backend or return 404
  if (env.API_BACKEND_URL) {
    response = await proxyToBackend(request, env);
    ctx.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  }

  return createJsonResponse({ error: 'Not Found' }, 404);
}

// ============================================================================
// GitHub Integration
// ============================================================================

/**
 * Handle GitHub webhook events
 */
async function handleGitHubWebhook(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') {
    return createJsonResponse({ error: 'Method not allowed' }, 405);
  }

  const signature = request.headers.get('X-Hub-Signature-256');
  const event = request.headers.get('X-GitHub-Event');

  if (!event) {
    return createJsonResponse({ error: 'Missing GitHub event header' }, 400);
  }

  const body = await request.text();

  // Verify webhook signature if secret is configured
  if (env.GITHUB_WEBHOOK_SECRET && signature) {
    const isValid = await verifyGitHubSignature(body, signature, env.GITHUB_WEBHOOK_SECRET);
    if (!isValid) {
      return createJsonResponse({ error: 'Invalid signature' }, 401);
    }
  }

  const payload: GitHubWebhookPayload = JSON.parse(body);

  // Log webhook event
  console.log(`GitHub webhook: ${event}`, {
    action: payload.action,
    repository: payload.repository?.full_name,
    sender: payload.sender?.login,
  });

  // Store webhook event in KV for processing
  const eventId = crypto.randomUUID();
  await env.CACHE.put(
    `webhook:${eventId}`,
    JSON.stringify({ event, payload, timestamp: Date.now() }),
    { expirationTtl: 86400 } // 24 hours
  );

  // Process different webhook events
  switch (event) {
    case 'push':
      await handlePushEvent(payload, env);
      break;
    case 'pull_request':
      await handlePullRequestEvent(payload, env);
      break;
    case 'issues':
      await handleIssuesEvent(payload, env);
      break;
    case 'workflow_run':
      await handleWorkflowRunEvent(payload, env);
      break;
    case 'release':
      await handleReleaseEvent(payload, env);
      break;
    default:
      console.log(`Unhandled GitHub event: ${event}`);
  }

  return createJsonResponse({
    received: true,
    event_id: eventId,
    event_type: event
  });
}

/**
 * Verify GitHub webhook signature
 */
async function verifyGitHubSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signatureBuffer = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(payload)
  );

  const expectedSignature = 'sha256=' + Array.from(new Uint8Array(signatureBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  return signature === expectedSignature;
}

/**
 * Handle GitHub API proxy requests
 */
async function handleGitHubAPI(request: Request, env: Env, url: URL): Promise<Response> {
  if (!env.GITHUB_TOKEN) {
    return createJsonResponse({ error: 'GitHub token not configured' }, 500);
  }

  const githubPath = url.pathname.replace('/api/github/', '');
  const githubUrl = `https://api.github.com/${githubPath}${url.search}`;

  const response = await fetch(githubUrl, {
    method: request.method,
    headers: {
      'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'MachineNativeOps-Worker/1.0',
    },
    body: request.method !== 'GET' ? await request.text() : undefined,
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      ...CORS_HEADERS,
      'Content-Type': 'application/json',
    },
  });
}

// ============================================================================
// GitHub Event Handlers
// ============================================================================

async function handlePushEvent(payload: GitHubWebhookPayload, env: Env): Promise<void> {
  console.log('Processing push event', payload.repository?.full_name);
  // Trigger CI/CD pipeline, update caches, etc.
}

async function handlePullRequestEvent(payload: GitHubWebhookPayload, env: Env): Promise<void> {
  console.log('Processing pull request event', payload.action);
  // Handle PR opened, closed, merged, etc.
}

async function handleIssuesEvent(payload: GitHubWebhookPayload, env: Env): Promise<void> {
  console.log('Processing issues event', payload.action);
  // Handle issue opened, closed, labeled, etc.
}

async function handleWorkflowRunEvent(payload: GitHubWebhookPayload, env: Env): Promise<void> {
  console.log('Processing workflow run event', payload.action);
  // Handle workflow completed, failed, etc.
}

async function handleReleaseEvent(payload: GitHubWebhookPayload, env: Env): Promise<void> {
  console.log('Processing release event', payload.action);
  // Handle new releases, deployments, etc.
}

// ============================================================================
// Rate Limiting
// ============================================================================

async function checkRateLimit(request: Request, env: Env): Promise<Response | null> {
  const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';

  const id = env.RATE_LIMITER.idFromName(clientIP);
  const rateLimiter = env.RATE_LIMITER.get(id);

  const response = await rateLimiter.fetch(request);

  if (response.status === 429) {
    return createJsonResponse(
      { error: 'Rate limit exceeded', retry_after: 60 },
      429,
      { 'Retry-After': '60' }
    );
  }

  return null;
}

// ============================================================================
// API Request Handler
// ============================================================================

async function handleAPIRequest(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
  url: URL
): Promise<Response> {
  const path = url.pathname.replace('/api/', '');

  // Try to get from cache first
  const cacheKey = `api:${path}:${url.search}`;
  const cached = await env.CACHE.get(cacheKey);

  if (cached && request.method === 'GET') {
    return createJsonResponse(JSON.parse(cached));
  }

  // Proxy to backend
  if (env.API_BACKEND_URL) {
    const response = await proxyToBackend(request, env);

    // Cache GET responses
    if (request.method === 'GET' && response.ok) {
      const body = await response.text();
      ctx.waitUntil(env.CACHE.put(cacheKey, body, { expirationTtl: 300 }));
      return new Response(body, {
        status: response.status,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    return response;
  }

  return createJsonResponse({ error: 'Backend not configured' }, 503);
}

// ============================================================================
// Asset Handler
// ============================================================================

async function handleAssetRequest(
  request: Request,
  env: Env,
  url: URL
): Promise<Response> {
  const key = url.pathname.replace('/assets/', '');

  const object = await env.ASSETS.get(key);

  if (!object) {
    return createJsonResponse({ error: 'Asset not found' }, 404);
  }

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('etag', object.httpEtag);
  headers.set('Cache-Control', 'public, max-age=31536000, immutable');

  return new Response(object.body, { headers });
}

// ============================================================================
// Backend Proxy
// ============================================================================

async function proxyToBackend(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const backendUrl = new URL(url.pathname + url.search, env.API_BACKEND_URL);

  const response = await fetch(backendUrl.toString(), {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' && request.method !== 'HEAD'
      ? await request.arrayBuffer()
      : undefined,
  });

  return new Response(response.body, {
    status: response.status,
    headers: { ...CORS_HEADERS, ...Object.fromEntries(response.headers) },
  });
}

// ============================================================================
// Scheduled Tasks
// ============================================================================

async function cleanupExpiredCache(env: Env): Promise<void> {
  console.log('Running cache cleanup...');
  // KV automatically handles TTL, but we can clean up specific patterns
  const list = await env.CACHE.list({ prefix: 'temp:' });
  for (const key of list.keys) {
    await env.CACHE.delete(key.name);
  }
}

async function generateDailyReport(env: Env): Promise<void> {
  console.log('Generating daily report...');
  // Generate and store daily metrics
}

// ============================================================================
// Utility Functions
// ============================================================================

function createJsonResponse(
  data: unknown,
  status = 200,
  extraHeaders: Record<string, string> = {}
): Response {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
      ...extraHeaders,
    },
  });
}

function createErrorResponse(error: Error): Response {
  return createJsonResponse(
    {
      error: 'Internal Server Error',
      message: error.message,
      timestamp: new Date().toISOString(),
    },
    500
  );
}
