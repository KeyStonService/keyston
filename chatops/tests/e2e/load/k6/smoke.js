/**
 * k6 Smoke Test
 *
 * Purpose: Verify system is working under minimal load
 * Duration: 1 minute
 * VUs: 1-2
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 1 }, // Ramp up to 1 user
    { duration: '30s', target: 2 }, // Stay at 2 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    errors: ['rate<0.01'], // Error rate should be less than 1%
  },
};

// Environment configuration
const BASE_URL = __ENV.CHATOPS_API_URL || 'http://localhost:8080';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

// Headers
const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${AUTH_TOKEN}`,
};

/**
 * Main test scenario
 */
export default function () {
  // Test 1: Health check
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check returns healthy': (r) => {
      try {
        return JSON.parse(r.body).status === 'healthy';
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  apiLatency.add(healthResponse.timings.duration);
  sleep(1);

  // Test 2: API Status
  let statusResponse = http.get(`${BASE_URL}/api/v1/status`, { headers });
  check(statusResponse, {
    'status endpoint returns 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  apiLatency.add(statusResponse.timings.duration);
  sleep(1);

  // Test 3: Send a message
  let messagePayload = JSON.stringify({
    content: `Smoke test message at ${new Date().toISOString()}`,
    channel: 'test',
  });

  let messageResponse = http.post(`${BASE_URL}/api/v1/messages`, messagePayload, {
    headers,
  });

  check(messageResponse, {
    'message creation successful': (r) => r.status >= 200 && r.status < 300,
    'message has ID': (r) => {
      try {
        let body = JSON.parse(r.body);
        return body.id || body.message_id;
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  apiLatency.add(messageResponse.timings.duration);
  sleep(2);
}

/**
 * Setup function - runs once before the test
 */
export function setup() {
  console.log('Starting smoke test...');
  console.log(`Target URL: ${BASE_URL}`);

  // Verify system is up
  let response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    throw new Error(`System not healthy: ${response.status}`);
  }

  return { startTime: new Date().toISOString() };
}

/**
 * Teardown function - runs once after the test
 */
export function teardown(data) {
  console.log(`Smoke test completed. Started at: ${data.startTime}`);
}
