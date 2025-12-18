#!/usr/bin/env node

/**
 * Documentation Generator MCP Server
 * Enterprise-grade documentation generation for JSDoc, API docs, and guides
 *
 * @module doc-generator
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
const GenerateJSDocSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  style: z.enum(['standard', 'google', 'typescript']).optional().default('standard'),
});

const GenerateAPIDocsSchema = z.object({
  endpoints: z
    .array(
      z.object({
        method: z.string(),
        path: z.string(),
        description: z.string().optional(),
        parameters: z.array(z.any()).optional(),
        responses: z.array(z.any()).optional(),
      })
    )
    .min(1, 'At least one endpoint is required'),
  format: z.enum(['markdown', 'openapi', 'postman']).optional().default('markdown'),
});

const GenerateGuidesSchema = z.object({
  topic: z.string().min(1, 'Topic is required'),
  sections: z.array(z.string()).optional(),
  audience: z.enum(['developer', 'user', 'admin']).optional().default('developer'),
});

/**
 * Documentation generation engine
 */
class DocGenerator {
  /**
   * Generate JSDoc documentation
   */
  generateJSDoc(code, style = 'standard') {
    const functions = this._extractFunctions(code);
    const classes = this._extractClasses(code);

    const docs = {
      style,
      functions: functions.map((f) => this._generateFunctionDoc(f, style)),
      classes: classes.map((c) => this._generateClassDoc(c, style)),
      summary: {
        totalFunctions: functions.length,
        totalClasses: classes.length,
        documentedFunctions: 0,
        documentedClasses: 0,
      },
    };

    return docs;
  }

  /**
   * Generate API documentation
   */
  generateAPIDocs(endpoints, format = 'markdown') {
    const docs = {
      format,
      title: 'API Documentation',
      version: '1.0.0',
      baseUrl: '/api',
      endpoints: endpoints.map((e) => this._generateEndpointDoc(e, format)),
    };

    if (format === 'markdown') {
      docs.markdown = this._generateMarkdownDocs(docs);
    } else if (format === 'openapi') {
      docs.openapi = this._generateOpenAPISpec(docs);
    }

    return docs;
  }

  /**
   * Generate development guides
   */
  generateGuides(topic, sections = [], audience = 'developer') {
    const guide = {
      topic,
      audience,
      sections: sections.length > 0 ? sections : this._suggestSections(topic, audience),
      content: {},
    };

    for (const section of guide.sections) {
      guide.content[section] = this._generateSectionContent(topic, section, audience);
    }

    guide.markdown = this._formatGuideAsMarkdown(guide);

    return guide;
  }

  // Private helper methods

  _extractFunctions(code) {
    const functions = [];
    const functionRegex =
      /(?:\/\*\*[\s\S]*?\*\/)?\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)|(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>/g;

    let match;
    while ((match = functionRegex.exec(code)) !== null) {
      const name = match[1] || match[3];
      const params = (match[2] || match[4])
        .split(',')
        .map((p) => p.trim())
        .filter((p) => p);
      const existingDoc = this._extractExistingDoc(code, match.index);

      functions.push({
        name,
        params: params.map((p) => this._parseParameter(p)),
        existingDoc,
        isAsync: match[0].includes('async'),
      });
    }

    return functions;
  }

  _extractClasses(code) {
    const classes = [];
    const classRegex =
      /(?:\/\*\*[\s\S]*?\*\/)?\s*(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{/g;

    let match;
    while ((match = classRegex.exec(code)) !== null) {
      const name = match[1];
      const parent = match[2];
      const existingDoc = this._extractExistingDoc(code, match.index);
      const methods = this._extractClassMethods(code, match.index);

      classes.push({
        name,
        parent,
        methods,
        existingDoc,
      });
    }

    return classes;
  }

  _extractExistingDoc(code, position) {
    const beforeCode = code.substring(Math.max(0, position - 500), position);
    const docMatch = beforeCode.match(/\/\*\*([\s\S]*?)\*\//);
    return docMatch ? docMatch[1].trim() : null;
  }

  _parseParameter(param) {
    const [name, defaultValue] = param.split('=').map((s) => s.trim());
    const typeMatch = name.match(/:\s*(\w+)/);

    return {
      name: name.replace(/:\s*\w+/, '').trim(),
      type: typeMatch ? typeMatch[1] : 'any',
      hasDefault: Boolean(defaultValue),
      defaultValue,
    };
  }

  _extractClassMethods(code, classStartIndex) {
    const methods = [];
    const classCode = code.substring(classStartIndex);
    const methodRegex = /(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*{/g;

    let match;
    while ((match = methodRegex.exec(classCode)) !== null) {
      if (
        classCode.indexOf('}', match.index) < classCode.indexOf('{', classCode.indexOf('{') + 1)
      ) {
        break;
      }

      methods.push({
        name: match[1],
        params: match[2]
          .split(',')
          .map((p) => p.trim())
          .filter((p) => p)
          .map((p) => this._parseParameter(p)),
        isAsync: match[0].includes('async'),
      });
    }

    return methods;
  }

  _generateFunctionDoc(func, style) {
    const doc = {
      name: func.name,
      description: func.existingDoc || `Function: ${func.name}`,
      params: func.params.map((p) => ({
        name: p.name,
        type: p.type,
        description: `${p.name} parameter`,
        optional: p.hasDefault,
        default: p.defaultValue,
      })),
      returns: {
        type: func.isAsync ? 'Promise<any>' : 'any',
        description: 'Return value',
      },
      jsdoc: this._formatJSDoc(func, style),
    };

    return doc;
  }

  _generateClassDoc(cls, style) {
    const doc = {
      name: cls.name,
      description: cls.existingDoc || `Class: ${cls.name}`,
      extends: cls.parent,
      methods: cls.methods.map((m) => this._generateFunctionDoc(m, style)),
      jsdoc: this._formatClassJSDoc(cls, style),
    };

    return doc;
  }

  _formatJSDoc(func, style) {
    const lines = ['/**', ` * ${func.existingDoc || `Function: ${func.name}`}`];

    if (style === 'typescript' || style === 'standard') {
      lines.push(' *');
      for (const param of func.params) {
        lines.push(` * @param {${param.type}} ${param.name} - ${param.name} parameter`);
      }
      lines.push(` * @returns {${func.isAsync ? 'Promise<any>' : 'any'}} Return value`);
    }

    if (style === 'google') {
      lines.push(' *');
      lines.push(' * @param {Object} params - Parameters');
      for (const param of func.params) {
        lines.push(` * @param {${param.type}} params.${param.name} - ${param.name} parameter`);
      }
    }

    lines.push(' */');
    return lines.join('\n');
  }

  _formatClassJSDoc(cls, _style) {
    const lines = ['/**', ` * ${cls.existingDoc || `Class: ${cls.name}`}`, ' *'];

    if (cls.parent) {
      lines.push(` * @extends ${cls.parent}`);
    }

    lines.push(' * @class');
    lines.push(' */');
    return lines.join('\n');
  }

  _generateEndpointDoc(endpoint, _format) {
    return {
      method: endpoint.method.toUpperCase(),
      path: endpoint.path,
      description: endpoint.description || `${endpoint.method.toUpperCase()} ${endpoint.path}`,
      parameters: endpoint.parameters || [],
      responses: endpoint.responses || [
        { status: 200, description: 'Success' },
        { status: 400, description: 'Bad Request' },
        { status: 500, description: 'Internal Server Error' },
      ],
      example: this._generateExampleRequest(endpoint),
    };
  }

  _generateExampleRequest(endpoint) {
    const method = endpoint.method.toUpperCase();
    const hasBody = ['POST', 'PUT', 'PATCH'].includes(method);

    return {
      curl: `curl -X ${method} '${endpoint.path}'${hasBody ? " -H 'Content-Type: application/json' -d '{}'" : ''}`,
      javascript: `fetch('${endpoint.path}', {
  method: '${method}'${hasBody ? ",\n  headers: { 'Content-Type': 'application/json' },\n  body: JSON.stringify({})" : ''}
})`,
    };
  }

  _generateMarkdownDocs(docs) {
    let md = `# ${docs.title}\n\n`;
    md += `Version: ${docs.version}\n\n`;
    md += `Base URL: \`${docs.baseUrl}\`\n\n`;
    md += `## Endpoints\n\n`;

    for (const endpoint of docs.endpoints) {
      md += `### ${endpoint.method} ${endpoint.path}\n\n`;
      md += `${endpoint.description}\n\n`;

      if (endpoint.parameters.length > 0) {
        md += `#### Parameters\n\n`;
        for (const param of endpoint.parameters) {
          md += `- \`${param.name}\` (${param.type}): ${param.description}\n`;
        }
        md += '\n';
      }

      md += `#### Responses\n\n`;
      for (const response of endpoint.responses) {
        md += `- \`${response.status}\`: ${response.description}\n`;
      }
      md += '\n';

      md += `#### Example\n\n`;
      md += '```bash\n';
      md += endpoint.example.curl + '\n';
      md += '```\n\n';
    }

    return md;
  }

  _generateOpenAPISpec(docs) {
    const spec = {
      openapi: '3.0.0',
      info: {
        title: docs.title,
        version: docs.version,
      },
      servers: [{ url: docs.baseUrl }],
      paths: {},
    };

    for (const endpoint of docs.endpoints) {
      if (!spec.paths[endpoint.path]) {
        spec.paths[endpoint.path] = {};
      }

      spec.paths[endpoint.path][endpoint.method.toLowerCase()] = {
        summary: endpoint.description,
        responses: endpoint.responses.reduce((acc, r) => {
          acc[r.status] = { description: r.description };
          return acc;
        }, {}),
      };
    }

    return spec;
  }

  _suggestSections(topic, audience) {
    const commonSections = [
      'Overview',
      'Getting Started',
      'Installation',
      'Configuration',
      'Usage Examples',
      'API Reference',
      'Troubleshooting',
      'FAQ',
    ];

    if (audience === 'developer') {
      return [...commonSections, 'Architecture', 'Development Setup', 'Testing', 'Contributing'];
    } else if (audience === 'admin') {
      return [
        'Overview',
        'Installation',
        'Configuration',
        'Deployment',
        'Monitoring',
        'Security',
        'Backup and Recovery',
        'Troubleshooting',
      ];
    } else {
      return [
        'Overview',
        'Getting Started',
        'Basic Usage',
        'Features',
        'Examples',
        'FAQ',
        'Support',
      ];
    }
  }

  _generateSectionContent(topic, section, audience) {
    const templates = {
      Overview: `# Overview\n\nThis guide covers ${topic} for ${audience}s.\n\n## Key Features\n\n- Feature 1\n- Feature 2\n- Feature 3`,
      'Getting Started': `# Getting Started\n\n## Prerequisites\n\n- Requirement 1\n- Requirement 2\n\n## Quick Start\n\n\`\`\`bash\nnpm install\nnpm start\n\`\`\``,
      Installation: `# Installation\n\n## System Requirements\n\n- Node.js >= 18.0.0\n- npm >= 8.0.0\n\n## Install Steps\n\n\`\`\`bash\nnpm install ${topic}\n\`\`\``,
      'Usage Examples': `# Usage Examples\n\n## Basic Example\n\n\`\`\`javascript\n// Example code here\n\`\`\`\n\n## Advanced Example\n\n\`\`\`javascript\n// Advanced example here\n\`\`\``,
    };

    return templates[section] || `# ${section}\n\nContent for ${section} section.`;
  }

  _formatGuideAsMarkdown(guide) {
    let md = `# ${guide.topic} Guide\n\n`;
    md += `**Audience:** ${guide.audience}\n\n`;
    md += `## Table of Contents\n\n`;

    for (const section of guide.sections) {
      md += `- [${section}](#${section.toLowerCase().replace(/\s+/g, '-')})\n`;
    }

    md += '\n---\n\n';

    for (const section of guide.sections) {
      md += guide.content[section] + '\n\n';
    }

    return md;
  }
}

/**
 * Handle tool execution requests
 */
function handleToolCall(generator, name, args) {
  switch (name) {
    case 'generate-jsdoc': {
      const validated = GenerateJSDocSchema.parse(args);
      const result = generator.generateJSDoc(validated.code, validated.style);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'generate-api-docs': {
      const validated = GenerateAPIDocsSchema.parse(args);
      const result = generator.generateAPIDocs(validated.endpoints, validated.format);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'generate-guides': {
      const validated = GenerateGuidesSchema.parse(args);
      const result = generator.generateGuides(
        validated.topic,
        validated.sections,
        validated.audience
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Get tool definitions for the doc generator
 */
function getToolDefinitions() {
  return [
    {
      name: 'generate-jsdoc',
      description: 'Generate JSDoc documentation for functions and classes',
      inputSchema: {
        type: 'object',
        properties: {
          code: { type: 'string', description: 'Source code to document' },
          style: {
            type: 'string',
            enum: ['standard', 'google', 'typescript'],
            default: 'standard',
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'generate-api-docs',
      description: 'Generate API documentation in various formats',
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
          },
          format: {
            type: 'string',
            enum: ['markdown', 'openapi', 'postman'],
            default: 'markdown',
          },
        },
        required: ['endpoints'],
      },
    },
    {
      name: 'generate-guides',
      description: 'Generate comprehensive guides for different audiences',
      inputSchema: {
        type: 'object',
        properties: {
          topic: { type: 'string', description: 'Guide topic' },
          sections: {
            type: 'array',
            items: { type: 'string' },
          },
          audience: {
            type: 'string',
            enum: ['developer', 'user', 'admin'],
            default: 'developer',
          },
        },
        required: ['topic'],
      },
    },
  ];
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  const generator = new DocGenerator();
  const server = new Server(
    {
      name: 'doc-generator',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, () => ({
    tools: getToolDefinitions(),
  }));

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
        `Internal error: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Documentation Generator MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
