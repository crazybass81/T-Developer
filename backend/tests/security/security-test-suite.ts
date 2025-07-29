import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import supertest from 'supertest';
import app from '../../src/app';

class SecurityTestHelper {
  private app: any;
  
  constructor(app: any) {
    this.app = app;
  }
  
  async testSQLInjection(endpoint: string, params: Record<string, string>): Promise<void> {
    const sqlPayloads = [
      "' OR '1'='1",
      "'; DROP TABLE users;--",
      "1' UNION SELECT NULL--",
      "' OR 1=1--",
      "admin'--"
    ];
    
    for (const [key, value] of Object.entries(params)) {
      for (const payload of sqlPayloads) {
        const testParams = { ...params, [key]: payload };
        const response = await supertest(this.app)
          .get(endpoint)
          .query(testParams);
        
        expect(response.text).not.toMatch(/SQL syntax/i);
        expect(response.text).not.toMatch(/mysql_/i);
        expect(response.text).not.toMatch(/ORA-\d+/i);
        expect(response.status).toBeGreaterThanOrEqual(400);
      }
    }
  }
  
  async testXSS(endpoint: string, params: Record<string, string>): Promise<void> {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      '<svg onload=alert("XSS")>',
      'javascript:alert("XSS")'
    ];
    
    for (const [key, value] of Object.entries(params)) {
      for (const payload of xssPayloads) {
        const testParams = { ...params, [key]: payload };
        const response = await supertest(this.app)
          .post(endpoint)
          .send(testParams);
        
        expect(response.text).not.toContain(payload);
        expect(response.text).not.toMatch(/<script/i);
        expect(response.text).not.toMatch(/javascript:/i);
      }
    }
  }
  
  async testAuthBypass(protectedEndpoints: string[]): Promise<void> {
    for (const endpoint of protectedEndpoints) {
      const response1 = await supertest(this.app).get(endpoint);
      expect(response1.status).toBe(401);
      
      const response2 = await supertest(this.app)
        .get(endpoint)
        .set('Authorization', 'Bearer invalid-token');
      expect(response2.status).toBe(401);
    }
  }
  
  async testRateLimiting(endpoint: string, limit: number): Promise<void> {
    const requests = [];
    
    for (let i = 0; i < limit + 5; i++) {
      requests.push(
        supertest(this.app)
          .get(endpoint)
          .set('X-API-Key', 'test-key')
      );
    }
    
    const responses = await Promise.all(requests);
    const rateLimitedResponses = responses.filter(r => r.status === 429);
    expect(rateLimitedResponses.length).toBeGreaterThan(0);
  }
  
  async testSecurityHeaders(endpoint: string): Promise<void> {
    const response = await supertest(this.app).get(endpoint);
    
    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBe('DENY');
    expect(response.headers['x-xss-protection']).toBe('1; mode=block');
    expect(response.headers['strict-transport-security']).toMatch(/max-age=\d+/);
    expect(response.headers['content-security-policy']).toBeDefined();
  }
}

describe('Security Test Suite', () => {
  let securityTester: SecurityTestHelper;
  
  beforeAll(async () => {
    securityTester = new SecurityTestHelper(app);
  });
  
  describe('Injection Attacks', () => {
    test('should prevent SQL injection attacks', async () => {
      await securityTester.testSQLInjection('/api/projects', {
        search: 'test',
        sort: 'name'
      });
    });
    
    test('should prevent command injection', async () => {
      const payloads = ['; ls -la', '| whoami', '`rm -rf /`'];
      
      for (const payload of payloads) {
        const response = await supertest(app)
          .post('/api/execute')
          .send({ command: payload });
        
        expect(response.status).toBe(400);
      }
    });
  });
  
  describe('XSS Prevention', () => {
    test('should prevent reflected XSS', async () => {
      await securityTester.testXSS('/api/projects', {
        name: 'Test Project',
        description: 'Test Description'
      });
    });
  });
  
  describe('Authentication & Authorization', () => {
    test('should prevent authentication bypass', async () => {
      const protectedEndpoints = [
        '/api/projects',
        '/api/agents/execute'
      ];
      
      await securityTester.testAuthBypass(protectedEndpoints);
    });
    
    test('should prevent JWT token manipulation', async () => {
      const manipulatedToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJyb2xlIjoiYWRtaW4ifQ.invalid';
      
      const response = await supertest(app)
        .get('/api/projects')
        .set('Authorization', `Bearer ${manipulatedToken}`);
      
      expect(response.status).toBe(401);
    });
  });
  
  describe('API Security', () => {
    test('should validate API key format', async () => {
      const invalidKeys = ['invalid-key', 'sk_', 'sk_short'];
      
      for (const key of invalidKeys) {
        const response = await supertest(app)
          .get('/api/projects')
          .set('X-API-Key', key);
        
        expect(response.status).toBe(401);
        expect(response.body.code).toBe('INVALID_API_KEY_FORMAT');
      }
    });
  });
  
  describe('Security Headers', () => {
    test('should set all required security headers', async () => {
      await securityTester.testSecurityHeaders('/health');
    });
    
    test('should not expose sensitive information in errors', async () => {
      const response = await supertest(app)
        .get('/api/nonexistent');
      
      expect(response.status).toBe(404);
      expect(response.body).not.toHaveProperty('stack');
      expect(response.body).not.toHaveProperty('sql');
    });
  });
  
  describe('Data Protection', () => {
    test('should mask sensitive data in responses', async () => {
      const response = await supertest(app)
        .get('/api/secure/masked-data');
      
      if (response.status === 200) {
        expect(response.body.email).toMatch(/\*+/);
        expect(response.body.phone).toMatch(/\*+\d{4}$/);
      }
    });
  });
});