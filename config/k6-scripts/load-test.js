/**
 * T-Developer Load Testing Suite
 *
 * Phase 6: P6-T2 - Reliability Engineering
 * Comprehensive load testing scenarios for T-Developer APIs
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// Custom metrics
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const throughputCounter = new Counter('requests_total');

// Test configuration
export const options = {
  stages: [
    // Ramp up
    { duration: '2m', target: 10 },   // Ramp up to 10 users over 2 minutes
    { duration: '5m', target: 10 },   // Stay at 10 users for 5 minutes
    { duration: '2m', target: 50 },   // Ramp up to 50 users over 2 minutes
    { duration: '5m', target: 50 },   // Stay at 50 users for 5 minutes
    { duration: '2m', target: 100 },  // Ramp up to 100 users over 2 minutes
    { duration: '5m', target: 100 },  // Stay at 100 users for 5 minutes
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],

  thresholds: {
    // 95% of requests should complete within 200ms (P95 < 200ms target)
    'http_req_duration': ['p(95)<200'],

    // 99% of requests should complete within 500ms
    'http_req_duration{scenario:main}': ['p(99)<500'],

    // Error rate should be less than 1%
    'errors': ['rate<0.01'],

    // Request success rate should be above 99%
    'http_req_failed': ['rate<0.01'],

    // API latency should be within SLA
    'api_latency': ['p(95)<200', 'p(99)<500'],
  },

  // Environment configuration
  ext: {
    loadimpact: {
      distribution: {
        'amazon:us:ashburn': { loadZone: 'amazon:us:ashburn', percent: 50 },
        'amazon:gb:london': { loadZone: 'amazon:gb:london', percent: 25 },
        'amazon:sg:singapore': { loadZone: 'amazon:sg:singapore', percent: 25 },
      },
    },
  },
};

// Base configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || 'test-token';

// Request headers
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_TOKEN}`,
  'User-Agent': 'k6-load-test/1.0',
};

// Test data
const testRequirements = [
  {
    type: "microservice",
    description: "Create a user authentication service",
    requirements: {
      framework: "FastAPI",
      database: "PostgreSQL",
      auth: "JWT"
    }
  },
  {
    type: "rest-api",
    description: "Build a product catalog API",
    requirements: {
      framework: "Express",
      database: "MongoDB",
      features: ["CRUD", "search", "pagination"]
    }
  },
  {
    type: "web-app",
    description: "Develop a todo application",
    requirements: {
      frontend: "React",
      backend: "Node.js",
      database: "SQLite"
    }
  }
];

// Helper functions
function makeRequest(method, endpoint, payload = null) {
  const url = `${BASE_URL}${endpoint}`;
  const params = {
    headers: headers,
    timeout: '30s',
  };

  let response;
  const startTime = new Date().getTime();

  if (method === 'GET') {
    response = http.get(url, params);
  } else if (method === 'POST') {
    response = http.post(url, JSON.stringify(payload), params);
  } else if (method === 'PUT') {
    response = http.put(url, JSON.stringify(payload), params);
  } else if (method === 'DELETE') {
    response = http.del(url, null, params);
  }

  const endTime = new Date().getTime();
  const latency = endTime - startTime;

  // Record metrics
  apiLatency.add(latency);
  throughputCounter.add(1);

  // Check for errors
  const isError = response.status >= 400;
  errorRate.add(isError);

  return response;
}

function randomChoice(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Test scenarios
export default function() {
  group('Health Check', () => {
    const response = makeRequest('GET', '/health');

    check(response, {
      'health check status is 200': (r) => r.status === 200,
      'health check response time < 100ms': (r) => r.timings.duration < 100,
    });
  });

  group('Service Creation Flow', () => {
    // Step 1: Analyze requirements
    const requirement = randomChoice(testRequirements);

    const analyzeResponse = makeRequest('POST', '/api/v1/analyze', {
      description: requirement.description,
      type: requirement.type,
      requirements: requirement.requirements
    });

    check(analyzeResponse, {
      'analyze requirements status is 200': (r) => r.status === 200,
      'analyze requirements response time < 2s': (r) => r.timings.duration < 2000,
      'analyze response has required fields': (r) => {
        const body = JSON.parse(r.body);
        return body.hasOwnProperty('analysis_id') && body.hasOwnProperty('recommendations');
      },
    });

    if (analyzeResponse.status !== 200) {
      return;
    }

    const analysisId = JSON.parse(analyzeResponse.body).analysis_id;

    // Step 2: Generate service blueprint
    const blueprintResponse = makeRequest('POST', '/api/v1/blueprint', {
      analysis_id: analysisId,
      optimization_level: 'balanced'
    });

    check(blueprintResponse, {
      'blueprint generation status is 200': (r) => r.status === 200,
      'blueprint generation response time < 5s': (r) => r.timings.duration < 5000,
      'blueprint response has structure': (r) => {
        const body = JSON.parse(r.body);
        return body.hasOwnProperty('blueprint_id') && body.hasOwnProperty('components');
      },
    });

    if (blueprintResponse.status !== 200) {
      return;
    }

    const blueprintId = JSON.parse(blueprintResponse.body).blueprint_id;

    // Step 3: Check generation status
    const statusResponse = makeRequest('GET', `/api/v1/status/${blueprintId}`);

    check(statusResponse, {
      'status check is 200': (r) => r.status === 200,
      'status response time < 500ms': (r) => r.timings.duration < 500,
    });
  });

  group('Agent Operations', () => {
    // Research agent
    const researchResponse = makeRequest('POST', '/api/v1/research', {
      query: 'Best practices for microservice authentication',
      scope: 'architecture'
    });

    check(researchResponse, {
      'research agent status is 200': (r) => r.status === 200,
      'research response time < 3s': (r) => r.timings.duration < 3000,
    });

    // Planning agent
    const planResponse = makeRequest('POST', '/api/v1/plan', {
      requirements: randomChoice(testRequirements).requirements,
      constraints: {
        time_limit: '2h',
        complexity: 'medium'
      }
    });

    check(planResponse, {
      'planning agent status is 200': (r) => r.status === 200,
      'planning response time < 2s': (r) => r.timings.duration < 2000,
    });
  });

  group('Performance Critical Endpoints', () => {
    // Cache-heavy endpoint
    const cacheResponse = makeRequest('GET', '/api/v1/cache/patterns');

    check(cacheResponse, {
      'cache endpoint status is 200': (r) => r.status === 200,
      'cache endpoint response time < 50ms': (r) => r.timings.duration < 50,
    });

    // Database query endpoint
    const queryResponse = makeRequest('GET', '/api/v1/query/templates?limit=10');

    check(queryResponse, {
      'query endpoint status is 200': (r) => r.status === 200,
      'query endpoint response time < 100ms': (r) => r.timings.duration < 100,
    });
  });

  group('Error Handling', () => {
    // Test invalid input
    const invalidResponse = makeRequest('POST', '/api/v1/analyze', {
      invalid: 'data'
    });

    check(invalidResponse, {
      'invalid input returns 400': (r) => r.status === 400,
      'error response has message': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.hasOwnProperty('error') || body.hasOwnProperty('message');
        } catch (e) {
          return false;
        }
      },
    });

    // Test non-existent endpoint
    const notFoundResponse = makeRequest('GET', '/api/v1/nonexistent');

    check(notFoundResponse, {
      'non-existent endpoint returns 404': (r) => r.status === 404,
    });
  });

  // Random sleep between 1-3 seconds to simulate real user behavior
  sleep(Math.random() * 2 + 1);
}

// Spike test scenario
export function spikeTest() {
  group('Spike Test - High Load', () => {
    // Simulate sudden traffic spike
    for (let i = 0; i < 10; i++) {
      const response = makeRequest('GET', '/health');
      check(response, {
        'spike test health check': (r) => r.status === 200,
      });
    }
  });
}

// Stress test scenario
export function stressTest() {
  group('Stress Test - Resource Intensive', () => {
    const stressResponse = makeRequest('POST', '/api/v1/analyze', {
      description: 'Complex enterprise microservices architecture with multiple databases, message queues, and external APIs',
      type: 'enterprise-system',
      requirements: {
        services: 20,
        databases: ['PostgreSQL', 'MongoDB', 'Redis'],
        queues: ['RabbitMQ', 'Apache Kafka'],
        apis: ['REST', 'GraphQL', 'gRPC'],
        monitoring: true,
        logging: true,
        security: 'enterprise'
      }
    });

    check(stressResponse, {
      'stress test completes': (r) => r.status === 200 || r.status === 202,
      'stress test response time acceptable': (r) => r.timings.duration < 10000,
    });
  });
}

// Endurance test scenario
export function enduranceTest() {
  group('Endurance Test - Long Running', () => {
    // Simulate long-running operations
    const requirement = randomChoice(testRequirements);

    const response = makeRequest('POST', '/api/v1/generate', {
      ...requirement,
      options: {
        detailed_documentation: true,
        comprehensive_tests: true,
        production_ready: true
      }
    });

    check(response, {
      'endurance test handles long operations': (r) => r.status === 200 || r.status === 202,
      'endurance test memory efficient': (r) => r.timings.duration < 30000,
    });
  });
}

// Generate HTML report
export function handleSummary(data) {
  return {
    'load-test-report.html': htmlReport(data),
    'load-test-summary.txt': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}

// Setup function (runs once at the beginning)
export function setup() {
  console.log('Starting T-Developer load test...');
  console.log(`Target: ${BASE_URL}`);
  console.log(`VUs: ${options.stages.map(s => s.target).reduce((a, b) => Math.max(a, b))}`);

  // Warm up the system
  const warmupResponse = makeRequest('GET', '/health');
  if (warmupResponse.status !== 200) {
    console.error('System not ready for load testing');
    throw new Error('Health check failed during setup');
  }

  return { startTime: new Date().toISOString() };
}

// Teardown function (runs once at the end)
export function teardown(data) {
  console.log('Load test completed');
  console.log(`Started at: ${data.startTime}`);
  console.log(`Ended at: ${new Date().toISOString()}`);
}
