/**
 * @fileoverview HTTP request logging middleware for Express applications.
 *
 * This module provides comprehensive request/response logging with distributed
 * tracing support via trace IDs. It includes security-conscious header sanitization
 * to prevent sensitive data leakage in logs.
 *
 * @module middleware/logging
 */

import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';

/**
 * Structure for request log entries.
 *
 * Contains all relevant information about an HTTP request for
 * debugging, monitoring, and audit purposes.
 *
 * @interface RequestLog
 * @property {string} traceId - Unique identifier for request tracing across services
 * @property {string} method - HTTP method (GET, POST, PUT, DELETE, etc.)
 * @property {string} url - Request URL path and query string
 * @property {string} userAgent - Client user agent string
 * @property {string} ip - Client IP address
 * @property {string} timestamp - ISO 8601 timestamp of request start
 * @property {number} [duration] - Request duration in milliseconds (set on completion)
 * @property {number} [statusCode] - HTTP response status code (set on completion)
 */
interface RequestLog {
  traceId: string;
  method: string;
  url: string;
  userAgent: string;
  ip: string;
  timestamp: string;
  duration?: number;
  statusCode?: number;
}

/**
 * Allowlist of HTTP headers allowed in log output.
 * Helps prevent logging of sensitive custom headers while
 * retaining useful debugging information.
 * @constant
 */
const ALLOWED_HEADERS = [
  'user-agent',
  'content-type',
  'authorization',
  'x-forwarded-for',
  'x-real-ip',
] as const;

/**
 * Sanitizes HTTP headers for safe logging by filtering to allowed headers
 * and redacting sensitive values.
 *
 * This function prevents sensitive information from appearing in logs by:
 * 1. Only including headers from the ALLOWED_HEADERS allowlist
 * 2. Redacting the authorization header value to prevent token leakage
 *
 * @param headers - Raw request headers object
 * @returns Sanitized headers object safe for logging
 *
 * @example
 * const rawHeaders = {
 *   'user-agent': 'Mozilla/5.0',
 *   'authorization': 'Bearer secret-token',
 *   'x-custom-secret': 'sensitive-data',
 *   'content-type': 'application/json'
 * };
 *
 * sanitizeHeaders(rawHeaders);
 * // Returns:
 * // {
 * //   'user-agent': 'Mozilla/5.0',
 * //   'authorization': '[REDACTED]',
 * //   'content-type': 'application/json'
 * // }
 *
 * @security Prevents credential leakage in application logs
 */
function sanitizeHeaders(headers: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  for (const key of ALLOWED_HEADERS) {
    if (headers[key]) {
      sanitized[key] = key === 'authorization' ? '[REDACTED]' : headers[key];
    }
  }
  return sanitized;
}

/**
 * Express middleware for comprehensive HTTP request/response logging.
 *
 * This middleware:
 * 1. Generates a unique trace ID (UUID v4) for each request
 * 2. Attaches the trace ID to the request object for use in downstream handlers
 * 3. Logs request details at the start of processing
 * 4. Logs response details (including duration and status) on completion
 * 5. Uses appropriate log levels based on response status codes:
 *    - 5xx errors: console.error
 *    - 4xx errors: console.warn
 *    - Success: console.log
 *
 * In debug mode (LOG_LEVEL=debug), additional details like sanitized headers
 * are included in the log output.
 *
 * @param req - Express request object (modified to include traceId)
 * @param res - Express response object
 * @param next - Express next function
 *
 * @example
 * // Basic usage with Express
 * import express from 'express';
 * import loggingMiddleware from './middleware/logging';
 *
 * const app = express();
 * app.use(loggingMiddleware);
 *
 * @example
 * // Access trace ID in route handlers
 * app.get('/api/data', (req, res) => {
 *   console.log(`Processing request ${req.traceId}`);
 *   res.json({ data: 'example' });
 * });
 */
export const loggingMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const traceId = randomUUID();
  const startTime = Date.now();
  req.traceId = traceId;

  const requestLog: RequestLog = {
    traceId,
    method: req.method,
    url: req.url,
    userAgent: (typeof req.get === 'function' && req.get('user-agent')) || 'unknown',
    ip: req.ip || req.socket?.remoteAddress || 'unknown',
    timestamp: new Date().toISOString(),
  };

  if (config.LOG_LEVEL === 'debug') {
    console.log('Request started:', {
      ...requestLog,
      headers: sanitizeHeaders(req.headers as Record<string, unknown>),
      body: req.body ? '[BODY_PRESENT]' : '[NO_BODY]',
    });
  } else {
    console.log(
      'Request:',
      `${requestLog.method} ${requestLog.url} [${traceId}] ip=${requestLog.ip}`
    );
  }

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const responseLog = { ...requestLog, duration, statusCode: res.statusCode };
    const summary = `${responseLog.method} ${responseLog.url} ${responseLog.statusCode} ${duration}ms [${traceId}] ip=${responseLog.ip}`;
    if (res.statusCode >= 500) {
      console.error('Request completed with error:', responseLog);
      console.log('Request completed:', summary);
    } else if (res.statusCode >= 400) {
      console.warn('Request completed with client error:', responseLog);
      console.log('Request completed:', summary);
    } else {
      console.log('Request completed:', summary);
    }
  });

  next();
};

export default loggingMiddleware;
