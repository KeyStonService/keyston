/**
 * Realtime QA Engine
 *
 * Event-driven quality assurance system that validates execution
 * in real-time with <100ms latency.
 *
 * Core capabilities:
 * - Event-driven QA triggers
 * - Inline validation during execution
 * - Vector-based semantic checking
 * - Automatic remediation
 */

import { QAEvent, QAValidationResult, QAAction } from '../types';
import { SchemaValidator } from '../validators/schema-validator';
import { SecurityValidator } from '../validators/security-validator';
import { ComplianceValidator } from '../validators/compliance-validator';
import { SemanticValidator } from '../validators/semantic-validator';

export interface QAEngineConfig {
  maxLatencyMs: number;
  parallelValidators: boolean;
  autoFixEnabled: boolean;
  circuitBreaker: {
    enabled: boolean;
    failureThreshold: number;
    timeoutMs: number;
  };
}

export interface ValidationContext {
  eventId: string;
  dimensionId?: string;
  data: unknown;
  metadata?: Record<string, unknown>;
}

export class RealtimeQAEngine {
  private validators: Map<string, BaseValidator>;
  private config: QAEngineConfig;
  private metricsCollector: QAMetricsCollector;
  private circuitState: Map<string, CircuitBreakerState>;

  constructor(config: QAEngineConfig) {
    this.config = config;
    this.validators = new Map();
    this.circuitState = new Map();
    this.metricsCollector = new QAMetricsCollector();

    // Initialize validators
    this.registerValidator('schema', new SchemaValidator());
    this.registerValidator('security', new SecurityValidator());
    this.registerValidator('compliance', new ComplianceValidator());
    this.registerValidator('semantic', new SemanticValidator());
  }

  /**
   * Main entry point: Validate based on QA event
   */
  async validate(
    qaEvent: QAEvent,
    context: ValidationContext
  ): Promise<QAValidationResult> {
    const startTime = Date.now();

    try {
      // Check circuit breaker
      if (this.isCircuitOpen(qaEvent.id)) {
        return this.createFallbackResult(qaEvent, 'circuit_open');
      }

      // Get validators for this event
      const validatorNames = qaEvent.validators || [];

      // Run validators (parallel if configured)
      const validationPromises = validatorNames.map(name =>
        this.runValidator(name, context, qaEvent.max_latency_ms)
      );

      const results = this.config.parallelValidators
        ? await Promise.all(validationPromises)
        : await this.runSequential(validationPromises);

      // Aggregate results
      const aggregated = this.aggregateResults(results, qaEvent);

      // Record metrics
      const duration = Date.now() - startTime;
      this.metricsCollector.record({
        eventId: qaEvent.id,
        duration,
        passed: aggregated.passed,
        validatorCount: validatorNames.length
      });

      // Check latency SLA
      if (duration > this.config.maxLatencyMs) {
        console.warn(`QA latency exceeded: ${duration}ms > ${this.config.maxLatencyMs}ms`);
      }

      // Execute action based on result
      if (!aggregated.passed && qaEvent.block_on_fail) {
        await this.executeAction('block', aggregated, context);
      }

      // Attempt auto-fix if enabled and failed
      if (!aggregated.passed && this.config.autoFixEnabled) {
        const fixed = await this.attemptAutoFix(aggregated, context);
        if (fixed) {
          aggregated.passed = true;
          aggregated.autoFixed = true;
        }
      }

      return aggregated;

    } catch (error) {
      this.recordCircuitFailure(qaEvent.id);
      throw new QAEngineError(`Validation failed for ${qaEvent.id}`, error);
    }
  }

  /**
   * Inline validation - called during execution
   */
  async validateInline(
    data: unknown,
    validators: string[] = ['schema', 'security']
  ): Promise<{ pass: boolean; violations: string[] }> {
    const context: ValidationContext = {
      eventId: 'qa.inline_validation',
      data
    };

    const results = await Promise.all(
      validators.map(name => this.runValidator(name, context, 50))
    );

    const violations = results
      .filter(r => !r.passed)
      .flatMap(r => r.violations || []);

    return {
      pass: violations.length === 0,
      violations
    };
  }

  /**
   * Pre-execution check - fast validation before running tool
   */
  async preExecutionCheck(
    toolName: string,
    params: unknown
  ): Promise<boolean> {
    const context: ValidationContext = {
      eventId: 'qa.pre_execution_check',
      data: { toolName, params }
    };

    const result = await this.validateInline(params, ['schema', 'security']);
    return result.pass;
  }

  /**
   * Post-execution check - comprehensive validation after completion
   */
  async postExecutionCheck(
    output: unknown,
    metadata?: Record<string, unknown>
  ): Promise<QAValidationResult> {
    const context: ValidationContext = {
      eventId: 'qa.post_execution_check',
      data: output,
      metadata
    };

    const qaEvent: QAEvent = {
      id: 'qa.post_execution_check',
      name: 'Post-Execution QA Check',
      validators: ['compliance', 'semantic'],
      max_latency_ms: 200,
      block_on_fail: false,
      priority: 'high'
    };

    return this.validate(qaEvent, context);
  }

  // Private methods

  private registerValidator(name: string, validator: BaseValidator): void {
    this.validators.set(name, validator);
  }

  private async runValidator(
    name: string,
    context: ValidationContext,
    timeoutMs?: number
  ): Promise<ValidationResult> {
    const validator = this.validators.get(name);
    if (!validator) {
      throw new Error(`Validator not found: ${name}`);
    }

    const timeout = timeoutMs || this.config.maxLatencyMs;

    return Promise.race([
      validator.validate(context),
      this.createTimeoutPromise(timeout, name)
    ]);
  }

  private async runSequential(
    promises: Promise<ValidationResult>[]
  ): Promise<ValidationResult[]> {
    const results: ValidationResult[] = [];
    for (const promise of promises) {
      results.push(await promise);
    }
    return results;
  }

  private aggregateResults(
    results: ValidationResult[],
    qaEvent: QAEvent
  ): QAValidationResult {
    const failures = results.filter(r => !r.passed);

    return {
      eventId: qaEvent.id,
      passed: failures.length === 0,
      failures: failures.map(f => ({
        validator: f.validatorName,
        violations: f.violations || [],
        severity: f.severity || 'medium'
      })),
      timestamp: new Date().toISOString(),
      metadata: {
        totalValidators: results.length,
        failedValidators: failures.length
      }
    };
  }

  private async executeAction(
    action: 'block' | 'warn' | 'auto_fix',
    result: QAValidationResult,
    context: ValidationContext
  ): Promise<void> {
    switch (action) {
      case 'block':
        throw new QABlockError('Execution blocked by QA validation', result);
      case 'warn':
        console.warn('QA validation warning:', result);
        break;
      case 'auto_fix':
        await this.attemptAutoFix(result, context);
        break;
    }
  }

  private async attemptAutoFix(
    result: QAValidationResult,
    context: ValidationContext
  ): Promise<boolean> {
    // Implementation depends on specific validators
    // Each validator can provide fix suggestions
    return false; // Placeholder
  }

  private createTimeoutPromise(
    timeoutMs: number,
    validatorName: string
  ): Promise<ValidationResult> {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Validator ${validatorName} timed out after ${timeoutMs}ms`));
      }, timeoutMs);
    });
  }

  private createFallbackResult(
    qaEvent: QAEvent,
    reason: string
  ): QAValidationResult {
    return {
      eventId: qaEvent.id,
      passed: false,
      failures: [{ validator: 'engine', violations: [reason], severity: 'high' }],
      timestamp: new Date().toISOString(),
      metadata: { fallback: true }
    };
  }

  // Circuit breaker

  private isCircuitOpen(eventId: string): boolean {
    const state = this.circuitState.get(eventId);
    if (!state || !this.config.circuitBreaker.enabled) return false;

    if (state.failures >= this.config.circuitBreaker.failureThreshold) {
      const timeSinceOpen = Date.now() - state.lastFailure;
      return timeSinceOpen < this.config.circuitBreaker.timeoutMs;
    }

    return false;
  }

  private recordCircuitFailure(eventId: string): void {
    if (!this.config.circuitBreaker.enabled) return;

    const state = this.circuitState.get(eventId) || { failures: 0, lastFailure: 0 };
    state.failures += 1;
    state.lastFailure = Date.now();
    this.circuitState.set(eventId, state);
  }
}

// Supporting types and classes

interface BaseValidator {
  validate(context: ValidationContext): Promise<ValidationResult>;
}

interface ValidationResult {
  validatorName: string;
  passed: boolean;
  violations?: string[];
  severity?: 'low' | 'medium' | 'high' | 'critical';
  suggestions?: string[];
}

interface CircuitBreakerState {
  failures: number;
  lastFailure: number;
}

class QAMetricsCollector {
  private metrics: QAMetric[] = [];

  record(metric: QAMetric): void {
    this.metrics.push(metric);
    // TODO: Export to monitoring system
  }

  getMetrics(): QAMetric[] {
    return this.metrics;
  }
}

interface QAMetric {
  eventId: string;
  duration: number;
  passed: boolean;
  validatorCount: number;
}

export class QAEngineError extends Error {
  constructor(message: string, public cause?: unknown) {
    super(message);
    this.name = 'QAEngineError';
  }
}

export class QABlockError extends Error {
  constructor(message: string, public validationResult: QAValidationResult) {
    super(message);
    this.name = 'QABlockError';
  }
}

// Usage example
/*
const engine = new RealtimeQAEngine({
  maxLatencyMs: 150,
  parallelValidators: true,
  autoFixEnabled: true,
  circuitBreaker: { enabled: true, failureThreshold: 5, timeoutMs: 500 }
});

// Pre-execution
const canExecute = await engine.preExecutionCheck('deployAgent', { agentId: 'qa-01' });

// Inline validation
const inlineResult = await engine.validateInline(outputData);

// Post-execution
const postResult = await engine.postExecutionCheck(finalOutput);
*/
