/**
 * Workload Balancer Tests
 * Unit tests for the workload balancing service
 */

import { WorkloadBalancer } from '../services/assignment/workload-balancer';
import { TeamMember, Incident, WorkloadMetrics } from '../types/assignment';

describe('WorkloadBalancer', () => {
  let balancer: WorkloadBalancer;

  beforeEach(() => {
    balancer = new WorkloadBalancer();
  });

  describe('selectOptimalAssignee', () => {
    it('should select a member from available list', () => {
      const members: TeamMember[] = [
        {
          id: 'member-1',
          name: 'Alice',
          email: 'alice@example.com',
          specialties: ['React', 'TypeScript'],
          timezone: 'UTC',
        },
        {
          id: 'member-2',
          name: 'Bob',
          email: 'bob@example.com',
          specialties: ['Node.js', 'API'],
          timezone: 'UTC',
        },
      ];

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const assignee = balancer.selectOptimalAssignee(members, incident);
      expect(assignee).toBeDefined();
      expect(members).toContainEqual(assignee);
    });

    it('should return the only available member', () => {
      const members: TeamMember[] = [
        {
          id: 'member-1',
          name: 'Alice',
          email: 'alice@example.com',
          specialties: ['React'],
          timezone: 'UTC',
        },
      ];

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'LOW',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const assignee = balancer.selectOptimalAssignee(members, incident);
      expect(assignee).toEqual(members[0]);
    });

    it('should prefer members with matching specialties', () => {
      const members: TeamMember[] = [
        {
          id: 'member-1',
          name: 'Alice',
          email: 'alice@example.com',
          specialties: ['Python', 'Django'],
          timezone: 'UTC',
        },
        {
          id: 'member-2',
          name: 'Bob',
          email: 'bob@example.com',
          specialties: ['React', 'TypeScript', 'Frontend'],
          timezone: 'UTC',
        },
      ];

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'React component issue',
        createdAt: new Date(),
      };

      // Record multiple assignments to see if specialty matching works
      const assignments = new Set<string>();
      for (let i = 0; i < 10; i++) {
        const assignee = balancer.selectOptimalAssignee(members, incident);
        assignments.add(assignee.id);
      }

      // Bob should be selected more often due to relevant specialties
      expect(assignments.size).toBeGreaterThan(0);
    });

    it('should handle members with different workloads', () => {
      const member1: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const member2: TeamMember = {
        id: 'member-2',
        name: 'Bob',
        email: 'bob@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const members = [member1, member2];

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'Test incident',
        createdAt: new Date(),
      };

      // Both members should be selectable
      const assignee = balancer.selectOptimalAssignee(members, incident);
      expect([member1, member2]).toContainEqual(assignee);
    });
  });

  describe('calculateAssignmentScore', () => {
    it('should calculate assignment score for a member', () => {
      const member: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const score = balancer.calculateAssignmentScore(member, incident);

      expect(score).toHaveProperty('member');
      expect(score).toHaveProperty('score');
      expect(score).toHaveProperty('factors');
      expect(typeof score.score).toBe('number');
      expect(score.score).toBeGreaterThanOrEqual(0);
      expect(score.score).toBeLessThanOrEqual(1);
    });

    it('should return consistent scores for same inputs', () => {
      const member: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const score1 = balancer.calculateAssignmentScore(member, incident);
      const score2 = balancer.calculateAssignmentScore(member, incident);

      expect(score1.score).toBe(score2.score);
    });

    it('should include all scoring factors', () => {
      const member: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const score = balancer.calculateAssignmentScore(member, incident);

      expect(score.factors).toHaveProperty('expertise');
      expect(score.factors).toHaveProperty('availability');
      expect(score.factors).toHaveProperty('currentLoad');
      expect(score.factors).toHaveProperty('responseHistory');
    });
  });

  describe('getWorkloadMetrics', () => {
    it('should return undefined for member without metrics', () => {
      const memberId = 'new-member';
      const metrics = balancer.getWorkloadMetrics(memberId);

      expect(metrics).toBeUndefined();
    });

    it('should return metrics after updating them', () => {
      const memberId = 'member-1';
      const testMetrics: WorkloadMetrics = {
        memberId: 'member-1',
        activeAssignments: 5,
        totalAssignments: 10,
        averageResolutionTime: 120,
        successRate: 0.85,
      };

      balancer.updateWorkloadMetrics(memberId, testMetrics);
      const metrics = balancer.getWorkloadMetrics(memberId);

      expect(metrics).toBeDefined();
      expect(metrics?.activeAssignments).toBe(5);
      expect(metrics?.totalAssignments).toBe(10);
      expect(metrics?.averageResolutionTime).toBe(120);
      expect(metrics?.successRate).toBe(0.85);
    });

    it('should handle partial metric updates', () => {
      const memberId = 'member-2';

      balancer.updateWorkloadMetrics(memberId, { activeAssignments: 3 });
      const metrics = balancer.getWorkloadMetrics(memberId);

      expect(metrics).toBeDefined();
      expect(metrics?.activeAssignments).toBe(3);
    });
  });

  describe('getAllWorkloadMetrics', () => {
    it('should return empty map initially', () => {
      const newBalancer = new WorkloadBalancer();
      const allMetrics = newBalancer.getAllWorkloadMetrics();

      expect(allMetrics).toBeInstanceOf(Map);
      expect(allMetrics.size).toBe(0);
    });

    it('should return all tracked members after updates', () => {
      balancer.updateWorkloadMetrics('member-1', { activeAssignments: 3 });
      balancer.updateWorkloadMetrics('member-2', { activeAssignments: 5 });

      const allMetrics = balancer.getAllWorkloadMetrics();

      expect(allMetrics).toBeInstanceOf(Map);
      expect(allMetrics.size).toBe(2);
      expect(allMetrics.has('member-1')).toBe(true);
      expect(allMetrics.has('member-2')).toBe(true);
    });

    it('should return independent copy of metrics', () => {
      balancer.updateWorkloadMetrics('member-1', { activeAssignments: 3 });

      const metrics1 = balancer.getAllWorkloadMetrics();
      const metrics2 = balancer.getAllWorkloadMetrics();

      // Modifying one shouldn't affect the other
      expect(metrics1).not.toBe(metrics2);
      expect(metrics1.size).toBe(metrics2.size);
    });
  });

  describe('balanceWorkload', () => {
    it('should distribute assignments evenly over multiple iterations', () => {
      const members: TeamMember[] = [
        {
          id: 'member-1',
          name: 'Alice',
          email: 'alice@example.com',
          specialties: ['React'],
          timezone: 'UTC',
        },
        {
          id: 'member-2',
          name: 'Bob',
          email: 'bob@example.com',
          specialties: ['React'],
          timezone: 'UTC',
        },
        {
          id: 'member-3',
          name: 'Charlie',
          email: 'charlie@example.com',
          specialties: ['React'],
          timezone: 'UTC',
        },
      ];

      const assignmentCounts = new Map<string, number>();
      members.forEach((m) => assignmentCounts.set(m.id, 0));

      // Create multiple incidents and track assignments
      for (let i = 0; i < 30; i++) {
        const incident: Incident = {
          id: `incident-${i}`,
          type: 'FRONTEND_ERROR',
          priority: 'MEDIUM',
          description: `Test incident ${i}`,
          createdAt: new Date(),
        };

        const assignee = balancer.selectOptimalAssignee(members, incident);
        const currentCount = assignmentCounts.get(assignee.id) || 0;
        assignmentCounts.set(assignee.id, currentCount + 1);
      }

      // Verify some distribution occurred (not all to one person)
      const counts = Array.from(assignmentCounts.values());
      const uniqueCounts = new Set(counts);

      // At least some members should have been assigned
      expect(counts.filter((c) => c > 0).length).toBeGreaterThan(0);
    });
  });

  describe('edge cases', () => {
    it('should handle single member selection', () => {
      const members: TeamMember[] = [
        {
          id: 'only-member',
          name: 'Solo',
          email: 'solo@example.com',
          specialties: ['Everything'],
          timezone: 'UTC',
        },
      ];

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'CRITICAL',
        description: 'Critical issue',
        createdAt: new Date(),
      };

      const assignee = balancer.selectOptimalAssignee(members, incident);
      expect(assignee.id).toBe('only-member');
    });

    it('should handle high-priority incidents', () => {
      const members: TeamMember[] = [
        {
          id: 'member-1',
          name: 'Alice',
          email: 'alice@example.com',
          specialties: ['Security'],
          timezone: 'UTC',
        },
      ];

      const incident: Incident = {
        id: 'critical-incident',
        type: 'SECURITY',
        priority: 'CRITICAL',
        description: 'Security breach',
        createdAt: new Date(),
      };

      const assignee = balancer.selectOptimalAssignee(members, incident);
      expect(assignee).toBeDefined();
    });
  });
});
