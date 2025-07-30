// SubTask 1.18.2: 시스템 부하 테스트
interface LoadTestConfig {
  users: number;
  duration: number;
  rampUp: number;
  rampDown: number;
  thinkTime: number;
}

interface LoadTestResult {
  duration: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  throughput: number;
  latency: {
    min: number;
    max: number;
    mean: number;
    p95: number;
  };
}

interface VirtualUserConfig {
  id: number;
  scenario: UserAction[];
  thinkTime: number;
}

interface UserAction {
  name: string;
  method: string;
  url: string;
  body?: any;
}

interface RequestResult {
  action: string;
  success: boolean;
  duration: number;
  statusCode?: number;
  error?: string;
}

export class SystemLoadTester {
  async runLoadTest(
    scenario: LoadTestConfig
  ): Promise<LoadTestResult> {
    const startTime = Date.now();
    const results: RequestResult[] = [];
    
    // Create virtual users
    const users = this.createVirtualUsers(scenario);
    
    // Execute load test
    const promises = users.map(user => this.executeUser(user, scenario.duration));
    const userResults = await Promise.all(promises);
    
    // Flatten results
    userResults.forEach(userResult => results.push(...userResult));
    
    return this.analyzeLoadTestResults(results, Date.now() - startTime);
  }
  
  private createVirtualUsers(config: LoadTestConfig): VirtualUser[] {
    const users: VirtualUser[] = [];
    
    for (let i = 0; i < config.users; i++) {
      users.push(new VirtualUser({
        id: i,
        scenario: this.getDefaultScenario(),
        thinkTime: config.thinkTime
      }));
    }
    
    return users;
  }
  
  private async executeUser(user: VirtualUser, duration: number): Promise<RequestResult[]> {
    return await user.execute(duration);
  }
  
  private analyzeLoadTestResults(results: RequestResult[], duration: number): LoadTestResult {
    const successful = results.filter(r => r.success);
    const durations = results.map(r => r.duration);
    
    return {
      duration,
      totalRequests: results.length,
      successfulRequests: successful.length,
      failedRequests: results.length - successful.length,
      throughput: (results.length / duration) * 1000,
      latency: {
        min: Math.min(...durations),
        max: Math.max(...durations),
        mean: durations.reduce((a, b) => a + b, 0) / durations.length,
        p95: this.percentile(durations, 0.95)
      }
    };
  }
  
  private getDefaultScenario(): UserAction[] {
    return [
      { name: 'login', method: 'POST', url: '/api/auth/login' },
      { name: 'getProjects', method: 'GET', url: '/api/projects' },
      { name: 'createProject', method: 'POST', url: '/api/projects' }
    ];
  }
  
  private percentile(arr: number[], p: number): number {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil(p * sorted.length) - 1;
    return sorted[index];
  }
}

export class VirtualUser {
  constructor(private config: VirtualUserConfig) {}
  
  async execute(duration: number): Promise<RequestResult[]> {
    const results: RequestResult[] = [];
    const endTime = Date.now() + duration;
    
    while (Date.now() < endTime) {
      for (const action of this.config.scenario) {
        const result = await this.executeAction(action);
        results.push(result);
        
        // Think time
        await this.delay(this.randomThinkTime());
      }
    }
    
    return results;
  }
  
  private async executeAction(action: UserAction): Promise<RequestResult> {
    const startTime = Date.now();
    
    try {
      // Mock HTTP request
      await this.delay(Math.random() * 200 + 50); // 50-250ms
      
      return {
        action: action.name,
        success: Math.random() > 0.05, // 95% success rate
        duration: Date.now() - startTime,
        statusCode: 200
      };
    } catch (error: any) {
      return {
        action: action.name,
        success: false,
        duration: Date.now() - startTime,
        error: error.message
      };
    }
  }
  
  private randomThinkTime(): number {
    return Math.random() * this.config.thinkTime;
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}