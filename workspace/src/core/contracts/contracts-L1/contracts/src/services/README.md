# Services Layer

## Purpose

Services contain the **business logic** of the Contracts-L1 application. They are framework-agnostic and can be tested independently of the HTTP layer.

## Responsibilities

✅ **Services SHOULD:**

- Implement all business logic and rules
- Orchestrate workflows and operations
- Validate business constraints
- Call other services when needed
- Handle domain-specific operations
- Be framework-agnostic (no Express/HTTP dependencies)

❌ **Services SHOULD NOT:**

- Access HTTP objects (Request/Response)
- Handle HTTP status codes
- Format responses for HTTP
- Contain routing logic
- Depend on specific frameworks

## Service Structure

```typescript
import { SomeModel, SomeInput, SomeOutput } from '../models/some.model';

export class SomeService {
  /**
   * Business operation description
   * @param input - Input data
   * @returns Output data
   * @throws {AppError} When business rules violated
   */
  async create(input: SomeInput): Promise<SomeOutput> {
    // 1. Validate business rules
    this.validateBusinessRules(input);

    // 2. Perform operations
    const result = await this.performOperation(input);

    // 3. Return result
    return result;
  }

  private validateBusinessRules(input: SomeInput): void {
    if (!this.meetsRequirement(input)) {
      throw createError.validation('Business rule violated');
    }
  }

  private async performOperation(input: SomeInput): Promise<SomeOutput> {
    // Implementation
  }
}
```

## Existing Services

### Assignment Services (`services/assignment/`)

#### AutoAssignmentEngine (`auto-assignment-engine.ts`)

**Purpose:** Core engine for intelligent responsibility assignment.

**Key Methods:**

- `assignResponsibility(incident)` - Assign incident to team member
- `analyzeProblemType(incident)` - Analyze and categorize problem
- `identifyRelevantTeams(problemType)` - Find teams for problem type
- `checkMemberAvailability(teams)` - Get available team members
- `selectOptimalAssignee(members, incident)` - Choose best assignee
- `createAssignmentRecord(owner, incident)` - Create assignment record
- `getAssignment(id)` - Retrieve assignment by ID
- `updateAssignmentStatus(id, status)` - Update assignment status
- `getAllAssignments()` - Get all assignments

**Dependencies:**

- `ResponsibilityMatrix`
- `WorkloadBalancer`

#### ResponsibilityGovernance (`responsibility-governance.ts`)

**Purpose:** Governance and compliance tracking for assignments.

**Key Methods:**

- `validateAssignment(assignment)` - Validate assignment compliance
- `trackAssignment(assignment)` - Track assignment for governance
- `getComplianceReport()` - Generate compliance report
- `auditAssignment(id)` - Audit specific assignment

#### ResponsibilityMatrix (`responsibility-matrix.ts`)

**Purpose:** Maps problem types to responsible teams and members.

**Key Methods:**

- `identifyRelevantTeams(problemType)` - Get teams for problem
- `getTeamStructure(teamName)` - Get team details
- `getSpecialties(teamName)` - Get team specialties
- `updateTeamStructure(team)` - Update team information

#### WorkloadBalancer (`workload-balancer.ts`)

**Purpose:** Balances workload across team members.

**Key Methods:**

- `selectOptimalAssignee(members, incident)` - Choose best member
- `calculateExpertiseMatch(member, incident)` - Match expertise
- `calculateAvailability(member)` - Check member availability
- `calculateCurrentWorkload(member)` - Get current workload
- `calculateHistoricalPerformance(member)` - Get performance metrics
- `getWorkloadMetrics(memberId)` - Get detailed metrics
- `getAllWorkloadMetrics()` - Get all team metrics

### Escalation Services (`services/escalation/`)

#### EscalationEngine (`escalation-engine.ts`)

**Purpose:** Manages incident escalation workflows.

**Key Methods:**

- `createEscalation(incident, reason)` - Create new escalation
- `getEscalation(id)` - Get escalation details
- `updateStatus(id, status)` - Update escalation status
- `resolveEscalation(id, resolution)` - Resolve escalation
- `escalateFurther(id, reason)` - Escalate to higher level
- `getStatistics()` - Get escalation statistics

### Provenance Services

#### AttestationService (`attestation.ts`)

**Purpose:** Handles Sigstore attestation creation and verification.

**Key Methods:**

- `createAttestation(subject, predicate)` - Create signed attestation
- `verifyAttestation(attestation)` - Verify attestation signature
- `signWithSigstore(data)` - Sign data with Sigstore
- `validateProvenance(provenance)` - Validate provenance data

#### ProvenanceService (`provenance.ts`)

**Purpose:** Manages build provenance tracking with security controls.

**Key Methods:**

- `createAttestation(filePath, builder)` - Create build attestation
- `verifyAttestation(attestation)` - Verify build attestation
- `importAttestation(data)` - Import external attestation
- `exportAttestation(id)` - Export attestation
- `generateFileDigest(filePath)` - Calculate file digest with path validation
- `buildSLSAProvenance(file, builder)` - Build SLSA provenance

**Private Methods:**

- `resolveSafePath(userInputPath)` - Validate paths against SAFE_ROOT
**Security Enhancements (PR #351):**
- **Policy SEC-PATH-001**: Path traversal prevention using SAFE_ROOT validation
- **Environment Variable**: `SAFE_ROOT_PATH` defines allowed directory for file operations
- **Path Validation**: Uses `realpath()` and `relative()` to prevent directory traversal
- **Reference**: `governance/10-policy/base-policies/security-policies.yaml#SEC-PATH-001`
- **Documentation**: `docs/security/PR351_SECURITY_ENHANCEMENTS.md`

## Best Practices

### 1. Framework-Agnostic

Services should not depend on HTTP frameworks:

```typescript
// ❌ BAD: Depends on Express
import { Request, Response } from 'express';
export class BadService {
  create(req: Request, res: Response) { /* ... */ }
}

// ✅ GOOD: Pure business logic
export class GoodService {
  create(input: CreateInput): Promise<CreateOutput> { /* ... */ }
}
```

### 2. Single Responsibility

Each service should have one clear purpose:

```typescript
// ✅ GOOD: Focused service
export class UserService {
  async createUser(data: CreateUserInput): Promise<User> { /* ... */ }
  async updateUser(id: string, data: UpdateUserInput): Promise<User> { /* ... */ }
  async deleteUser(id: string): Promise<void> { /* ... */ }
}

// ❌ BAD: Too many responsibilities
export class MegaService {
  async createUser() { /* ... */ }
  async sendEmail() { /* ... */ }
  async processPayment() { /* ... */ }
  async generateReport() { /* ... */ }
}
```

### 3. Dependency Injection

Use constructor injection for dependencies:

```typescript
export class AssignmentService {
  private matrix: ResponsibilityMatrix;
  private balancer: WorkloadBalancer;

  constructor(
    matrix?: ResponsibilityMatrix,
    balancer?: WorkloadBalancer
  ) {
    this.matrix = matrix || new ResponsibilityMatrix();
    this.balancer = balancer || new WorkloadBalancer();
  }
}
```

### 4. Error Handling

Throw domain-specific errors:

```typescript
import { createError } from '../errors';

export class UserService {
  async getUser(id: string): Promise<User> {
    const user = await this.findById(id);
    
    if (!user) {
      throw createError.notFound(`User ${id} not found`);
    }
    
    if (!user.isActive) {
      throw createError.forbidden('User is not active');
    }
    
    return user;
  }
}
```

### 5. Type Safety

Use strong typing throughout:

```typescript
// models/user.model.ts
export interface CreateUserInput {
  email: string;
  name: string;
  role: UserRole;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
}

// services/user.service.ts
export class UserService {
  async create(input: CreateUserInput): Promise<User> {
    // Implementation
  }
}
```

### 6. Async/Await

Use async/await for asynchronous operations:

```typescript
export class UserService {
  // ✅ GOOD: Async/await
  async create(input: CreateUserInput): Promise<User> {
    const validated = await this.validate(input);
    const user = await this.save(validated);
    await this.sendWelcomeEmail(user);
    return user;
  }

  // ❌ BAD: Callback hell
  create(input: CreateUserInput, callback: Function) {
    this.validate(input, (err, validated) => {
      if (err) return callback(err);
      this.save(validated, (err, user) => {
        if (err) return callback(err);
        callback(null, user);
      });
    });
  }
}
```

### 7. Service Composition

Services can call other services:

```typescript
export class OrderService {
  constructor(
    private userService: UserService,
    private productService: ProductService,
    private paymentService: PaymentService
  ) {}

  async createOrder(input: CreateOrderInput): Promise<Order> {
    // Validate user
    const user = await this.userService.getUser(input.userId);
    
    // Validate products
    const products = await this.productService.getProducts(input.productIds);
    
    // Process payment
    const payment = await this.paymentService.charge(user, products);
    
    // Create order
    return this.save({ user, products, payment });
  }
}
```

## Testing Services

Services should be unit tested in isolation:

```typescript
import { UserService } from '../services/user.service';
import { UserRepository } from '../repositories/user.repository';

jest.mock('../repositories/user.repository');

describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = new UserRepository() as jest.Mocked<UserRepository>;
    service = new UserService(mockRepository);
  });

  describe('create', () => {
    it('should create user successfully', async () => {
      const input = { email: 'test@example.com', name: 'Test' };
      const expected = { id: '123', ...input, createdAt: new Date() };
      
      mockRepository.save.mockResolvedValue(expected);

      const result = await service.create(input);

      expect(result).toEqual(expected);
      expect(mockRepository.save).toHaveBeenCalledWith(input);
    });

    it('should throw error for duplicate email', async () => {
      const input = { email: 'duplicate@example.com', name: 'Test' };
      
      mockRepository.save.mockRejectedValue(new Error('Duplicate'));

      await expect(service.create(input)).rejects.toThrow();
    });
  });
});
```

## Adding a New Service

1. **Create the service file:**

```typescript
// services/example.service.ts
import { ExampleInput, ExampleOutput } from '../models/example.model';
import { createError } from '../errors';

export class ExampleService {
  /**
   * Create a new example
   * @param input - Example data
   * @returns Created example
   */
  async create(input: ExampleInput): Promise<ExampleOutput> {
    // Validate business rules
    this.validateInput(input);

    // Perform operation
    const result = await this.performCreate(input);

    return result;
  }

  private validateInput(input: ExampleInput): void {
    if (!input.name) {
      throw createError.validation('Name is required');
    }
  }

  private async performCreate(input: ExampleInput): Promise<ExampleOutput> {
    // Implementation
    return {
      id: 'generated-id',
      ...input,
      createdAt: new Date(),
    };
  }
}
```

1. **Create tests:**

```typescript
// __tests__/example.service.test.ts
import { ExampleService } from '../services/example.service';

describe('ExampleService', () => {
  let service: ExampleService;

  beforeEach(() => {
    service = new ExampleService();
  });

  it('should create example', async () => {
    const input = { name: 'Test' };
    const result = await service.create(input);
    
    expect(result).toHaveProperty('id');
    expect(result.name).toBe('Test');
  });
});
```

1. **Use in controller:**

```typescript
// controllers/example.controller.ts
import { ExampleService } from '../services/example.service';

export class ExampleController {
  private service: ExampleService;

  constructor() {
    this.service = new ExampleService();
  }

  create = async (req: Request, res: Response): Promise<void> => {
    const result = await this.service.create(req.body);
    sendSuccess(res, result, { status: 201 });
  };
}
```

## Common Patterns

### Repository Pattern

Separate data access from business logic:

```typescript
export class UserService {
  constructor(private repository: UserRepository) {}

  async create(input: CreateUserInput): Promise<User> {
    const user = await this.repository.save(input);
    return user;
  }
}
```

### Factory Pattern

Create complex objects:

```typescript
export class AssignmentFactory {
  createAssignment(incident: Incident, owner: TeamMember): Assignment {
    return {
      id: generateId(),
      incidentId: incident.id,
      primaryOwner: owner,
      status: 'ASSIGNED',
      assignedAt: new Date(),
      slaTarget: this.calculateSLA(incident.priority),
    };
  }
}
```

### Strategy Pattern

Different algorithms for different scenarios:

```typescript
interface AssignmentStrategy {
  selectAssignee(members: TeamMember[], incident: Incident): TeamMember;
}

export class WorkloadBalancer {
  constructor(private strategy: AssignmentStrategy) {}

  select(members: TeamMember[], incident: Incident): TeamMember {
    return this.strategy.selectAssignee(members, incident);
  }
}
```

## References

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
