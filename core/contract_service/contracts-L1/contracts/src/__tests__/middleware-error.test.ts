/**
 * Error Middleware Tests
 * Unit tests for error handling middleware
 */

import { Request, Response, NextFunction } from 'express';
import { errorMiddleware } from '../middleware/error';
import { createError, AppError, ErrorCode } from '../errors';

// Mock the config module
jest.mock('../config', () => {
  const mockConfigValues = {
    NODE_ENV: 'development',
    PORT: 3000,
    LOG_LEVEL: 'info',
    SERVICE_NAME: 'contracts-l1',
    SERVICE_VERSION: '1.0.0',
  };
  
  return {
    __esModule: true,
    default: mockConfigValues,
    config: mockConfigValues,
  };
});

describe('Error Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let jsonMock: jest.Mock;
  let statusMock: jest.Mock;

  beforeEach(() => {
    jsonMock = jest.fn();
    statusMock = jest.fn().mockReturnThis();

    mockRequest = {
      method: 'GET',
      url: '/test',
      headers: {},
      get: jest.fn((header: string) => {
        if (header === 'user-agent') return 'test-agent';
        return undefined;
      }),
      ip: '127.0.0.1',
    };

    mockResponse = {
      status: statusMock,
      json: jsonMock,
    };

    mockNext = jest.fn();
  });

  describe('HTTP Error Handling', () => {
    it('should handle 422 Validation errors (Bad Request)', () => {
      const error = createError.validation('Invalid input');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(422);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Invalid input',
            code: ErrorCode.VALIDATION_ERROR,
          }),
        })
      );
    });

    it('should handle 401 Unauthorized errors', () => {
      const error = createError.unauthorized('Authentication required');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(401);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Authentication required',
            code: ErrorCode.UNAUTHORIZED,
          }),
        })
      );
    });

    it('should handle 403 Forbidden errors', () => {
      const error = createError.forbidden('Access denied');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(403);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Access denied',
            code: ErrorCode.FORBIDDEN,
          }),
        })
      );
    });

    it('should handle 404 Not Found errors', () => {
      const error = createError.notFound('Resource');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(404);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Resource not found',
            code: ErrorCode.NOT_FOUND,
          }),
        })
      );
    });

    it('should handle 409 Conflict errors', () => {
      const error = createError.conflict('Resource already exists');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(409);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Resource already exists',
            code: ErrorCode.CONFLICT,
          }),
        })
      );
    });

    it('should handle 422 Validation errors', () => {
      const validationErrors = [
        { field: 'email', message: 'Invalid email format' },
        { field: 'age', message: 'Must be a positive number' },
      ];
      const error = createError.validation('Validation failed', validationErrors);

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(422);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Validation failed',
            code: ErrorCode.VALIDATION_ERROR,
          }),
        })
      );
    });

    it('should handle 429 Rate Limit errors', () => {
      // Create a custom AppError for rate limiting since no factory exists
      const error = new AppError('Too many requests', ErrorCode.RATE_LIMIT, 429);

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(429);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Too many requests',
            code: ErrorCode.RATE_LIMIT,
          }),
        })
      );
    });

    it('should handle 500 Internal Server errors', () => {
      const error = createError.internal('Server error occurred');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Server error occurred',
            code: ErrorCode.INTERNAL_ERROR,
          }),
        })
      );
    });

    it('should handle 503 Service Unavailable errors', () => {
      const error = createError.serviceUnavailable('External API');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(503);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'External API is currently unavailable',
            code: ErrorCode.SERVICE_UNAVAILABLE,
          }),
        })
      );
    });
  });

  describe('Generic Error Handling', () => {
    it('should handle generic Error objects as 500', () => {
      const error = new Error('Something went wrong');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Something went wrong',
            code: ErrorCode.INTERNAL_ERROR,
          }),
        })
      );
    });

    it('should handle errors with stack traces', () => {
      const error = new Error('Test error');
      error.stack = 'Error: Test error\n    at someFunction (file.ts:10:5)';

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error).toBeDefined();
    });

    it('should include request context in error response', () => {
      mockRequest.method = 'POST';
      mockRequest.url = '/api/v1/test';
      const error = createError.validation('Invalid data');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(422);
      expect(jsonMock).toHaveBeenCalled();
    });
  });

  describe('Error Response Format', () => {
    it('should return consistent error response structure', () => {
      const error = createError.notFound('Item not found');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response).toHaveProperty('error');
      expect(response.error).toHaveProperty('message');
      expect(response.error).toHaveProperty('code');
      expect(response.error).toHaveProperty('timestamp');
      expect(response.error).toHaveProperty('traceId');
    });

    it('should include timestamp in error response', () => {
      const error = createError.internal('Server error');
      const beforeTime = Date.now();

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      const afterTime = Date.now();
      const response = jsonMock.mock.calls[0][0];
      const timestamp = new Date(response.error.timestamp).getTime();

      expect(timestamp).toBeGreaterThanOrEqual(beforeTime);
      expect(timestamp).toBeLessThanOrEqual(afterTime);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null error', () => {
      errorMiddleware(null as any, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });

    it('should handle undefined error', () => {
      errorMiddleware(undefined as any, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });

    it('should handle string error', () => {
      errorMiddleware(
        'String error' as any,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });

    it('should handle error without message', () => {
      const error = new Error();

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).toBeDefined();
    });
  });

  describe('Production vs Development Mode', () => {
    it('should handle errors appropriately', () => {
      const error = createError.internal('Internal error');
      error.stack = 'Error stack trace...';

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });
  });

  describe('Error Message Sanitization', () => {
    it('should sanitize error messages with file paths in development', () => {
      const error = new Error('Cannot read property at /app/src/secret/file.ts:123:45');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('/app/src/secret/file.ts');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should sanitize error messages with stack traces in development', () => {
      const error = new Error('Error: Something failed\n    at /home/user/app.ts:10:5');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('at /home/user/app.ts');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should sanitize error messages with database connection strings', () => {
      const error = new Error('Connection failed to mongodb://user:pass@localhost:27017/db');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('mongodb://');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should sanitize error messages with passwords', () => {
      const error = new Error('Auth failed with password=secretpass123');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('secretpass123');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should sanitize error messages with API keys', () => {
      const error = new Error('Request failed with api_key=abc123xyz');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('abc123xyz');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should allow safe error messages to pass through in development', () => {
      const error = new Error('Invalid input provided');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).toBe('Invalid input provided');
    });

    it('should truncate overly long error messages', () => {
      const longMessage = 'A'.repeat(150);
      const error = new Error(longMessage);

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).toBe('Internal server error');
    });

    it('should handle Windows-style file paths', () => {
      const error = new Error('Error at C:\\Users\\App\\src\\file.ts:50');

      errorMiddleware(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).not.toContain('C:\\Users');
      expect(response.error.message).toBe('Internal server error');
    });

    it('should always show generic message in production', () => {
      // Mock config to simulate production environment
      const mockConfig = require('../config');
      const originalNodeEnv = mockConfig.default.NODE_ENV;
      mockConfig.default.NODE_ENV = 'production';
      mockConfig.config.NODE_ENV = 'production';

      const error = new Error('Invalid input provided');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).toBe('Internal server error');

      // Restore original config
      mockConfig.default.NODE_ENV = originalNodeEnv;
      mockConfig.config.NODE_ENV = originalNodeEnv;
    });
  });
});
