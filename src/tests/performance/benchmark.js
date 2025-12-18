#!/usr/bin/env node
/**
 * ============================================================================
 * 效能基準測試 (Performance Benchmark)
 * ============================================================================
 * 測試所有核心服務的效能指標
 * 包括：回應時間、吞吐量、資源使用率
 * ============================================================================
 */

const http = require('http');
const { performance } = require('perf_hooks');

// 配置
const CONFIG = {
  contracts: {
    host: process.env.CONTRACTS_HOST || 'localhost',
    port: process.env.CONTRACTS_PORT || 3000,
    endpoints: [
      '/healthz',
      '/api/v1/provenance',
      '/api/v1/slsa/validate',
    ],
  },
  mcp: {
    host: process.env.MCP_HOST || 'localhost',
    port: process.env.MCP_PORT || 3001,
    endpoints: [
      '/health',
      '/status',
      '/version',
    ],
  },
  benchmark: {
    warmupRequests: 10,
    testRequests: 100,
    concurrency: 10,
    timeout: 5000,
  },
};

// 基準指標
const BENCHMARKS = {
  responseTime: {
    excellent: 100,  // < 100ms
    good: 300,       // < 300ms
    acceptable: 500, // < 500ms
  },
  throughput: {
    minimum: 100,    // > 100 req/s
    target: 500,     // > 500 req/s
    excellent: 1000, // > 1000 req/s
  },
  errorRate: {
    maximum: 0.1,    // < 0.1%
  },
};

// 測試結果
class BenchmarkResult {
  constructor(service, endpoint) {
    this.service = service;
    this.endpoint = endpoint;
    this.requests = 0;
    this.successes = 0;
    this.failures = 0;
    this.responseTimes = [];
    this.startTime = 0;
    this.endTime = 0;
  }

  addRequest(duration, success) {
    this.requests++;
    if (success) {
      this.successes++;
      this.responseTimes.push(duration);
    } else {
      this.failures++;
    }
  }

  calculate() {
    if (this.responseTimes.length === 0) {
      return {
        service: this.service,
        endpoint: this.endpoint,
        requests: this.requests,
        successes: this.successes,
        failures: this.failures,
        errorRate: 100,
        avgResponseTime: 0,
        minResponseTime: 0,
        maxResponseTime: 0,
        p50: 0,
        p95: 0,
        p99: 0,
        throughput: 0,
        grade: 'F',
      };
    }

    const sorted = this.responseTimes.sort((a, b) => a - b);
    const total = sorted.reduce((a, b) => a + b, 0);
    const avg = total / sorted.length;
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const p50 = sorted[Math.floor(sorted.length * 0.5)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    const p99 = sorted[Math.floor(sorted.length * 0.99)];
    
    const duration = (this.endTime - this.startTime) / 1000; // 秒
    const throughput = this.successes / duration;
    const errorRate = (this.failures / this.requests) * 100;

    // 評分
    let grade = 'F';
    if (p95 < BENCHMARKS.responseTime.excellent && 
        throughput > BENCHMARKS.throughput.excellent &&
        errorRate < BENCHMARKS.errorRate.maximum) {
      grade = 'A+';
    } else if (p95 < BENCHMARKS.responseTime.good && 
               throughput > BENCHMARKS.throughput.target &&
               errorRate < BENCHMARKS.errorRate.maximum) {
      grade = 'A';
    } else if (p95 < BENCHMARKS.responseTime.acceptable && 
               throughput > BENCHMARKS.throughput.minimum &&
               errorRate < BENCHMARKS.errorRate.maximum * 5) {
      grade = 'B';
    } else if (errorRate < 1) {
      grade = 'C';
    }

    return {
      service: this.service,
      endpoint: this.endpoint,
      requests: this.requests,
      successes: this.successes,
      failures: this.failures,
      errorRate: errorRate.toFixed(2),
      avgResponseTime: avg.toFixed(2),
      minResponseTime: min.toFixed(2),
      maxResponseTime: max.toFixed(2),
      p50: p50.toFixed(2),
      p95: p95.toFixed(2),
      p99: p99.toFixed(2),
      throughput: throughput.toFixed(2),
      grade,
    };
  }
}

// HTTP 請求工具
function makeRequest(host, port, path, timeout) {
  return new Promise((resolve, reject) => {
    const startTime = performance.now();
    
    const req = http.request(
      {
        hostname: host,
        port,
        path,
        method: 'GET',
        timeout,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          const endTime = performance.now();
          const duration = endTime - startTime;
          resolve({ success: res.statusCode < 400, duration, statusCode: res.statusCode });
        });
      }
    );

    req.on('error', (err) => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      resolve({ success: false, duration, error: err.message });
    });

    req.on('timeout', () => {
      req.destroy();
      const endTime = performance.now();
      const duration = endTime - startTime;
      resolve({ success: false, duration, error: 'Timeout' });
    });

    req.end();
  });
}

// 基準測試單個端點
async function benchmarkEndpoint(service, host, port, endpoint, config) {
  console.log(`\n📊 測試: ${service}${endpoint}`);
  
  const result = new BenchmarkResult(service, endpoint);
  
  // 預熱
  console.log(`  預熱中 (${config.warmupRequests} 請求)...`);
  for (let i = 0; i < config.warmupRequests; i++) {
    await makeRequest(host, port, endpoint, config.timeout);
  }
  
  // 實際測試
  console.log(`  執行測試 (${config.testRequests} 請求，並發 ${config.concurrency})...`);
  result.startTime = performance.now();
  
  const batches = Math.ceil(config.testRequests / config.concurrency);
  for (let batch = 0; batch < batches; batch++) {
    const batchSize = Math.min(config.concurrency, config.testRequests - batch * config.concurrency);
    const promises = [];
    
    for (let i = 0; i < batchSize; i++) {
      promises.push(makeRequest(host, port, endpoint, config.timeout));
    }
    
    const results = await Promise.all(promises);
    results.forEach((r) => {
      result.addRequest(r.duration, r.success);
    });
  }
  
  result.endTime = performance.now();
  
  return result.calculate();
}

// 執行所有基準測試
async function runBenchmarks() {
  console.log('============================================================================');
  console.log('🚀 SynergyMesh 效能基準測試');
  console.log('============================================================================\n');
  
  console.log('配置:');
  console.log(`  預熱請求: ${CONFIG.benchmark.warmupRequests}`);
  console.log(`  測試請求: ${CONFIG.benchmark.testRequests}`);
  console.log(`  並發數: ${CONFIG.benchmark.concurrency}`);
  console.log(`  超時: ${CONFIG.benchmark.timeout}ms`);
  
  const allResults = [];
  
  // 測試 Contracts L1 服務
  console.log('\n\n===========================================================================');
  console.log('📦 Tier 1: Contracts L1 Service');
  console.log('===========================================================================');
  
  for (const endpoint of CONFIG.contracts.endpoints) {
    try {
      const result = await benchmarkEndpoint(
        'Contracts L1',
        CONFIG.contracts.host,
        CONFIG.contracts.port,
        endpoint,
        CONFIG.benchmark
      );
      allResults.push(result);
    } catch (err) {
      console.error(`  ❌ 錯誤: ${err.message}`);
    }
  }
  
  // 測試 MCP Servers
  console.log('\n\n===========================================================================');
  console.log('🔧 Tier 2: MCP Servers');
  console.log('===========================================================================');
  
  for (const endpoint of CONFIG.mcp.endpoints) {
    try {
      const result = await benchmarkEndpoint(
        'MCP Servers',
        CONFIG.mcp.host,
        CONFIG.mcp.port,
        endpoint,
        CONFIG.benchmark
      );
      allResults.push(result);
    } catch (err) {
      console.error(`  ❌ 錯誤: ${err.message}`);
    }
  }
  
  // 顯示結果
  console.log('\n\n===========================================================================');
  console.log('📋 測試結果摘要');
  console.log('===========================================================================\n');
  
  console.log('┌─────────────────────┬──────────────────────┬──────────┬──────────┬─────────┬─────────┬─────────┬──────────────┬───────┐');
  console.log('│ Service             │ Endpoint             │ Requests │ Success  │ P50(ms) │ P95(ms) │ P99(ms) │ Throughput   │ Grade │');
  console.log('├─────────────────────┼──────────────────────┼──────────┼──────────┼─────────┼─────────┼─────────┼──────────────┼───────┤');
  
  allResults.forEach((r) => {
    const service = r.service.padEnd(19);
    const endpoint = r.endpoint.substring(0, 20).padEnd(20);
    const requests = r.requests.toString().padStart(8);
    const successRate = `${((r.successes / r.requests) * 100).toFixed(1)}%`.padStart(8);
    const p50 = r.p50.padStart(7);
    const p95 = r.p95.padStart(7);
    const p99 = r.p99.padStart(7);
    const throughput = `${r.throughput} req/s`.padStart(12);
    const grade = r.grade.padStart(5);
    
    console.log(`│ ${service} │ ${endpoint} │ ${requests} │ ${successRate} │ ${p50} │ ${p95} │ ${p99} │ ${throughput} │ ${grade} │`);
  });
  
  console.log('└─────────────────────┴──────────────────────┴──────────┴──────────┴─────────┴─────────┴─────────┴──────────────┴───────┘');
  
  // 整體評估
  const avgGrade = allResults.reduce((sum, r) => {
    const gradeMap = { 'A+': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0 };
    return sum + (gradeMap[r.grade] || 0);
  }, 0) / allResults.length;
  
  console.log('\n');
  console.log('===========================================================================');
  console.log('🎯 整體評估');
  console.log('===========================================================================\n');
  
  if (avgGrade >= 4.5) {
    console.log('  ✅ 優秀 (A+) - 系統效能達到生產級別標準');
  } else if (avgGrade >= 3.5) {
    console.log('  ✅ 良好 (A) - 系統效能符合生產級別要求');
  } else if (avgGrade >= 2.5) {
    console.log('  ⚠️  可接受 (B) - 建議進行效能優化');
  } else {
    console.log('  ❌ 需要改進 - 系統效能未達生產級別要求');
  }
  
  // 儲存結果
  const fs = require('fs');
  const reportPath = '/tmp/benchmark-results.json';
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    config: CONFIG,
    results: allResults,
    averageGrade: avgGrade,
  }, null, 2));
  
  console.log(`\n  📄 詳細報告已儲存至: ${reportPath}`);
  console.log('\n');
}

// 執行
if (require.main === module) {
  runBenchmarks().catch((err) => {
    console.error('基準測試失敗:', err);
    process.exit(1);
  });
}

module.exports = { runBenchmarks, benchmarkEndpoint };
