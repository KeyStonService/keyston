import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';

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

const ALLOWED_HEADERS = [
  'user-agent',
  'content-type',
  'authorization',
  'x-forwarded-for',
  'x-real-ip',
] as const;

function sanitizeHeaders(headers: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  for (const key of ALLOWED_HEADERS) {
    if (headers[key]) {
      sanitized[key] = key === 'authorization' ? '[REDACTED]' : headers[key];
    }
  }
  return sanitized;
}

export const loggingMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const traceId = randomUUID();
  const startTime = Date.now();
  req.traceId = traceId;

  const requestLog: RequestLog = {
    traceId,
    method: req.method,
    url: req.url,
    userAgent: req.get('user-agent') || 'unknown',
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
    console.log('Request:', `${requestLog.method} ${requestLog.url} [${traceId}]`);
  }

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const responseLog = { ...requestLog, duration, statusCode: res.statusCode };
    if (res.statusCode >= 500) {
      console.error('Request completed with error:', responseLog);
    } else if (res.statusCode >= 400) {
      console.warn('Request completed with client error:', responseLog);
    } else {
      console.log(
        'Request completed:',
        `${responseLog.method} ${responseLog.url} ${responseLog.statusCode} ${duration}ms [${traceId}]`
      );
    }
  });

  next();
};

export default loggingMiddleware;
