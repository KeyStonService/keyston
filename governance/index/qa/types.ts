/**
 * Realtime QA Engine Type Definitions
 */

export interface QAEvent {
  id: string;
  name: string;
  validators: ValidatorType[];
  max_latency_ms: number;
  block_on_fail: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
  trigger?: string;
  emit_to?: string[];
  auto_fix_enabled?: boolean;
}

export type ValidatorType = 'schema' | 'security' | 'compliance' | 'semantic';

export type Severity = 'low' | 'medium' | 'high' | 'critical';

export interface ValidationContext {
  eventId: string;
  dimensionId?: string;
  data: unknown;
  metadata?: Record<string, unknown>;
}

export interface ValidationResult {
  validatorName: string;
  passed: boolean;
  violations: string[];
  severity?: Severity;
  suggestions?: string[];
  metadata?: Record<string, unknown>;
}

export interface QAValidationResult {
  eventId: string;
  passed: boolean;
  failures: QAFailure[];
  timestamp: string;
  metadata?: Record<string, unknown>;
  autoFixed?: boolean;
}

export interface QAFailure {
  validator: string;
  violations: string[];
  severity: Severity;
}

export type QAAction = 'block' | 'warn' | 'auto_fix';

export interface BaseValidator {
  validate(context: ValidationContext): Promise<ValidationResult>;
}

export interface QAEngineConfig {
  maxLatencyMs: number;
  parallelValidators: boolean;
  autoFixEnabled: boolean;
  circuitBreaker: CircuitBreakerConfig;
}

export interface CircuitBreakerConfig {
  enabled: boolean;
  failureThreshold: number;
  timeoutMs: number;
}

export interface QAMetric {
  eventId: string;
  duration: number;
  passed: boolean;
  validatorCount: number;
  timestamp?: string;
}

export interface QARulesVectorIndex {
  id: string;
  name: string;
  description: string;
  version: string;
  model: {
    name: string;
    dimensions: number;
    similarity_metric: string;
  };
  rules: QARule[];
  semantic_search: {
    enabled: boolean;
    threshold: number;
    max_results: number;
    fallback_to_keyword: boolean;
  };
  auto_fix_config: {
    enabled: boolean;
    confidence_threshold: number;
    max_attempts: number;
    require_approval: {
      critical: boolean;
      high: boolean;
      medium: boolean;
      low: boolean;
    };
  };
}

export interface QARule {
  id: string;
  category: 'security' | 'compliance' | 'tech_debt' | 'architecture' | 'performance' | 'testing';
  pattern: string;
  description: string;
  severity: Severity;
  action: string;
  auto_fix?: string;
  embedding: number[] | null;
  examples?: string[];
}

export interface SemanticMatch {
  rule: QARule;
  similarity: number;
}

export interface QAEventsRegistry {
  id: string;
  name: string;
  description: string;
  version: string;
  events: QAEvent[];
  triggers_map: Record<string, string[]>;
  validators_config: Record<ValidatorType, ValidatorConfig>;
  actions: Record<QAAction, ActionConfig>;
  metrics: {
    track: string[];
    alert_on: Record<string, number | string>;
  };
}

export interface ValidatorConfig {
  engine?: string;
  checks?: string[];
  frameworks?: string[];
  model?: string;
  threshold?: number;
  fail_mode: 'block' | 'warn' | 'warn_critical_block';
  timeout_ms: number;
}

export interface ActionConfig {
  description: string;
  emit_event?: string;
  notify?: string[];
  log_level?: string;
  max_attempts?: number;
  fallback?: QAAction;
}

export interface QADimensionConfig {
  id: string;
  name: string;
  qa_required: boolean;
  qa_validators: ValidatorType[];
  qa_block_on_fail: boolean;
  qa_events: string[];
  rationale: string;
}

// Errors

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

export class ComplianceError extends Error {
  constructor(message: string, public violations: QAFailure[]) {
    super(message);
    this.name = 'ComplianceError';
  }
}

// Agent Integration Types

export interface AgentContext {
  agentId: string;
  dimensionId?: string;
  payload: Record<string, unknown>;
  qa_required?: boolean;
  metadata?: Record<string, unknown>;
}

export interface AgentInsight {
  title: string;
  description: string;
  signal: 'info' | 'warn' | 'error';
  data?: Record<string, unknown>;
}
