/**
 * Schema Validator
 *
 * Validates data structure against JSON Schema / Zod schemas
 * Avg latency: <20ms
 */

import { z, ZodSchema, ZodError } from 'zod';

export class SchemaValidator {
  private schemas: Map<string, ZodSchema>;

  constructor() {
    this.schemas = new Map();
    this.registerDefaultSchemas();
  }

  async validate(context: ValidationContext): Promise<ValidationResult> {
    const startTime = Date.now();
    const { data, metadata } = context;

    try {
      // Determine which schema to use
      const schemaKey = metadata?.schemaKey as string || 'default';
      const schema = this.schemas.get(schemaKey);

      if (!schema) {
        return {
          validatorName: 'schema',
          passed: true, // No schema = no validation (permissive)
          violations: [],
          suggestions: [`No schema found for key: ${schemaKey}`]
        };
      }

      // Validate using Zod
      const result = schema.safeParse(data);

      if (result.success) {
        return {
          validatorName: 'schema',
          passed: true,
          violations: [],
          metadata: {
            duration: Date.now() - startTime
          }
        };
      }

      // Extract violations from Zod errors
      const violations = this.formatZodErrors(result.error);

      return {
        validatorName: 'schema',
        passed: false,
        violations,
        severity: 'high',
        suggestions: this.generateSuggestions(result.error)
      };

    } catch (error) {
      return {
        validatorName: 'schema',
        passed: false,
        violations: [`Validation error: ${error.message}`],
        severity: 'critical'
      };
    }
  }

  /**
   * Register a schema for a specific context
   */
  registerSchema(key: string, schema: ZodSchema): void {
    this.schemas.set(key, schema);
  }

  private registerDefaultSchemas(): void {
    // Agent deployment schema
    this.schemas.set('agent_deploy', z.object({
      agentId: z.string().min(1),
      name: z.string().min(1),
      type: z.enum(['architect', 'security', 'qa', 'devops', 'data', 'pm']),
      config: z.record(z.unknown()),
      status: z.enum(['pending', 'running', 'stopped']).optional()
    }));

    // Automation task schema
    this.schemas.set('automation_task', z.object({
      taskId: z.string(),
      action: z.string(),
      params: z.record(z.unknown()),
      priority: z.enum(['low', 'medium', 'high', 'critical']),
      timeout: z.number().positive().optional()
    }));

    // Contract schema
    this.schemas.set('contract', z.object({
      contractId: z.string(),
      type: z.enum(['sla', 'policy', 'agreement']),
      parties: z.array(z.string()).min(2),
      terms: z.record(z.unknown()),
      validUntil: z.string().datetime().optional()
    }));

    // Self-healing action schema
    this.schemas.set('self_healing', z.object({
      triggerId: z.string(),
      issue: z.string(),
      action: z.enum(['restart', 'scale', 'failover', 'patch']),
      target: z.string(),
      dryRun: z.boolean().optional()
    }));
  }

  private formatZodErrors(error: ZodError): string[] {
    return error.errors.map(err => {
      const path = err.path.join('.');
      return `${path}: ${err.message}`;
    });
  }

  private generateSuggestions(error: ZodError): string[] {
    return error.errors.map(err => {
      switch (err.code) {
        case 'invalid_type':
          return `Expected ${err.expected} but got ${err.received}`;
        case 'too_small':
          return `Minimum length/value is ${err.minimum}`;
        case 'too_big':
          return `Maximum length/value is ${err.maximum}`;
        default:
          return 'Check schema documentation';
      }
    });
  }
}

interface ValidationContext {
  eventId: string;
  data: unknown;
  metadata?: Record<string, unknown>;
}

interface ValidationResult {
  validatorName: string;
  passed: boolean;
  violations: string[];
  severity?: 'low' | 'medium' | 'high' | 'critical';
  suggestions?: string[];
  metadata?: Record<string, unknown>;
}
