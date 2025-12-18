#!/usr/bin/env node

/**
 * Comprehensive Validator
 * Runs all validation checks and generates detailed report
 *
 * @module comprehensive-validator
 * @author SynergyMesh Team
 * @license MIT
 */

import { readdir, readFile } from 'fs/promises';
import { resolve, extname } from 'path';

import { DeploymentValidator } from './deployment-validator.js';
import { LogicValidator } from './logic-validator.js';

/**
 * Comprehensive validation orchestrator
 */
class ComprehensiveValidator {
  constructor(basePath = process.cwd()) {
    this.basePath = basePath;
    this.deploymentValidator = new DeploymentValidator();
    this.logicValidator = new LogicValidator();
  }

  /**
   * Run all validations
   */
  async validate() {
    const report = {
      timestamp: new Date().toISOString(),
      basePath: this.basePath,
      overall: {
        valid: true,
        score: 0,
        grade: 'A+',
      },
      validations: {},
      summary: {
        totalFiles: 0,
        validatedFiles: 0,
        totalIssues: 0,
        criticalIssues: 0,
        warnings: 0,
      },
      recommendations: [],
    };

    try {
      // 1. Deployment configuration validation
      console.info('Running deployment validation...');
      report.validations.deployment = await this.deploymentValidator.validate(this.basePath);

      if (!report.validations.deployment.valid) {
        report.overall.valid = false;
      }

      // 2. Code logic validation for all JS files
      console.info('Running logic validation...');
      const jsFiles = await this._findJavaScriptFiles(this.basePath);
      report.summary.totalFiles = jsFiles.length;

      report.validations.codeLogic = {
        files: {},
        summary: {
          totalFiles: jsFiles.length,
          validFiles: 0,
          invalidFiles: 0,
          totalWarnings: 0,
        },
      };

      for (const file of jsFiles) {
        try {
          const code = await readFile(file, 'utf-8');
          const validation = this.logicValidator.validate(code);

          report.validations.codeLogic.files[file] = {
            valid: validation.valid,
            score: validation.score,
            warnings: validation.summary.warnings,
            integrity: validation.checks.authenticity?.integrity,
          };

          if (validation.valid) {
            report.validations.codeLogic.summary.validFiles++;
          } else {
            report.validations.codeLogic.summary.invalidFiles++;
            report.overall.valid = false;
          }

          report.validations.codeLogic.summary.totalWarnings += validation.summary.warnings;
          report.summary.validatedFiles++;
        } catch (error) {
          console.error(`Failed to validate ${file}:`, error.message);
          report.validations.codeLogic.files[file] = {
            error: error.message,
          };
        }
      }

      // 3. Calculate overall metrics
      report.summary.totalIssues =
        report.validations.deployment.errors.length +
        report.validations.codeLogic.summary.invalidFiles;

      report.summary.criticalIssues = report.validations.deployment.errors.length;
      report.summary.warnings =
        report.validations.deployment.warnings.length +
        report.validations.codeLogic.summary.totalWarnings;

      // 4. Calculate overall score
      const deploymentScore = report.validations.deployment.score;
      const avgCodeScore = this._calculateAverageCodeScore(report.validations.codeLogic.files);

      report.overall.score = Math.round(deploymentScore * 0.3 + avgCodeScore * 0.7);
      report.overall.grade = this._calculateGrade(report.overall.score);

      // 5. Generate recommendations
      report.recommendations = this._generateRecommendations(report);
    } catch (error) {
      report.overall.valid = false;
      report.error = error.message;
    }

    return report;
  }

  /**
   * Find all JavaScript files
   */
  async _findJavaScriptFiles(basePath) {
    const files = [];

    try {
      const entries = await readdir(basePath, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = resolve(basePath, entry.name);

        if (entry.isFile() && extname(entry.name) === '.js') {
          // Exclude node_modules and test files for now
          if (!fullPath.includes('node_modules') && !entry.name.includes('.test.')) {
            files.push(fullPath);
          }
        }
      }
    } catch (error) {
      console.error('Error reading directory:', error.message);
    }

    return files;
  }

  /**
   * Calculate average code score
   */
  _calculateAverageCodeScore(files) {
    const scores = Object.values(files)
      .filter((f) => typeof f.score === 'number')
      .map((f) => f.score);

    if (scores.length === 0) {
      return 0;
    }

    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }

  /**
   * Calculate grade
   */
  _calculateGrade(score) {
    if (score >= 95) {
      return 'A+';
    }
    if (score >= 90) {
      return 'A';
    }
    if (score >= 85) {
      return 'A-';
    }
    if (score >= 80) {
      return 'B+';
    }
    if (score >= 75) {
      return 'B';
    }
    if (score >= 70) {
      return 'C';
    }
    return 'F';
  }

  /**
   * Generate recommendations
   */
  _generateRecommendations(report) {
    const recommendations = [];

    // Deployment recommendations
    if (report.validations.deployment.errors.length > 0) {
      recommendations.push({
        priority: 'CRITICAL',
        category: 'Deployment',
        message: 'Fix deployment configuration errors before proceeding',
        action: 'Review and address all deployment validation errors',
      });
    }

    // Code quality recommendations
    const invalidFiles = report.validations.codeLogic.summary.invalidFiles;
    if (invalidFiles > 0) {
      recommendations.push({
        priority: 'HIGH',
        category: 'Code Quality',
        message: `${invalidFiles} file(s) failed logic validation`,
        action: 'Review and fix logic issues in affected files',
      });
    }

    // Warning recommendations
    const totalWarnings = report.summary.warnings;
    if (totalWarnings > 10) {
      recommendations.push({
        priority: 'MEDIUM',
        category: 'Code Quality',
        message: `${totalWarnings} warnings detected across codebase`,
        action: 'Address warnings to improve code quality',
      });
    }

    // Score-based recommendations
    if (report.overall.score < 80) {
      recommendations.push({
        priority: 'HIGH',
        category: 'Overall Quality',
        message: `Overall score (${report.overall.score}) is below acceptable threshold`,
        action: 'Improve code quality and fix validation issues',
      });
    }

    // Success message
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'INFO',
        category: 'Status',
        message: 'All validations passed successfully',
        action: 'Maintain current quality standards',
      });
    }

    return recommendations;
  }

  /**
   * Generate formatted report
   */
  formatReport(report) {
    const lines = [];

    lines.push('');
    lines.push('=======================================================');
    lines.push('          COMPREHENSIVE VALIDATION REPORT');
    lines.push('=======================================================');
    lines.push('');

    // Overall Status
    const statusSymbol = report.overall.valid ? '✓' : '✗';
    const statusText = report.overall.valid ? 'PASSED' : 'FAILED';
    lines.push(`Overall Status: ${statusSymbol} ${statusText}`);
    lines.push(`Overall Score: ${report.overall.score}/100 (Grade: ${report.overall.grade})`);
    lines.push(`Timestamp: ${report.timestamp}`);
    lines.push('');

    // Summary
    lines.push('─── SUMMARY ───');
    lines.push(`Total Files: ${report.summary.totalFiles}`);
    lines.push(`Validated Files: ${report.summary.validatedFiles}`);
    lines.push(`Total Issues: ${report.summary.totalIssues}`);
    lines.push(`Critical Issues: ${report.summary.criticalIssues}`);
    lines.push(`Warnings: ${report.summary.warnings}`);
    lines.push('');

    // Deployment Validation
    lines.push('─── DEPLOYMENT VALIDATION ───');
    lines.push(`Status: ${report.validations.deployment.valid ? '✓ PASSED' : '✗ FAILED'}`);
    lines.push(`Score: ${report.validations.deployment.score}/100`);
    lines.push(`Errors: ${report.validations.deployment.errors.length}`);
    lines.push(`Warnings: ${report.validations.deployment.warnings.length}`);
    lines.push('');

    // Code Logic Validation
    lines.push('─── CODE LOGIC VALIDATION ───');
    lines.push(`Total Files: ${report.validations.codeLogic.summary.totalFiles}`);
    lines.push(`Valid Files: ${report.validations.codeLogic.summary.validFiles}`);
    lines.push(`Invalid Files: ${report.validations.codeLogic.summary.invalidFiles}`);
    lines.push(`Total Warnings: ${report.validations.codeLogic.summary.totalWarnings}`);
    lines.push('');

    // File Details (top 5 by warnings)
    const fileEntries = Object.entries(report.validations.codeLogic.files)
      .filter(([_, data]) => typeof data.warnings === 'number')
      .sort(([_, a], [__, b]) => (b.warnings || 0) - (a.warnings || 0))
      .slice(0, 5);

    if (fileEntries.length > 0) {
      lines.push('Top Files by Warnings:');
      for (const [file, data] of fileEntries) {
        const fileName = file.split('/').pop();
        const status = data.valid ? '✓' : '✗';
        lines.push(
          `  ${status} ${fileName} - Score: ${data.score}/100, Warnings: ${data.warnings}`
        );
      }
      lines.push('');
    }

    // Recommendations
    lines.push('─── RECOMMENDATIONS ───');
    for (const rec of report.recommendations) {
      lines.push(`[${rec.priority}] ${rec.category}`);
      lines.push(`  ${rec.message}`);
      lines.push(`  → ${rec.action}`);
      lines.push('');
    }

    lines.push('=======================================================');

    return lines.join('\n');
  }
}

/**
 * Main execution
 */
async function main() {
  const validator = new ComprehensiveValidator();

  console.info('Starting comprehensive validation...\n');

  const report = await validator.validate();
  const formattedReport = validator.formatReport(report);

  console.info(formattedReport);

  // Exit with appropriate code
  process.exit(report.overall.valid ? 0 : 1);
}

// Run if executed directly
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

export { ComprehensiveValidator };
