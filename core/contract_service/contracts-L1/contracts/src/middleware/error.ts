import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';
import { AppError, ErrorCode, createError } from '../errors';

/**
 * Whitelist of safe error message patterns that can be exposed to clients
 * These are generic messages that don't reveal internal implementation details
 */
const SAFE_ERROR_PATTERNS = [
  /^Invalid input/i,
  /^Validation failed/i,
  /^Authentication required/i,
  /^Access denied/i,
  /^Resource not found/i,
  /^Too many requests/i,
  /^Service unavailable/i,
  /^Unauthorized/i,
  /^Forbidden/i,
  /^Bad request/i,
  /^Conflict/i,
  /^Request timeout/i,
];

/**
 * Patterns that indicate sensitive information that should be removed
 */
const SENSITIVE_PATTERNS = [
  /at\s+[^\n:]+:\d+:\d+/gi, // Stack trace locations (at file.ts:10:5)
  /\/(?:[\w\-.]+\/)+[\w\-.]+\.(?:js|ts|py|java|go|rb|json|yaml|yml|env|config)/gi, // Unix file paths (require at least one directory)
  /(?:[a-zA-Z]:)?\\(?:[\w\-.]+\\)+[\w\-.]+\.(?:js|ts|py|java|go|rb|json|yaml|yml|env|config)/gi, // Windows file paths (require drive or UNC and at least one directory)
  /\/(?:etc|proc|var|usr|home)\/[^\s]*/gi, // System paths
  /Error:\s+[\w\s]+\n\s+at/gi, // Stack trace beginnings
  /\w+:\/\/[^\s]+/gi, // Generic connection strings (mongodb://, postgres://, etc.)
  /password[=:]\s*\S+/gi, // Password parameters
  /token[=:]\s*\S+/gi, // Token parameters
  /api[_-]?key[=:]\s*\S+/gi, // API key parameters
  /secret[=:]\s*\S+/gi, // Secret parameters
];

/**
 * Maximum length for sanitized error messages to prevent information disclosure
 */
const MAX_SAFE_ERROR_MESSAGE_LENGTH = 100;

/**
 * Sanitizes error messages to prevent leakage of sensitive information
 * @param message - The error message to sanitize
 * @returns Sanitized error message safe for client exposure
 */
function sanitizeErrorMessage(message: string): string {
  if (!message) {
    return 'Internal server error';
  }

  // Check if message matches any safe pattern
  const isSafe = SAFE_ERROR_PATTERNS.some((pattern) => pattern.test(message));
  if (isSafe) {
    return message;
  }

  // Remove sensitive information
  let sanitized = message;
  for (const pattern of SENSITIVE_PATTERNS) {
    sanitized = sanitized.replace(pattern, '[REDACTED]');
  }

  // If message was redacted or is too short after redaction, use generic message
  if (sanitized.includes('[REDACTED]')) {
    return 'Internal server error';
  }

  // Limit message length to prevent information disclosure through long error messages
  if (sanitized.length > MAX_SAFE_ERROR_MESSAGE_LENGTH) {
    return 'Internal server error';
  }

  return sanitized;
}

export const errorMiddleware = (
  err: Error | AppError,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const traceId = req.traceId || randomUUID();
  let logLevel: 'error' | 'warn' = 'error';

  // Handle null, undefined, or non-Error objects
  if (!err || !(err instanceof Error)) {
    const errorResponse = {
      error: {
        code: ErrorCode.INTERNAL_ERROR,
        message: 'Internal server error',
        traceId,
        timestamp: new Date().toISOString(),
      },
    };
    res.status(500).json(errorResponse);
    console.error('Application error:', {
      traceId,
      error: { message: 'Non-error object passed to error middleware', value: err },
      request: {
        method: req.method,
        url: req.url,
        userAgent: req.get('user-agent'),
        ip: req.ip,
      },
      timestamp: new Date().toISOString(),
    });
    return;
  }

  if (err instanceof AppError) {
    const errorResponse = {
      error: {
        code: err.code,
        message: err.message,
        traceId: err.traceId,
        timestamp: err.timestamp,
      },
    };
    if (err.statusCode < 500) {
      logLevel = 'warn';
    }
    res.status(err.statusCode).json(errorResponse);
  } else {
    // Sanitize error message to prevent sensitive information leakage
    const sanitizedMessage =
      config.NODE_ENV === 'production'
        ? 'Internal server error'
        : sanitizeErrorMessage(err.message || 'Internal server error');

    const errorResponse = {
      error: {
        code: ErrorCode.INTERNAL_ERROR,
        message: sanitizedMessage,
        traceId,
        timestamp: new Date().toISOString(),
      },
    };
    res.status(500).json(errorResponse);
  }

  const errorLog = {
    traceId,
    error: {
      name: err.name,
      message: err.message,
      code: err instanceof AppError ? err.code : ErrorCode.INTERNAL_ERROR,
      stack: config.NODE_ENV !== 'production' ? err.stack : undefined,
    },
    request: {
      method: req.method,
      url: req.url,
      userAgent: req.get('user-agent'),
      ip: req.ip,
    },
    timestamp: new Date().toISOString(),
  };

  if (logLevel === 'error') {
    console.error('Application error:', errorLog);
  } else {
    console.warn('Client error:', errorLog);
  }
};

export const notFoundMiddleware = (req: Request, res: Response, _next: NextFunction): void => {
  const error = createError.notFound(`Route ${req.method} ${req.url} not found`);
  const traceId = req.traceId || randomUUID();

  res.status(404).json({
    error: {
      code: error.code,
      message: error.message,
      traceId,
      timestamp: new Date().toISOString(),
    },
  });
};

export default errorMiddleware;
