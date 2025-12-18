/**
 * Validation Middleware Tests
 * Unit tests for Zod-based validation middleware
 */

import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { validate, validateBody, validateQuery, validateParams } from '../middleware/validation';

describe('Validation Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockRequest = {
      body: {},
      query: {},
      params: {},
    };

    mockResponse = {};
    mockNext = jest.fn();
  });

  describe('validate() - Basic Functionality', () => {
    it('should pass validation for valid data', () => {
      const schema = z.object({
        name: z.string(),
        age: z.number(),
      });

      mockRequest.body = {
        name: 'John',
        age: 30,
      };

      const middleware = validate(schema, 'body');
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.body).toEqual({ name: 'John', age: 30 });
    });

    it('should fail validation for invalid data', () => {
      const schema = z.object({
        name: z.string(),
        age: z.number(),
      });

      mockRequest.body = {
        name: 'John',
        age: 'thirty', // Invalid: should be number
      };

      const middleware = validate(schema, 'body');
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should remove extra fields not in schema', () => {
      const schema = z.object({
        name: z.string(),
      });

      mockRequest.body = {
        name: 'John',
        extraField: 'should be removed',
      };

      const middleware = validate(schema, 'body');
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.body).toEqual({ name: 'John' });
      expect(mockRequest.body).not.toHaveProperty('extraField');
    });
  });

  describe('validateBody()', () => {
    it('should validate request body', () => {
      const schema = z.object({
        email: z.string().email(),
        password: z.string().min(8),
      });

      mockRequest.body = {
        email: 'test@example.com',
        password: 'secure123',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should reject invalid email format', () => {
      const schema = z.object({
        email: z.string().email(),
      });

      mockRequest.body = {
        email: 'not-an-email',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should reject password too short', () => {
      const schema = z.object({
        password: z.string().min(8),
      });

      mockRequest.body = {
        password: 'short',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('validateQuery()', () => {
    it('should validate query parameters', () => {
      const schema = z.object({
        page: z.string().regex(/^\d+$/),
        limit: z.string().regex(/^\d+$/),
      });

      mockRequest.query = {
        page: '1',
        limit: '10',
      };

      const middleware = validateQuery(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should coerce query strings to numbers when specified', () => {
      const schema = z.object({
        page: z.coerce.number().int().positive(),
        limit: z.coerce.number().int().positive().max(100),
      });

      mockRequest.query = {
        page: '2',
        limit: '20',
      };

      const middleware = validateQuery(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.query).toEqual({ page: 2, limit: 20 });
    });

    it('should reject invalid query parameters', () => {
      const schema = z.object({
        status: z.enum(['active', 'inactive']),
      });

      mockRequest.query = {
        status: 'invalid',
      };

      const middleware = validateQuery(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('validateParams()', () => {
    it('should validate URL parameters', () => {
      const schema = z.object({
        id: z.string().uuid(),
      });

      mockRequest.params = {
        id: '123e4567-e89b-12d3-a456-426614174000',
      };

      const middleware = validateParams(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should reject invalid UUID format', () => {
      const schema = z.object({
        id: z.string().uuid(),
      });

      mockRequest.params = {
        id: 'not-a-uuid',
      };

      const middleware = validateParams(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should validate numeric ID parameters', () => {
      const schema = z.object({
        id: z.string().regex(/^\d+$/),
      });

      mockRequest.params = {
        id: '12345',
      };

      const middleware = validateParams(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });
  });

  describe('Complex Validations', () => {
    it('should validate nested objects', () => {
      const schema = z.object({
        user: z.object({
          name: z.string(),
          email: z.string().email(),
          address: z.object({
            street: z.string(),
            city: z.string(),
          }),
        }),
      });

      mockRequest.body = {
        user: {
          name: 'John',
          email: 'john@example.com',
          address: {
            street: '123 Main St',
            city: 'New York',
          },
        },
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should validate arrays', () => {
      const schema = z.object({
        tags: z.array(z.string()),
        numbers: z.array(z.number()),
      });

      mockRequest.body = {
        tags: ['tag1', 'tag2', 'tag3'],
        numbers: [1, 2, 3],
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should reject arrays with wrong item types', () => {
      const schema = z.object({
        numbers: z.array(z.number()),
      });

      mockRequest.body = {
        numbers: [1, 'two', 3],
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should validate optional fields', () => {
      const schema = z.object({
        required: z.string(),
        optional: z.string().optional(),
      });

      mockRequest.body = {
        required: 'value',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should validate with default values', () => {
      const schema = z.object({
        name: z.string(),
        role: z.string().default('user'),
      });

      mockRequest.body = {
        name: 'John',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.body.role).toBe('user');
    });
  });

  describe('Error Messages', () => {
    it('should provide detailed error information', () => {
      const schema = z.object({
        email: z.string().email(),
        age: z.number().min(18),
      });

      mockRequest.body = {
        email: 'invalid',
        age: 15,
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalled();
      const error = mockNext.mock.calls[0][0];
      expect(error).toBeInstanceOf(Error);
    });

    it('should handle missing required fields', () => {
      const schema = z.object({
        required1: z.string(),
        required2: z.string(),
      });

      mockRequest.body = {};

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty request body', () => {
      const schema = z.object({}).strict();

      mockRequest.body = {};

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should handle null values appropriately', () => {
      const schema = z.object({
        value: z.string().nullable(),
      });

      mockRequest.body = {
        value: null,
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should handle undefined values in optional fields', () => {
      const schema = z.object({
        optional: z.string().optional(),
      });

      mockRequest.body = {};

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should validate enums correctly', () => {
      const schema = z.object({
        status: z.enum(['pending', 'approved', 'rejected']),
      });

      mockRequest.body = {
        status: 'approved',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should reject invalid enum values', () => {
      const schema = z.object({
        status: z.enum(['pending', 'approved', 'rejected']),
      });

      mockRequest.body = {
        status: 'invalid',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('Type Coercion', () => {
    it('should coerce strings to dates', () => {
      const schema = z.object({
        createdAt: z.coerce.date(),
      });

      mockRequest.body = {
        createdAt: '2024-01-01T00:00:00Z',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.body.createdAt).toBeInstanceOf(Date);
    });

    it('should coerce strings to numbers', () => {
      const schema = z.object({
        count: z.coerce.number(),
      });

      mockRequest.body = {
        count: '42',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(mockRequest.body.count).toBe(42);
    });

    it('should coerce to booleans', () => {
      const schema = z.object({
        active: z.coerce.boolean(),
      });

      mockRequest.body = {
        active: 'true',
      };

      const middleware = validateBody(schema);
      middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(typeof mockRequest.body.active).toBe('boolean');
    });
  });
});
