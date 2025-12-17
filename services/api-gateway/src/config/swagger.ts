import { config } from './index';

export const swaggerDocument = {
  openapi: '3.0.0',
  info: {
    title: 'Unmanned Island System API',
    version: '1.0.0',
    description: 'REST API for external integrations with the Unmanned Island System',
    contact: {
      name: 'API Support',
      email: 'api-support@machinenativeops.io'
    },
    license: {
      name: 'MIT',
      url: 'https://opensource.org/licenses/MIT'
    }
  },
  servers: [
    {
      url: `http://localhost:${config.port}`,
      description: 'Development server'
    },
    {
      url: 'https://api.machinenativeops.io',
      description: 'Production server'
    }
  ],
  tags: [
    {
      name: 'Authentication',
      description: 'User authentication and authorization'
    },
    {
      name: 'System',
      description: 'System operations and health checks'
    },
    {
      name: 'Resources',
      description: 'Resource management operations'
    },
    {
      name: 'Tasks',
      description: 'Task management and execution'
    },
    {
      name: 'Metrics',
      description: 'Monitoring and analytics'
    }
  ],
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: 'Enter JWT token'
      }
    },
    schemas: {
      Error: {
        type: 'object',
        properties: {
          error: {
            type: 'string',
            description: 'Error message'
          },
          message: {
            type: 'string',
            description: 'Detailed error description'
          }
        }
      },
      LoginRequest: {
        type: 'object',
        required: ['email', 'password'],
        properties: {
          email: {
            type: 'string',
            format: 'email',
            example: 'admin@example.com'
          },
          password: {
            type: 'string',
            format: 'password',
            example: 'password123'
          }
        }
      },
      LoginResponse: {
        type: 'object',
        properties: {
          token: {
            type: 'string',
            description: 'JWT access token'
          },
          expiresIn: {
            type: 'string',
            example: '1h'
          },
          user: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              email: { type: 'string' },
              role: { type: 'string' }
            }
          }
        }
      },
      HealthResponse: {
        type: 'object',
        properties: {
          status: {
            type: 'string',
            example: 'healthy'
          },
          timestamp: {
            type: 'string',
            format: 'date-time'
          },
          uptime: {
            type: 'number',
            description: 'Uptime in seconds'
          },
          memory: {
            type: 'object'
          },
          cpu: {
            type: 'object'
          },
          services: {
            type: 'object',
            properties: {
              database: { type: 'string' },
              cache: { type: 'string' },
              messageQueue: { type: 'string' }
            }
          }
        }
      },
      Resource: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          type: { type: 'string' },
          config: { type: 'object' },
          createdAt: {
            type: 'string',
            format: 'date-time'
          },
          updatedAt: {
            type: 'string',
            format: 'date-time'
          }
        }
      },
      Task: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          type: { type: 'string' },
          config: { type: 'object' },
          status: {
            type: 'string',
            enum: ['pending', 'running', 'completed', 'failed', 'cancelled']
          },
          createdAt: {
            type: 'string',
            format: 'date-time'
          },
          startedAt: {
            type: 'string',
            format: 'date-time',
            nullable: true
          },
          completedAt: {
            type: 'string',
            format: 'date-time',
            nullable: true
          },
          logs: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    }
  },
  paths: {
    '/health': {
      get: {
        tags: ['System'],
        summary: 'Health check endpoint',
        description: 'Check if the API is running and healthy',
        responses: {
          '200': {
            description: 'API is healthy',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/HealthResponse'
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/auth/login': {
      post: {
        tags: ['Authentication'],
        summary: 'User login',
        description: 'Authenticate user and receive JWT token',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/LoginRequest'
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Login successful',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/LoginResponse'
                }
              }
            }
          },
          '400': {
            description: 'Missing credentials',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Error'
                }
              }
            }
          },
          '401': {
            description: 'Invalid credentials',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Error'
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/auth/register': {
      post: {
        tags: ['Authentication'],
        summary: 'User registration',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/LoginRequest'
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'User registered successfully'
          },
          '409': {
            description: 'User already exists'
          }
        }
      }
    },
    '/api/v1/system/health': {
      get: {
        tags: ['System'],
        summary: 'Detailed system health check',
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'System health information',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/HealthResponse'
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/system/metrics': {
      get: {
        tags: ['System'],
        summary: 'Get system metrics',
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'System metrics',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    requests: {
                      type: 'object',
                      properties: {
                        total: { type: 'number' },
                        perMinute: { type: 'number' },
                        errorRate: { type: 'number' }
                      }
                    },
                    performance: {
                      type: 'object',
                      properties: {
                        avgResponseTime: { type: 'number' },
                        p95ResponseTime: { type: 'number' },
                        p99ResponseTime: { type: 'number' }
                      }
                    },
                    resources: {
                      type: 'object',
                      properties: {
                        cpu: { type: 'number' },
                        memory: { type: 'number' },
                        disk: { type: 'number' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/resources': {
      get: {
        tags: ['Resources'],
        summary: 'List all resources',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'limit',
            in: 'query',
            schema: { type: 'integer', default: 10 }
          },
          {
            name: 'offset',
            in: 'query',
            schema: { type: 'integer', default: 0 }
          }
        ],
        responses: {
          '200': {
            description: 'List of resources',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    data: {
                      type: 'array',
                      items: {
                        $ref: '#/components/schemas/Resource'
                      }
                    },
                    pagination: {
                      type: 'object',
                      properties: {
                        total: { type: 'number' },
                        limit: { type: 'number' },
                        offset: { type: 'number' },
                        hasMore: { type: 'boolean' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      post: {
        tags: ['Resources'],
        summary: 'Create a new resource',
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['name', 'type'],
                properties: {
                  name: { type: 'string' },
                  type: { type: 'string' },
                  config: { type: 'object' }
                }
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'Resource created',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Resource'
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/resources/{id}': {
      get: {
        tags: ['Resources'],
        summary: 'Get resource by ID',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' }
          }
        ],
        responses: {
          '200': {
            description: 'Resource details',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Resource'
                }
              }
            }
          },
          '404': {
            description: 'Resource not found'
          }
        }
      },
      put: {
        tags: ['Resources'],
        summary: 'Update resource',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' }
          }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  type: { type: 'string' },
                  config: { type: 'object' }
                }
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Resource updated',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Resource'
                }
              }
            }
          }
        }
      },
      delete: {
        tags: ['Resources'],
        summary: 'Delete resource',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: { type: 'string' }
          }
        ],
        responses: {
          '204': {
            description: 'Resource deleted'
          },
          '404': {
            description: 'Resource not found'
          }
        }
      }
    },
    '/api/v1/tasks': {
      get: {
        tags: ['Tasks'],
        summary: 'List all tasks',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'status',
            in: 'query',
            schema: {
              type: 'string',
              enum: ['pending', 'running', 'completed', 'failed', 'cancelled']
            }
          },
          {
            name: 'limit',
            in: 'query',
            schema: { type: 'integer', default: 10 }
          }
        ],
        responses: {
          '200': {
            description: 'List of tasks',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    data: {
                      type: 'array',
                      items: {
                        $ref: '#/components/schemas/Task'
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      post: {
        tags: ['Tasks'],
        summary: 'Create a new task',
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['name', 'type'],
                properties: {
                  name: { type: 'string' },
                  type: { type: 'string' },
                  config: { type: 'object' }
                }
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'Task created',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/Task'
                }
              }
            }
          }
        }
      }
    },
    '/api/v1/metrics/timeseries': {
      get: {
        tags: ['Metrics'],
        summary: 'Get time series metrics',
        security: [{ bearerAuth: [] }],
        parameters: [
          {
            name: 'metric',
            in: 'query',
            schema: { type: 'string' }
          },
          {
            name: 'interval',
            in: 'query',
            schema: { type: 'string', default: '1m' }
          }
        ],
        responses: {
          '200': {
            description: 'Time series data'
          }
        }
      }
    }
  }
};
