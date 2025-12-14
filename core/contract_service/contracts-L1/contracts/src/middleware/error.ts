import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';
import { ErrorCode, AppError, createError } from '../errors';

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
