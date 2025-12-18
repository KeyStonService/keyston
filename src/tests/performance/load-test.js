#!/usr/bin/env node
/**
 * ============================================================================
 * 負載測試 (Load Testing)
 * ============================================================================
 * 模擬真實負載情況，測試系統在高負載下的表現
 * 包括：壓力測試、峰值測試、持續負載測試
 * ============================================================================
 */

const http = require('http');
const { performance } = require('perf_hooks');
const fs = require('fs');

// 負載測試配置
const LOAD_PROFILES = {
  // 輕量負載 - 正常操作
  light: {
    duration: 60,        // 60 秒
    rps: 10,             // 10 requests/second
    rampUp: 10,          // 10 秒漸增
    rampDown: 10,        // 10 秒漸減
  },
  // 中等負載 - 高峰時段
  medium: {
    duration: 120,
    rps: 50,
    rampUp: 20,
    rampDown: 20,
  },
  // 高負載 - 壓力測試
  heavy: {
    duration: 180,
    rps: 100,
    rampUp: 30,
    rampDown: 30,
  },
  // 峰值測試 - 突發流量
  spike: {
    duration: 300,
    phases: [
      { duration: 60, rps: 20 },   // 基準
      { duration: 30, rps: 200 },  // 峰值
      { duration: 60, rps: 20 },   // 恢復
      { duration: 30, rps: 200 },  // 第二次峰值
      { duration: 120, rps: 20 },  // 穩定
    ],
  },
};

// 測試目標
const TARGETS = {
  contracts: {
    host: process.env.CONTRACTS_HOST || 'localhost',
    port: process.env.CONTRACTS_PORT || 3000,
    path: '/healthz',
  },
  mcp: {
    host: process.env.MCP_HOST || 'localhost',
    port: process.env.MCP_PORT || 3001,
    path: '/health',
  },
};

// 負載測試結果
class LoadTestResult {
  constructor(profile, target) {
    this.profile = profile;
    this.target = target;
    this.startTime = Date.now();
    this.requests = [];
    this.errors = [];
    this.stats = {
      total: 0,
      success: 0,
      failed: 0,
      timeout: 0,
    };
  }

  addRequest(result) {
    this.requests.push(result);
    this.stats.total++;
    
    if (result.success) {
      this.stats.success++;
    } else {
      this.stats.failed++;
      this.errors.push(result.error);
      if (result.error === 'Timeout') {
        this.stats.timeout++;
      }
    }
  }

  calculateStats() {
    if (this.requests.length === 0) {
      return null;
    }

    const successfulRequests = this.requests.filter((r) => r.success);
    const durations = successfulRequests.map((r) => r.duration);
    
    if (durations.length === 0) {
      return {
        profile: this.profile,
        target: this.target,
        duration: (Date.now() - this.startTime) / 1000,
        totalRequests: this.stats.total,
        successRate: 0,
        avgResponseTime: 0,
        minResponseTime: 0,
        maxResponseTime: 0,
        p95: 0,
        p99: 0,
        throughput: 0,
        errorRate: 100,
        status: 'FAILED',
      };
    }

    durations.sort((a, b) => a - b);
    
    const testDuration = (Date.now() - this.startTime) / 1000;
    const sum = durations.reduce((a, b) => a + b, 0);
    const avg = sum / durations.length;
    const min = durations[0];
    const max = durations[durations.length - 1];
    const p95 = durations[Math.floor(durations.length * 0.95)];
    const p99 = durations[Math.floor(durations.length * 0.99)];
    const throughput = this.stats.success / testDuration;
    const successRate = (this.stats.success / this.stats.total) * 100;
    const errorRate = (this.stats.failed / this.stats.total) * 100;

    // 狀態判定
    let status = 'PASSED';
    if (errorRate > 1) {
      status = 'FAILED';
    } else if (errorRate > 0.5 || p95 > 1000) {
      status = 'WARNING';
    }

    return {
      profile: this.profile,
      target: this.target,
      duration: testDuration.toFixed(2),
      totalRequests: this.stats.total,
      successRate: successRate.toFixed(2),
      avgResponseTime: avg.toFixed(2),
      minResponseTime: min.toFixed(2),
      maxResponseTime: max.toFixed(2),
      p95: p95.toFixed(2),
      p99: p99.toFixed(2),
      throughput: throughput.toFixed(2),
      errorRate: errorRate.toFixed(2),
      timeoutCount: this.stats.timeout,
      status,
    };
  }

  getTimeSeriesData() {
    // 按時間分組統計
    const buckets = {};
    const bucketSize = 5000; // 5 秒一個桶

    this.requests.forEach((req) => {
      const bucket = Math.floor((req.timestamp - this.startTime) / bucketSize);
      if (!buckets[bucket]) {
        buckets[bucket] = {
          timestamp: bucket * bucketSize / 1000,
          requests: 0,
          successes: 0,
          failures: 0,
          totalDuration: 0,
        };
      }
      
      buckets[bucket].requests++;
      if (req.success) {
        buckets[bucket].successes++;
        buckets[bucket].totalDuration += req.duration;
      } else {
        buckets[bucket].failures++;
      }
    });

    return Object.values(buckets).map((b) => ({
      timestamp: b.timestamp,
      rps: b.requests / (bucketSize / 1000),
      successRate: (b.successes / b.requests) * 100,
      avgResponseTime: b.successes > 0 ? b.totalDuration / b.successes : 0,
    }));
  }
}

// HTTP 請求
function makeRequest(host, port, path, timeout = 5000) {
  return new Promise((resolve) => {
    const startTime = performance.now();
    const timestamp = Date.now();
    
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
          resolve({
            timestamp,
            success: res.statusCode < 400,
            duration: endTime - startTime,
            statusCode: res.statusCode,
          });
        });
      }
    );

    req.on('error', (err) => {
      const endTime = performance.now();
      resolve({
        timestamp,
        success: false,
        duration: endTime - startTime,
        error: err.message,
      });
    });

    req.on('timeout', () => {
      req.destroy();
      const endTime = performance.now();
      resolve({
        timestamp,
        success: false,
        duration: endTime - startTime,
        error: 'Timeout',
      });
    });

    req.end();
  });
}

// 執行負載測試
async function runLoadTest(profileName, targetName) {
  const profile = LOAD_PROFILES[profileName];
  const target = TARGETS[targetName];
  
  if (!profile) {
    throw new Error(`Unknown profile: ${profileName}`);
  }
  if (!target) {
    throw new Error(`Unknown target: ${targetName}`);
  }

  console.log(`\n🚀 開始負載測試`);
  console.log(`  配置: ${profileName}`);
  console.log(`  目標: ${targetName} (${target.host}:${target.port}${target.path})`);
  
  const result = new LoadTestResult(profileName, targetName);
  
  // 處理峰值測試的階段性負載
  if (profile.phases) {
    console.log(`  階段性測試，共 ${profile.phases.length} 個階段\n`);
    
    for (let i = 0; i < profile.phases.length; i++) {
      const phase = profile.phases[i];
      console.log(`  階段 ${i + 1}/${profile.phases.length}: ${phase.duration}s @ ${phase.rps} RPS`);
      
      await runPhase(phase.duration, phase.rps, target, result);
    }
  } else {
    // 標準負載測試
    const { duration, rps, rampUp, rampDown } = profile;
    console.log(`  持續時間: ${duration}s`);
    console.log(`  目標 RPS: ${rps}`);
    console.log(`  漸增時間: ${rampUp}s`);
    console.log(`  漸減時間: ${rampDown}s\n`);
    
    // 漸增階段
    if (rampUp > 0) {
      console.log(`  📈 漸增階段 (0 → ${rps} RPS)`);
      await runRamp(rampUp, 0, rps, target, result);
    }
    
    // 穩定負載階段
    const stableTime = duration - rampUp - rampDown;
    if (stableTime > 0) {
      console.log(`  ⚡ 穩定負載階段 (${rps} RPS)`);
      await runPhase(stableTime, rps, target, result);
    }
    
    // 漸減階段
    if (rampDown > 0) {
      console.log(`  📉 漸減階段 (${rps} → 0 RPS)`);
      await runRamp(rampDown, rps, 0, target, result);
    }
  }
  
  return result;
}

// 執行測試階段
async function runPhase(duration, rps, target, result) {
  const interval = 1000 / rps; // 請求間隔 (ms)
  const totalRequests = duration * rps;
  const startTime = Date.now();
  
  let requestCount = 0;
  
  while (requestCount < totalRequests) {
    const elapsed = Date.now() - startTime;
    if (elapsed >= duration * 1000) {
      break;
    }
    
    // 發送請求
    makeRequest(target.host, target.port, target.path).then((res) => {
      result.addRequest(res);
    }).catch((err) => {
      console.error('Request failed:', err);
      result.addRequest({ success: false, duration: 0, error: err.message, timestamp: Date.now() });
    });
    
    requestCount++;
    
    // 等待下一個請求
    await new Promise((resolve) => setTimeout(resolve, interval));
    
    // 每秒顯示進度
    if (requestCount % rps === 0) {
      process.stdout.write(`\r    進度: ${requestCount}/${totalRequests} 請求 (${((requestCount / totalRequests) * 100).toFixed(1)}%)`);
    }
  }
  
  console.log(`\r    完成: ${requestCount}/${totalRequests} 請求 (100.0%)`);
}

// 執行漸增/漸減階段
async function runRamp(duration, startRps, endRps, target, result) {
  const steps = duration; // 每秒一步
  const stepDuration = 1000; // ms
  
  for (let step = 0; step < steps; step++) {
    const progress = (step + 1) / steps;
    const currentRps = startRps + (endRps - startRps) * progress;
    const requestsThisSecond = Math.round(currentRps);
    
    for (let i = 0; i < requestsThisSecond; i++) {
      makeRequest(target.host, target.port, target.path).then((res) => {
        result.addRequest(res);
      });
      
      if (requestsThisSecond > 1) {
        await new Promise((resolve) => setTimeout(resolve, stepDuration / requestsThisSecond));
      }
    }
    
    process.stdout.write(`\r    進度: ${step + 1}/${steps} 步 (${currentRps.toFixed(1)} RPS)`);
    
    // 計算實際已用時間並等待剩餘時間
    const timeSpent = requestsThisSecond > 0 ? (stepDuration / requestsThisSecond) * requestsThisSecond : 0;
    const remainingTime = Math.max(0, stepDuration - timeSpent);
    if (remainingTime > 0) {
      await new Promise((resolve) => setTimeout(resolve, remainingTime));
    }
  }
  
  console.log(`\r    完成: ${steps}/${steps} 步`);
}

// 主程序
async function main() {
  console.log('============================================================================');
  console.log('⚡ SynergyMesh 負載測試');
  console.log('============================================================================');
  
  const profileName = process.argv[2] || 'light';
  const targetName = process.argv[3] || 'contracts';
  
  try {
    const result = await runLoadTest(profileName, targetName);
    
    // 等待所有請求完成
    console.log('\n  ⏳ 等待所有請求完成...');
    await new Promise((resolve) => setTimeout(resolve, 5000));
    
    const stats = result.calculateStats();
    
    console.log('\n');
    console.log('===========================================================================');
    console.log('📊 測試結果');
    console.log('===========================================================================\n');
    
    console.log(`  配置檔: ${stats.profile}`);
    console.log(`  目標: ${stats.target}`);
    console.log(`  測試時長: ${stats.duration}s`);
    console.log(`  總請求數: ${stats.totalRequests}`);
    console.log(`  成功率: ${stats.successRate}%`);
    console.log(`  錯誤率: ${stats.errorRate}%`);
    console.log(`  超時數: ${stats.timeoutCount}`);
    console.log(`  平均回應時間: ${stats.avgResponseTime}ms`);
    console.log(`  最小回應時間: ${stats.minResponseTime}ms`);
    console.log(`  最大回應時間: ${stats.maxResponseTime}ms`);
    console.log(`  P95: ${stats.p95}ms`);
    console.log(`  P99: ${stats.p99}ms`);
    console.log(`  吞吐量: ${stats.throughput} req/s`);
    console.log(`  狀態: ${stats.status}\n`);
    
    // 儲存結果
    const reportPath = `/tmp/load-test-${profileName}-${targetName}.json`;
    fs.writeFileSync(reportPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      stats,
      timeSeries: result.getTimeSeriesData(),
    }, null, 2));
    
    console.log(`  📄 詳細報告已儲存至: ${reportPath}\n`);
    
    if (stats.status === 'FAILED') {
      process.exit(1);
    }
  } catch (err) {
    console.error('\n❌ 負載測試失敗:', err.message);
    process.exit(1);
  }
}

// 執行
if (require.main === module) {
  main();
}

module.exports = { runLoadTest, LOAD_PROFILES, TARGETS };
