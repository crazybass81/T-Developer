// SubTask 1.19.2: 통합 테스트 실행기
import { TestEnvironmentManager } from './test-environment';

export interface IntegrationTest {
  name: string;
  description: string;
  setup?: () => Promise<void>;
  test: () => Promise<void>;
  teardown?: () => Promise<void>;
  timeout?: number;
}

export interface TestResult {
  name: string;
  success: boolean;
  duration: number;
  error?: string;
}

export interface TestSuite {
  name: string;
  tests: IntegrationTest[];
  beforeAll?: () => Promise<void>;
  afterAll?: () => Promise<void>;
}

export class IntegrationTestRunner {
  private envManager = new TestEnvironmentManager();
  
  async runSuite(suite: TestSuite): Promise<TestResult[]> {
    console.log(`🧪 Running integration test suite: ${suite.name}`);
    
    // Setup environment
    const env = await this.envManager.setupEnvironment('integration');
    
    const results: TestResult[] = [];
    
    try {
      // Run beforeAll
      if (suite.beforeAll) {
        await suite.beforeAll();
      }
      
      // Run tests
      for (const test of suite.tests) {
        const result = await this.runTest(test);
        results.push(result);
        
        if (result.success) {
          console.log(`✅ ${test.name}`);
        } else {
          console.log(`❌ ${test.name}: ${result.error}`);
        }
      }
      
      // Run afterAll
      if (suite.afterAll) {
        await suite.afterAll();
      }
      
    } finally {
      // Cleanup environment
      await this.envManager.teardownEnvironment('integration');
    }
    
    return results;
  }
  
  private async runTest(test: IntegrationTest): Promise<TestResult> {
    const startTime = Date.now();
    
    try {
      // Setup
      if (test.setup) {
        await test.setup();
      }
      
      // Run test with timeout
      await this.withTimeout(test.test(), test.timeout || 30000);
      
      // Teardown
      if (test.teardown) {
        await test.teardown();
      }
      
      return {
        name: test.name,
        success: true,
        duration: Date.now() - startTime
      };
      
    } catch (error: any) {
      return {
        name: test.name,
        success: false,
        duration: Date.now() - startTime,
        error: error.message
      };
    }
  }
  
  private async withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
    const timeout = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Test timeout')), timeoutMs);
    });
    
    return Promise.race([promise, timeout]);
  }
  
  async runParallel(suites: TestSuite[]): Promise<Map<string, TestResult[]>> {
    const results = new Map<string, TestResult[]>();
    
    const promises = suites.map(async (suite) => {
      const suiteResults = await this.runSuite(suite);
      results.set(suite.name, suiteResults);
    });
    
    await Promise.all(promises);
    return results;
  }
}