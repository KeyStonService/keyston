#!/usr/bin/env node

/**
 * Deployment Configuration Validator
 * Validates deployment configurations for production readiness
 *
 * @module deployment-validator
 * @author SynergyMesh Team
 * @license MIT
 */

import { existsSync } from 'fs';
import { readFile } from 'fs/promises';
import { resolve } from 'path';

/**
 * Deployment configuration validator
 */
class DeploymentValidator {
  constructor() {
    this.requiredFiles = ['package.json', 'README.md', '.gitignore'];

    this.requiredPackageFields = [
      'name',
      'version',
      'description',
      'main',
      'scripts',
      'license',
      'engines',
    ];

    this.requiredScripts = ['start', 'test'];
  }

  /**
   * Validate complete deployment configuration
   */
  async validate(basePath = process.cwd()) {
    const results = {
      valid: true,
      timestamp: new Date().toISOString(),
      checks: [],
      errors: [],
      warnings: [],
      score: 100,
    };

    try {
      // Check required files
      results.checks.push(await this._checkRequiredFiles(basePath));

      // Validate package.json
      results.checks.push(await this._validatePackageJson(basePath));

      // Check security configurations
      results.checks.push(await this._checkSecurityConfig(basePath));

      // Validate environment variables
      results.checks.push(this._validateEnvironmentConfig());

      // Check Node.js version
      results.checks.push(this._checkNodeVersion());

      // Aggregate results
      for (const check of results.checks) {
        if (!check.passed) {
          results.valid = false;
          if (check.severity === 'error') {
            results.errors.push(check);
            results.score -= 20;
          } else {
            results.warnings.push(check);
            results.score -= 5;
          }
        }
      }

      results.score = Math.max(0, results.score);
      results.grade = this._calculateGrade(results.score);
    } catch (error) {
      results.valid = false;
      results.errors.push({
        name: 'Validation Error',
        message: error.message,
        severity: 'error',
      });
    }

    return results;
  }

  /**
   * Check required files exist
   */
  _checkRequiredFiles(basePath) {
    const check = {
      name: 'Required Files Check',
      passed: true,
      severity: 'error',
      details: [],
    };

    for (const file of this.requiredFiles) {
      const filePath = resolve(basePath, file);
      if (!existsSync(filePath)) {
        check.passed = false;
        check.details.push(`Missing required file: ${file}`);
      }
    }

    if (check.passed) {
      check.details.push('All required files present');
    }

    return check;
  }

  /**
   * Validate package.json configuration
   */
  async _validatePackageJson(basePath) {
    const check = {
      name: 'Package.json Validation',
      passed: true,
      severity: 'error',
      details: [],
    };

    try {
      const pkgPath = resolve(basePath, 'package.json');
      const content = await readFile(pkgPath, 'utf-8');
      const pkg = JSON.parse(content);

      // Check required fields
      for (const field of this.requiredPackageFields) {
        if (!pkg[field]) {
          check.passed = false;
          check.details.push(`Missing required field: ${field}`);
        }
      }

      // Check required scripts
      if (pkg.scripts) {
        for (const script of this.requiredScripts) {
          if (!pkg.scripts[script]) {
            check.passed = false;
            check.details.push(`Missing required script: ${script}`);
          }
        }
      } else {
        check.passed = false;
        check.details.push('No scripts defined');
      }

      // Check version format
      if (pkg.version && !/^\d+\.\d+\.\d+/.test(pkg.version)) {
        check.passed = false;
        check.details.push('Invalid version format (should be semver)');
      }

      // Check license
      if (pkg.license && !['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'].includes(pkg.license)) {
        check.severity = 'warning';
        check.details.push(`Non-standard license: ${pkg.license}`);
      }

      if (check.passed) {
        check.details.push('Package.json is valid');
      }
    } catch (error) {
      check.passed = false;
      check.details.push(`Failed to validate package.json: ${error.message}`);
    }

    return check;
  }

  /**
   * Check security configurations
   */
  async _checkSecurityConfig(basePath) {
    const check = {
      name: 'Security Configuration Check',
      passed: true,
      severity: 'warning',
      details: [],
    };

    // Check for .gitignore
    const gitignorePath = resolve(basePath, '.gitignore');
    if (!existsSync(gitignorePath)) {
      check.passed = false;
      check.details.push('Missing .gitignore file');
    } else {
      try {
        const content = await readFile(gitignorePath, 'utf-8');
        const requiredPatterns = ['node_modules', '.env', '*.log'];

        for (const pattern of requiredPatterns) {
          if (!content.includes(pattern)) {
            check.details.push(`Missing .gitignore pattern: ${pattern}`);
          }
        }
      } catch (error) {
        check.details.push(`Failed to read .gitignore: ${error.message}`);
      }
    }

    // Check for sensitive files that shouldn't exist
    const sensitiveFiles = ['.env', 'secrets.json', 'credentials.json'];
    for (const file of sensitiveFiles) {
      if (existsSync(resolve(basePath, file))) {
        check.passed = false;
        check.severity = 'error';
        check.details.push(`Sensitive file should not be committed: ${file}`);
      }
    }

    if (check.passed && check.details.length === 0) {
      check.details.push('Security configuration is adequate');
    }

    return check;
  }

  /**
   * Validate environment variable configuration
   */
  _validateEnvironmentConfig() {
    const check = {
      name: 'Environment Configuration',
      passed: true,
      severity: 'warning',
      details: [],
    };

    const nodeEnv = process.env.NODE_ENV;
    if (!nodeEnv) {
      check.details.push('NODE_ENV not set (defaulting to development)');
    } else if (!['development', 'production', 'test'].includes(nodeEnv)) {
      check.passed = false;
      check.details.push(`Invalid NODE_ENV value: ${nodeEnv}`);
    }

    if (check.passed && check.details.length === 0) {
      check.details.push('Environment configuration is valid');
    }

    return check;
  }

  /**
   * Check Node.js version
   */
  _checkNodeVersion() {
    const check = {
      name: 'Node.js Version Check',
      passed: true,
      severity: 'error',
      details: [],
    };

    const currentVersion = process.version;
    const majorVersion = parseInt(currentVersion.slice(1).split('.')[0]);

    if (majorVersion < 18) {
      check.passed = false;
      check.details.push(`Node.js version ${currentVersion} is below minimum required (18.x)`);
    } else {
      check.details.push(`Node.js version ${currentVersion} is supported`);
    }

    return check;
  }

  /**
   * Calculate grade based on score
   */
  _calculateGrade(score) {
    if (score >= 95) {
      return 'A+';
    }
    if (score >= 90) {
      return 'A';
    }
    if (score >= 80) {
      return 'B';
    }
    if (score >= 70) {
      return 'C';
    }
    if (score >= 60) {
      return 'D';
    }
    return 'F';
  }
}

/**
 * Main execution
 */
async function main() {
  const validator = new DeploymentValidator();
  const results = await validator.validate();

  console.warn('\n=== Deployment Configuration Validation ===\n');
  console.info(`Overall Status: ${results.valid ? '✓ PASSED' : '✗ FAILED'}`);
  console.info(`Score: ${results.score}/100 (Grade: ${results.grade})`);
  console.info(`Errors: ${results.errors.length}`);
  console.info(`Warnings: ${results.warnings.length}`);

  if (results.errors.length > 0) {
    console.info('\n--- Errors ---');
    for (const error of results.errors) {
      console.warn(`\n${error.name}:`);
      for (const detail of error.details) {
        console.warn(`  ✗ ${detail}`);
      }
    }
  }

  if (results.warnings.length > 0) {
    console.info('\n--- Warnings ---');
    for (const warning of results.warnings) {
      console.warn(`\n${warning.name}:`);
      for (const detail of warning.details) {
        console.warn(`  ⚠ ${detail}`);
      }
    }
  }

  console.info('\n--- All Checks ---');
  for (const check of results.checks) {
    const status = check.passed ? '✓' : '✗';
    console.warn(`\n${status} ${check.name}:`);
    for (const detail of check.details) {
      console.warn(`  ${detail}`);
    }
  }

  process.exit(results.valid ? 0 : 1);
}

// Run if executed directly
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

export { DeploymentValidator };
