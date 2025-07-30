// Test load testing system
class VirtualUser {
  constructor(config) {
    this.config = config;
  }
  
  async execute(duration) {
    const results = [];
    const endTime = Date.now() + duration;
    
    while (Date.now() < endTime) {
      for (const action of this.config.scenario) {
        const result = await this.executeAction(action);
        results.push(result);
        
        // Think time
        await this.delay(Math.random() * this.config.thinkTime);
      }
    }
    
    return results;
  }
  
  async executeAction(action) {
    const startTime = Date.now();
    
    try {
      // Mock HTTP request with realistic delays
      const delay = Math.random() * 200 + 50; // 50-250ms
      await this.delay(delay);
      
      // 95% success rate
      const success = Math.random() > 0.05;
      
      return {
        action: action.name,
        success,
        duration: Date.now() - startTime,
        statusCode: success ? 200 : 500
      };
    } catch (error) {
      return {
        action: action.name,
        success: false,
        duration: Date.now() - startTime,
        error: error.message
      };
    }
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class SystemLoadTester {
  async runLoadTest(config) {
    console.log(`🚀 Starting load test: ${config.users} users for ${config.duration}ms`);
    
    const startTime = Date.now();
    const results = [];
    
    // Create virtual users
    const users = this.createVirtualUsers(config);
    
    console.log(`👥 Created ${users.length} virtual users`);
    
    // Execute load test
    const promises = users.map((user, index) => {
      return new Promise(async (resolve) => {
        // Stagger user start times (ramp up)
        const startDelay = (config.rampUp / config.users) * index;
        await new Promise(r => setTimeout(r, startDelay));
        
        const userResults = await user.execute(config.duration - startDelay);
        resolve(userResults);
      });
    });
    
    const userResults = await Promise.all(promises);
    
    // Flatten results
    userResults.forEach(userResult => results.push(...userResult));
    
    return this.analyzeLoadTestResults(results, Date.now() - startTime);
  }
  
  createVirtualUsers(config) {
    const users = [];
    
    for (let i = 0; i < config.users; i++) {
      users.push(new VirtualUser({
        id: i,
        scenario: [
          { name: 'login', method: 'POST', url: '/api/auth/login' },
          { name: 'getProjects', method: 'GET', url: '/api/projects' },
          { name: 'createProject', method: 'POST', url: '/api/projects' }
        ],
        thinkTime: config.thinkTime
      }));
    }
    
    return users;
  }
  
  analyzeLoadTestResults(results, duration) {
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
  
  percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil(p * sorted.length) - 1;
    return sorted[index];
  }
}

// Test load testing
async function testLoadTesting() {
  console.log('⚡ Starting Load Testing Test\n');
  
  const loadTester = new SystemLoadTester();
  
  const config = {
    users: 10,
    duration: 5000, // 5 seconds
    rampUp: 2000,   // 2 seconds ramp up
    rampDown: 1000, // 1 second ramp down
    thinkTime: 500  // 500ms think time
  };
  
  try {
    const result = await loadTester.runLoadTest(config);
    
    console.log('\n📈 Load Test Results:');
    console.log('===================');
    console.log(`Duration: ${result.duration}ms`);
    console.log(`Total Requests: ${result.totalRequests}`);
    console.log(`Successful: ${result.successfulRequests}`);
    console.log(`Failed: ${result.failedRequests}`);
    console.log(`Success Rate: ${((result.successfulRequests / result.totalRequests) * 100).toFixed(2)}%`);
    console.log(`Throughput: ${result.throughput.toFixed(2)} RPS`);
    console.log('\nLatency:');
    console.log(`  Min: ${result.latency.min.toFixed(2)}ms`);
    console.log(`  Max: ${result.latency.max.toFixed(2)}ms`);
    console.log(`  Mean: ${result.latency.mean.toFixed(2)}ms`);
    console.log(`  P95: ${result.latency.p95.toFixed(2)}ms`);
    
    console.log('\n✅ Load testing test completed!');
    
  } catch (error) {
    console.error('❌ Load test failed:', error.message);
  }
}

// Run the test
testLoadTesting();