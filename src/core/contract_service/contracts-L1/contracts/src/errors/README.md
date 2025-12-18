# Error Classes

This directory contains custom error classes used throughout the contracts service.

## Overview

All custom errors extend the base `AppError` class, which provides:
- Consistent error structure
- Trace IDs for debugging
- HTTP status codes
- Operational vs programmer error distinction

## Error Classes

### AppError

Base class for all application errors.

```typescript
export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly traceId: string;
  public readonly timestamp: string;
  public readonly isOperational: boolean;
}
```

### ValidationError

Thrown when input validation fails (400 Bad Request).

**Usage:**
```typescript
throw new ValidationError('Invalid email format', [
  { field: 'email', message: 'Must be valid email', code: 'INVALID_EMAIL' }
]);
```

### NotFoundError

Thrown when a requested resource is not found (404 Not Found).

**Usage:**
```typescript
throw new NotFoundError('User');
// Returns: "User not found"
```

### PathValidationError

**⚠️ Security-Critical Error**

Thrown when file path validation fails due to path traversal attempts or unauthorized access.

**Why 404 instead of 403?**

Returns 404 (Not Found) instead of 403 (Forbidden) to prevent information disclosure. If we returned 403, attackers could:
1. Enumerate valid paths by distinguishing between "not found" and "forbidden"
2. Learn about the file system structure
3. Identify protected files outside the safe directory

**Usage:**
```typescript
const resolvedPath = path.resolve(SAFE_ROOT, userPath);
const relativePath = path.relative(SAFE_ROOT, resolvedPath);

if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
  throw new PathValidationError(); // Returns 404 to client
}
```

**Attack Scenarios Blocked:**

| Attack | Example | Response |
|--------|---------|----------|
| Directory Traversal | `../../../etc/passwd` | 404 Not Found |
| Absolute Path | `/etc/passwd` | 404 Not Found |
| Windows Path | `C:\Windows\System32` | 404 Not Found |

**Security Benefits:**
- ✅ Prevents path enumeration attacks
- ✅ Protects file system structure information
- ✅ Consistent error response for all path violations
- ✅ No information leakage about the file system

### UnauthorizedError

Thrown when authentication fails (401 Unauthorized).

**Usage:**
```typescript
throw new UnauthorizedError('Invalid API key');
```

### ForbiddenError

Thrown when access is forbidden (403 Forbidden).

**Usage:**
```typescript
throw new ForbiddenError('Insufficient permissions');
```

### ConflictError

Thrown when there's a conflict with current state (409 Conflict).

**Usage:**
```typescript
throw new ConflictError('Resource already exists');
```

### ServiceUnavailableError

Thrown when a service is temporarily unavailable (503 Service Unavailable).

**Usage:**
```typescript
throw new ServiceUnavailableError('Database');
// Returns: "Database is currently unavailable"
```

## Error Handling Middleware

Errors are caught and processed by the error middleware in `src/middleware/error.ts`:

```typescript
app.use(errorMiddleware);
```

The middleware:
1. Logs operational errors at appropriate levels
2. Returns consistent JSON error responses
3. Hides internal error details in production
4. Includes trace IDs for debugging

## Best Practices

### 1. Use Specific Error Classes

❌ Don't:
```typescript
throw new Error('File not found');
```

✅ Do:
```typescript
throw new NotFoundError('File');
```

### 2. Provide Context

❌ Don't:
```typescript
throw new ValidationError('Invalid input');
```

✅ Do:
```typescript
throw new ValidationError('Invalid email format', [
  { field: 'email', message: 'Must be valid email', code: 'INVALID_EMAIL' }
]);
```

### 3. Catch Specific Errors

❌ Don't:
```typescript
try {
  await operation();
} catch (error) {
  console.log(error);
}
```

✅ Do:
```typescript
try {
  await operation();
} catch (error) {
  if (error instanceof PathValidationError) {
    // Handle path validation specifically
  } else if (error instanceof NotFoundError) {
    // Handle not found
  } else {
    // Handle unexpected errors
    throw error;
  }
}
```

### 4. Security-Sensitive Errors

For security-critical operations, use errors that don't leak information:

```typescript
// ❌ Reveals system information
throw new Error(`Path ${resolvedPath} is outside safe directory ${SAFE_ROOT}`);

// ✅ Generic error that prevents information disclosure
throw new PathValidationError(); // Returns "File not found"
```

## Error Response Format

All errors return consistent JSON structure:

```json
{
  "success": false,
  "error": {
    "message": "File not found",
    "code": "NOT_FOUND",
    "traceId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-12-12T08:33:59.932Z"
  }
}
```

Validation errors include additional details:

```json
{
  "success": false,
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "traceId": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2025-12-12T08:33:59.932Z",
    "validationErrors": [
      {
        "field": "email",
        "message": "Must be valid email",
        "code": "INVALID_EMAIL"
      }
    ]
  }
}
```

## Testing Errors

Example test for PathValidationError:

```typescript
describe('Path Validation', () => {
  it('should throw PathValidationError for directory traversal', async () => {
    await expect(
      service.generateFileDigest('../../../etc/passwd')
    ).rejects.toThrow(PathValidationError);
  });

  it('should return 404 for path validation failures', async () => {
    const response = await request(app)
      .post('/api/v1/provenance/attestations')
      .send({ filePath: '../../../etc/passwd', builder: mockBuilder });
    
    expect(response.status).toBe(404);
    expect(response.body.error.message).toBe('File not found');
  });
});
```

## References

- [Error Handling Best Practices](https://nodejs.org/en/docs/guides/error-handling)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [OWASP Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)

---

**Last Updated**: 2025-12-12  
**Maintainer**: SynergyMesh Development Team
