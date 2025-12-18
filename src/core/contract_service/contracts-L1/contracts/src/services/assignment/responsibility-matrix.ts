/**
 * 責任矩陣自動化 (Responsibility Matrix)
 * Manages expertise mapping and team structure
 */

import { ProblemType, TeamMember, TeamStructure } from '../../types/assignment';

export class ResponsibilityMatrix {
  private expertiseMap: Map<ProblemType, string[]>;
  private teamStructures: Map<string, TeamStructure>;

  constructor() {
    this.expertiseMap = new Map();
    this.teamStructures = new Map();
    this.initializeExpertiseMap();
    this.initializeTeamStructures();
  }

  /**
   * 初始化專業領域映射
   * Initialize expertise mapping
   */
  private initializeExpertiseMap(): void {
    this.expertiseMap.set('FRONTEND_ERROR', ['frontend', 'ui']);
    this.expertiseMap.set('BACKEND_API', ['backend', 'api']);
    this.expertiseMap.set('DATABASE_ISSUE', ['backend', 'database']);
    this.expertiseMap.set('PERFORMANCE', ['devops', 'backend']);
    this.expertiseMap.set('SECURITY', ['security', 'backend']);
    this.expertiseMap.set('INFRASTRUCTURE', ['devops', 'infrastructure']);
  }

  /**
   * 初始化團隊結構
   * Initialize team structures
   */
  private initializeTeamStructures(): void {
    this.teamStructures.set('frontend', {
      name: 'frontend',
      members: [
        {
          id: 'alice.chen',
          name: 'Alice Chen',
          email: 'alice.chen@synergymesh.dev',
          specialties: ['react', 'vue', 'typescript', 'ui/ux'],
          timezone: 'Asia/Taipei',
        },
        {
          id: 'bob.wang',
          name: 'Bob Wang',
          email: 'bob.wang@synergymesh.dev',
          specialties: ['react', 'typescript', 'performance'],
          timezone: 'Asia/Taipei',
        },
        {
          id: 'carol.liu',
          name: 'Carol Liu',
          email: 'carol.liu@synergymesh.dev',
          specialties: ['vue', 'ui/ux', 'accessibility'],
          timezone: 'Asia/Taipei',
        },
      ],
      specialties: ['react', 'vue', 'typescript', 'ui/ux'],
      timezone: 'Asia/Taipei',
    });

    this.teamStructures.set('backend', {
      name: 'backend',
      members: [
        {
          id: 'david.zhang',
          name: 'David Zhang',
          email: 'david.zhang@synergymesh.dev',
          specialties: ['node.js', 'python', 'api', 'database'],
          timezone: 'Asia/Taipei',
        },
        {
          id: 'eva.wu',
          name: 'Eva Wu',
          email: 'eva.wu@synergymesh.dev',
          specialties: ['node.js', 'database', 'performance'],
          timezone: 'Asia/Taipei',
        },
        {
          id: 'frank.lin',
          name: 'Frank Lin',
          email: 'frank.lin@synergymesh.dev',
          specialties: ['python', 'api', 'microservices'],
          timezone: 'Asia/Taipei',
        },
      ],
      specialties: ['node.js', 'python', 'database', 'api'],
      timezone: 'Asia/Taipei',
    });

    this.teamStructures.set('devops', {
      name: 'devops',
      members: [
        {
          id: 'grace.huang',
          name: 'Grace Huang',
          email: 'grace.huang@synergymesh.dev',
          specialties: ['docker', 'kubernetes', 'aws', 'ci/cd'],
          timezone: 'UTC',
        },
        {
          id: 'henry.chen',
          name: 'Henry Chen',
          email: 'henry.chen@synergymesh.dev',
          specialties: ['kubernetes', 'monitoring', 'infrastructure'],
          timezone: 'UTC',
        },
      ],
      specialties: ['docker', 'kubernetes', 'aws', 'ci/cd'],
      timezone: 'UTC',
    });

    this.teamStructures.set('security', {
      name: 'security',
      members: [
        {
          id: 'iris.lee',
          name: 'Iris Lee',
          email: 'iris.lee@synergymesh.dev',
          specialties: ['authentication', 'encryption', 'audit'],
          timezone: 'Asia/Shanghai',
        },
        {
          id: 'jack.yang',
          name: 'Jack Yang',
          email: 'jack.yang@synergymesh.dev',
          specialties: ['penetration-testing', 'security-review', 'compliance'],
          timezone: 'Asia/Shanghai',
        },
      ],
      specialties: ['authentication', 'encryption', 'audit'],
      timezone: 'Asia/Shanghai',
    });
  }

  /**
   * 根據問題類型識別相關團隊
   * Identify relevant teams based on problem type
   */
  identifyRelevantTeams(problemType: ProblemType): TeamStructure[] {
    const teamNames = this.expertiseMap.get(problemType) || [];
    return teamNames
      .map((name) => this.teamStructures.get(name))
      .filter((team): team is TeamStructure => team !== undefined);
  }

  /**
   * 獲取所有團隊成員
   * Get all team members
   */
  getAllMembers(): TeamMember[] {
    const members: TeamMember[] = [];
    this.teamStructures.forEach((team) => {
      members.push(...team.members);
    });
    return members;
  }

  /**
   * 根據 ID 獲取成員
   * Get member by ID
   */
  getMemberById(id: string): TeamMember | undefined {
    return this.getAllMembers().find((member) => member.id === id);
  }

  /**
   * 獲取團隊結構
   * Get team structure
   */
  getTeamStructure(teamName: string): TeamStructure | undefined {
    return this.teamStructures.get(teamName);
  }
}
