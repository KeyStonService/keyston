/**
 * Auto Assignment Engine Tests
 * Unit tests for the auto-assignment engine service
 */

import { AutoAssignmentEngine } from '../services/assignment/auto-assignment-engine';
import { Incident, TeamMember, ProblemType } from '../types/assignment';

describe('AutoAssignmentEngine', () => {
  let engine: AutoAssignmentEngine;

  beforeEach(() => {
    engine = new AutoAssignmentEngine();
  });

  describe('analyzeProblemType', () => {
    it('should return the incident type', async () => {
      const incident: Incident = {
        id: 'test-incident-1',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test frontend error',
        createdAt: new Date(),
      };

      const result = await engine.analyzeProblemType(incident);
      expect(result).toBe('FRONTEND_ERROR');
    });

    it('should handle different problem types', async () => {
      const problemTypes: ProblemType[] = [
        'FRONTEND_ERROR',
        'BACKEND_API',
        'DATABASE_ISSUE',
        'PERFORMANCE',
        'SECURITY',
        'INFRASTRUCTURE',
      ];

      for (const type of problemTypes) {
        const incident: Incident = {
          id: `test-${type}`,
          type,
          priority: 'MEDIUM',
          description: `Test ${type}`,
          createdAt: new Date(),
        };

        const result = await engine.analyzeProblemType(incident);
        expect(result).toBe(type);
      }
    });
  });

  describe('identifyRelevantTeams', () => {
    it('should identify teams for frontend errors', () => {
      const teams = engine.identifyRelevantTeams('FRONTEND_ERROR');
      expect(teams).toContain('frontend');
      expect(teams.length).toBeGreaterThan(0);
    });

    it('should identify teams for backend API issues', () => {
      const teams = engine.identifyRelevantTeams('BACKEND_API');
      expect(teams).toContain('backend');
      expect(teams.length).toBeGreaterThan(0);
    });

    it('should identify teams for database issues', () => {
      const teams = engine.identifyRelevantTeams('DATABASE_ISSUE');
      expect(teams).toContain('backend');
      expect(teams.length).toBeGreaterThan(0);
    });

    it('should identify teams for security issues', () => {
      const teams = engine.identifyRelevantTeams('SECURITY');
      expect(teams).toContain('security');
      expect(teams.length).toBeGreaterThan(0);
    });

    it('should identify teams for infrastructure issues', () => {
      const teams = engine.identifyRelevantTeams('INFRASTRUCTURE');
      expect(teams).toContain('devops');
      expect(teams.length).toBeGreaterThan(0);
    });
  });

  describe('checkMemberAvailability', () => {
    it('should return available members for given teams', async () => {
      const teams = ['frontend'];
      const members = await engine.checkMemberAvailability(teams);

      expect(Array.isArray(members)).toBe(true);
      expect(members.length).toBeGreaterThan(0);
      members.forEach((member) => {
        expect(member).toHaveProperty('id');
        expect(member).toHaveProperty('name');
        expect(member).toHaveProperty('email');
        expect(member).toHaveProperty('specialties');
        expect(member).toHaveProperty('timezone');
      });
    });

    it('should handle multiple teams', async () => {
      const teams = ['frontend', 'backend'];
      const members = await engine.checkMemberAvailability(teams);

      expect(members.length).toBeGreaterThan(0);
    });

    it('should return empty array for non-existent teams', async () => {
      const teams = ['non-existent-team'];
      const members = await engine.checkMemberAvailability(teams);

      expect(Array.isArray(members)).toBe(true);
    });
  });

  describe('selectOptimalAssignee', () => {
    it('should select an assignee from available members', () => {
      const availableMembers: TeamMember[] = [
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

      const assignee = engine.selectOptimalAssignee(availableMembers, incident);
      expect(assignee).toBeDefined();
      expect(availableMembers).toContainEqual(assignee);
    });

    it('should return the only available member', () => {
      const availableMembers: TeamMember[] = [
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

      const assignee = engine.selectOptimalAssignee(availableMembers, incident);
      expect(assignee).toEqual(availableMembers[0]);
    });
  });

  describe('createAssignmentRecord', () => {
    it('should create a valid assignment record', async () => {
      const primaryOwner: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const assignment = await engine.createAssignmentRecord(primaryOwner, incident);

      expect(assignment).toHaveProperty('id');
      expect(assignment.incidentId).toBe(incident.id);
      expect(assignment.primaryOwner).toEqual(primaryOwner);
      expect(assignment.status).toBe('ASSIGNED');
      expect(assignment).toHaveProperty('assignedAt');
      expect(assignment).toHaveProperty('slaTarget');
    });

    it('should handle secondary owner assignment', async () => {
      const primaryOwner: TeamMember = {
        id: 'member-1',
        name: 'Alice',
        email: 'alice@example.com',
        specialties: ['React'],
        timezone: 'UTC',
      };

      const secondaryOwner: TeamMember = {
        id: 'member-2',
        name: 'Bob',
        email: 'bob@example.com',
        specialties: ['TypeScript'],
        timezone: 'UTC',
      };

      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'CRITICAL',
        description: 'Test critical incident',
        createdAt: new Date(),
      };

      const assignment = await engine.createAssignmentRecord(
        primaryOwner,
        incident,
        secondaryOwner
      );

      expect(assignment.secondaryOwner).toEqual(secondaryOwner);
    });
  });

  describe('assignResponsibility (integration)', () => {
    it('should complete full assignment workflow', async () => {
      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test frontend error',
        affectedFiles: ['src/components/Button.tsx'],
        createdAt: new Date(),
      };

      const assignment = await engine.assignResponsibility(incident);

      expect(assignment).toHaveProperty('id');
      expect(assignment.incidentId).toBe(incident.id);
      expect(assignment.primaryOwner).toBeDefined();
      expect(assignment.status).toBe('ASSIGNED');
      expect(assignment.assignedAt).toBeInstanceOf(Date);
    });

    it('should handle critical priority incidents', async () => {
      const incident: Incident = {
        id: 'critical-incident',
        type: 'SECURITY',
        priority: 'CRITICAL',
        description: 'Security vulnerability detected',
        createdAt: new Date(),
      };

      const assignment = await engine.assignResponsibility(incident);

      expect(assignment.primaryOwner).toBeDefined();
      expect(assignment.slaTarget).toBeDefined();
      expect(assignment.slaTarget.responseTime).toBeLessThanOrEqual(60); // Critical should be fast
    });

    it('should handle different problem types', async () => {
      const problemTypes: ProblemType[] = [
        'FRONTEND_ERROR',
        'BACKEND_API',
        'DATABASE_ISSUE',
        'PERFORMANCE',
        'SECURITY',
        'INFRASTRUCTURE',
      ];

      for (const type of problemTypes) {
        const incident: Incident = {
          id: `incident-${type}`,
          type,
          priority: 'MEDIUM',
          description: `Test ${type} incident`,
          createdAt: new Date(),
        };

        const assignment = await engine.assignResponsibility(incident);
        expect(assignment).toBeDefined();
        expect(assignment.primaryOwner).toBeDefined();
      }
    });
  });

  describe('getAssignment', () => {
    it('should retrieve an existing assignment', async () => {
      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const created = await engine.assignResponsibility(incident);
      const retrieved = engine.getAssignment(created.id);

      expect(retrieved).toEqual(created);
    });

    it('should return undefined for non-existent assignment', () => {
      const retrieved = engine.getAssignment('non-existent-id');
      expect(retrieved).toBeUndefined();
    });
  });

  describe('updateAssignmentStatus', () => {
    it('should update assignment status', async () => {
      const incident: Incident = {
        id: 'test-incident',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test incident',
        createdAt: new Date(),
      };

      const assignment = await engine.assignResponsibility(incident);
      const updated = engine.updateAssignmentStatus(assignment.id, 'IN_PROGRESS');

      expect(updated).toBeDefined();
      expect(updated?.status).toBe('IN_PROGRESS');
    });

    it('should throw error for non-existent assignment', () => {
      expect(() => {
        engine.updateAssignmentStatus('non-existent-id', 'IN_PROGRESS');
      }).toThrow('Assignment non-existent-id not found');
    });
  });

  describe('getAllAssignments', () => {
    it('should return all assignments', async () => {
      const incident1: Incident = {
        id: 'incident-1',
        type: 'FRONTEND_ERROR',
        priority: 'HIGH',
        description: 'Test 1',
        createdAt: new Date(),
      };

      const incident2: Incident = {
        id: 'incident-2',
        type: 'BACKEND_API',
        priority: 'MEDIUM',
        description: 'Test 2',
        createdAt: new Date(),
      };

      await engine.assignResponsibility(incident1);
      await engine.assignResponsibility(incident2);

      const allAssignments = engine.getAllAssignments();
      expect(allAssignments.length).toBeGreaterThanOrEqual(2);
    });
  });
});
