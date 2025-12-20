/**
 * Self-Healing Governance Integration
 *
 * Connects the self-healing path validation system with governance policies,
 * attestation, and monitoring systems.
 */

import {
  pathValidationEvents,
  PathValidationEventType,
  PathValidationEvent,
} from '../events/path-validation-events';

export interface SelfHealingMetrics {
  totalValidations: number;
  totalFailures: number;
  totalRecoveries: number;
  successfulRecoveries: number;
  failedRecoveries: number;
  snapshotsCreated: number;
  dagNodesRebuilt: number;
  lastEventTimestamp: string;
}

export interface SelfHealingAttestation {
  id: string;
  timestamp: string;
  eventType: PathValidationEventType;
  filePath: string;
  recoveryAttempted: boolean;
  recoverySuccessful: boolean;
  governanceCompliant: boolean;
  policyViolations: string[];
  attestation?: unknown;
}

/**
 * Governance integration for self-healing mechanisms
 */
export class SelfHealingGovernanceIntegration {
  private metrics: SelfHealingMetrics;
  private attestations: SelfHealingAttestation[] = [];

  constructor() {
    this.metrics = {
      totalValidations: 0,
      totalFailures: 0,
      totalRecoveries: 0,
      successfulRecoveries: 0,
      failedRecoveries: 0,
      snapshotsCreated: 0,
      dagNodesRebuilt: 0,
      lastEventTimestamp: new Date().toISOString(),
    };

    this.initializeEventListeners();
  }

  /**
   * Initialize event listeners for governance tracking
   */
  private initializeEventListeners(): void {
    // Track validation failures
    pathValidationEvents.on(PathValidationEventType.VALIDATION_FAILED, (event) => {
      this.metrics.totalValidations++;
      this.metrics.totalFailures++;
      this.metrics.lastEventTimestamp = event.timestamp;
      this.createAttestation(event);
    });

    // Track structure recoveries
    pathValidationEvents.on(PathValidationEventType.STRUCTURE_RECOVERED, (event) => {
      this.metrics.totalRecoveries++;
      if (event.data.recoverySuccessful) {
        this.metrics.successfulRecoveries++;
      } else {
        this.metrics.failedRecoveries++;
      }
      this.metrics.lastEventTimestamp = event.timestamp;
      this.createAttestation(event);
    });

    // Track snapshots
    pathValidationEvents.on(PathValidationEventType.SNAPSHOT_CREATED, (event) => {
      this.metrics.snapshotsCreated++;
      this.metrics.lastEventTimestamp = event.timestamp;
    });

    // Track DAG node rebuilds
    pathValidationEvents.on(PathValidationEventType.DAG_NODE_REBUILT, (event) => {
      this.metrics.dagNodesRebuilt++;
      this.metrics.lastEventTimestamp = event.timestamp;
      this.createAttestation(event);
    });

    // Track fallback triggers
    pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, (event) => {
      this.metrics.lastEventTimestamp = event.timestamp;
      this.createAttestation(event);
    });
  }

  /**
   * Create attestation for self-healing events
   */
  private async createAttestation(event: PathValidationEvent): Promise<void> {
    const attestation: SelfHealingAttestation = {
      id: `sh_${Date.now()}_${Math.random().toString(36).substring(7)}`,
      timestamp: event.timestamp,
      eventType: event.type,
      filePath: event.data.filePath,
      recoveryAttempted: event.data.recoveryAttempted || false,
      recoverySuccessful: event.data.recoverySuccessful || false,
      governanceCompliant: true, // Default to compliant
      policyViolations: [],
    };

    // Check governance compliance
    const violations = await this.checkGovernanceCompliance(event);
    if (violations.length > 0) {
      attestation.governanceCompliant = false;
      attestation.policyViolations = violations;
    }

    this.attestations.push(attestation);

    // Limit attestation history
    if (this.attestations.length > 1000) {
      this.attestations = this.attestations.slice(-1000);
    }
  }

  /**
   * Check if the event complies with governance policies
   */
  private async checkGovernanceCompliance(event: PathValidationEvent): Promise<string[]> {
    const violations: string[] = [];

    // Check if too many recovery attempts
    if (event.type === PathValidationEventType.STRUCTURE_RECOVERED) {
      const recentRecoveries = this.attestations.filter(
        (a) =>
          a.filePath === event.data.filePath &&
          a.eventType === PathValidationEventType.STRUCTURE_RECOVERED &&
          new Date(a.timestamp) > new Date(Date.now() - 60000) // Last minute
      );

      if (recentRecoveries.length > 5) {
        violations.push('EXCESSIVE_RECOVERY_ATTEMPTS');
      }
    }

    // Check for boundary violations
    if (event.type === PathValidationEventType.BOUNDARY_VIOLATION) {
      violations.push('PATH_BOUNDARY_VIOLATION');
    }

    // Check for failed recoveries
    if (event.data.recoveryAttempted && !event.data.recoverySuccessful) {
      violations.push('RECOVERY_FAILURE');
    }

    return violations;
  }

  /**
   * Get current metrics
   */
  getMetrics(): SelfHealingMetrics {
    return { ...this.metrics };
  }

  /**
   * Get attestations
   */
  getAttestations(limit = 100): SelfHealingAttestation[] {
    return this.attestations.slice(-limit);
  }

  /**
   * Get success rate
   */
  getSuccessRate(): number {
    if (this.metrics.totalRecoveries === 0) {
      return 0;
    }
    return this.metrics.successfulRecoveries / this.metrics.totalRecoveries;
  }

  /**
   * Export governance report
   */
  exportGovernanceReport(): string {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: this.metrics,
      successRate: this.getSuccessRate(),
      recentAttestations: this.getAttestations(50),
      policyCompliance: {
        totalEvents: this.attestations.length,
        compliantEvents: this.attestations.filter((a) => a.governanceCompliant).length,
        violations: this.attestations.filter((a) => !a.governanceCompliant).length,
      },
    };

    return JSON.stringify(report, null, 2);
  }
}

// Global governance integration instance
export const selfHealingGovernance = new SelfHealingGovernanceIntegration();
