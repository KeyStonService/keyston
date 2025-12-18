#!/usr/bin/env node

/**
 * Test Generator MCP Server
 * Enterprise-grade test generation for unit, integration, and e2e tests
 *
 * @module test-generator
 * @author SynergyMesh Team
 * @license MIT
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Validation schemas
const GenerateUnitTestsSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  _framework: z.enum(['jest', 'mocha', 'vitest']).optional().default('jest'),
  coverage: z.enum(['basic', 'comprehensive', 'exhaustive']).optional().default('comprehensive'),
});

const GenerateIntegrationTestsSchema = z.object({
  endpoints: z
    .array(
      z.object({
        method: z.string(),
        path: z.string(),
        description: z.string().optional(),
      })
    )
    .min(1, 'At least one endpoint is required'),
  _framework: z.enum(['jest', 'supertest', 'chai']).optional().default('jest'),
});

const GenerateE2ETestsSchema = z.object({
  scenarios: z
    .array(
      z.object({
        name: z.string(),
        steps: z.array(z.string()),
        assertions: z.array(z.string()).optional(),
      })
    )
    .min(1, 'At least one scenario is required'),
  _framework: z.enum(['playwright', 'cypress', 'puppeteer']).optional().default('playwright'),
});

/**
 * Test generation engine
 */
class TestGenerator {
  /**
   * Generate unit tests
   */
  generateUnitTests(code, _framework = 'jest', coverage = 'comprehensive') {
    const functions = this._extractFunctions(code);
    const classes = this._extractClasses(code);

    const tests = {
      _framework,
      totalTests: 0,
      testSuites: [],
    };

    // Generate tests for functions
    for (const func of functions) {
      const suite = this._generateFunctionTests(func, _framework, coverage);
      tests.testSuites.push(suite);
      tests.totalTests += suite.tests.length;
    }

    // Generate tests for classes
    for (const cls of classes) {
      const suite = this._generateClassTests(cls, _framework, coverage);
      tests.testSuites.push(suite);
      tests.totalTests += suite.tests.length;
    }

    tests.code = this._generateTestCode(tests, _framework);

    return tests;
  }

  /**
   * Generate integration tests
   */
  generateIntegrationTests(endpoints, _framework = 'jest') {
    const tests = {
      _framework,
      totalTests: 0,
      testSuites: [],
    };

    // Group endpoints by resource
    const grouped = this._groupEndpointsByResource(endpoints);

    for (const [resource, resourceEndpoints] of Object.entries(grouped)) {
      const suite = this._generateEndpointTests(resource, resourceEndpoints, _framework);
      tests.testSuites.push(suite);
      tests.totalTests += suite.tests.length;
    }

    tests.code = this._generateIntegrationTestCode(tests, _framework);

    return tests;
  }

  /**
   * Generate end-to-end tests
   */
  generateE2ETests(scenarios, _framework = 'playwright') {
    const tests = {
      _framework,
      totalTests: scenarios.length,
      testSuites: [],
    };

    for (const scenario of scenarios) {
      const suite = this._generateScenarioTest(scenario, _framework);
      tests.testSuites.push(suite);
    }

    tests.code = this._generateE2ETestCode(tests, _framework);

    return tests;
  }

  // Private helper methods

  _extractFunctions(code) {
    const functions = [];
    const functionRegex =
      /(?:function\s+(\w+)\s*\([^)]*\)|const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)/g;

    let match;
    while ((match = functionRegex.exec(code)) !== null) {
      const name = match[1] || match[2];
      const startIndex = match.index;
      const params = this._extractParameters(code, startIndex);

      functions.push({
        name,
        params,
        isAsync: code.substring(startIndex, startIndex + 50).includes('async'),
      });
    }

    return functions;
  }

  _extractClasses(code) {
    const classes = [];
    const classRegex = /class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{/g;

    let match;
    while ((match = classRegex.exec(code)) !== null) {
      const name = match[1];
      const parent = match[2];
      const methods = this._extractClassMethods(code, match.index);

      classes.push({
        name,
        parent,
        methods,
      });
    }

    return classes;
  }

  _extractParameters(code, startIndex) {
    const paramMatch = code.substring(startIndex).match(/\(([^)]*)\)/);
    if (!paramMatch) {
      return [];
    }

    return paramMatch[1]
      .split(',')
      .map((p) => p.trim())
      .filter((p) => p.length > 0)
      .map((p) => {
        const [name, defaultValue] = p.split('=').map((s) => s.trim());
        return { name, hasDefault: Boolean(defaultValue) };
      });
  }

  _extractClassMethods(code, classStartIndex) {
    const methods = [];
    const classCode = code.substring(classStartIndex);
    const methodRegex = /(?:async\s+)?(\w+)\s*\([^)]*\)\s*{/g;

    let match;
    let depth = 0;
    let foundClassOpen = false;

    for (let i = 0; i < classCode.length; i++) {
      if (classCode[i] === '{') {
        if (!foundClassOpen) {
          foundClassOpen = true;
        } else {
          depth++;
        }
      } else if (classCode[i] === '}') {
        if (depth === 0) {
          break;
        }
        depth--;
      }
    }

    const classBody = classCode.substring(0, classCode.indexOf('}', classCode.indexOf('{') + 1));

    while ((match = methodRegex.exec(classBody)) !== null) {
      const name = match[1];
      if (name !== 'constructor') {
        methods.push({
          name,
          isAsync: classBody.substring(match.index, match.index + 10).includes('async'),
        });
      }
    }

    return methods;
  }

  _generateFunctionTests(func, _framework, coverage) {
    const tests = [];

    // Happy path test
    tests.push({
      name: `should ${func.name} successfully with valid input`,
      type: 'happy-path',
      code: this._generateHappyPathTest(func, _framework),
    });

    if (coverage !== 'basic') {
      // Edge case tests
      tests.push({
        name: `should handle edge cases for ${func.name}`,
        type: 'edge-case',
        code: this._generateEdgeCaseTest(func, _framework),
      });

      // Error handling tests
      tests.push({
        name: `should handle errors in ${func.name}`,
        type: 'error-handling',
        code: this._generateErrorTest(func, _framework),
      });
    }

    if (coverage === 'exhaustive') {
      // Parameter validation tests
      for (const param of func.params) {
        tests.push({
          name: `should validate ${param.name} parameter`,
          type: 'validation',
          code: this._generateValidationTest(func, param, _framework),
        });
      }
    }

    return {
      name: func.name,
      type: 'function',
      tests,
    };
  }

  _generateClassTests(cls, _framework, coverage) {
    const tests = [];

    // Constructor test
    tests.push({
      name: `should create instance of ${cls.name}`,
      type: 'constructor',
      code: this._generateConstructorTest(cls, _framework),
    });

    // Method tests
    for (const method of cls.methods) {
      tests.push({
        name: `should ${method.name} correctly`,
        type: 'method',
        code: this._generateMethodTest(cls, method, _framework),
      });

      if (coverage !== 'basic') {
        tests.push({
          name: `should handle ${method.name} errors`,
          type: 'error-handling',
          code: this._generateMethodErrorTest(cls, method, _framework),
        });
      }
    }

    return {
      name: cls.name,
      type: 'class',
      tests,
    };
  }

  _generateHappyPathTest(func, _framework) {
    const testParams = func.params.map((p) => `'test-${p.name}'`).join(', ');

    return `test('${func.name} should work with valid input', ${func.isAsync ? 'async ' : ''}() => {
  const result = ${func.isAsync ? 'await ' : ''}${func.name}(${testParams});
  expect(result).toBeDefined();
  expect(result).not.toBeNull();
});`;
  }

  _generateEdgeCaseTest(func, _framework) {
    return `test('${func.name} should handle edge cases', ${func.isAsync ? 'async ' : ''}() => {
  // Test with empty values
  const result1 = ${func.isAsync ? 'await ' : ''}${func.name}(${func.params.map(() => "''").join(', ')});
  expect(result1).toBeDefined();
  
  // Test with boundary values
  const result2 = ${func.isAsync ? 'await ' : ''}${func.name}(${func.params.map(() => '0').join(', ')});
  expect(result2).toBeDefined();
});`;
  }

  _generateErrorTest(func, _framework) {
    return `test('${func.name} should handle errors gracefully', ${func.isAsync ? 'async ' : ''}() => {
  ${func.isAsync ? 'await ' : ''}expect(${func.isAsync ? 'async () => ' : ''}${func.name}(${func.params.map(() => 'null').join(', ')}))${func.isAsync ? '.rejects' : ''}.toThrow();
});`;
  }

  _generateValidationTest(func, param, _framework) {
    return `test('${func.name} should validate ${param.name} parameter', ${func.isAsync ? 'async ' : ''}() => {
  const invalidValues = [null, undefined, '', 0, false];
  
  for (const value of invalidValues) {
    ${func.isAsync ? 'await ' : ''}expect(${func.isAsync ? 'async () => ' : ''}${func.name}(value))${func.isAsync ? '.rejects' : ''}.toThrow();
  }
});`;
  }

  _generateConstructorTest(cls, _framework) {
    return `test('should create ${cls.name} instance', () => {
  const instance = new ${cls.name}();
  expect(instance).toBeInstanceOf(${cls.name});
  ${cls.parent ? `expect(instance).toBeInstanceOf(${cls.parent});` : ''}
});`;
  }

  _generateMethodTest(cls, method, _framework) {
    return `test('${cls.name}.${method.name} should work correctly', ${method.isAsync ? 'async ' : ''}() => {
  const instance = new ${cls.name}();
  const result = ${method.isAsync ? 'await ' : ''}instance.${method.name}();
  expect(result).toBeDefined();
});`;
  }

  _generateMethodErrorTest(cls, method, _framework) {
    return `test('${cls.name}.${method.name} should handle errors', ${method.isAsync ? 'async ' : ''}() => {
  const instance = new ${cls.name}();
  ${method.isAsync ? 'await ' : ''}expect(${method.isAsync ? 'async () => ' : ''}instance.${method.name}(null))${method.isAsync ? '.rejects' : ''}.toThrow();
});`;
  }

  _groupEndpointsByResource(endpoints) {
    const grouped = {};

    for (const endpoint of endpoints) {
      const resource = endpoint.path.split('/')[1] || 'root';
      if (!grouped[resource]) {
        grouped[resource] = [];
      }
      grouped[resource].push(endpoint);
    }

    return grouped;
  }

  _generateEndpointTests(resource, endpoints, _framework) {
    const tests = [];

    for (const endpoint of endpoints) {
      // Success test
      tests.push({
        name: `${endpoint.method} ${endpoint.path} should return 200`,
        type: 'success',
        code: this._generateEndpointSuccessTest(endpoint, _framework),
      });

      // Error test
      tests.push({
        name: `${endpoint.method} ${endpoint.path} should handle errors`,
        type: 'error',
        code: this._generateEndpointErrorTest(endpoint, _framework),
      });

      // Validation test
      if (['POST', 'PUT', 'PATCH'].includes(endpoint.method.toUpperCase())) {
        tests.push({
          name: `${endpoint.method} ${endpoint.path} should validate input`,
          type: 'validation',
          code: this._generateEndpointValidationTest(endpoint, _framework),
        });
      }
    }

    return {
      name: resource,
      type: 'integration',
      tests,
    };
  }

  _generateEndpointSuccessTest(endpoint, _framework) {
    const method = endpoint.method.toLowerCase();
    return `test('${endpoint.method} ${endpoint.path} should succeed', async () => {
  const response = await request(app)
    .${method}('${endpoint.path}')
    ${['post', 'put', 'patch'].includes(method) ? '.send({ /* test data */ })' : ''}
    .expect(200);
    
  expect(response.body).toBeDefined();
  expect(response.body.success).toBe(true);
});`;
  }

  _generateEndpointErrorTest(endpoint, _framework) {
    return `test('${endpoint.method} ${endpoint.path} should handle errors', async () => {
  const response = await request(app)
    .${endpoint.method.toLowerCase()}('${endpoint.path}')
    .send({ /* invalid data */ })
    .expect(400);
    
  expect(response.body.error).toBeDefined();
});`;
  }

  _generateEndpointValidationTest(endpoint, _framework) {
    return `test('${endpoint.method} ${endpoint.path} should validate input', async () => {
  const invalidData = {};
  
  const response = await request(app)
    .${endpoint.method.toLowerCase()}('${endpoint.path}')
    .send(invalidData)
    .expect(400);
    
  expect(response.body.error).toMatch(/validation/i);
});`;
  }

  _generateScenarioTest(scenario, _framework) {
    const steps = scenario.steps
      .map(
        (step, index) =>
          `  // Step ${index + 1}: ${step}\n  await page.click('/* selector */');\n  await page.waitForTimeout(1000);`
      )
      .join('\n');

    const assertions =
      scenario.assertions
        ?.map(
          (assertion) =>
            `  expect(await page.textContent('/* selector */')).toContain('${assertion}');`
        )
        .join('\n') || '  // Add assertions';

    return {
      name: scenario.name,
      type: 'e2e',
      tests: [
        {
          name: scenario.name,
          type: 'scenario',
          code: `test('${scenario.name}', async ({ page }) => {
${steps}

${assertions}
});`,
        },
      ],
    };
  }

  _generateTestCode(tests, _framework) {
    const imports = this._getFrameworkImports(_framework);
    const suites = tests.testSuites
      .map(
        (suite) =>
          `describe('${suite.name}', () => {
${suite.tests.map((t) => '  ' + t.code).join('\n\n')}
});`
      )
      .join('\n\n');

    return `${imports}\n\n${suites}`;
  }

  _generateIntegrationTestCode(tests, _framework) {
    const imports = `import request from 'supertest';
import { app } from '../server';

`;
    const suites = tests.testSuites
      .map(
        (suite) =>
          `describe('${suite.name} endpoints', () => {
${suite.tests.map((t) => '  ' + t.code).join('\n\n')}
});`
      )
      .join('\n\n');

    return `${imports}\n${suites}`;
  }

  _generateE2ETestCode(tests, _framework) {
    const imports =
      _framework === 'playwright'
        ? "import { test, expect } from '@playwright/test';\n\n"
        : "import { describe, it, expect } from 'vitest';\n\n";

    const suites = tests.testSuites
      .map((suite) => suite.tests.map((t) => t.code).join('\n\n'))
      .join('\n\n');

    return `${imports}${suites}`;
  }

  _getFrameworkImports(_framework) {
    const imports = {
      jest: "import { describe, test, expect } from '@jest/globals';",
      mocha: "import { describe, it } from 'mocha';\nimport { expect } from 'chai';",
      vitest: "import { describe, test, expect } from 'vitest';",
    };

    return imports[_framework] || imports.jest;
  }
}

/**
 * Handle tool execution requests
 */
function handleToolCall(generator, name, args) {
  switch (name) {
    case 'generate-unit-tests': {
      const validated = GenerateUnitTestsSchema.parse(args);
      const result = generator.generateUnitTests(
        validated.code,
        validated._framework,
        validated.coverage
      );
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    case 'generate-integration-tests': {
      const validated = GenerateIntegrationTestsSchema.parse(args);
      const result = generator.generateIntegrationTests(validated.endpoints, validated._framework);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    case 'generate-e2e-tests': {
      const validated = GenerateE2ETestsSchema.parse(args);
      const result = generator.generateE2ETests(validated.scenarios, validated._framework);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Get tool definitions for the test generator
 */
function getToolDefinitions() {
  return [
    {
      name: 'generate-unit-tests',
      description: 'Generate comprehensive unit tests for functions and classes',
      inputSchema: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'The source code to generate tests for',
          },
          framework: {
            type: 'string',
            enum: ['jest', 'mocha', 'vitest'],
            description: 'Testing framework',
            default: 'jest',
          },
          coverage: {
            type: 'string',
            enum: ['basic', 'comprehensive', 'exhaustive'],
            description: 'Test coverage level',
            default: 'comprehensive',
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'generate-integration-tests',
      description: 'Generate integration tests for API endpoints',
      inputSchema: {
        type: 'object',
        properties: {
          endpoints: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                method: { type: 'string' },
                path: { type: 'string' },
                description: { type: 'string' },
              },
              required: ['method', 'path'],
            },
            description: 'API endpoints to test',
          },
          framework: {
            type: 'string',
            enum: ['jest', 'supertest', 'chai'],
            description: 'Testing framework',
            default: 'jest',
          },
        },
        required: ['endpoints'],
      },
    },
    {
      name: 'generate-e2e-tests',
      description: 'Generate end-to-end tests from user scenarios',
      inputSchema: {
        type: 'object',
        properties: {
          scenarios: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                steps: {
                  type: 'array',
                  items: { type: 'string' },
                },
                assertions: {
                  type: 'array',
                  items: { type: 'string' },
                },
              },
              required: ['name', 'steps'],
            },
            description: 'Test scenarios to implement',
          },
          framework: {
            type: 'string',
            enum: ['playwright', 'cypress', 'puppeteer'],
            description: 'E2E testing framework',
            default: 'playwright',
          },
        },
        required: ['scenarios'],
      },
    },
  ];
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  const generator = new TestGenerator();
  const server = new Server(
    {
      name: 'test-generator',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, () => ({
    tools: getToolDefinitions(),
  }));

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, (request) => {
    const { name, arguments: args } = request.params;

    try {
      return handleToolCall(generator, name, args);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `Invalid parameters: ${error.errors.map((e) => e.message).join(', ')}`
        );
      }
      if (error instanceof McpError) {
        throw error;
      }
      throw new McpError(
        ErrorCode.InternalError,
        `Tool execution failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  });

  // Start the server
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Test Generator MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
