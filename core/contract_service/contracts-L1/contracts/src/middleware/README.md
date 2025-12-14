# Middleware Layer

## Purpose

Middleware handles **cross-cutting concerns** that apply across multiple routes and controllers. Middleware functions process requests before they reach controllers and responses before they're sent to clients.

## Middleware Components

### audit-log.ts

**Purpose:** Tracks critical operations for audit trail.

**Usage:**
```typescript
import { auditLogMiddleware } from './middleware/audit-log';
router.post('/api/v1/critical', auditLogMiddleware('CREATE'), controller.create);
```

**Features:**
- Records user actions
- Tracks sensitive operations
- Maintains audit trail

### error.ts

**Purpose:** Centralized error handling and formatting.

**Usage:**
```typescript
import { errorMiddleware, notFoundMiddleware } from './middleware/error';

app.use(routes);
app.use(notFoundMiddleware); // Handle 404s
app.use(errorMiddleware);    // Handle all errors
```

**Features:**
- Consistent error responses
- Stack trace handling (dev/prod)
- Error logging
- HTTP status code mapping

**Error Response Format:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "traceId": "uuid-v4",
    "timestamp": "2024-12-09T00:00:00.000Z",
    "validationErrors": []  // Optional
  }
}
```

### logging.ts

**Purpose:** Request/response logging with performance tracking.

**Usage:**
```typescript
import { loggingMiddleware } from './middleware/logging';
app.use(loggingMiddleware);
```

**Features:**
- Request logging (method, URL, IP, user-agent)
- Response logging (status code, duration)
- Trace ID generation
- Performance metrics
- Sensitive data redaction

**Log Levels:**
- `debug`: Full request/response details
- `info`: Basic request/response info
- `warn`: Client errors (4xx)
- `error`: Server errors (5xx)

### rate-limit.ts

**Purpose:** Protects endpoints from abuse.

**Usage:**
```typescript
import { rateLimitMiddleware } from './middleware/rate-limit';

// Global rate limiting
app.use(rateLimitMiddleware);

// Per-route rate limiting
router.post('/api/v1/expensive', 
  rateLimitMiddleware({ max: 10, windowMs: 60000 }), 
  controller.expensiveOperation
);
```

**Features:**
- Configurable limits per endpoint
- Time window configuration
- IP-based tracking
- Custom error messages

### response.ts

**Purpose:** Standardized response formatting.

**Usage:**
```typescript
import { sendSuccess, sendError, handleControllerError } from './middleware/response';

// Success response
sendSuccess(res, data, { status: 201 });

// Error response
sendError(res, error);

// Controller error handling
try {
  const result = await service.operation();
  sendSuccess(res, result);
} catch (error) {
  handleControllerError(res, error);
}
```

**Success Response Format:**
```json
{
  "data": { /* your data */ },
  "metadata": {
    "timestamp": "2024-12-09T00:00:00.000Z",
    "traceId": "uuid-v4"
  }
}
```

### validation.ts

**Purpose:** Zod-based input validation.

**Usage:**
```typescript
import { validateBody, validateQuery, validateParams } from './middleware/validation';
import { createUserSchema } from './models/user.model';

// Validate request body
router.post('/api/v1/users', validateBody(createUserSchema), controller.create);

// Validate query parameters
router.get('/api/v1/users', validateQuery(userQuerySchema), controller.list);

// Validate URL parameters
router.get('/api/v1/users/:id', validateParams(userIdSchema), controller.get);
```

**Features:**
- Schema-based validation
- Type coercion
- Detailed error messages
- Extra field removal
- Multiple targets (body/query/params)

### zodErrorHandler.ts

**Purpose:** Formats Zod validation errors.

**Usage:**
```typescript
import { formatZodError, isZodError } from './middleware/zodErrorHandler';

if (isZodError(error)) {
  const formatted = formatZodError(error);
  // Handle formatted error
}
```

**Features:**
- Human-readable error messages
- Field-level error details
- Integration with error middleware

## Middleware Order

Middleware order is critical for proper functionality:

```typescript
// 1. Logging (first - logs all requests)
app.use(loggingMiddleware);

// 2. Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 3. Rate limiting (protect expensive operations)
app.use(rateLimitMiddleware);

// 4. Routes (includes validation middleware)
app.use(routes);

// 5. 404 handler
app.use(notFoundMiddleware);

// 6. Error handler (last - catches all errors)
app.use(errorMiddleware);
```

## Best Practices

### 1. Keep Middleware Focused

Each middleware should have one responsibility:

```typescript
// ✅ GOOD: Single responsibility
export const loggingMiddleware = (req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
};

// ❌ BAD: Multiple responsibilities
export const megaMiddleware = (req, res, next) => {
  console.log(req.url);        // Logging
  validateInput(req.body);     // Validation
  checkAuth(req.headers);      // Authentication
  next();
};
```

### 2. Always Call next()

Middleware must call `next()` or send a response:

```typescript
// ✅ GOOD: Calls next()
export const middleware = (req, res, next) => {
  doSomething();
  next();
};

// ✅ GOOD: Sends response
export const middleware = (req, res, next) => {
  if (error) {
    return res.status(400).json({ error: 'Bad request' });
  }
  next();
};

// ❌ BAD: Neither calls next() nor sends response
export const middleware = (req, res, next) => {
  doSomething();
  // Request hangs!
};
```

### 3. Error Handling

Pass errors to error middleware:

```typescript
// ✅ GOOD: Pass to error middleware
export const middleware = (req, res, next) => {
  try {
    validate(req.body);
    next();
  } catch (error) {
    next(error);  // Error middleware will handle it
  }
};

// ❌ BAD: Handle error directly
export const middleware = (req, res, next) => {
  try {
    validate(req.body);
    next();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
```

### 4. Type Safety

Use TypeScript types:

```typescript
import { Request, Response, NextFunction } from 'express';

export const middleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // Implementation
  next();
};
```

### 5. Async Middleware

Handle async operations properly:

```typescript
// ✅ GOOD: Async middleware with error handling
export const asyncMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    await doAsyncOperation();
    next();
  } catch (error) {
    next(error);
  }
};

// Alternative: Wrapper function
const asyncHandler = (fn: Function) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

export const middleware = asyncHandler(async (req, res, next) => {
  await doAsyncOperation();
  next();
});
```

## Common Patterns

### Conditional Middleware

Apply middleware conditionally:

```typescript
export const conditionalMiddleware = (condition: boolean) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (condition) {
      // Do something
      doSomething();
    }
    next();
  };
};

// Usage
app.use(conditionalMiddleware(config.ENABLE_FEATURE));
```

### Configurable Middleware

Create middleware factories:

```typescript
export const rateLimitMiddleware = (options?: RateLimitOptions) => {
  const max = options?.max || 100;
  const windowMs = options?.windowMs || 60000;
  
  return (req: Request, res: Response, next: NextFunction) => {
    // Implementation using options
    next();
  };
};

// Usage
app.use(rateLimitMiddleware({ max: 50, windowMs: 30000 }));
```

### Middleware Composition

Combine multiple middleware:

```typescript
export const protectedRoute = [
  authMiddleware,
  rateLimitMiddleware({ max: 10 }),
  validateBody(schema),
];

// Usage
router.post('/api/v1/protected', ...protectedRoute, controller.create);
```

## Testing Middleware

Test middleware with mocked Express objects:

```typescript
import { loggingMiddleware } from '../middleware/logging';
import { Request, Response, NextFunction } from 'express';

describe('loggingMiddleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockRequest = {
      method: 'GET',
      url: '/test',
    };
    mockResponse = {};
    mockNext = jest.fn();
  });

  it('should log request and call next', () => {
    const consoleSpy = jest.spyOn(console, 'log');
    
    loggingMiddleware(
      mockRequest as Request,
      mockResponse as Response,
      mockNext
    );

    expect(consoleSpy).toHaveBeenCalled();
    expect(mockNext).toHaveBeenCalled();
  });
});
```

## Adding New Middleware

1. **Create middleware file:**
```typescript
// middleware/example.ts
import { Request, Response, NextFunction } from 'express';

export const exampleMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // Implementation
  next();
};
```

2. **Add tests:**
```typescript
// __tests__/middleware-example.test.ts
import { exampleMiddleware } from '../middleware/example';

describe('exampleMiddleware', () => {
  it('should work correctly', () => {
    // Test implementation
  });
});
```

3. **Register in app:**
```typescript
// server.ts
import { exampleMiddleware } from './middleware/example';

app.use(exampleMiddleware);
```

## Security Considerations

### Input Sanitization

```typescript
export const sanitizeMiddleware = (req, res, next) => {
  if (req.body) {
    req.body = sanitize(req.body);
  }
  next();
};
```

### CORS Headers

```typescript
export const corsMiddleware = (req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  next();
};
```

### Security Headers

```typescript
export const securityHeadersMiddleware = (req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
};
```

## References

- [Express Middleware Guide](https://expressjs.com/en/guide/using-middleware.html)
- [Express Error Handling](https://expressjs.com/en/guide/error-handling.html)
- [Zod Documentation](https://zod.dev/)
