import supertest from 'supertest';
import app from '../../src/app';

export class PenetrationTester {
  private app: any;
  
  constructor(app: any) {
    this.app = app;
  }
  
  async runFullSecurityScan(): Promise<SecurityScanReport> {
    console.log('🔒 Starting penetration test...');
    
    const results = await Promise.all([
      this.testInjectionVulnerabilities(),
      this.testAuthenticationFlaws(),
      this.testSessionManagement(),
      this.testInputValidation(),
      this.testErrorHandling()
    ]);
    
    return {
      timestamp: new Date().toISOString(),
      results: results.flat(),
      summary: this.generateSummary(results.flat())
    };
  }
  
  private async testInjectionVulnerabilities(): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // SQL Injection
    const sqlPayloads = ["' OR 1=1--", "'; DROP TABLE users;--"];
    for (const payload of sqlPayloads) {
      const response = await supertest(this.app)
        .get('/api/projects')
        .query({ search: payload });
      
      results.push({
        test: 'SQL Injection',
        payload,
        passed: !response.text.match(/SQL|mysql|error/i),
        severity: 'high'
      });
    }
    
    // NoSQL Injection
    const noSqlPayload = { '$ne': null };
    const noSqlResponse = await supertest(this.app)
      .post('/api/projects/search')
      .send({ filter: noSqlPayload });
    
    results.push({
      test: 'NoSQL Injection',
      payload: JSON.stringify(noSqlPayload),
      passed: noSqlResponse.status === 400,
      severity: 'high'
    });
    
    return results;
  }
  
  private async testAuthenticationFlaws(): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // Weak password test
    const weakPasswords = ['123456', 'password', 'admin'];
    for (const password of weakPasswords) {
      const response = await supertest(this.app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com', password });
      
      results.push({
        test: 'Weak Password Rejection',
        payload: password,
        passed: response.status !== 200,
        severity: 'medium'
      });
    }
    
    // Brute force protection
    const bruteForceAttempts = Array(10).fill(0).map((_, i) => 
      supertest(this.app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com', password: `wrong${i}` })
    );
    
    const bruteForceResponses = await Promise.all(bruteForceAttempts);
    const blockedResponses = bruteForceResponses.filter(r => r.status === 429);
    
    results.push({
      test: 'Brute Force Protection',
      payload: '10 failed attempts',
      passed: blockedResponses.length > 0,
      severity: 'high'
    });
    
    return results;
  }
  
  private async testSessionManagement(): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // Session fixation
    const response1 = await supertest(this.app).get('/api/auth/session');
    const sessionId1 = response1.headers['set-cookie']?.[0];
    
    const response2 = await supertest(this.app)
      .post('/api/auth/login')
      .set('Cookie', sessionId1 || '')
      .send({ email: 'test@example.com', password: 'validpassword' });
    
    const sessionId2 = response2.headers['set-cookie']?.[0];
    
    results.push({
      test: 'Session Fixation Prevention',
      payload: 'session_id_change',
      passed: sessionId1 !== sessionId2,
      severity: 'medium'
    });
    
    return results;
  }
  
  private async testInputValidation(): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // Large payload test
    const largePayload = 'A'.repeat(1024 * 1024 * 11); // 11MB
    const response = await supertest(this.app)
      .post('/api/projects')
      .send({ name: largePayload });
    
    results.push({
      test: 'Large Payload Rejection',
      payload: '11MB payload',
      passed: response.status === 413,
      severity: 'medium'
    });
    
    // Invalid JSON
    const invalidJsonResponse = await supertest(this.app)
      .post('/api/projects')
      .set('Content-Type', 'application/json')
      .send('{"invalid": json}');
    
    results.push({
      test: 'Invalid JSON Handling',
      payload: 'malformed JSON',
      passed: invalidJsonResponse.status === 400,
      severity: 'low'
    });
    
    return results;
  }
  
  private async testErrorHandling(): Promise<TestResult[]> {
    const results: TestResult[] = [];
    
    // Stack trace exposure
    const response = await supertest(this.app)
      .get('/api/nonexistent/endpoint/that/causes/error');
    
    results.push({
      test: 'Stack Trace Exposure',
      payload: 'error_endpoint',
      passed: !response.text.includes('at ') && !response.text.includes('Error:'),
      severity: 'low'
    });
    
    return results;
  }
  
  private generateSummary(results: TestResult[]): SecuritySummary {
    const passed = results.filter(r => r.passed).length;
    const failed = results.length - passed;
    const high = results.filter(r => r.severity === 'high' && !r.passed).length;
    const medium = results.filter(r => r.severity === 'medium' && !r.passed).length;
    const low = results.filter(r => r.severity === 'low' && !r.passed).length;
    
    return {
      total: results.length,
      passed,
      failed,
      vulnerabilities: { high, medium, low },
      score: Math.round((passed / results.length) * 100)
    };
  }
}

interface TestResult {
  test: string;
  payload: string;
  passed: boolean;
  severity: 'high' | 'medium' | 'low';
}

interface SecuritySummary {
  total: number;
  passed: number;
  failed: number;
  vulnerabilities: {
    high: number;
    medium: number;
    low: number;
  };
  score: number;
}

interface SecurityScanReport {
  timestamp: string;
  results: TestResult[];
  summary: SecuritySummary;
}

export async function runAutomatedSecurityScan(): Promise<void> {
  const tester = new PenetrationTester(app);
  const report = await tester.runFullSecurityScan();
  
  console.log('📊 Security Scan Results:');
  console.log(`Score: ${report.summary.score}/100`);
  console.log(`Vulnerabilities: High(${report.summary.vulnerabilities.high}) Medium(${report.summary.vulnerabilities.medium}) Low(${report.summary.vulnerabilities.low})`);
  
  // Save report
  const fs = require('fs');
  fs.writeFileSync('security-report.json', JSON.stringify(report, null, 2));
  
  console.log('✅ Security scan completed. Report saved to security-report.json');
}