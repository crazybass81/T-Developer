/**
 * T-Developer Spike Testing
 *
 * Tests system behavior under sudden traffic spikes
 */

import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('spike_errors');
const responseTime = new Trend('spike_response_time');

export const options = {
  stages: [
    { duration: '1m', target: 10 },    // Normal load
    { duration: '30s', target: 200 },  // Sudden spike
    { duration: '1m', target: 200 },   // Sustained spike
    { duration: '30s', target: 10 },   // Back to normal
    { duration: '1m', target: 10 },    // Recovery period
  ],

  thresholds: {
    'spike_response_time': ['p(95)<1000'], // Allow higher latency during spike
    'spike_errors': ['rate<0.05'],         // 5% error rate acceptable during spike
    'http_req_failed': ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function() {
  const response = http.get(`${BASE_URL}/health`);

  responseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);

  check(response, {
    'spike test status check': (r) => r.status === 200 || r.status === 503,
    'spike test response exists': (r) => r.body !== null,
  });
}
