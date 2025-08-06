import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import supertest from 'supertest';
import { createTestApp } from '../helpers/test-server';

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
        expect(response.status).toBeGreaterThanOrEqual(400);
      }
    }
  }
  
  async testXSS(endpoint: string, params: Record<string, string>): Promise<void> {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      '<svg onload=alert("XSS")>'
    ];
    
    for (const [key, value] of Object.entries(params)) {
      for (const payload of xssPayloads) {
        const testParams = { ...params, [key]: payload };
        const response = await supertest(this.app)
          .post(endpoint)
          .send(testParams);
        
        expect(response.text).not.toContain(payload);
        expect(response.text).not.toMatch(/<script/i);
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
  
  async testSecurityHeaders(endpoint: string): Promise<void> {
    const response = await supertest(this.app).get(endpoint);
    
    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBe('DENY');
    expect(response.headers['x-xss-protection']).toBe('1; mode=block');
    expect(response.headers['x-powered-by']).toBeUndefined();
  }
}

describe('Security Test Suite', () => {
  let app: any;
  let securityTester: SecurityTestHelper;
  
  beforeAll(async () => {
    app = await createTestApp();
    securityTester = new SecurityTestHelper(app);
  });
  
  afterAll(async () => {
    // cleanup
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
        '/api/admin/users',
        '/api/projects/private'
      ];
      
      await securityTester.testAuthBypass(protectedEndpoints);
    });
  });
  
  describe('Security Headers', () => {
    test('should set all required security headers', async () => {
      await securityTester.testSecurityHeaders('/api/health');
    });
  });
});