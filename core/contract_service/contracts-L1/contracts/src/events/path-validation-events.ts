/**
 * Path Validation Events
 *
 * Event-driven structure completion and self-healing events
 * for path validation failures and recovery.
 */

export enum PathValidationEventType {
  VALIDATION_FAILED = 'path.validation.failed',
  STRUCTURE_MISSING = 'path.structure.missing',
  STRUCTURE_RECOVERED = 'path.structure.recovered',
  FALLBACK_TRIGGERED = 'path.fallback.triggered',
  BOUNDARY_VIOLATION = 'path.boundary.violation',
  SNAPSHOT_CREATED = 'path.snapshot.created',
  DAG_NODE_MISSING = 'path.dag.node.missing',
  DAG_NODE_REBUILT = 'path.dag.node.rebuilt',
}

export interface PathValidationEvent {
  type: PathValidationEventType;
  timestamp: string;
  source: string;
  data: PathValidationEventData;
  metadata?: Record<string, unknown>;
}

export interface PathValidationEventData {
  filePath: string;
  resolvedPath?: string;
  canonicalPath?: string;
  safeRoot: string;
  error?: string;
  errorCode?: string;
  recoveryAttempted?: boolean;
  recoverySuccessful?: boolean;
  snapshotId?: string;
  dagNodeId?: string;
}

export interface StructureSnapshot {
  id: string;
  timestamp: string;
  pathMappings: Map<string, string>;
  boundaries: {
    safeRoot: string;
    allowedPrefixes: string[];
  };
  dagNodes: Map<string, DAGNodeState>;
  metadata: Record<string, unknown>;
}

export interface DAGNodeState {
  nodeId: string;
  path: string;
  canonicalPath: string;
  status: 'valid' | 'missing' | 'invalid' | 'recovered';
  dependencies: string[];
  lastValidated: string;
  metadata?: Record<string, unknown>;
}

/**
 * Event emitter for path validation events
 */
export class PathValidationEventEmitter {
  private listeners: Map<PathValidationEventType, Array<(event: PathValidationEvent) => void>> =
    new Map();

  /**
   * Subscribe to a specific event type
   */
  on(eventType: PathValidationEventType, handler: (event: PathValidationEvent) => void): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(handler);
  }

  /**
   * Emit an event to all subscribed handlers
   */
  emit(event: PathValidationEvent): void {
    const handlers = this.listeners.get(event.type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(event);
        } catch (error) {
          console.error(`Error in event handler for ${event.type}:`, error);
        }
      });
    }
  }

  /**
   * Create and emit a validation failed event
   */
  emitValidationFailed(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.VALIDATION_FAILED,
      timestamp: new Date().toISOString(),
      source: 'PathValidator',
      data,
    });
  }

  /**
   * Create and emit a structure missing event
   */
  emitStructureMissing(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.STRUCTURE_MISSING,
      timestamp: new Date().toISOString(),
      source: 'PathValidator',
      data,
    });
  }

  /**
   * Create and emit a structure recovered event
   */
  emitStructureRecovered(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.STRUCTURE_RECOVERED,
      timestamp: new Date().toISOString(),
      source: 'PathValidator',
      data,
    });
  }

  /**
   * Create and emit a fallback triggered event
   */
  emitFallbackTriggered(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.FALLBACK_TRIGGERED,
      timestamp: new Date().toISOString(),
      source: 'PathValidator',
      data,
    });
  }

  /**
   * Create and emit a DAG node missing event
   */
  emitDAGNodeMissing(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.DAG_NODE_MISSING,
      timestamp: new Date().toISOString(),
      source: 'DAGEngine',
      data,
    });
  }

  /**
   * Create and emit a DAG node rebuilt event
   */
  emitDAGNodeRebuilt(data: PathValidationEventData): void {
    this.emit({
      type: PathValidationEventType.DAG_NODE_REBUILT,
      timestamp: new Date().toISOString(),
      source: 'DAGEngine',
      data,
    });
  }
}

// Global event emitter instance
export const pathValidationEvents = new PathValidationEventEmitter();
