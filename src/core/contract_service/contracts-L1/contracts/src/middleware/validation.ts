/**
 * Request Validation Middleware
 * Centralized validation middleware using Zod schemas
 */

import { Request, Response, NextFunction } from 'express';
import { z, ZodError } from 'zod';

import { createError } from '../errors';

/**
 * Validation target type
 */
export type ValidationTarget = 'body' | 'query' | 'params';

/**
 * Validation middleware factory
 * Creates a middleware function that validates request data against a Zod schema
 *
 * @param schema - Zod schema to validate against
 * @param target - Which part of the request to validate (body, query, or params)
 * @returns Express middleware function
 *
 * @example
 * ```typescript
 * router.post('/users', validate(createUserSchema), userController.create);
 * router.get('/users/:id', validate(userIdSchema, 'params'), userController.get);
 * ```
 */
export const validate = (schema: z.ZodSchema, target: ValidationTarget = 'body') => {
  return (req: Request, _res: Response, next: NextFunction): void => {
    try {
      // Validate the specified part of the request
      const validated = schema.parse(req[target]);

      // Replace the original data with validated data
      // This ensures type safety and removes any extra fields
      req[target] = validated;

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        // Format Zod validation errors into a readable structure
        const validationErrors = error.errors.map((err) => ({
          field: err.path.join('.'),
          message: err.message,
          code: err.code,
        }));

        // Create a validation error with detailed information
        const validationError = createError.validation(
          `Validation failed: ${validationErrors.map((e) => `${e.field} - ${e.message}`).join('; ')}`,
          validationErrors
        );

        next(validationError);
      } else {
        // Handle unexpected errors
        next(createError.internal('Validation middleware encountered an unexpected error'));
      }
    }
  };
};

/**
 * Body validation middleware
 * Shorthand for validating request body
 *
 * @example
 * ```typescript
 * router.post('/users', validateBody(createUserSchema), userController.create);
 * ```
 */
export const validateBody = (schema: z.ZodSchema) => validate(schema, 'body');

/**
 * Query validation middleware
 * Shorthand for validating query parameters
 *
 * @example
 * ```typescript
 * router.get('/users', validateQuery(userQuerySchema), userController.list);
 * ```
 */
export const validateQuery = (schema: z.ZodSchema) => validate(schema, 'query');

/**
 * Params validation middleware
 * Shorthand for validating URL parameters
 *
 * @example
 * ```typescript
 * router.get('/users/:id', validateParams(userIdSchema), userController.get);
 * ```
 */
export const validateParams = (schema: z.ZodSchema) => validate(schema, 'params');
