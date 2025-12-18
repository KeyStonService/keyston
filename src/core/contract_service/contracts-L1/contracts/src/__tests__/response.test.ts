/**
 * Response Utilities Tests
 * Tests for the shared API response helper functions
 */

import { Response } from 'express';
import { z } from 'zod';
import {
  sendSuccess,
  sendError,
  sendValidationError,
  sendNotFound,
  sendInternalError,
  getErrorMessage,
  handleControllerError,
  createTimestamp,
} from '../middleware/response';

describe('Response Utilities', () => {
  let mockResponse: Partial<Response>;
  let statusMock: jest.Mock;
  let jsonMock: jest.Mock;

  beforeEach(() => {
    jsonMock = jest.fn();
    statusMock = jest.fn().mockReturnValue({ json: jsonMock });
    mockResponse = {
      status: statusMock,
      json: jsonMock,
    };
  });

  describe('createTimestamp', () => {
    it('should return ISO 8601 formatted timestamp', () => {
      const timestamp = createTimestamp();
      expect(timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });

  describe('sendSuccess', () => {
    it('should send success response with data', () => {
      const data = { id: 1, name: 'test' };
      sendSuccess(mockResponse as Response, data);

      expect(statusMock).toHaveBeenCalledWith(200);
      expect(jsonMock).toHaveBeenCalledWith({
        success: true,
        data,
      });
    });

    it('should send success response with custom status', () => {
      const data = { id: 1 };
      sendSuccess(mockResponse as Response, data, { status: 201 });

      expect(statusMock).toHaveBeenCalledWith(201);
    });

    it('should include message when provided', () => {
      const data = { id: 1 };
      sendSuccess(mockResponse as Response, data, { message: 'Created successfully' });

      expect(jsonMock).toHaveBeenCalledWith({
        success: true,
        data,
        message: 'Created successfully',
      });
    });

    it('should include count when provided', () => {
      const data = [{ id: 1 }, { id: 2 }];
      sendSuccess(mockResponse as Response, data, { count: 2 });

      expect(jsonMock).toHaveBeenCalledWith({
        success: true,
        data,
        count: 2,
      });
    });

    it('should include timestamp when requested', () => {
      const data = { id: 1 };
      sendSuccess(mockResponse as Response, data, { includeTimestamp: true });

      const response = jsonMock.mock.calls[0][0];
      expect(response.success).toBe(true);
      expect(response.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });

  describe('sendError', () => {
    it('should send error response with default 500 status', () => {
      sendError(mockResponse as Response, 'Something went wrong');

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Something went wrong',
      });
    });

    it('should send error response with custom status', () => {
      sendError(mockResponse as Response, 'Not found', { status: 404 });

      expect(statusMock).toHaveBeenCalledWith(404);
    });

    it('should include details when provided', () => {
      const details = { field: 'email', issue: 'invalid' };
      sendError(mockResponse as Response, 'Validation failed', { details });

      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Validation failed',
        details,
      });
    });

    it('should include timestamp when requested', () => {
      sendError(mockResponse as Response, 'Error', { includeTimestamp: true });

      const response = jsonMock.mock.calls[0][0];
      expect(response.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });

  describe('sendValidationError', () => {
    it('should send 400 status with validation error', () => {
      sendValidationError(mockResponse as Response, 'Invalid input');

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Invalid input',
      });
    });

    it('should include validation details', () => {
      const details = [{ field: 'name', message: 'Required' }];
      sendValidationError(mockResponse as Response, 'Validation error', details);

      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Validation error',
        details,
      });
    });
  });

  describe('sendNotFound', () => {
    it('should send 404 with formatted message', () => {
      sendNotFound(mockResponse as Response, 'User');

      expect(statusMock).toHaveBeenCalledWith(404);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'User not found',
      });
    });

    it('should include timestamp when requested', () => {
      sendNotFound(mockResponse as Response, 'Resource', true);

      const response = jsonMock.mock.calls[0][0];
      expect(response.timestamp).toBeDefined();
    });
  });

  describe('sendInternalError', () => {
    it('should send error message from Error instance', () => {
      const error = new Error('Database connection failed');
      sendInternalError(mockResponse as Response, error);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Database connection failed',
      });
    });

    it('should use fallback message for non-Error types', () => {
      sendInternalError(mockResponse as Response, 'string error', 'Operation failed');

      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Operation failed',
      });
    });
  });

  describe('getErrorMessage', () => {
    it('should return message from Error instance', () => {
      const error = new Error('Test error');
      expect(getErrorMessage(error)).toBe('Test error');
    });

    it('should return fallback message for non-Error types', () => {
      expect(getErrorMessage('string')).toBe('Unknown error occurred');
      expect(getErrorMessage(null)).toBe('Unknown error occurred');
      expect(getErrorMessage(undefined)).toBe('Unknown error occurred');
    });

    it('should use custom fallback message', () => {
      expect(getErrorMessage({}, 'Custom fallback')).toBe('Custom fallback');
    });
  });

  describe('handleControllerError', () => {
    it('should handle ZodError with validation response', () => {
      const schema = z.object({ name: z.string() });
      let zodError: z.ZodError | undefined;

      try {
        schema.parse({ name: 123 });
      } catch (error) {
        zodError = error as z.ZodError;
      }

      handleControllerError(mockResponse as Response, zodError);

      expect(statusMock).toHaveBeenCalledWith(400);
      const response = jsonMock.mock.calls[0][0];
      expect(response.error).toBe('Validation error');
      expect(response.details).toBeDefined();
    });

    it('should handle Error with not found check', () => {
      const error = new Error('Assignment not found');

      handleControllerError(mockResponse as Response, error, {
        notFoundCheck: (msg) => msg.includes('not found'),
      });

      expect(statusMock).toHaveBeenCalledWith(404);
    });

    it('should handle Error without not found check', () => {
      const error = new Error('Database error');

      handleControllerError(mockResponse as Response, error);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Database error',
      });
    });

    it('should handle unknown error types', () => {
      handleControllerError(mockResponse as Response, 'string error');

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Unknown error occurred',
      });
    });

    it('should use custom fallback message', () => {
      handleControllerError(mockResponse as Response, null, {
        fallbackMessage: 'Custom error',
      });

      expect(jsonMock).toHaveBeenCalledWith({
        success: false,
        error: 'Custom error',
      });
    });
  });
});
