/**
 * k6 Load Test
 *
 * Purpose: Verify system handles expected production load
 * Duration: 10 minutes
 * VUs: Up to 100
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const messagesCreated = new Counter('messages_created');
const messagesProcessed = new Counter('messages_processed');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 20 },  // Ramp up to 20 users
    { duration: '3m', target: 50 },  // Ramp up to 50 users
    { duration: '3m', target: 100 }, // Ramp up to 100 users
    { duration: '2m', target: 0 },   // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'], // 95% < 1s, 99% < 2s
    errors: ['rate<0.05'], // Error rate should be less than 5%
    http_req_failed: ['rate<0.05'], // HTTP failures < 5%
  },
};

// Environment configuration
const BASE_URL = __ENV.CHATOPS_API_URL || 'http://localhost:8080';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${AUTH_TOKEN}`,
};

/**
 * Main test scenario
 */
export default function () {
  // Simulate realistic user behavior with different actions
  let scenario = randomIntBetween(1, 100);

  if (scenario <= 60) {
    // 60% - Read operations
    readOperations();
  } else if (scenario <= 90) {
    // 30% - Write operations
    writeOperations();
  } else {
    // 10% - Complex workflows
    complexWorkflow();
  }

  // Think time between actions
  sleep(randomIntBetween(1, 3));
}

/**
 * Read operations - most common
 */
function readOperations() {
  group('Read Operations', function () {
    // Get status
    let statusResponse = http.get(`${BASE_URL}/api/v1/status`, { headers });
    check(statusResponse, {
      'status is 200': (r) => r.status === 200,
    }) || errorRate.add(1);
    apiLatency.add(statusResponse.timings.duration);

    sleep(0.5);

    // List messages
    let listResponse = http.get(`${BASE_URL}/api/v1/messages?limit=10`, { headers });
    check(listResponse, {
      'list messages successful': (r) => r.status === 200,
    }) || errorRate.add(1);
    apiLatency.add(listResponse.timings.duration);
  });
}

/**
 * Write operations
 */
function writeOperations() {
  group('Write Operations', function () {
    // Create a message
    let messagePayload = JSON.stringify({
      content: `Load test message ${randomString(10)}`,
      channel: `channel-${randomIntBetween(1, 10)}`,
      metadata: {
        test: true,
        timestamp: new Date().toISOString(),
      },
    });

    let createResponse = http.post(`${BASE_URL}/api/v1/messages`, messagePayload, {
      headers,
    });

    let success = check(createResponse, {
      'message created': (r) => r.status >= 200 && r.status < 300,
    });

    if (success) {
      messagesCreated.add(1);
    } else {
      errorRate.add(1);
    }

    apiLatency.add(createResponse.timings.duration);
  });
}

/**
 * Complex workflow - mimics real user behavior
 */
function complexWorkflow() {
  group('Complex Workflow', function () {
    // Step 1: Create a message
    let messagePayload = JSON.stringify({
      content: `Workflow test ${randomString(8)}`,
      channel: 'workflow-test',
      priority: 'high',
    });

    let createResponse = http.post(`${BASE_URL}/api/v1/messages`, messagePayload, {
      headers,
    });

    if (createResponse.status >= 200 && createResponse.status < 300) {
      messagesCreated.add(1);

      try {
        let messageData = JSON.parse(createResponse.body);
        let messageId = messageData.id || messageData.message_id;

        if (messageId) {
          sleep(1);

          // Step 2: Check message status
          let statusResponse = http.get(
            `${BASE_URL}/api/v1/messages/${messageId}/status`,
            { headers }
          );

          check(statusResponse, {
            'status check successful': (r) => r.status === 200,
          });

          sleep(1);

          // Step 3: Get message details
          let detailResponse = http.get(`${BASE_URL}/api/v1/messages/${messageId}`, {
            headers,
          });

          if (check(detailResponse, {
            'message details retrieved': (r) => r.status === 200,
          })) {
            messagesProcessed.add(1);
          }
        }
      } catch (e) {
        console.error(`Workflow error: ${e.message}`);
        errorRate.add(1);
      }
    } else {
      errorRate.add(1);
    }
  });
}

/**
 * Setup
 */
export function setup() {
  console.log('=== Load Test Configuration ===');
  console.log(`Target URL: ${BASE_URL}`);
  console.log(`Max VUs: 100`);
  console.log(`Duration: 10 minutes`);
  console.log('================================');

  // Verify system is healthy
  let response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    throw new Error(`System not healthy before test: ${response.status}`);
  }

  return { startTime: Date.now() };
}

/**
 * Teardown
 */
export function teardown(data) {
  let duration = (Date.now() - data.startTime) / 1000;
  console.log(`\n=== Load Test Complete ===`);
  console.log(`Duration: ${duration.toFixed(2)} seconds`);
  console.log('===========================\n');
}
