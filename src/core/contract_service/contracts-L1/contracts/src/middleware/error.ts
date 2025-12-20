import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

// eslint-disable-next-line import/no-named-as-default
import config from '../config';
import { AppError, ErrorCode } from '../errors';

const UNKNOWN_ERROR_FALLBACK = 'Unknown error';
const MAX_SAFE_ERROR_MESSAGE_LENGTH = 100;
const testPattern = (pattern: RegExp, value: string): boolean => {
  pattern.lastIndex = 0;
  return pattern.test(value);
};

/**
 * Centralized holder for regex patterns used by the error middleware.
 * Ensures patterns are compiled once and reused.
 */
export class ErrorCleanupPatterns {
  // Matches ANSI escape sequences to strip terminal color/style codes from error messages
  // eslint-disable-next-line no-control-regex
  public static readonly ansiEscapePattern: RegExp = /\x1B\[[0-?]*[ -/]*[@-~]/g;

  public static sanitizeMessage(message: string): string {
    const sanitized = message.replace(ErrorCleanupPatterns.ansiEscapePattern, '').trim();
    return sanitized || UNKNOWN_ERROR_FALLBACK;
  }
}

/**
 * Pre-compiled regex patterns for error message sanitization.
 */
class ErrorSanitizationPatterns {
  static readonly SAFE_PATTERNS: ReadonlyArray<RegExp> = Object.freeze([
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
  ]);

  static readonly FILE_EXTENSIONS = 'js|ts|py|java|go|rb|json|yaml|yml|env|config';

  static readonly SENSITIVE_PATTERNS: ReadonlyArray<RegExp> = Object.freeze([
    /at\s+[^\n:]+:\d+(?::\d+)?/gi, // Stack trace locations
    new RegExp(
      `\\/(?:[\\w\\-.]+\\/)+[\\w\\-.]+\\.(?:${ErrorSanitizationPatterns.FILE_EXTENSIONS})`,
      'gi'
    ), // Unix file paths
    new RegExp(
      `(?:[a-zA-Z]:)?\\\\(?:[\\w\\-.]+\\\\)+[\\w\\-.]+\\.(?:${ErrorSanitizationPatterns.FILE_EXTENSIONS})`,
      'gi'
    ), // Windows file paths
    /\/(?:etc|proc|var|usr|home)\/[^\s]*/gi, // System paths
    /\w+:\/\/[^\s]+/gi, // Connection strings/URLs
    /password[=:]\s*\S+/gi, // Password parameters
    /token[=:]\s*\S+/gi, // Token parameters
    /api[_-]?key[=:]\s*\S+/gi, // API keys
    /secret[=:]\s*\S+/gi, // Secret parameters
  ]);
}

/**
 * Safely converts any thrown value to an Error object.
 */
const convertToError = (err: unknown): Error => {
  if (err instanceof Error) {
    return err;
  }
  if (err === null || err === undefined) {
    return new Error(UNKNOWN_ERROR_FALLBACK);
  }
  if (typeof err === 'string' || typeof err === 'number' || typeof err === 'boolean') {
    return new Error(String(err));
  }
  try {
    return new Error(JSON.stringify(err));
  } catch {
    return new Error(UNKNOWN_ERROR_FALLBACK);
  }
};

/**
 * Sanitizes error messages to prevent leakage of sensitive information.
 */
function sanitizeErrorMessage(message: string, isProduction: boolean): string {
  if (!message) {
    return 'Internal server error';
  }

  const cleaned = ErrorCleanupPatterns.sanitizeMessage(message);

  if (isProduction) {
    return 'Internal server error';
  }

  if (cleaned.length > MAX_SAFE_ERROR_MESSAGE_LENGTH) {
    return 'Internal server error';
  }

  const hasSensitive = ErrorSanitizationPatterns.SENSITIVE_PATTERNS.some((pattern) =>
    testPattern(pattern, cleaned)
  );

  if (hasSensitive) {
    return 'Internal server error';
  }

  return cleaned;
}

/**
 * Express middleware that handles requests to unmatched routes by returning a standardized
 * 404 Not Found error response.
 *
 * @param req - The incoming Express request object.
 * @param res - The Express response object used to send the 404 error payload.
 * @param _next - The next middleware function in the Express stack (unused).
 * @returns void
 */
export function notFoundMiddleware(req: Request, res: Response): void {
  res.status(404).json({
    error: {
      message: 'Route not found',
      code: ErrorCode.NOT_FOUND,
      traceId: randomUUID(),
      timestamp: new Date().toISOString(),
      path: req.url,
      method: req.method,
      status: 404,
    },
  });
}

/**
 * Express error-handling middleware.
 */
export function errorMiddleware(
  err: unknown,
  req: Request,
  res: Response,
  _next: NextFunction
): void {
  const isProduction = config.NODE_ENV === 'production';
  const normalizedError = err instanceof AppError ? err : convertToError(err);

  const status = normalizedError instanceof AppError ? normalizedError.statusCode : 500;
  const code = normalizedError instanceof AppError ? normalizedError.code : ErrorCode.INTERNAL_ERROR;
  const traceId =
    normalizedError instanceof AppError && normalizedError.traceId
      ? normalizedError.traceId
      : randomUUID();
  const rawMessage = normalizedError.message || UNKNOWN_ERROR_FALLBACK;
  const message =
    normalizedError instanceof AppError && !isProduction
      ? rawMessage
      : sanitizeErrorMessage(rawMessage, isProduction);

  res.status(status).json({
    error: {
      message,
      code,
      traceId,
      timestamp: new Date().toISOString(),
      path: req.url,
      method: req.method,
      status,
    },
  });
}
