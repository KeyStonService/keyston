/**
 * Advisory Database Bot Engine
 *
 * Implements the workflow automation patterns from GitHub Advisory Database
 * including staging branch management, stale PR handling, and curation workflows
 *
 * @module services/advisory-bot
 * @author SynergyMesh Team
 * @license MIT
 */

import { AdvisoryBotConfig, ValidationRule, Advisory, Ecosystem } from '../types/advisory.js';

/**
 * Default bot configuration matching GitHub Advisory Database patterns
 */
export const DEFAULT_BOT_CONFIG: AdvisoryBotConfig = {
  stagingBranch: {
    baseBranch: 'main',
    branchPattern: '{author}/advisory-improvement-{pr_number}',
    autoCleanup: true,
    cleanupDelayDays: 0,
  },
  stalePR: {
    enabled: true,
    staleDays: 15,
    closeDays: 15,
    staleLabel: 'Stale',
    exemptLabels: ['Keep'],
    staleMessage: `👋 This pull request has been marked as stale because it has been open with no activity. You can: comment on the issue or remove the stale label to hold stale off for a while, add the \`Keep\` label to hold stale off permanently, or do nothing. If you do nothing this pull request will be closed eventually by the stale bot. Please see CONTRIBUTING.md for more policy details.`,
    closeMessage:
      '🔒 This pull request has been closed due to inactivity. Feel free to reopen or submit a new PR.',
  },
  curationTeam: [],
  supportedEcosystems: [
    'actions',
    'composer',
    'erlang',
    'go',
    'maven',
    'npm',
    'nuget',
    'other',
    'pip',
    'pub',
    'rubygems',
    'rust',
    'swift',
  ],
  validationRules: [],
};

/**
 * Pull request information
 */
export interface PullRequestInfo {
  number: number;
  author: string;
  title: string;
  baseBranch: string;
  headBranch: string;
  files: string[];
  labels: string[];
  createdAt: Date;
  updatedAt: Date;
  state: 'open' | 'closed' | 'merged';
}

/**
 * Branch operation result
 */
export interface BranchOperationResult {
  success: boolean;
  branchName: string;
  message: string;
  error?: string;
}

/**
 * Stale check result
 */
export interface StaleCheckResult {
  isStale: boolean;
  shouldClose: boolean;
  daysSinceActivity: number;
  exemptReason?: string;
}

/**
 * Curation workflow action
 */
export interface CurationAction {
  type: 'approve' | 'request_changes' | 'comment' | 'mention';
  message: string;
  mentions?: string[];
  labels?: string[];
}

/**
 * Advisory Bot Engine
 *
 * Implements GitHub Advisory Database bot patterns for:
 * - Staging branch creation and management
 * - Stale PR detection and cleanup
 * - Advisory validation and curation workflows
 */
export class AdvisoryBotEngine {
  private _config: AdvisoryBotConfig;

  constructor(config: Partial<AdvisoryBotConfig> = {}) {
    this._config = {
      ...DEFAULT_BOT_CONFIG,
      ...config,
      stagingBranch: { ...DEFAULT_BOT_CONFIG.stagingBranch, ...config.stagingBranch },
      stalePR: { ...DEFAULT_BOT_CONFIG.stalePR, ...config.stalePR },
    };
  }

  /**
   * Get current configuration
   */
  get config(): AdvisoryBotConfig {
    return { ...this._config };
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<AdvisoryBotConfig>): void {
    this._config = {
      ...this._config,
      ...updates,
      stagingBranch: { ...this._config.stagingBranch, ...updates.stagingBranch },
      stalePR: { ...this._config.stalePR, ...updates.stalePR },
    };
  }

  // =========================================================================
  // Staging Branch Management
  // =========================================================================

  /**
   * Generate staging branch name for a PR
   *
   * @param pr - Pull request info
   * @returns Staging branch name
   */
  generateStagingBranchName(pr: PullRequestInfo): string {
    const pattern = this._config.stagingBranch.branchPattern;
    return pattern.replace('{author}', pr.author).replace('{pr_number}', pr.number.toString());
  }

  /**
   * Check if a PR should create a staging branch
   *
   * @param pr - Pull request info
   * @returns Whether staging branch should be created
   */
  shouldCreateStagingBranch(pr: PullRequestInfo): boolean {
    // Only for PRs targeting main with advisory changes
    if (pr.baseBranch !== this._config.stagingBranch.baseBranch) {
      return false;
    }

    // Check if any advisory files are changed
    return pr.files.some((f) => this._isAdvisoryFile(f));
  }

  /**
   * Generate staging branch creation commands
   *
   * @param pr - Pull request info
   * @returns Git commands for staging branch creation
   */
  generateStagingBranchCommands(pr: PullRequestInfo): string[] {
    const branchName = this.generateStagingBranchName(pr);
    return [
      `git checkout ${this._config.stagingBranch.baseBranch}`,
      `git checkout -b "${branchName}"`,
      `git push origin "${branchName}"`,
      `gh pr edit ${pr.number} --base "${branchName}"`,
    ];
  }

  /**
   * Generate staging branch deletion commands
   *
   * @param stagingBranch - Staging branch name
   * @param headBranch - Head branch name
   * @returns Git commands for cleanup
   */
  generateCleanupCommands(stagingBranch: string, headBranch: string): string[] {
    return [
      `git push origin --delete --force "${stagingBranch}"`,
      `git push origin --delete --force "${headBranch}"`,
    ];
  }

  // =========================================================================
  // Stale PR Management
  // =========================================================================

  /**
   * Check if a PR is stale
   *
   * @param pr - Pull request info
   * @returns Stale check result
   */
  checkStaleStatus(pr: PullRequestInfo): StaleCheckResult {
    if (!this._config.stalePR.enabled) {
      return {
        isStale: false,
        shouldClose: false,
        daysSinceActivity: 0,
        exemptReason: 'Stale PR management disabled',
      };
    }

    // Check exempt labels
    const exemptLabels = this._config.stalePR.exemptLabels;
    const hasExemptLabel = pr.labels.some((l) => exemptLabels.includes(l));
    if (hasExemptLabel) {
      return {
        isStale: false,
        shouldClose: false,
        daysSinceActivity: 0,
        exemptReason: `Has exempt label: ${pr.labels.find((l) => exemptLabels.includes(l))}`,
      };
    }

    const now = new Date();
    const lastActivity = pr.updatedAt;
    const daysSinceActivity = Math.floor(
      (now.getTime() - lastActivity.getTime()) / (1000 * 60 * 60 * 24)
    );

    const isStale = daysSinceActivity >= this._config.stalePR.staleDays;
    const shouldClose =
      daysSinceActivity >= this._config.stalePR.staleDays + this._config.stalePR.closeDays;

    return {
      isStale,
      shouldClose,
      daysSinceActivity,
    };
  }

  /**
   * Get stale PR message
   */
  getStaleMessage(): string {
    return this._config.stalePR.staleMessage;
  }

  /**
   * Get close message
   */
  getCloseMessage(): string {
    return this._config.stalePR.closeMessage;
  }

  /**
   * Get stale label
   */
  getStaleLabel(): string {
    return this._config.stalePR.staleLabel;
  }

  // =========================================================================
  // Advisory Validation & Curation
  // =========================================================================

  /**
   * Check if an ecosystem is supported
   *
   * @param ecosystem - Ecosystem to check
   * @returns Whether the ecosystem is supported
   */
  isEcosystemSupported(ecosystem: Ecosystem): boolean {
    return this._config.supportedEcosystems.includes(ecosystem);
  }

  /**
   * Validate advisory for curation
   *
   * @param advisory - Advisory to validate
   * @returns Validation issues
   */
  validateForCuration(advisory: Advisory): {
    valid: boolean;
    issues: Array<{ severity: 'error' | 'warning'; message: string }>;
  } {
    const issues: Array<{ severity: 'error' | 'warning'; message: string }> = [];

    // Check ecosystem support
    for (const affected of advisory.affected) {
      if (!this.isEcosystemSupported(affected.package.ecosystem)) {
        issues.push({
          severity: 'error',
          message: `Unsupported ecosystem: ${affected.package.ecosystem}. Supported ecosystems: ${this._config.supportedEcosystems.join(', ')}`,
        });
      }
    }

    // Run custom validation rules
    for (const rule of this._config.validationRules) {
      if (rule.enabled && !rule.validate(advisory)) {
        issues.push({
          severity: rule.severity,
          message: rule.message,
        });
      }
    }

    return {
      valid: issues.filter((i) => i.severity === 'error').length === 0,
      issues,
    };
  }

  /**
   * Generate curation actions for a PR
   *
   * @param pr - Pull request info
   * @param advisory - Advisory being submitted
   * @returns Curation actions to take
   */
  generateCurationActions(_pr: PullRequestInfo, advisory: Advisory): CurationAction[] {
    const actions: CurationAction[] = [];
    const validation = this.validateForCuration(advisory);

    if (!validation.valid) {
      // Request changes for invalid advisories
      actions.push({
        type: 'request_changes',
        message: this._formatValidationMessage(validation.issues),
      });
    } else if (validation.issues.length > 0) {
      // Add comment for warnings
      actions.push({
        type: 'comment',
        message: this._formatValidationMessage(validation.issues),
      });
    }

    // Mention curation team for review
    if (this._config.curationTeam.length > 0 && validation.valid) {
      actions.push({
        type: 'mention',
        message: 'Ready for curation review.',
        mentions: this._config.curationTeam,
      });
    }

    return actions;
  }

  /**
   * Add a custom validation rule
   *
   * @param rule - Validation rule to add
   */
  addValidationRule(rule: ValidationRule): void {
    this._config.validationRules.push(rule);
  }

  /**
   * Remove a validation rule by ID
   *
   * @param ruleId - ID of the rule to remove
   */
  removeValidationRule(ruleId: string): void {
    this._config.validationRules = this._config.validationRules.filter((r) => r.id !== ruleId);
  }

  // =========================================================================
  // GitHub Actions Workflow Generation
  // =========================================================================

  /**
   * Generate staging branch workflow YAML
   *
   * @returns Workflow YAML content
   */
  generateStagingBranchWorkflow(): string {
    return `name: Create PR staging branch

on:
  pull_request_target:
    branches: [${this._config.stagingBranch.baseBranch}]
    types: [opened, synchronize, reopened, edited]
    paths:
      - "advisories/**"
  workflow_dispatch:

permissions:
  contents: write        # Required to create and push branches
  pull-requests: write   # Required to edit PR base branch

jobs:
  ensure-base-is-staging:
    runs-on: ubuntu-latest
    steps:
     - uses: actions/checkout@v4
     - name: ensure base is staging
       env:
         PR_AUTHOR: \${{ github.event.pull_request.user.login }}
         PR_NUMBER: \${{ github.event.pull_request.number }}
         GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
       run: |
         set -xeo pipefail
         BRANCH_NAME="$PR_AUTHOR"/advisory-improvement-"$PR_NUMBER"
         git checkout -b "$BRANCH_NAME"
         git push origin "$BRANCH_NAME"
         gh pr edit --repo \${{ github.repository }} $PR_NUMBER --base "$BRANCH_NAME"
`;
  }

  /**
   * Generate cleanup workflow YAML
   *
   * @returns Workflow YAML content
   */
  generateCleanupWorkflow(): string {
    return `name: Delete PR staging and head branches

on:
  pull_request_target:
    branches: ["*/advisory-improvement-*"]
    types: [closed]
    paths:
      - "advisories/**"
  workflow_dispatch:

permissions:
  contents: write   # Required to delete branches

jobs:
  delete-staging-and-head-branches:
    if: \${{ !github.event.pull_request.head.repo.fork }}
    runs-on: ubuntu-latest
    steps:
     - uses: actions/checkout@v4
     - name: Delete staging and head branches
       env:
         STAGING_BRANCH: \${{ github.event.pull_request.base.ref }}
         HEAD_BRANCH: \${{ github.event.pull_request.head.ref }}
         GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
       run: |
         set -xeo pipefail
         git push origin --delete --force $STAGING_BRANCH
         git push origin --delete --force $HEAD_BRANCH
`;
  }

  /**
   * Generate stale PR workflow YAML
   *
   * @returns Workflow YAML content
   */
  generateStalePRWorkflow(): string {
    const config = this._config.stalePR;
    return `name: Close stale PRs

on:
  schedule:
  - cron: "00 0 * * *" # runs at 00:00 daily

permissions:
  pull-requests: write   # Required to comment on, label, and close PRs

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/stale@v9.0.0
      name: Clean up stale PRs
      with:
        repo-token: \${{ secrets.GITHUB_TOKEN }}
        stale-pr-message: "${this._escapeYamlString(config.staleMessage)}"
        stale-pr-label: "${config.staleLabel}"
        exempt-pr-labels: "${config.exemptLabels.join(',')}"
        days-before-pr-stale: ${config.staleDays}
        days-before-pr-close: ${config.closeDays}
        days-before-issue-stale: -1  # prevents issues from being tagged
        days-before-issue-close: -1  # prevents issues from being closed
        ascending: true
`;
  }

  // =========================================================================
  // Private Helper Methods
  // =========================================================================

  /**
   * Escape a string for use in YAML double-quoted strings
   * Properly handles backslashes, double quotes, and newlines
   */
  private _escapeYamlString(str: string): string {
    return str
      .replace(/\\/g, '\\\\') // Escape backslashes first
      .replace(/"/g, '\\"') // Escape double quotes
      .replace(/\n/g, '\\n'); // Escape newlines
  }

  /**
   * Check if a file path is an advisory file
   */
  private _isAdvisoryFile(filePath: string): boolean {
    return (
      filePath.startsWith('advisories/') ||
      (filePath.endsWith('.json') && filePath.includes('advisory'))
    );
  }

  /**
   * Format validation issues into a message
   */
  private _formatValidationMessage(
    issues: Array<{ severity: 'error' | 'warning'; message: string }>
  ): string {
    const errors = issues.filter((i) => i.severity === 'error');
    const warnings = issues.filter((i) => i.severity === 'warning');

    let message = '';

    if (errors.length > 0) {
      message += '## ❌ Errors\n\n';
      for (const error of errors) {
        message += `- ${error.message}\n`;
      }
      message += '\n';
    }

    if (warnings.length > 0) {
      message += '## ⚠️ Warnings\n\n';
      for (const warning of warnings) {
        message += `- ${warning.message}\n`;
      }
    }

    return message;
  }
}

export default AdvisoryBotEngine;
