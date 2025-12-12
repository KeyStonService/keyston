# Controllers Layer

## Purpose

Controllers are the **presentation layer** of the Contracts-L1 service. They
handle HTTP request/response cycle and orchestrate service calls.

## Responsibilities

✅ **Controllers SHOULD:**

- Extract and validate data from HTTP requests
- Call appropriate service methods
- Format and send HTTP responses
- Handle HTTP-specific concerns (status codes, headers)
- Use middleware for input validation

❌ **Controllers SHOULD NOT:**

- Contain business logic
- Access database directly
- Perform complex calculations
- Handle file system operations
- Implement validation logic (use Zod schemas instead)

## Controller Structure

```typescript
import { Request, Response } from 'express';
import { sendSuccess, handleControllerError } from '../middleware/response';
import { SomeService } from '../services/some-service';

export class SomeController {
  private service: SomeService;

  constructor() {
    this.service = new SomeService();
  }

  /**
   * Handler description
   * POST /api/v1/resource
   */
  create = async (req: Request, res: Response): Promise<void> => {
    try {
      // 1. Extract validated data (validation done by middleware)
      const data = req.body;

      // 2. Call service
      const result = await this.service.create(data);

      // 3. Send response
      sendSuccess(res, result, { status: 201 });
    } catch (error) {
      handleControllerError(res, error);
    }
  };
}
```

## Existing Controllers

### AssignmentController (`assignment.ts`)

**Endpoints:**

- `POST /api/v1/assignment/assign` - Create new assignment
- `POST /api/v1/assignment/status/:id` - Update assignment status
- `GET /api/v1/assignment/status/:id` - Get assignment status
- `GET /api/v1/assignment/workload` - Get workload metrics
- `POST /api/v1/assignment/reassign/:id` - Reassign incident
- `POST /api/v1/assignment/escalate/:id` - Escalate incident
- `GET /api/v1/assignment/all` - Get all assignments
- `GET /api/v1/assignment/report` - Get performance report

**Services Used:**

- `AutoAssignmentEngine`
- `ResponsibilityGovernance`

### EscalationController (`escalation.ts`)

**Endpoints:**

- `POST /api/v1/escalation/create` - Create escalation
- `GET /api/v1/escalation/:escalationId` - Get escalation details
- `GET /api/v1/escalation/incident/:incidentId` - Get escalations by incident
- `POST /api/v1/escalation/:escalationId/status` - Update status
- `POST /api/v1/escalation/:escalationId/resolve` - Resolve escalation
- `POST /api/v1/escalation/:escalationId/escalate` - Escalate further
- `GET /api/v1/escalation/customer-service/available` - Get available agents
- `GET /api/v1/escalation/statistics` - Get escalation statistics

**Services Used:**

- `EscalationEngine`

### ProvenanceController (`provenance.ts`)

**Endpoints:**

- `POST /api/v1/provenance/attestations` - Create attestation
- `POST /api/v1/provenance/verify` - Verify attestation
- `POST /api/v1/provenance/import` - Import attestation
- `GET /api/v1/provenance/digest/:filePath` - Get file digest
- `GET /api/v1/provenance/export/:id` - Export attestation

**Services Used:**

- `ProvenanceService`
- `AttestationService`

### SLSAController (`slsa.ts`)

**Endpoints:**

- `POST /api/v1/slsa/attestations` - Create SLSA attestation
- `POST /api/v1/slsa/verify` - Verify SLSA attestation
- `POST /api/v1/slsa/digest` - Generate digest
- `POST /api/v1/slsa/contracts` - Create contract attestation
- `POST /api/v1/slsa/summary` - Get attestation summary

**Services Used:**

- `SLSAAttestationService`

## Best Practices

### 1. Thin Controllers

Keep controllers thin by moving logic to services:

```typescript
// ❌ BAD: Logic in controller
create = async (req: Request, res: Response) => {
  const data = req.body;
  // Complex validation logic
  if (!data.email || !data.email.includes('@')) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  // Business logic
  const result = await doSomething(data);
  res.json(result);
};

// ✅ GOOD: Delegate to service
create = async (req: Request, res: Response) => {
  const data = req.body; // Validated by middleware
  const result = await this.service.create(data);
  sendSuccess(res, result, { status: 201 });
};
```

### 2. Consistent Error Handling

Use middleware for error handling:

```typescript
// ✅ GOOD: Let errors bubble to error middleware
create = async (req: Request, res: Response): Promise<void> => {
  try {
    const result = await this.service.create(req.body);
    sendSuccess(res, result, { status: 201 });
  } catch (error) {
    handleControllerError(res, error);
  }
};
```

### 3. Use Response Helpers

Use standardized response formatting:

```typescript
import { sendSuccess, sendError } from '../middleware/response';

// Success response
sendSuccess(res, data, { status: 200 });

// Error response
sendError(res, error);
```

### 4. Arrow Functions for Binding

Use arrow functions to maintain `this` context:

```typescript
export class SomeController {
  // ✅ GOOD: Arrow function maintains this binding
  create = async (req: Request, res: Response): Promise<void> => {
    await this.service.create(req.body);
  };

  // ❌ BAD: Regular method loses this binding when passed to router
  async create(req: Request, res: Response): Promise<void> {
    await this.service.create(req.body);
  }
}
```

### 5. Type Safety

Always type request/response:

```typescript
// ✅ GOOD: Typed parameters
create = async (req: Request, res: Response): Promise<void> => {
  // Implementation
};

// ❌ BAD: Untyped parameters
create = async (req: any, res: any) => {
  // Implementation
};
```

## Adding a New Controller

1. **Create the controller file:**

```typescript
// controllers/example.ts
import { Request, Response } from 'express';
import { sendSuccess, handleControllerError } from '../middleware/response';
import { ExampleService } from '../services/example';

export class ExampleController {
  private service: ExampleService;

  constructor() {
    this.service = new ExampleService();
  }

  create = async (req: Request, res: Response): Promise<void> => {
    try {
      const result = await this.service.create(req.body);
      sendSuccess(res, result, { status: 201 });
    } catch (error) {
      handleControllerError(res, error);
    }
  };
}
```

1. **Register routes:**

```typescript
// routes.ts
import { ExampleController } from './controllers/example';

const exampleController = new ExampleController();

router.post('/api/v1/examples', exampleController.create);
```

1. **Add validation middleware:**

```typescript
import { validateBody } from './middleware/validation';
import { createExampleSchema } from './models/example.model';

router.post(
  '/api/v1/examples',
  validateBody(createExampleSchema),
  exampleController.create
);
```

1. **Write tests:**

```typescript
// __tests__/example-controller.test.ts
describe('ExampleController', () => {
  it('should create example', async () => {
    // Test implementation
  });
});
```

## Testing Controllers

Controllers should be tested with mocked services:

```typescript
import { ExampleController } from '../controllers/example';
import { ExampleService } from '../services/example';

jest.mock('../services/example');

describe('ExampleController', () => {
  let controller: ExampleController;
  let mockService: jest.Mocked<ExampleService>;

  beforeEach(() => {
    controller = new ExampleController();
    mockService = controller['service'] as jest.Mocked<ExampleService>;
  });

  it('should call service and return result', async () => {
    const mockData = { id: '123', name: 'Test' };
    mockService.create.mockResolvedValue(mockData);

    const req = { body: { name: 'Test' } } as Request;
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    } as unknown as Response;

    await controller.create(req, res);

    expect(mockService.create).toHaveBeenCalledWith({ name: 'Test' });
    expect(res.status).toHaveBeenCalledWith(201);
  });
});
```

## Common Patterns

### Pagination

```typescript
list = async (req: Request, res: Response): Promise<void> => {
  const { page = 1, limit = 10 } = req.query;
  const result = await this.service.list(Number(page), Number(limit));
  sendSuccess(res, result);
};
```

### Filtering

```typescript
list = async (req: Request, res: Response): Promise<void> => {
  const filters = req.query;
  const result = await this.service.list(filters);
  sendSuccess(res, result);
};
```

### Resource by ID

```typescript
get = async (req: Request, res: Response): Promise<void> => {
  const { id } = req.params;
  const result = await this.service.getById(id);
  sendSuccess(res, result);
};
```

## References

- [Express Request Documentation](https://expressjs.com/en/api.html#req)
- [Express Response Documentation](https://expressjs.com/en/api.html#res)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
