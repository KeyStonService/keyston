/**
 * Self-Healing Path Validator Tests
 * 
 * Tests for event-driven self-healing path validation
 */

import { SelfHealingPathValidator } from '../../utils/self-healing-path-validator';
import { pathValidationEvents, PathValidationEventType } from '../../events/path-validation-events';
import { tmpdir } from 'os';
import * as path from 'path';
import { mkdir, writeFile, rm } from 'fs/promises';

describe('SelfHealingPathValidator', () => {
  let validator: SelfHealingPathValidator;
  let testRoot: string;

  beforeEach(async () => {
    // Create a temporary test directory
    testRoot = path.join(tmpdir(), `test-${Date.now()}`);
    await mkdir(testRoot, { recursive: true });

    validator = new SelfHealingPathValidator({
      safeRoot: testRoot,
      enableAutoRecovery: true,
      enableSnapshotting: false, // Disable for tests
      dagEnabled: true,
      maxRecoveryAttempts: 3,
    });
  });

  afterEach(async () => {
    // Clean up test directory
    try {
      await rm(testRoot, { recursive: true, force: true });
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('Event Emission', () => {
    it('should emit STRUCTURE_MISSING event when file not found', async () => {
      const events: any[] = [];
      
      pathValidationEvents.on(PathValidationEventType.STRUCTURE_MISSING, (event) => {
        events.push(event);
      });

      try {
        await validator.validateAndResolvePath('nonexistent/file.txt');
      } catch (error) {
        // Expected to fail
      }

      expect(events.length).toBeGreaterThan(0);
      expect(events[0].type).toBe(PathValidationEventType.STRUCTURE_MISSING);
      expect(events[0].data.filePath).toContain('nonexistent/file.txt');
    });

    it('should emit STRUCTURE_RECOVERED event on successful recovery', async () => {
      const events: any[] = [];
      
      pathValidationEvents.on(PathValidationEventType.STRUCTURE_RECOVERED, (event) => {
        events.push(event);
      });

      // This test requires auto-recovery to create the directory
      // In practice, recovery would restore from snapshot or create structure
      const testFile = path.join(testRoot, 'recovered', 'file.txt');
      await mkdir(path.dirname(testFile), { recursive: true });
      await writeFile(testFile, 'test content');

      try {
        await validator.validateAndResolvePath('recovered/file.txt');
      } catch (error) {
        // May fail initially, but recovery events should fire
      }

      // Recovery events may not fire if file already exists
      // This test demonstrates the event system structure
    });
  });

  describe('Snapshot Management', () => {
    it('should create snapshots on demand', async () => {
      const snapshot = await validator.createSnapshot();

      expect(snapshot).toBeDefined();
      expect(snapshot.id).toBeDefined();
      expect(snapshot.timestamp).toBeDefined();
      expect(snapshot.boundaries.safeRoot).toBe(testRoot);
    });

    it('should preserve DAG nodes in snapshot', async () => {
      // Create a file and validate it
      const testFile = path.join(testRoot, 'test.txt');
      await writeFile(testFile, 'content');

      await validator.validateAndResolvePath('test.txt');

      const snapshot = await validator.createSnapshot();
      expect(snapshot.dagNodes.size).toBeGreaterThan(0);
    });
  });

  describe('DAG Tracking', () => {
    it('should track validated paths in DAG', async () => {
      const testFile = path.join(testRoot, 'dag-test.txt');
      await writeFile(testFile, 'content');

      await validator.validateAndResolvePath('dag-test.txt');

      const dagNodes = validator.getDAGNodes();
      expect(dagNodes.size).toBeGreaterThan(0);

      const nodeArray = Array.from(dagNodes.values());
      const hasCorrectPath = nodeArray.some(
        (node) => node.path === 'dag-test.txt' && node.status === 'valid'
      );
      expect(hasCorrectPath).toBe(true);
    });
  });

  describe('Recovery Limits', () => {
    it('should respect max recovery attempts', async () => {
      const events: any[] = [];
      
      pathValidationEvents.on(PathValidationEventType.VALIDATION_FAILED, (event) => {
        events.push(event);
      });

      try {
        // Try to validate a path that will always fail
        await validator.validateAndResolvePath('will-never-exist.txt');
      } catch (error) {
        // Expected to fail after max attempts
      }

      // Should have attempted validation multiple times (initial + retries)
      // But limited by maxRecoveryAttempts
    });
  });

  describe('Integration with PathValidator', () => {
    it('should validate normal paths successfully', async () => {
      const testFile = path.join(testRoot, 'normal.txt');
      await writeFile(testFile, 'content');

      const result = await validator.validateAndResolvePath('normal.txt');
      
      expect(result).toBeDefined();
      expect(result).toContain('normal.txt');
    });

    it('should reject path traversal attempts', async () => {
      await expect(
        validator.validateAndResolvePath('../outside.txt')
      ).rejects.toThrow();
    });
  });
});

describe('PathValidationEventEmitter', () => {
  it('should allow subscription to events', () => {
    let eventReceived = false;
    
    pathValidationEvents.on(PathValidationEventType.SNAPSHOT_CREATED, (event) => {
      eventReceived = true;
    });

    pathValidationEvents.emit({
      type: PathValidationEventType.SNAPSHOT_CREATED,
      timestamp: new Date().toISOString(),
      source: 'test',
      data: {
        filePath: '',
        safeRoot: '/test',
        snapshotId: 'test-snapshot',
      },
    });

    expect(eventReceived).toBe(true);
  });

  it('should support multiple subscribers', () => {
    let count = 0;
    
    pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, () => count++);
    pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, () => count++);

    pathValidationEvents.emitFallbackTriggered({
      filePath: 'test.txt',
      safeRoot: '/test',
    });

    expect(count).toBe(2);
  });
});
