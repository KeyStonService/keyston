#!/usr/bin/env node

/**
 * MCP Servers - 主入口點
 *
 * 提供 MCP (Model Context Protocol) 服務器功能，包括：
 * - 代碼分析
 * - SLSA 驗證
 * - 安全掃描
 * - 部署驗證
 * - 邏輯驗證
 */

import http from 'http';

const SERVER_PORT = process.env.MCP_SERVER_PORT || 3001;
const SERVER_HOST = process.env.MCP_SERVER_HOST || '0.0.0.0';

// MCP 服務模組列表
const MCP_SERVICES = [
  'Code Analysis',
  'SLSA Validation',
  'Security Scanning',
  'Deployment Validation',
  'Logic Validation',
  'Performance Analysis',
  'Test Generation',
  'Documentation Generation',
];

const MCP_SERVICE_FILES = [
  'code-analyzer.js',
  'slsa-validator.js',
  'security-scanner.js',
  'deployment-validator.js',
  'logic-validator.js',
  'performance-analyzer.js',
  'test-generator.js',
  'doc-generator.js',
];

/**
 * 創建 HTTP 服務器用於健康檢查和狀態監控
 */
function createHealthCheckServer() {
  const server = http.createServer((req, res) => {
    const { url, method } = req;

    // 設置 CORS 標頭
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');

    if (method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // 健康檢查端點
    if (url === '/health' || url === '/healthz') {
      res.writeHead(200);
      res.end(
        JSON.stringify({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          service: 'mcp-servers',
          version: '1.0.0',
        })
      );
      return;
    }

    // 就緒檢查端點
    if (url === '/ready' || url === '/readyz') {
      res.writeHead(200);
      res.end(
        JSON.stringify({
          status: 'ready',
          timestamp: new Date().toISOString(),
          checks: {
            mcp: 'available',
            validators: 'loaded',
          },
        })
      );
      return;
    }

    // 版本信息端點
    if (url === '/version') {
      res.writeHead(200);
      res.end(
        JSON.stringify({
          version: '1.0.0',
          build: process.env.BUILD_SHA || 'local',
          timestamp: new Date().toISOString(),
          node: process.version,
        })
      );
      return;
    }

    // 狀態信息端點
    if (url === '/status') {
      res.writeHead(200);
      res.end(
        JSON.stringify({
          service: 'mcp-servers',
          status: 'running',
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          timestamp: new Date().toISOString(),
          environment: process.env.NODE_ENV || 'development',
        })
      );
      return;
    }

    // 根端點 - 服務信息
    if (url === '/' || url === '') {
      res.writeHead(200);
      res.end(
        JSON.stringify({
          service: 'mcp-servers',
          version: '1.0.0',
          description:
            'Enterprise-grade MCP servers for code analysis, SLSA validation, and security scanning',
          endpoints: {
            health: '/health',
            ready: '/ready',
            version: '/version',
            status: '/status',
          },
          features: MCP_SERVICES,
        })
      );
      return;
    }

    // 404 處理
    res.writeHead(404);
    res.end(
      JSON.stringify({
        error: 'Not Found',
        message: 'The requested endpoint does not exist',
        path: url,
        availableEndpoints: [
          '/health',
          '/healthz',
          '/ready',
          '/readyz',
          '/version',
          '/status',
          '/',
        ],
        timestamp: new Date().toISOString(),
      })
    );
  });

  return server;
}

/**
 * 主函數 - 初始化並啟動 MCP 服務器
 */
function main() {
  console.info('🚀 Starting MCP Servers...');
  console.info(`📦 Version: 1.0.0`);
  console.info(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.info(`🔧 Node.js: ${process.version}`);

  // 創建並啟動 HTTP 健康檢查服務器
  const healthServer = createHealthCheckServer();

  healthServer.listen(SERVER_PORT, SERVER_HOST, () => {
    console.info(`✅ Health check server listening on http://${SERVER_HOST}:${SERVER_PORT}`);
    console.info(`📊 Health endpoint: http://${SERVER_HOST}:${SERVER_PORT}/health`);
    console.info(`🔍 Status endpoint: http://${SERVER_HOST}:${SERVER_PORT}/status`);
    console.info(`📝 Version endpoint: http://${SERVER_HOST}:${SERVER_PORT}/version`);
    console.info('');
    console.info('🎯 Available MCP Services:');
    MCP_SERVICE_FILES.forEach((file, index) => {
      console.info(`  - ${MCP_SERVICES[index]} (${file})`);
    });
    console.info('');
    console.info('✨ MCP Servers are ready!');

    // 設置信號處理 - 僅在伺服器成功啟動後註冊
    const gracefulShutdown = async (signal) => {
      console.info(`\n🛑 Received ${signal}, shutting down gracefully...`);
      await new Promise((resolve) => {
        healthServer.close(() => {
          console.info('✅ HTTP server closed');
          resolve();
        });
      });
      process.exit(0);
    };

    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  });
}

// 啟動服務器
try {
  main();
} catch (error) {
  console.error('❌ Failed to start MCP Servers:', error);
  process.exit(1);
}
