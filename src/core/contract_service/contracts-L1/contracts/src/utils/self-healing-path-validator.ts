/**
 * Self-Healing Path Validator
 *
 * Extends path validation with event-driven self-healing capabilities:
 * - Structure snapshots for state preservation
 * - Automatic recovery on validation failures
 * - DAG-based dependency tracking
 * - Integration with governance policies
 */

import { createHash } from 'crypto';
import { realpath, mkdir, access } from 'fs/promises';
import * as path from 'path';

import {
  PathValidationEventType,
  PathValidationEventData,
  StructureSnapshot,
  DAGNodeState,
  pathValidationEvents,
} from '../events/path-validation-events';

import { PathValidator, PathValidationError, PathValidatorConfig } from './path-validator';

export interface SelfHealingConfig extends Partial<PathValidatorConfig> {
  enableAutoRecovery?: boolean;
  enableSnapshotting?: boolean;
  snapshotInterval?: number;
  maxRecoveryAttempts?: number;
  dagEnabled?: boolean;
}

/**
 * Self-healing path validator with event-driven recovery
 */
export class SelfHealingPathValidator extends PathValidator {
  protected config: SelfHealingConfig;
  private currentSnapshot: StructureSnapshot | null = null;
  private dagNodes: Map<string, DAGNodeState> = new Map();
  private recoveryAttempts: Map<string, number> = new Map();
  private snapshotIntervalId: NodeJS.Timeout | null = null;
  private logger: Console = console; // Can be replaced with structured logger

  constructor(config: SelfHealingConfig = {}) {
    super(config);
    this.config = {
      enableAutoRecovery: config.enableAutoRecovery ?? true,
      enableSnapshotting: config.enableSnapshotting ?? true,
      snapshotInterval: config.snapshotInterval ?? 60000, // 1 minute
      maxRecoveryAttempts: config.maxRecoveryAttempts ?? 3,
      dagEnabled: config.dagEnabled ?? true,
      ...config,
    };

    // Initialize event listeners for self-healing
    this.initializeEventListeners();

    // Start periodic snapshotting if enabled
    if (this.config.enableSnapshotting) {
      this.startPeriodicSnapshotting();
    }
  }

  /**
   * Initialize event listeners for self-healing actions
   */
  private initializeEventListeners(): void {
    // Listen for structure missing events and attempt recovery
    pathValidationEvents.on(PathValidationEventType.STRUCTURE_MISSING, (event) => {
      if (this.config.enableAutoRecovery) {
        this.handleStructureMissing(event.data).catch((error) => {
          this.logger.error('Error handling structure missing event:', error);
        });
      }
    });

    // Listen for DAG node missing events
    pathValidationEvents.on(PathValidationEventType.DAG_NODE_MISSING, (event) => {
      if (this.config.dagEnabled) {
        this.handleDAGNodeMissing(event.data).catch((error) => {
          this.logger.error('Error handling DAG node missing event:', error);
        });
      }
    });
  }

  /**
   * Validate and resolve path with self-healing capabilities
   */
  async validateAndResolvePath(filePath: string): Promise<string> {
    const attemptKey = filePath;
    const attempts = this.recoveryAttempts.get(attemptKey) || 0;
    const safeRoot = this.config.safeRoot || process.cwd();
    const normalizedInput = path.normalize(filePath);

    if (!normalizedInput.includes('..')) {
      try {
        const candidatePath = path.resolve(safeRoot, normalizedInput);
        await access(candidatePath);
      } catch {
        pathValidationEvents.emitStructureMissing({
          filePath,
          safeRoot,
          error: 'ENOENT',
        });
      }
    }

    try {
      // Attempt normal validation
      const resolvedPath = await super.validateAndResolvePath(filePath);

      // Update DAG node if enabled
      if (this.config.dagEnabled) {
        await this.updateDAGNode(filePath, resolvedPath, 'valid');
      }

      // Reset recovery attempts on success
      this.recoveryAttempts.delete(attemptKey);

      return resolvedPath;
    } catch (error) {
      // Emit validation failed event
      const eventData: PathValidationEventData = {
        filePath,
        safeRoot,
        error: error instanceof Error ? error.message : String(error),
        errorCode: error instanceof PathValidationError ? error.code : undefined,
      };

      pathValidationEvents.emitValidationFailed(eventData);

      // Emit structure missing only for missing/invalid structure to drive recovery flows
      const isStructureMissing =
        (error instanceof Error &&
          'code' in error &&
          (error as Error & { code: string }).code === 'ENOENT') ||
        error instanceof PathValidationError;

      if (isStructureMissing) {
        pathValidationEvents.emitStructureMissing(eventData);

        // Attempt recovery if enabled and within retry limits
        if (this.config.enableAutoRecovery && attempts < (this.config.maxRecoveryAttempts || 3)) {
          this.recoveryAttempts.set(attemptKey, attempts + 1);

          try {
            const recovered = await this.attemptStructureRecovery(filePath, eventData);
            if (recovered) {
              // Retry validation after recovery
              return await this.validateAndResolvePath(filePath);
            }
          } catch (recoveryError) {
            this.logger.error('Recovery attempt failed:', recoveryError);
          }
        }
      }

      // Re-throw original error if recovery failed or not attempted
      throw error;
    }
  }

  /**
   * Attempt to recover missing structure
   */
  private async attemptStructureRecovery(
    filePath: string,
    eventData: PathValidationEventData
  ): Promise<boolean> {
    try {
      // Try to recover from snapshot
      if (this.currentSnapshot && this.config.enableSnapshotting) {
        const recoveredPath = await this.recoverFromSnapshot(filePath);
        if (recoveredPath) {
          pathValidationEvents.emitStructureRecovered({
            ...eventData,
            resolvedPath: recoveredPath,
            recoverySuccessful: true,
          });
          return true;
        }
      }

      // Try to create missing directory structure
      const resolvedDir = path.dirname(
        path.resolve(this.config.safeRoot || process.cwd(), filePath)
      );
      await mkdir(resolvedDir, { recursive: true });

      pathValidationEvents.emitStructureRecovered({
        ...eventData,
        resolvedPath: resolvedDir,
        recoverySuccessful: true,
      });

      return true;
    } catch (error) {
      pathValidationEvents.emitStructureRecovered({
        ...eventData,
        recoverySuccessful: false,
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }

  /**
   * Handle structure missing event
   */
  private async handleStructureMissing(data: PathValidationEventData): Promise<void> {
    this.logger.log(`Handling structure missing for: ${data.filePath}`);
    // Additional recovery logic can be added here
  }

  /**
   * Handle DAG node missing event
   */
  private async handleDAGNodeMissing(data: PathValidationEventData): Promise<void> {
    if (!data.dagNodeId) {
      return;
    }

    try {
      // Attempt to rebuild DAG node from snapshot or governance rules
      const rebuilt = await this.rebuildDAGNode(data.dagNodeId, data.filePath);

      if (rebuilt) {
        pathValidationEvents.emitDAGNodeRebuilt({
          ...data,
          recoverySuccessful: true,
        });
      }
    } catch (error) {
      this.logger.error(`Failed to rebuild DAG node ${data.dagNodeId}:`, error);
    }
  }

  /**
   * Create a structure snapshot
   */
  async createSnapshot(): Promise<StructureSnapshot> {
    const snapshotId = createHash('sha256')
      .update(`${Date.now()}-${Math.random()}`)
      .digest('hex')
      .substring(0, 16);

    const snapshot: StructureSnapshot = {
      id: snapshotId,
      timestamp: new Date().toISOString(),
      pathMappings: new Map(),
      boundaries: {
        safeRoot: this.config.safeRoot || process.cwd(),
        allowedPrefixes: this.config.allowedAbsolutePrefixes || [],
      },
      dagNodes: new Map(this.dagNodes),
      metadata: {
        dagEnabled: this.config.dagEnabled,
        autoRecoveryEnabled: this.config.enableAutoRecovery,
      },
    };

    this.currentSnapshot = snapshot;

    pathValidationEvents.emit({
      type: PathValidationEventType.SNAPSHOT_CREATED,
      timestamp: new Date().toISOString(),
      source: 'SelfHealingPathValidator',
      data: {
        filePath: '',
        safeRoot: snapshot.boundaries.safeRoot,
        snapshotId,
      },
    });

    return snapshot;
  }

  /**
   * Recover path from snapshot
   */
  private async recoverFromSnapshot(filePath: string): Promise<string | null> {
    if (!this.currentSnapshot) {
      return null;
    }

    // Check if path exists in snapshot
    const mapping = this.currentSnapshot.pathMappings.get(filePath);
    if (mapping) {
      return mapping;
    }

    // Check DAG nodes for related paths
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    for (const [, node] of this.currentSnapshot.dagNodes) {
      if (node.path === filePath && node.status === 'valid') {
        return node.canonicalPath;
      }
    }

    return null;
  }

  /**
   * Update or create a DAG node
   */
  private async updateDAGNode(
    filePath: string,
    canonicalPath: string,
    status: DAGNodeState['status']
  ): Promise<void> {
    const nodeId = createHash('sha256').update(filePath).digest('hex').substring(0, 16);

    const node: DAGNodeState = {
      nodeId,
      path: filePath,
      canonicalPath,
      status,
      dependencies: [],
      lastValidated: new Date().toISOString(),
    };

    this.dagNodes.set(nodeId, node);
  }

  /**
   * Rebuild a DAG node
   */
  private async rebuildDAGNode(nodeId: string, filePath: string): Promise<boolean> {
    try {
      // Check if node exists in snapshot
      if (this.currentSnapshot?.dagNodes.has(nodeId)) {
        const snapshotNode = this.currentSnapshot.dagNodes.get(nodeId)!;
        this.dagNodes.set(nodeId, {
          ...snapshotNode,
          status: 'recovered',
          lastValidated: new Date().toISOString(),
        });
        return true;
      }

      // Attempt to create new node from current state
      const safeRoot = this.config.safeRoot || process.cwd();
      const resolvedPath = path.resolve(safeRoot, filePath);

      try {
        const canonicalPath = await realpath(resolvedPath);
        await this.updateDAGNode(filePath, canonicalPath, 'recovered');
        return true;
      } catch {
        // If realpath fails, use normalized path
        const normalizedPath = path.normalize(resolvedPath);
        await this.updateDAGNode(filePath, normalizedPath, 'recovered');
        return true;
      }
    } catch (error) {
      this.logger.error(`Failed to rebuild DAG node ${nodeId}:`, error);
      return false;
    }
  }

  /**
   * Start periodic snapshotting
   */
  private startPeriodicSnapshotting(): void {
    if (this.snapshotIntervalId) {
      clearInterval(this.snapshotIntervalId);
    }

    this.snapshotIntervalId = setInterval(() => {
      this.createSnapshot().catch((error) => {
        this.logger.error('Error creating periodic snapshot:', error);
      });
    }, this.config.snapshotInterval || 60000);
  }

  /**
   * Stop periodic snapshotting and cleanup resources
   */
  dispose(): void {
    if (this.snapshotIntervalId) {
      clearInterval(this.snapshotIntervalId);
      this.snapshotIntervalId = null;
    }
  }

  /**
   * Get current snapshot
   */
  getSnapshot(): StructureSnapshot | null {
    return this.currentSnapshot;
  }

  /**
   * Get DAG nodes
   */
  getDAGNodes(): Map<string, DAGNodeState> {
    return new Map(this.dagNodes);
  }
}
