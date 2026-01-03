import { v4 as uuidv4 } from "uuid";
import type {
  PlanCardData,
  PlanStep,
  RiskLevel,
  ExecutionMode,
  Rollbackability,
  RequiredPermission,
  AffectedResource,
} from "../../shared/types";

interface IntentAnalysis {
  intent: string;
  provider?: string;
  scope?: string;
  targets?: string[];
  action?: string;
  confidence: number;
}

const INTENT_PATTERNS: { pattern: RegExp; intent: string; provider?: string }[] = [
  {
    pattern: /apply\s+security\s+baseline/i,
    intent: "apply_security_baseline",
  },
  {
    pattern: /enable\s+(branch\s+)?protection/i,
    intent: "enable_branch_protection",
    provider: "github",
  },
  {
    pattern: /enable\s+vulnerability\s+alerts?/i,
    intent: "enable_vulnerability_alerts",
    provider: "github",
  },
  {
    pattern: /enable\s+automated\s+security\s+fix(es)?/i,
    intent: "enable_automated_security_fixes",
    provider: "github",
  },
  {
    pattern: /review\s+security\s+(settings?|config)/i,
    intent: "review_security_settings",
  },
  {
    pattern: /check\s+(repo(sitory)?|branch)\s+protection/i,
    intent: "check_protection",
    provider: "github",
  },
  {
    pattern: /list\s+(my\s+)?repos?(itories)?/i,
    intent: "list_repos",
    provider: "github",
  },
  {
    pattern: /connect\s+(to\s+)?github/i,
    intent: "connect_github",
    provider: "github",
  },
  {
    pattern: /rollback/i,
    intent: "rollback",
  },
  {
    pattern: /help|what\s+can\s+you\s+do/i,
    intent: "help",
  },
];

function analyzeIntent(message: string): IntentAnalysis {
  for (const { pattern, intent, provider } of INTENT_PATTERNS) {
    if (pattern.test(message)) {
      return {
        intent,
        provider,
        confidence: 0.8,
      };
    }
  }

  return {
    intent: "unknown",
    confidence: 0.3,
  };
}

function extractTargets(message: string): string[] {
  // Prevent ReDoS: Limit input length and use a more specific pattern
  // that doesn't allow ambiguous backtracking.
  // Pattern: alphanumeric boundaries with hyphens allowed in owner name,
  // slash separator, then alphanumeric with hyphens/dots/underscores in repo name.
  // Max length check prevents excessive processing on malicious input.
  if (message.length > 10000) {
    return [];
  }
  
  // Safe pattern with explicit character classes to prevent polynomial backtracking:
  // - Owner: 1-40 chars, alphanumeric, hyphens allowed in middle
  // - Repo: 1-101 chars, alphanumeric, hyphens/dots/underscores allowed in middle
  // Matches: a/b, owner/repo, owner-name/repo-name.git, etc.
  const repoPattern = /\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,38}[a-zA-Z0-9])?\/[a-zA-Z0-9](?:[a-zA-Z0-9._-]{0,99}[a-zA-Z0-9])?\b/g;
  const matches = message.match(repoPattern) || [];
  return matches;
}

interface PlanGenerationContext {
  userId: string;
  tenantId: string;
  connectionId?: string;
  provider?: string;
  capabilities?: string[];
}

export async function generatePlan(
  message: string,
  context: PlanGenerationContext
): Promise<PlanCardData | null> {
  const intent = analyzeIntent(message);
  const targets = extractTargets(message);

  if (intent.intent === "unknown" || intent.intent === "help") {
    return null;
  }

  switch (intent.intent) {
    case "apply_security_baseline":
      return generateSecurityBaselinePlan(targets, context);

    case "enable_branch_protection":
      return generateBranchProtectionPlan(targets, context);

    case "enable_vulnerability_alerts":
      return generateVulnerabilityAlertsPlan(targets, context);

    case "check_protection":
      return generateCheckProtectionPlan(targets, context);

    default:
      return null;
  }
}

function generateSecurityBaselinePlan(
  targets: string[],
  context: PlanGenerationContext
): PlanCardData {
  const planId = uuidv4();
  const steps: PlanStep[] = [];

  for (let i = 0; i < targets.length; i++) {
    const [owner, repo] = targets[i].split("/");

    steps.push(
      {
        id: uuidv4(),
        action: "github.repo.get_settings",
        description: `Fetch current settings for ${targets[i]}`,
        order: i * 5 + 1,
        status: "pending",
      },
      {
        id: uuidv4(),
        action: "github.repo.get_branch_protection",
        description: `Check branch protection for ${targets[i]}`,
        order: i * 5 + 2,
        status: "pending",
      },
      {
        id: uuidv4(),
        action: "github.repo.set_branch_protection",
        description: `Enable branch protection on default branch`,
        order: i * 5 + 3,
        status: "pending",
      },
      {
        id: uuidv4(),
        action: "github.repo.enable_vulnerability_alerts",
        description: `Enable vulnerability alerts for ${targets[i]}`,
        order: i * 5 + 4,
        status: "pending",
      },
      {
        id: uuidv4(),
        action: "github.repo.enable_automated_security_fixes",
        description: `Enable automated security fixes for ${targets[i]}`,
        order: i * 5 + 5,
        status: "pending",
      }
    );
  }

  if (steps.length === 0) {
    steps.push({
      id: uuidv4(),
      action: "github.security.apply_baseline",
      description: "Apply security baseline to connected repositories",
      order: 1,
      status: "pending",
    });
  }

  const affectedResources: AffectedResource[] = targets.map((t) => {
    const [org, repo] = t.split("/");
    return {
      platform: "GitHub",
      organization: org,
      resource: repo,
    };
  });

  return {
    id: planId,
    title: "Apply Security Baseline",
    description: `Apply comprehensive security settings to ${targets.length || "selected"} repositories`,
    steps,
    riskLevel: "MED",
    executionMode: "AUTO",
    rollbackability: "YES",
    requiredPermissions: [
      {
        scope: "repo",
        description: "Full repository access",
        hasPermission: !!context.connectionId,
      },
      {
        scope: "admin:repo_hook",
        description: "Repository webhooks",
        hasPermission: !!context.connectionId,
      },
    ],
    affectedResources,
    status: "draft",
    canApprove: true,
    canDryRun: true,
    canRollback: true,
    confirmRequired: true,
  };
}

function generateBranchProtectionPlan(
  targets: string[],
  context: PlanGenerationContext
): PlanCardData {
  const planId = uuidv4();
  const steps: PlanStep[] = [];

  for (let i = 0; i < targets.length; i++) {
    steps.push(
      {
        id: uuidv4(),
        action: "github.repo.get_branch_protection",
        description: `Check current protection for ${targets[i]}`,
        order: i * 2 + 1,
        status: "pending",
      },
      {
        id: uuidv4(),
        action: "github.repo.set_branch_protection",
        description: `Enable branch protection for ${targets[i]}`,
        order: i * 2 + 2,
        status: "pending",
      }
    );
  }

  const affectedResources: AffectedResource[] = targets.map((t) => {
    const [org, repo] = t.split("/");
    return {
      platform: "GitHub",
      organization: org,
      resource: repo,
    };
  });

  return {
    id: planId,
    title: "Enable Branch Protection",
    description: `Configure branch protection rules for ${targets.length} repositories`,
    steps,
    riskLevel: "MED",
    executionMode: "AUTO",
    rollbackability: "YES",
    requiredPermissions: [
      {
        scope: "repo",
        description: "Repository admin access",
        hasPermission: !!context.connectionId,
      },
    ],
    affectedResources,
    status: "draft",
    canApprove: true,
    canDryRun: true,
    canRollback: true,
    confirmRequired: true,
  };
}

function generateVulnerabilityAlertsPlan(
  targets: string[],
  context: PlanGenerationContext
): PlanCardData {
  const planId = uuidv4();
  const steps: PlanStep[] = targets.map((target, i) => ({
    id: uuidv4(),
    action: "github.repo.enable_vulnerability_alerts",
    description: `Enable vulnerability alerts for ${target}`,
    order: i + 1,
    status: "pending",
  }));

  const affectedResources: AffectedResource[] = targets.map((t) => {
    const [org, repo] = t.split("/");
    return {
      platform: "GitHub",
      organization: org,
      resource: repo,
    };
  });

  return {
    id: planId,
    title: "Enable Vulnerability Alerts",
    description: `Enable Dependabot vulnerability alerts for ${targets.length} repositories`,
    steps,
    riskLevel: "LOW",
    executionMode: "AUTO",
    rollbackability: "YES",
    requiredPermissions: [
      {
        scope: "repo",
        description: "Repository access",
        hasPermission: !!context.connectionId,
      },
    ],
    affectedResources,
    status: "draft",
    canApprove: true,
    canDryRun: true,
    canRollback: true,
    confirmRequired: false,
  };
}

function generateCheckProtectionPlan(
  targets: string[],
  context: PlanGenerationContext
): PlanCardData {
  const planId = uuidv4();
  const steps: PlanStep[] = targets.map((target, i) => ({
    id: uuidv4(),
    action: "github.repo.get_branch_protection",
    description: `Check branch protection for ${target}`,
    order: i + 1,
    status: "pending",
  }));

  const affectedResources: AffectedResource[] = targets.map((t) => {
    const [org, repo] = t.split("/");
    return {
      platform: "GitHub",
      organization: org,
      resource: repo,
    };
  });

  return {
    id: planId,
    title: "Review Branch Protection",
    description: `Check branch protection status for ${targets.length} repositories`,
    steps,
    riskLevel: "LOW",
    executionMode: "READ_ONLY",
    rollbackability: "NO",
    requiredPermissions: [
      {
        scope: "repo:read",
        description: "Repository read access",
        hasPermission: !!context.connectionId,
      },
    ],
    affectedResources,
    status: "draft",
    canApprove: true,
    canDryRun: false,
    canRollback: false,
    confirmRequired: false,
  };
}

export function generateHelpResponse(): string {
  return `I can help you with the following:

**GitHub Security Operations:**
- Apply security baseline to repositories
- Enable branch protection rules
- Enable vulnerability alerts
- Enable automated security fixes
- Review current security settings

**Example commands:**
- "Apply security baseline to owner/repo"
- "Enable branch protection for owner/repo"
- "Check protection status for owner/repo"
- "Enable vulnerability alerts for owner/repo"

Would you like to connect to GitHub first, or shall I help you with something specific?`;
}

export const planner = {
  generatePlan,
  generateHelpResponse,
  analyzeIntent,
};
