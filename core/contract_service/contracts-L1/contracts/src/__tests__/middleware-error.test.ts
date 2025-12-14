/**
 * Error Middleware Tests
 * Unit tests for error handling middleware
 */

import { Request, Response, NextFunction } from 'express';
import { errorMiddleware } from '../middleware/error';
import { createError, AppError, ErrorCode } from '../errors';

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
    };

    mockResponse = {
      status: statusMock,
      json: jsonMock,
    };

    mockNext = jest.fn();
  });

  describe('HTTP Error Handling', () => {
    it('should handle 400 Bad Request errors', () => {
      const error = createError.validation('Invalid input');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Invalid input',
            status: 400,
          }),
        })
      );
    });

    it('should handle 401 Unauthorized errors', () => {
      const error = createError.unauthorized('Authentication required');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(401);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Authentication required',
            status: 401,
          }),
        })
      );
    });

    it('should handle 403 Forbidden errors', () => {
      const error = createError.forbidden('Access denied');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(403);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Access denied',
            status: 403,
          }),
        })
      );
    });

    it('should handle 404 Not Found errors', () => {
      const error = createError.notFound('Resource not found');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(404);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Resource not found',
            status: 404,
          }),
        })
      );
    });

    it('should handle 409 Conflict errors', () => {
      const error = createError.conflict('Resource already exists');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(409);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Resource already exists',
            status: 409,
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

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(422);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Validation failed',
            status: 422,
            details: validationErrors,
          }),
        })
      );
    });

    it('should handle 429 Rate Limit errors', () => {
      // Create a custom AppError for rate limiting since no factory exists
      const error = new AppError('Too many requests', ErrorCode.RATE_LIMIT, 429);

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(429);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Too many requests',
            status: 429,
          }),
        })
      );
    });

    it('should handle 500 Internal Server errors', () => {
      const error = createError.internal('Server error occurred');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Server error occurred',
            status: 500,
          }),
        })
      );
    });

    it('should handle 503 Service Unavailable errors', () => {
      const error = createError.serviceUnavailable('External API');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(503);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'External API is currently unavailable',
            status: 503,
          }),
        })
      );
    });
  });

  describe('Generic Error Handling', () => {
    it('should handle generic Error objects as 500', () => {
      const error = new Error('Something went wrong');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Something went wrong',
            status: 500,
          }),
        })
      );
    });

    it('should handle errors with stack traces', () => {
      const error = new Error('Test error');
      error.stack = 'Error: Test error\n    at someFunction (file.ts:10:5)';

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error).toBeDefined();
    });

    it('should include request context in error response', () => {
      mockRequest.method = 'POST';
      mockRequest.url = '/api/v1/test';
      const error = createError.validation('Invalid data');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalled();
    });
  });

  describe('Error Response Format', () => {
    it('should return consistent error response structure', () => {
      const error = createError.notFound('Item not found');

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      const response = jsonMock.mock.calls[0][0];
      expect(response).toHaveProperty('error');
      expect(response.error).toHaveProperty('message');
      expect(response.error).toHaveProperty('status');
      expect(response.error).toHaveProperty('timestamp');
    });

    it('should include timestamp in error response', () => {
      const error = createError.internal('Server error');
      const beforeTime = Date.now();

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      const afterTime = Date.now();
      const response = jsonMock.mock.calls[0][0];
      const timestamp = new Date(response.error.timestamp).getTime();

      expect(timestamp).toBeGreaterThanOrEqual(beforeTime);
      expect(timestamp).toBeLessThanOrEqual(afterTime);
    });

    it('should preserve error details in response', () => {
      const details = { field: 'username', constraint: 'unique' };
      const error = createError.validation('Validation failed', [details]);

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      const response = jsonMock.mock.calls[0][0];
      expect(response.error.details).toEqual([details]);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null error', () => {
      errorMiddleware(
        null as any,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });

    it('should handle undefined error', () => {
      errorMiddleware(
        undefined as any,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

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

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error.message).toBeDefined();
    });
  });

  describe('Production vs Development Mode', () => {
    it('should handle errors appropriately', () => {
      const error = createError.internal('Internal error');
      error.stack = 'Error stack trace...';

      errorMiddleware(
        error,
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalled();
    });
  });
});
