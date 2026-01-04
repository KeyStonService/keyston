/**
 * k6 Stress Test
 *
 * Purpose: Find system breaking points and observe recovery
 * Duration: 20 minutes
 * VUs: Up to 300
 */

import http from 'k6/http';
import { check, sleep, fail } from 'k6';
import { Rate, Trend, Gauge } from 'k6/metrics';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const concurrentUsers = new Gauge('concurrent_users');

// Stress test configuration - push beyond normal limits
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Warm up
    { duration: '3m', target: 100 },  // Normal load
    { duration: '3m', target: 200 },  // Stress
    { duration: '3m', target: 300 },  // Breaking point
    { duration: '3m', target: 300 },  // Stay at breaking point
    { duration: '3m', target: 100 },  // Recovery
    { duration: '3m', target: 0 },    // Cool down
  ],
  thresholds: {
    // More lenient thresholds for stress test
    http_req_duration: ['p(95)<3000', 'p(99)<5000'],
    errors: ['rate<0.30'], // Allow up to 30% errors during stress
  },
};

const BASE_URL = __ENV.CHATOPS_API_URL || 'http://localhost:8080';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${AUTH_TOKEN}`,
};

/**
 * Main stress test scenario
 */
export default function () {
  concurrentUsers.add(__VU);

  // Mix of operations
  let operation = randomIntBetween(1, 100);

  if (operation <= 40) {
    // 40% - Health checks (lightweight)
    healthCheck();
  } else if (operation <= 70) {
    // 30% - Read operations
    readOperation();
  } else {
    // 30% - Write operations (heavy)
    writeOperation();
  }

  // Minimal think time during stress test
  sleep(randomIntBetween(0.1, 0.5));
}

function healthCheck() {
  let start = Date.now();
  let response = http.get(`${BASE_URL}/health`, { timeout: '10s' });

  apiLatency.add(Date.now() - start);

  if (!check(response, {
    'health check ok': (r) => r.status === 200,
  })) {
    errorRate.add(1);
  }
}

function readOperation() {
  let start = Date.now();
  let response = http.get(`${BASE_URL}/api/v1/messages?limit=5`, {
    headers,
    timeout: '15s',
  });

  apiLatency.add(Date.now() - start);

  if (!check(response, {
    'read successful': (r) => r.status === 200 || r.status === 429, // Accept rate limiting
  })) {
    errorRate.add(1);
    if (response.status >= 500) {
      console.log(`Server error: ${response.status} at ${__VU} VUs`);
    }
  }
}

function writeOperation() {
  let payload = JSON.stringify({
    content: `Stress test ${randomString(20)}`,
    channel: `stress-${randomIntBetween(1, 5)}`,
    timestamp: new Date().toISOString(),
  });

  let start = Date.now();
  let response = http.post(`${BASE_URL}/api/v1/messages`, payload, {
    headers,
    timeout: '20s',
  });

  apiLatency.add(Date.now() - start);

  if (!check(response, {
    'write successful': (r) => r.status >= 200 && r.status < 300,
    'or rate limited': (r) => r.status === 429,
  })) {
    errorRate.add(1);
    if (response.status >= 500) {
      console.log(`Write error: ${response.status} at ${__VU} VUs`);
    }
  }
}

export function setup() {
  console.log('=== Stress Test Starting ===');
  console.log(`Target: ${BASE_URL}`);
  console.log('WARNING: This test will push the system to its limits');
  console.log('Monitor system metrics during the test');
  console.log('============================');

  // Verify system is up before stress test
  let response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    fail('System not healthy - aborting stress test');
  }

  return { startTime: Date.now() };
}

export function teardown(data) {
  let duration = (Date.now() - data.startTime) / 1000 / 60;
  console.log(`\n=== Stress Test Complete ===`);
  console.log(`Duration: ${duration.toFixed(2)} minutes`);
  console.log('Review metrics to identify breaking points');
  console.log('============================\n');
}
