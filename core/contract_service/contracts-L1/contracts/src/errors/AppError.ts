/**
 * Custom Application Error Classes
 * Centralized error definitions for the application
 */

import { randomUUID } from 'crypto';

/**
 * Standard error codes used across the application
 */
export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  RATE_LIMIT = 'RATE_LIMIT',
  CONFLICT = 'CONFLICT',
  BAD_REQUEST = 'BAD_REQUEST',
}

/**
 * Base application error class
 * All custom errors should extend this class
 */
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

    // Maintains proper stack trace for where our error was thrown
    Error.captureStackTrace(this, this.constructor);

    // Set the prototype explicitly to maintain instanceof checks
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

/**
 * Validation error - thrown when input validation fails
 */
export class ValidationError extends AppError {
  public readonly validationErrors?: Array<{
    field: string;
    message: string;
    code: string;
  }>;

  constructor(
    message: string,
    validationErrors?: Array<{ field: string; message: string; code: string }>
  ) {
    super(message, ErrorCode.VALIDATION_ERROR, 400);
    this.validationErrors = validationErrors;
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * Not found error - thrown when a resource is not found
 */
export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, ErrorCode.NOT_FOUND, 404);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * Unauthorized error - thrown when authentication fails
 */
export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized access') {
    super(message, ErrorCode.UNAUTHORIZED, 401);
    Object.setPrototypeOf(this, UnauthorizedError.prototype);
  }
}

/**
 * Forbidden error - thrown when access is forbidden
 */
export class ForbiddenError extends AppError {
  constructor(message = 'Access forbidden') {
    super(message, ErrorCode.FORBIDDEN, 403);
    Object.setPrototypeOf(this, ForbiddenError.prototype);
  }
}

/**
 * Conflict error - thrown when there's a conflict with current state
 */
export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, ErrorCode.CONFLICT, 409);
    Object.setPrototypeOf(this, ConflictError.prototype);
  }
}

/**
 * Service unavailable error - thrown when a service is temporarily unavailable
 */
export class ServiceUnavailableError extends AppError {
  constructor(service: string) {
    super(`${service} is currently unavailable`, ErrorCode.SERVICE_UNAVAILABLE, 503);
    Object.setPrototypeOf(this, ServiceUnavailableError.prototype);
  }
}

/**
 * Internal server error - thrown for unexpected errors
 */
export class InternalError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, ErrorCode.INTERNAL_ERROR, 500, false);
    Object.setPrototypeOf(this, InternalError.prototype);
  }
}

/**
 * Factory functions for creating common errors
 */
export const createError = {
  validation: (message: string, errors?: Array<{ field: string; message: string; code: string }>) =>
    new ValidationError(message, errors),
  notFound: (resource: string) => new NotFoundError(resource),
  unauthorized: (message?: string) => new UnauthorizedError(message),
  forbidden: (message?: string) => new ForbiddenError(message),
  conflict: (message: string) => new ConflictError(message),
  internal: (message?: string) => new InternalError(message),
  serviceUnavailable: (service: string) => new ServiceUnavailableError(service),
};
