# Contracts-L1 Architecture Documentation

## Overview

Contracts-L1 is a core service of the SynergyMesh platform that provides **build provenance tracking**, **SLSA attestation**, and **automated responsibility assignment** capabilities. The service follows a **clean layered architecture** pattern to ensure maintainability, testability, and scalability.

## Architecture Pattern

The service implements a **3-tier layered architecture**:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Controllers, Routes, Middleware)      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│         (Services)                      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Data Layer                      │
│    (Models, Types, Schemas)             │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Presentation Layer (`controllers/`, `routes.ts`, `middleware/`)

**Purpose:** Handles HTTP request/response cycle, input validation, and routing.

**Components:**


- **Routes** (`routes.ts`): Define API endpoints and map them to controllers
- **Middleware** (`middleware/`): Cross-cutting concerns (logging, validation, error handling, rate limiting)

**Key Principles:**

- Controllers should be thin - only handle request/response
- No business logic in controllers
- All input validation via Zod schemas
- Use middleware for cross-cutting concerns

**Example:**

```typescript
// controllers/provenance.ts
export class ProvenanceController {
  async createAttestation(req: Request, res: Response): Promise<void> {
    // 1. Extract validated data from request
    const { filePath, builder } = req.body;
    
    // 2. Call service layer
    const attestation = await provenanceService.createAttestation(filePath, builder);
    
    // 3. Format and send response
    sendSuccess(res, attestation, { status: 201 });
  }
}
```

#### 2. Business Logic Layer (`services/`)

**Purpose:** Contains core business logic, orchestrates workflows, enforces business rules.

**Components:**


- **Escalation Engine** (`services/escalation/`): Incident escalation workflows

**Key Principles:**

- Services contain all business logic
- Services are framework-agnostic (no Express/HTTP dependencies)
- Services can call other services
- All business rules enforced here
- Testable without HTTP layer

**Example:**

```typescript
// services/provenance.ts
export class ProvenanceService {
  async createAttestation(filePath: string, builder: BuilderInfo): Promise<Attestation> {
    // Business logic:
    // 1. Validate file exists
    // 2. Calculate digest
    // 3. Create SLSA provenance
    // 4. Sign with Sigstore
    // 5. Store attestation
    return attestation;
  }
}
```

#### 3. Data Layer (`models/`, `types/`)

**Purpose:** Defines data structures, validation schemas, and type definitions.

**Components:**

- **Models** (`models/`): Zod schemas for data validation and TypeScript types
- **Types** (`types/`): TypeScript type definitions and interfaces
- **Errors** (`errors/`): Custom error types

**Key Principles:**

- All data structures validated with Zod
- Strong typing throughout
- Models are immutable
- Clear separation of input/output types

**Example:**

```typescript
// models/provenance.model.ts
export const createAttestationSchema = z.object({
  filePath: z.string().min(1),
  builder: z.object({
    id: z.string().url(),
    version: z.string(),
  }),
});

export type CreateAttestationInput = z.infer<typeof createAttestationSchema>;
```

## Directory Structure

```
src/
├── controllers/           # HTTP request handlers
│   ├── assignment.ts      # Auto-assignment endpoints
│   ├── escalation.ts      # Escalation management endpoints
│   ├── provenance.ts      # Provenance tracking endpoints
│   └── slsa.ts            # SLSA attestation endpoints
│
├── services/              # Business logic layer
│   ├── assignment/        # Assignment system services
│   │   ├── auto-assignment-engine.ts
│   │   ├── responsibility-governance.ts
│   │   ├── responsibility-matrix.ts
│   │   └── workload-balancer.ts
│   ├── escalation/        # Escalation services
│   │   └── escalation-engine.ts
│   ├── attestation.ts     # Sigstore attestation service
│   └── provenance.ts      # Provenance tracking service
│
├── models/                # Data models and schemas
│   ├── assignment.model.ts
│   ├── escalation.model.ts
│   ├── provenance.model.ts
│   └── slsa.model.ts
│
├── middleware/            # HTTP middleware
│   ├── audit-log.ts       # Audit logging
│   ├── error.ts           # Error handling
│   ├── logging.ts         # Request logging
│   ├── rate-limit.ts      # Rate limiting
│   ├── response.ts        # Response formatting
│   ├── validation.ts      # Input validation
│   └── zodErrorHandler.ts # Zod error formatting
│
├── types/                 # TypeScript type definitions
│   └── assignment.ts      # Assignment system types
│
├── errors/                # Custom error types
│   └── index.ts
│
├── routes.ts              # API route definitions
├── server.ts              # Express app initialization
└── config.ts              # Configuration management
```

## Data Flow

### Typical Request Flow

```
1. HTTP Request
   ↓
2. Logging Middleware (logs request)
   ↓
3. Validation Middleware (validates input with Zod)
   ↓
4. Rate Limit Middleware (checks rate limits)
   ↓
5. Controller (extracts data, calls service)
   ↓
6. Service (executes business logic)
   ↓
7. Controller (formats response)
   ↓
8. Response Middleware (formats success/error)
   ↓
9. Logging Middleware (logs response)
   ↓
10. HTTP Response
```

### Example: Create Provenance Attestation

```typescript
// 1. Route definition (routes.ts)
router.post(
  '/api/v1/provenance/attestations',
  provenanceController.createAttestation
);

// 2. Controller (controllers/provenance.ts)
async createAttestation(req: Request, res: Response) {
  const { filePath, builder } = req.body; // Validated by middleware
  const attestation = await this.provenanceService.createAttestation(filePath, builder);
  sendSuccess(res, attestation, { status: 201 });
}

// 3. Service (services/provenance.ts)
async createAttestation(filePath: string, builder: BuilderInfo) {
  // Business logic implementation
  const digest = await this.calculateDigest(filePath);
  const provenance = this.buildSLSAProvenance(filePath, builder, digest);
  const attestation = await this.signWithSigstore(provenance);
  return attestation;
}
```

## Key Design Patterns

### 1. Dependency Injection

Services are instantiated in controllers and can be injected for testing:

```typescript
export class ProvenanceController {
  constructor(private provenanceService: ProvenanceService = new ProvenanceService()) {}
}
```

### 2. Middleware Chain

Express middleware chain for cross-cutting concerns:

```typescript
app.use(loggingMiddleware);
app.use(express.json());
app.use(rateLimitMiddleware);
app.use(routes);
app.use(errorMiddleware);
```

### 3. Zod Schema Validation

All input validation uses Zod schemas:

```typescript
const schema = z.object({
  email: z.string().email(),
  age: z.number().min(18),
});

router.post('/users', validateBody(schema), controller.create);
```

### 4. Centralized Error Handling

All errors flow through error middleware:

```typescript
// In service or controller
throw createError.notFound('Resource not found');

// Caught by error middleware
app.use(errorMiddleware);
```

### 5. Response Formatting

Consistent response format using helper functions:

```typescript
sendSuccess(res, data, { status: 200 });
sendError(res, error);
```

## Testing Strategy

### Unit Tests (`__tests__/`)

- **Services**: Test business logic in isolation
- **Middleware**: Test with mocked Express objects
- **Models**: Test Zod schema validation
- **Controllers**: Test with mocked services

### Integration Tests

- Test full request/response cycle
- Test middleware chain
- Test database interactions
- Test external API calls

### Test Organization

```
src/
├── __tests__/
│   ├── auto-assignment-engine.test.ts    # Service test
│   ├── workload-balancer.test.ts         # Service test
│   ├── middleware-error.test.ts          # Middleware test
│   ├── middleware-logging.test.ts        # Middleware test
│   ├── middleware-validation.test.ts     # Middleware test
│   └── api.test.ts                       # Integration test
```

## Module Boundaries

### Clear Separation of Concerns

1. **Controllers** never contain business logic
2. **Services** never access HTTP objects (Request/Response)
3. **Models** are pure data structures
4. **Middleware** handles cross-cutting concerns only

### Communication Rules

- Controllers → Services ✅
- Services → Services ✅
- Services → Models ✅
- Controllers → Models ✅
- Models → Services ❌
- Services → Controllers ❌

## Configuration Management

Configuration is centralized in `config.ts` using Zod validation:

```typescript
const configSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  // ... more config
});

export default configSchema.parse(process.env);
```

## Error Handling Strategy

### Custom Error Types

```typescript
class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: ErrorCode,
    message: string
  ) {
    super(message);
  }
}
```

### Error Creation Helpers

```typescript
const createError = {
  badRequest: (message: string) => new AppError(400, 'BAD_REQUEST', message),
  unauthorized: (message: string) => new AppError(401, 'UNAUTHORIZED', message),
  notFound: (message: string) => new AppError(404, 'NOT_FOUND', message),
  // ... more helpers
};
```

### Error Middleware

Centralized error handling ensures consistent error responses:

```typescript
export const errorMiddleware = (err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        traceId: req.traceId,
        timestamp: new Date().toISOString(),
      },
    });
  } else {
    // Handle unexpected errors
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: config.NODE_ENV === 'production' ? 'Internal server error' : err.message,
        traceId: req.traceId,
        timestamp: new Date().toISOString(),
      },
    });
  }
};
```

## Security Considerations

### Input Validation

- All inputs validated with Zod schemas
- Type coercion handled explicitly
- Extra fields stripped by default

### Rate Limiting

- Rate limiting middleware protects against abuse
- Configurable limits per endpoint

### Audit Logging

- All requests logged with trace IDs
- Sensitive data redacted in logs
- Audit log middleware tracks critical operations

### Error Information

- Production mode hides internal error details
- Stack traces only in development
- Trace IDs for debugging

## Performance Optimization

### Middleware Order

Middleware ordered for optimal performance:

1. Logging (fast, needed for all requests)
2. Body parsing (fast)
3. Rate limiting (fast, protects expensive operations)
4. Validation (medium, fails fast on bad input)
5. Business logic (slowest)

### Caching Strategy

- In-memory caching for frequently accessed data
- Cache invalidation on updates
- Configurable TTL

## Deployment Architecture

```
┌─────────────────────────────────────┐
│     Load Balancer / API Gateway     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     Contracts-L1 Service (Node.js)  │
│  - Express Server                   │
│  - Controllers + Services           │
│  - Middleware Chain                 │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     External Dependencies           │
│  - Sigstore (attestation)           │
│  - File System (provenance)         │
└─────────────────────────────────────┘
```

## Future Enhancements

### Planned Improvements

1. **Database Integration**: Add persistent storage for attestations
2. **Message Queue**: Asynchronous processing for heavy operations
3. **Caching Layer**: Redis for distributed caching
4. **GraphQL API**: Alternative to REST for flexible queries
5. **Microservices Split**: Separate assignment and provenance services

### Extensibility Points

- **New Controllers**: Add to `controllers/` and register in `routes.ts`
- **New Services**: Add to `services/` and inject into controllers
- **New Middleware**: Add to `middleware/` and register in `server.ts`
- **New Models**: Add Zod schemas to `models/`

## Development Guidelines

### Adding a New Feature

1. **Define Model** (`models/`): Create Zod schema for data validation
2. **Create Service** (`services/`): Implement business logic
3. **Create Controller** (`controllers/`): Handle HTTP requests
4. **Register Routes** (`routes.ts`): Map endpoints to controller methods
5. **Add Tests** (`__tests__/`): Unit and integration tests
6. **Update Documentation**: Update this file and related docs

### Code Style

- Use TypeScript strict mode
- Follow existing naming conventions
- Add JSDoc comments for public APIs
- Use async/await for asynchronous code
- Handle errors explicitly

### Testing Guidelines

- Write tests before implementation (TDD)
- Test both success and failure cases
- Mock external dependencies
- Aim for 80%+ code coverage
- Test edge cases

## References

- [Express.js Documentation](https://expressjs.com/)
- [Zod Documentation](https://zod.dev/)
- [SLSA Specification](https://slsa.dev/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## Maintainers

For questions or contributions, refer to the main repository documentation.

---

**Last Updated:** 2024-12-09
**Version:** 1.0.0
