#!/usr/bin/env node

/**
 * Logic Validator
 * Validates code logic, authenticity, and correctness
 *
 * @module logic-validator
 * @author SynergyMesh Team
 * @license MIT
 */

import { createHash } from 'crypto';

/**
 * Logic validation engine
 */
class LogicValidator {
  /**
   * Validate code logic and authenticity
   */
  validate(code, _options = {}) {
    const validation = {
      timestamp: new Date().toISOString(),
      valid: true,
      checks: {
        authenticity: this._validateAuthenticity(code),
        logic: this._validateLogic(code),
        consistency: this._validateConsistency(code),
        patterns: this._validatePatterns(code),
        dependencies: this._validateDependencies(code),
      },
      summary: {
        totalChecks: 0,
        passed: 0,
        failed: 0,
        warnings: 0,
      },
      score: 0,
    };

    // Count results
    for (const result of Object.values(validation.checks)) {
      validation.summary.totalChecks++;
      if (result.valid) {
        validation.summary.passed++;
      } else {
        validation.summary.failed++;
        validation.valid = false;
      }
      validation.summary.warnings += result.warnings?.length || 0;
    }

    // Calculate score
    validation.score = Math.round(
      (validation.summary.passed / validation.summary.totalChecks) * 100
    );

    return validation;
  }

  /**
   * Validate code authenticity
   */
  _validateAuthenticity(code) {
    const result = {
      valid: true,
      checks: [],
      warnings: [],
    };

    // Check for suspicious patterns
    const suspiciousPatterns = [
      {
        pattern: /eval\s*\(/g,
        message: 'Use of eval() detected - potential security risk',
      },
      {
        pattern: /Function\s*\(/g,
        message: 'Dynamic function creation detected',
      },
      {
        pattern: /\.innerHTML\s*=/g,
        message: 'Direct innerHTML manipulation - XSS risk',
      },
      {
        pattern: /document\.write/g,
        message: 'document.write usage - potential security issue',
      },
    ];

    for (const { pattern, message } of suspiciousPatterns) {
      if (pattern.test(code)) {
        result.valid = false;
        result.checks.push({
          passed: false,
          message,
          severity: 'error',
        });
      }
    }

    // Check for obfuscation
    const obfuscationIndicators = [
      /\\x[0-9a-f]{2}/gi, // Hex escape sequences
      /\\u[0-9a-f]{4}/gi, // Unicode escape sequences
      /String\.fromCharCode/g,
      /_0x[a-f0-9]{4,}/g, // Common obfuscation variable names
    ];

    for (const pattern of obfuscationIndicators) {
      const matches = code.match(pattern);
      if (matches && matches.length > 5) {
        result.warnings.push({
          message: 'Possible code obfuscation detected',
          count: matches.length,
        });
      }
    }

    // Calculate integrity hash
    result.integrity = {
      sha256: createHash('sha256').update(code).digest('hex'),
      length: code.length,
      lines: code.split('\n').length,
    };

    if (result.checks.length === 0) {
      result.checks.push({
        passed: true,
        message: 'No suspicious patterns detected',
      });
    }

    return result;
  }

  /**
   * Check for unreachable code
   */
  _checkUnreachableCode(code, warnings) {
    const unreachablePatterns = [/return\s+[^;]+;[\s\S]*?(?=\})/g];

    for (const pattern of unreachablePatterns) {
      const matches = code.match(pattern);
      if (matches) {
        for (const match of matches) {
          const afterReturn = match.split('return')[1];
          if (
            afterReturn?.includes('\n') &&
            /[a-z]/i.test(afterReturn.split('\n').slice(1).join('\n'))
          ) {
            warnings.push({
              message: 'Potential unreachable code after return statement',
            });
          }
        }
      }
    }
  }

  /**
   * Check for infinite loops
   */
  _checkInfiniteLoops(code, result) {
    const infiniteLoopPatterns = [
      /while\s*\(\s*true\s*\)\s*\{[^}]*\}/g,
      /for\s*\(\s*;\s*;\s*\)\s*\{[^}]*\}/g,
    ];

    for (const pattern of infiniteLoopPatterns) {
      const matches = code.match(pattern);
      if (matches) {
        for (const match of matches) {
          if (!match.includes('break') && !match.includes('return')) {
            result.valid = false;
            result.checks.push({
              passed: false,
              message: 'Potential infinite loop without break/return',
              severity: 'error',
            });
          }
        }
      }
    }
  }

  /**
   * Check for variable shadowing
   */
  _checkVariableShadowing(code, warnings) {
    const functionScopes = code.match(/function\s+\w+\s*\([^)]*\)\s*\{/g) || [];
    if (functionScopes.length > 0) {
      const varNames = new Set();
      const shadowedVars = [];

      const varDeclarations = code.match(/(?:var|let|const)\s+(\w+)/g) || [];
      for (const decl of varDeclarations) {
        const varName = decl.split(/\s+/)[1];
        if (varNames.has(varName)) {
          shadowedVars.push(varName);
        }
        varNames.add(varName);
      }

      if (shadowedVars.length > 0) {
        warnings.push({
          message: `Variable shadowing detected: ${shadowedVars.join(', ')}`,
        });
      }
    }
  }

  /**
   * Validate code logic
   */
  _validateLogic(code) {
    const result = {
      valid: true,
      checks: [],
      warnings: [],
    };

    // Check for logical inconsistencies
    this._checkUnreachableCode(code, result.warnings);

    // Empty catch blocks
    if (/catch\s*\([^)]*\)\s*\{\s*\}/.test(code)) {
      result.warnings.push({
        message: 'Empty catch block found - errors may be silently ignored',
      });
    }

    this._checkInfiniteLoops(code, result);

    // Equality comparisons
    if (/==(?!=)/.test(code) || /!=(?!=)/.test(code)) {
      result.warnings.push({
        message: 'Loose equality (==, !=) used - consider strict equality (===, !==)',
      });
    }

    // Unhandled promises
    const promisePattern = /new\s+Promise\s*\([^)]*\)|\.then\s*\([^)]*\)/g;
    const catchPattern = /\.catch\s*\([^)]*\)/g;
    const promiseCount = (code.match(promisePattern) || []).length;
    const catchCount = (code.match(catchPattern) || []).length;

    if (promiseCount > catchCount * 2) {
      result.warnings.push({
        message: 'Some promises may lack error handling',
      });
    }

    this._checkVariableShadowing(code, result.warnings);

    if (result.checks.length === 0) {
      result.checks.push({
        passed: true,
        message: 'No critical logic issues detected',
      });
    }

    return result;
  }

  /**
   * Check indentation consistency
   */
  _checkIndentation(code, warnings) {
    const lines = code.split('\n');
    const indentations = lines
      .filter((line) => line.trim().length > 0)
      .map((line) => line.match(/^(\s*)/)[0].length);

    const spaceCounts = indentations.filter((i) => i > 0);
    if (spaceCounts.length > 0) {
      const gcd = spaceCounts.reduce((a, b) => {
        while (b !== 0) {
          const temp = b;
          b = a % b;
          a = temp;
        }
        return a;
      });

      if (gcd !== 2 && gcd !== 4) {
        warnings.push({
          message: `Inconsistent indentation detected (GCD: ${gcd})`,
        });
      }
    }
  }

  /**
   * Check naming convention consistency
   */
  _checkNamingConventions(code, warnings) {
    const functionNames = (code.match(/function\s+(\w+)|const\s+(\w+)\s*=/g) || [])
      .map((m) => m.match(/\w+$/)?.[0])
      .filter(Boolean);

    if (functionNames.length > 0) {
      const camelCaseCount = functionNames.filter((name) =>
        /^[a-z][a-zA-Z0-9]*$/.test(name)
      ).length;
      const snakeCaseCount = functionNames.filter((name) => /^[a-z][a-z0-9_]*$/.test(name)).length;

      if (
        camelCaseCount > 0 &&
        snakeCaseCount > 0 &&
        Math.abs(camelCaseCount - snakeCaseCount) < functionNames.length * 0.8
      ) {
        warnings.push({
          message: 'Mixed naming conventions detected (camelCase vs snake_case)',
        });
      }
    }
  }

  /**
   * Check quote style consistency
   */
  _checkQuoteStyle(code, warnings) {
    const singleQuotes = (code.match(/'/g) || []).length;
    const doubleQuotes = (code.match(/"/g) || []).length;
    const backticks = (code.match(/`/g) || []).length;

    const totalQuotes = singleQuotes + doubleQuotes + backticks;
    if (totalQuotes > 10) {
      const quoteCounts = [singleQuotes, doubleQuotes, backticks];
      const maxCount = Math.max(...quoteCounts);

      if (maxCount < totalQuotes * 0.7) {
        warnings.push({
          message: 'Inconsistent quote style detected',
        });
      }
    }
  }

  /**
   * Validate code consistency
   */
  _validateConsistency(code) {
    const result = {
      valid: true,
      checks: [],
      warnings: [],
    };

    const lines = code.split('\n');

    this._checkIndentation(code, result.warnings);
    this._checkNamingConventions(code, result.warnings);
    this._checkQuoteStyle(code, result.warnings);

    // Consistent semicolon usage
    const linesWithCode = lines.filter((line) => {
      const trimmed = line.trim();
      return (
        trimmed.length > 0 &&
        !trimmed.startsWith('//') &&
        !trimmed.startsWith('/*') &&
        !trimmed.startsWith('*') &&
        !trimmed.endsWith('{') &&
        !trimmed.endsWith('}')
      );
    });

    const linesWithSemicolon = linesWithCode.filter((line) => line.trim().endsWith(';')).length;
    const semicolonRatio = linesWithSemicolon / linesWithCode.length;

    if (semicolonRatio > 0.2 && semicolonRatio < 0.8) {
      result.warnings.push({
        message: 'Inconsistent semicolon usage detected',
      });
    }

    result.checks.push({
      passed: true,
      message: 'Consistency checks completed',
    });

    return result;
  }

  /**
   * Validate code patterns
   */
  _validatePatterns(code) {
    const result = {
      valid: true,
      checks: [],
      warnings: [],
    };

    // 1. Error handling patterns
    const tryBlocks = (code.match(/try\s*\{/g) || []).length;
    const catchBlocks = (code.match(/catch\s*\(/g) || []).length;

    if (tryBlocks !== catchBlocks) {
      result.valid = false;
      result.checks.push({
        passed: false,
        message: 'Mismatched try-catch blocks',
        severity: 'error',
      });
    }

    // 2. Async/await patterns
    const asyncFunctions = (code.match(/async\s+function|async\s*\(/g) || []).length;
    const awaitCalls = (code.match(/await\s+/g) || []).length;

    if (asyncFunctions > 0 && awaitCalls === 0) {
      result.warnings.push({
        message: 'Async functions without await - consider if async is necessary',
      });
    }

    // 3. Callback hell detection
    const nestedCallbacks = code.match(
      /function\s*\([^)]*\)\s*\{[^}]*function\s*\([^)]*\)\s*\{[^}]*function\s*\(/g
    );
    if (nestedCallbacks && nestedCallbacks.length > 0) {
      result.warnings.push({
        message: 'Deeply nested callbacks detected - consider using async/await',
      });
    }

    // 4. Resource cleanup patterns
    if (/setInterval\s*\(/.test(code) && !/clearInterval/.test(code)) {
      result.warnings.push({
        message: 'setInterval without clearInterval - potential memory leak',
      });
    }

    if (/addEventListener\s*\(/.test(code) && !/removeEventListener/.test(code)) {
      result.warnings.push({
        message: 'addEventListener without removeEventListener - potential memory leak',
      });
    }

    if (result.checks.length === 0) {
      result.checks.push({
        passed: true,
        message: 'Code patterns are acceptable',
      });
    }

    return result;
  }

  /**
   * Validate dependencies
   */
  _validateDependencies(code) {
    const result = {
      valid: true,
      checks: [],
      warnings: [],
      imports: [],
      requires: [],
    };

    // Extract imports
    const importMatches = code.matchAll(/import\s+(?:{[^}]+}|\w+)\s+from\s+['"]([^'"]+)['"]/g);
    for (const match of importMatches) {
      result.imports.push(match[1]);
    }

    // Extract requires
    const requireMatches = code.matchAll(/require\s*\(\s*['"]([^'"]+)['"]\s*\)/g);
    for (const match of requireMatches) {
      result.requires.push(match[1]);
    }

    // Check for mixed import styles
    if (result.imports.length > 0 && result.requires.length > 0) {
      result.warnings.push({
        message: 'Mixed import styles (ES6 import and CommonJS require)',
      });
    }

    // Check for relative imports
    const relativeImports = [...result.imports, ...result.requires].filter(
      (dep) => dep.startsWith('./') || dep.startsWith('../')
    );

    if (relativeImports.length > 10) {
      result.warnings.push({
        message: `Many relative imports (${relativeImports.length}) - consider module aliases`,
      });
    }

    result.checks.push({
      passed: true,
      message: `Found ${result.imports.length + result.requires.length} dependencies`,
    });

    return result;
  }
}

/**
 * Main execution
 */
function main() {
  const validator = new LogicValidator();

  // Example usage
  const testCode = `
    function example(x) {
      if (x == 0) {
        return "zero";
      }
      return "non-zero";
    }
  `;

  const results = validator.validate(testCode);

  console.warn('\n=== Logic Validation ===\n');
  console.info(`Overall: ${results.valid ? '✓ VALID' : '✗ INVALID'}`);
  console.info(`Score: ${results.score}/100`);
  console.info(`Passed: ${results.summary.passed}/${results.summary.totalChecks}`);
  console.warn(`Warnings: ${results.summary.warnings}`);

  for (const [checkName, checkResult] of Object.entries(results.checks)) {
    console.warn(`\n--- ${checkName.toUpperCase()} ---`);
    for (const check of checkResult.checks) {
      const status = check.passed ? '✓' : '✗';
      console.warn(`${status} ${check.message}`);
    }
    if (checkResult.warnings?.length > 0) {
      console.warn('\nWarnings:');
      for (const warning of checkResult.warnings) {
        console.warn(`⚠ ${warning.message}`);
      }
    }
  }
}

// Run if executed directly
try {
  main();
} catch (error) {
  console.error('Fatal error:', error);
  process.exit(1);
}

export { LogicValidator };
