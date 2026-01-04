/**
 * k6 Spike Test
 *
 * Purpose: Test system behavior under sudden traffic spikes
 * Duration: 10 minutes
 * Pattern: Normal -> Spike -> Normal -> Spike -> Normal
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const requestsTotal = new Counter('requests_total');
const spikeRecovery = new Trend('spike_recovery_time');

// Spike test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Normal load
    { duration: '10s', target: 200 }, // Spike 1: Rapid increase
    { duration: '30s', target: 200 }, // Hold spike
    { duration: '10s', target: 10 },  // Rapid decrease
    { duration: '1m', target: 10 },   // Recovery period
    { duration: '10s', target: 250 }, // Spike 2: Even higher
    { duration: '30s', target: 250 }, // Hold spike
    { duration: '10s', target: 10 },  // Rapid decrease
    { duration: '2m', target: 10 },   // Final recovery
    { duration: '30s', target: 0 },   // Cool down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // Allow higher latency during spikes
    errors: ['rate<0.20'], // Allow 20% errors during spikes
  },
};

const BASE_URL = __ENV.CHATOPS_API_URL || 'http://localhost:8080';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${AUTH_TOKEN}`,
};

let lastResponseTime = 0;
let inSpike = false;

export default function () {
  requestsTotal.add(1);

  // Detect if we're in a spike (high VU count)
  let currentSpike = __VU > 50;
  if (currentSpike !== inSpike) {
    inSpike = currentSpike;
    if (!inSpike && lastResponseTime > 0) {
      // Record recovery time
      spikeRecovery.add(lastResponseTime);
    }
  }

  // Mix of read and write operations
  if (__VU % 3 === 0) {
    writeRequest();
  } else {
    readRequest();
  }

  // Very short think time to maximize load during spikes
  sleep(0.1);
}

function readRequest() {
  let start = Date.now();
  let response = http.get(`${BASE_URL}/api/v1/status`, {
    headers,
    timeout: '10s',
  });

  let duration = Date.now() - start;
  apiLatency.add(duration);
  lastResponseTime = duration;

  let success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 2000,
  });

  if (!success) {
    errorRate.add(1);
  }
}

function writeRequest() {
  let payload = JSON.stringify({
    content: `Spike test ${randomString(10)}`,
    channel: 'spike-test',
    timestamp: new Date().toISOString(),
  });

  let start = Date.now();
  let response = http.post(`${BASE_URL}/api/v1/messages`, payload, {
    headers,
    timeout: '15s',
  });

  let duration = Date.now() - start;
  apiLatency.add(duration);
  lastResponseTime = duration;

  let success = check(response, {
    'message created or rate limited': (r) =>
      (r.status >= 200 && r.status < 300) || r.status === 429,
  });

  if (!success) {
    errorRate.add(1);
  }
}

export function setup() {
  console.log('=== Spike Test Starting ===');
  console.log(`Target: ${BASE_URL}`);
  console.log('This test simulates sudden traffic spikes');
  console.log('Watch for:');
  console.log('  - Response time during spikes');
  console.log('  - Error rate during spikes');
  console.log('  - Recovery time after spikes');
  console.log('===========================');

  return { startTime: Date.now() };
}

export function teardown(data) {
  let duration = (Date.now() - data.startTime) / 1000;
  console.log(`\n=== Spike Test Complete ===`);
  console.log(`Total duration: ${duration.toFixed(2)} seconds`);
  console.log('Check spike_recovery_time metric for recovery analysis');
  console.log('===========================\n');
}
