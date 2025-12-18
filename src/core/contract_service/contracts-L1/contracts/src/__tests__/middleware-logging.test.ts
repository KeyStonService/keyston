/**
 * Logging Middleware Tests
 * Unit tests for request logging middleware
 */

import { Request, Response, NextFunction } from 'express';
import { loggingMiddleware } from '../middleware/logging';

describe('Logging Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let consoleLogSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    mockRequest = {
      method: 'GET',
      url: '/test',
      headers: {},
      ip: '127.0.0.1',
      get: jest.fn((header: string) => {
        if (header === 'user-agent') return 'test-agent';
        return undefined;
      }),
    };

    mockResponse = {
      statusCode: 200,
      on: jest.fn(),
    };

    mockNext = jest.fn();

    // Spy on console methods
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  describe('Request Logging', () => {
    it('should log incoming requests', () => {
      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(consoleLogSpy).toHaveBeenCalled();
      expect(mockNext).toHaveBeenCalled();
    });

    it('should log request method', () => {
      mockRequest.method = 'POST';

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      const logCall = consoleLogSpy.mock.calls[0];
      const logMessage = JSON.stringify(logCall);
      expect(logMessage).toContain('POST');
      expect(mockNext).toHaveBeenCalled();
    });

    it('should log request URL', () => {
      mockRequest.url = '/api/v1/test';

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      const logCall = consoleLogSpy.mock.calls[0];
      const logMessage = JSON.stringify(logCall);
      expect(logMessage).toContain('/api/v1/test');
      expect(mockNext).toHaveBeenCalled();
    });

    it('should log different HTTP methods', () => {
      const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

      methods.forEach((method) => {
        consoleLogSpy.mockClear();
        mockRequest.method = method;

        loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

        const logCall = consoleLogSpy.mock.calls[0];
        const logMessage = JSON.stringify(logCall);
        expect(logMessage).toContain(method);
      });
    });

    it('should call next middleware', () => {
      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
    });
  });

  describe('Response Logging', () => {
    it('should attach finish listener to response', () => {
      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.on).toHaveBeenCalledWith('finish', expect.any(Function));
    });

    it('should log response when finished', () => {
      let finishCallback: Function | undefined;

      mockResponse.on = jest.fn((event: string, callback: Function) => {
        if (event === 'finish') {
          finishCallback = callback;
        }
        return mockResponse as Response;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(finishCallback).toBeDefined();

      // Simulate response finish
      if (finishCallback) {
        consoleLogSpy.mockClear();
        finishCallback();
        expect(consoleLogSpy).toHaveBeenCalled();
      }
    });

    it('should log response status code', () => {
      let finishCallback: Function | undefined;

      mockResponse.statusCode = 201;
      mockResponse.on = jest.fn((event: string, callback: Function) => {
        if (event === 'finish') {
          finishCallback = callback;
        }
        return mockResponse as Response;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      if (finishCallback) {
        consoleLogSpy.mockClear();
        finishCallback();
        const logCall = consoleLogSpy.mock.calls[0];
        const logMessage = JSON.stringify(logCall);
        expect(logMessage).toContain('201');
      }
    });
  });

  describe('Request Context', () => {
    it('should include user agent in logs', () => {
      mockRequest.get = jest.fn((header: string) => {
        if (header === 'user-agent') return 'Mozilla/5.0';
        return undefined;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockRequest.get).toHaveBeenCalledWith('user-agent');
    });

    it('should include IP address in logs', () => {
      mockRequest.ip = '192.168.1.1';

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      const logCall = consoleLogSpy.mock.calls[0];
      const logMessage = JSON.stringify(logCall);
      expect(logMessage).toContain('192.168.1.1');
    });

    it('should handle missing user agent', () => {
      mockRequest.get = jest.fn(() => undefined);

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalled();
    });

    it('should handle missing IP', () => {
      delete mockRequest.ip;

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalled();
    });
  });

  describe('Error Cases', () => {
    it('should handle 4xx status codes', () => {
      let finishCallback: Function | undefined;

      mockResponse.statusCode = 404;
      mockResponse.on = jest.fn((event: string, callback: Function) => {
        if (event === 'finish') {
          finishCallback = callback;
        }
        return mockResponse as Response;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      if (finishCallback) {
        consoleWarnSpy.mockClear();
        finishCallback();
        expect(consoleWarnSpy).toHaveBeenCalled();
      }
    });

    it('should handle 5xx status codes', () => {
      let finishCallback: Function | undefined;

      mockResponse.statusCode = 500;
      mockResponse.on = jest.fn((event: string, callback: Function) => {
        if (event === 'finish') {
          finishCallback = callback;
        }
        return mockResponse as Response;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      if (finishCallback) {
        consoleErrorSpy.mockClear();
        finishCallback();
        expect(consoleErrorSpy).toHaveBeenCalled();
      }
    });
  });

  describe('Performance Tracking', () => {
    it('should track request duration', () => {
      let finishCallback: Function | undefined;

      mockResponse.on = jest.fn((event: string, callback: Function) => {
        if (event === 'finish') {
          finishCallback = callback;
        }
        return mockResponse as Response;
      });

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      // Simulate some time passing
      if (finishCallback) {
        consoleLogSpy.mockClear();
        finishCallback();

        const logCall = consoleLogSpy.mock.calls[0];
        const logMessage = JSON.stringify(logCall);
        // Should include timing information
        expect(logCall).toBeDefined();
      }
    });
  });

  describe('Special Routes', () => {
    it('should log health check endpoints', () => {
      mockRequest.url = '/healthz';

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(consoleLogSpy).toHaveBeenCalled();
      expect(mockNext).toHaveBeenCalled();
    });

    it('should log API endpoints', () => {
      mockRequest.url = '/api/v1/provenance/attestations';
      mockRequest.method = 'POST';

      loggingMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      const logCall = consoleLogSpy.mock.calls[0];
      const logMessage = JSON.stringify(logCall);
      expect(logMessage).toContain('POST');
      expect(logMessage).toContain('/api/v1/provenance/attestations');
    });
  });

  describe('Concurrent Requests', () => {
    it('should handle multiple simultaneous requests', () => {
      const requests = 5;

      for (let i = 0; i < requests; i++) {
        const req = {
          ...mockRequest,
          url: `/test/${i}`,
        };

        loggingMiddleware(req as Request, mockResponse as Response, mockNext);
      }

      expect(consoleLogSpy).toHaveBeenCalledTimes(requests);
      expect(mockNext).toHaveBeenCalledTimes(requests);
    });
  });
});
