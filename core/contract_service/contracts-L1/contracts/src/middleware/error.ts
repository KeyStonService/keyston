import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';

export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  RATE_LIMIT = 'RATE_LIMIT',
}

export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly traceId: string;
  public readonly timestamp: string;
  public readonly isOperational: boolean;

  constructor(message: string, code: ErrorCode, statusCode = 500, isOperational = true) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.traceId = randomUUID();
    this.timestamp = new Date().toISOString();
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}

export const createError = {
  validation: (message: string) => new AppError(message, ErrorCode.VALIDATION_ERROR, 400),
  notFound: (resource: string) => new AppError(`${resource} not found`, ErrorCode.NOT_FOUND, 404),
  unauthorized: (message = 'Unauthorized') => new AppError(message, ErrorCode.UNAUTHORIZED, 401),
  forbidden: (message = 'Forbidden') => new AppError(message, ErrorCode.FORBIDDEN, 403),
  internal: (message = 'Internal server error') =>
    new AppError(message, ErrorCode.INTERNAL_ERROR, 500, false),
  serviceUnavailable: (service: string) =>
    new AppError(`${service} is unavailable`, ErrorCode.SERVICE_UNAVAILABLE, 503),
};

export const errorMiddleware = (
  err: Error | AppError,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const traceId = req.traceId || randomUUID();
  let logLevel: 'error' | 'warn' = 'error';

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
    const errorResponse = {
      error: {
        code: ErrorCode.INTERNAL_ERROR,
        message: config.NODE_ENV === 'production' ? 'Internal server error' : err.message,
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
  const error = createError.notFound(`Route ${req.method} ${req.url}`);
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
