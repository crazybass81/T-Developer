/**
 * T-Developer Stress Testing
 *
 * Tests system limits and breaking points
 */

import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('stress_errors');
const responseTime = new Trend('stress_response_time');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 100 },  // Normal stress
    { duration: '5m', target: 200 },  // High stress
    { duration: '5m', target: 300 },  // Higher stress
    { duration: '5m', target: 400 },  // Breaking point test
    { duration: '2m', target: 0 },    // Ramp down
  ],

  thresholds: {
    'stress_response_time': ['p(95)<2000'], // Allow degraded performance
    'stress_errors': ['rate<0.1'],          // 10% error rate acceptable
    'http_req_failed': ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function() {
  group('Stress Test - Core Endpoints', () => {
    const endpoints = [
      '/health',
      '/api/v1/analyze',
      '/api/v1/research',
      '/api/v1/plan'
    ];

    endpoints.forEach(endpoint => {
      const response = http.get(`${BASE_URL}${endpoint}`);

      responseTime.add(response.timings.duration);
      errorRate.add(response.status >= 400);

      check(response, {
        [`stress ${endpoint} responds`]: (r) => r.status < 500,
        [`stress ${endpoint} performance`]: (r) => r.timings.duration < 5000,
      });
    });
  });
}
