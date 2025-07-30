// Agent integration tests
import { TestSuite } from './test-runner';

export class MockAgent {
  constructor(
    public name: string,
    public type: string
  ) {}
  
  async execute(input: any): Promise<any> {
    // Simulate processing time
    await this.delay(Math.random() * 200 + 100);
    
    // Simulate different agent behaviors
    switch (this.type) {
      case 'nl-input':
        return {
          success: true,
          parsed: {
            intent: 'create_web_app',
            requirements: ['user_auth', 'database', 'api']
          }
        };
        
      case 'generation':
        return {
          success: true,
          generated: {
            files: ['app.js', 'package.json', 'README.md'],
            code: 'console.log("Generated code");'
          }
        };
        
      case 'assembly':
        return {
          success: true,
          assembled: {
            package: 'project.zip',
            size: 1024000
          }
        };
        
      default:
        return { success: true, result: 'processed' };
    }
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export class AgentOrchestrator {
  private agents: Map<string, MockAgent> = new Map();
  
  registerAgent(agent: MockAgent): void {
    this.agents.set(agent.name, agent);
  }
  
  async executeWorkflow(workflow: string[]): Promise<any[]> {
    const results: any[] = [];
    
    for (const agentName of workflow) {
      const agent = this.agents.get(agentName);
      if (!agent) {
        throw new Error(`Agent ${agentName} not found`);
      }
      
      const result = await agent.execute({ previousResults: results });
      results.push(result);
    }
    
    return results;
  }
  
  async executeParallel(agentNames: string[], input: any): Promise<any[]> {
    const promises = agentNames.map(name => {
      const agent = this.agents.get(name);
      if (!agent) {
        throw new Error(`Agent ${name} not found`);
      }
      return agent.execute(input);
    });
    
    return Promise.all(promises);
  }
}

export const agentTestSuite: TestSuite = {
  name: 'Agent Integration Tests',
  
  beforeAll: async () => {
    console.log('🤖 Setting up agent test environment...');
  },
  
  afterAll: async () => {
    console.log('🧹 Cleaning up agent test data...');
  },
  
  tests: [
    {
      name: 'Single Agent Execution',
      description: 'Test individual agent execution',
      test: async () => {
        const agent = new MockAgent('test-agent', 'nl-input');
        
        const result = await agent.execute({
          input: 'Create a web application with user authentication'
        });
        
        if (!result.success) {
          throw new Error('Agent execution failed');
        }
        
        if (!result.parsed || !result.parsed.intent) {
          throw new Error('Agent output validation failed');
        }
      }
    },
    
    {
      name: 'Agent Workflow Execution',
      description: 'Test sequential agent workflow',
      test: async () => {
        const orchestrator = new AgentOrchestrator();
        
        // Register agents
        orchestrator.registerAgent(new MockAgent('nl-input', 'nl-input'));
        orchestrator.registerAgent(new MockAgent('generation', 'generation'));
        orchestrator.registerAgent(new MockAgent('assembly', 'assembly'));
        
        // Execute workflow
        const workflow = ['nl-input', 'generation', 'assembly'];
        const results = await orchestrator.executeWorkflow(workflow);
        
        if (results.length !== 3) {
          throw new Error(`Expected 3 results, got ${results.length}`);
        }
        
        // Verify each step succeeded
        for (const result of results) {
          if (!result.success) {
            throw new Error('Workflow step failed');
          }
        }
      }
    },
    
    {
      name: 'Parallel Agent Execution',
      description: 'Test parallel agent execution',
      test: async () => {
        const orchestrator = new AgentOrchestrator();
        
        // Register multiple agents of same type
        for (let i = 1; i <= 3; i++) {
          orchestrator.registerAgent(new MockAgent(`agent-${i}`, 'generation'));
        }
        
        const startTime = Date.now();
        const results = await orchestrator.executeParallel(
          ['agent-1', 'agent-2', 'agent-3'],
          { task: 'parallel processing' }
        );
        const duration = Date.now() - startTime;
        
        if (results.length !== 3) {
          throw new Error(`Expected 3 results, got ${results.length}`);
        }
        
        // Parallel execution should be faster than sequential
        if (duration > 500) { // Should complete in under 500ms for parallel
          throw new Error('Parallel execution took too long');
        }
        
        // Verify all succeeded
        for (const result of results) {
          if (!result.success) {
            throw new Error('Parallel agent execution failed');
          }
        }
      }
    },
    
    {
      name: 'Agent Error Handling',
      description: 'Test agent error handling and recovery',
      test: async () => {
        const orchestrator = new AgentOrchestrator();
        
        // Create an agent that fails
        const failingAgent = new MockAgent('failing-agent', 'error');
        failingAgent.execute = async () => {
          throw new Error('Simulated agent failure');
        };
        
        orchestrator.registerAgent(failingAgent);
        orchestrator.registerAgent(new MockAgent('recovery-agent', 'generation'));
        
        // Test error handling
        try {
          await orchestrator.executeWorkflow(['failing-agent', 'recovery-agent']);
          throw new Error('Expected workflow to fail');
        } catch (error: any) {
          if (!error.message.includes('Simulated agent failure')) {
            throw new Error('Unexpected error type');
          }
        }
      }
    },
    
    {
      name: 'Agent State Management',
      description: 'Test agent state persistence and sharing',
      test: async () => {
        const orchestrator = new AgentOrchestrator();
        
        // Create stateful agents
        class StatefulAgent extends MockAgent {
          private state: any = {};
          
          async execute(input: any): Promise<any> {
            // Update state based on input
            if (input.setState) {
              this.state = { ...this.state, ...input.setState };
            }
            
            return {
              success: true,
              state: this.state,
              result: `Processed with state: ${JSON.stringify(this.state)}`
            };
          }
        }
        
        const agent1 = new StatefulAgent('stateful-1', 'stateful');
        const agent2 = new StatefulAgent('stateful-2', 'stateful');
        
        orchestrator.registerAgent(agent1);
        orchestrator.registerAgent(agent2);
        
        // Set state in first agent
        const result1 = await agent1.execute({
          setState: { step: 1, data: 'test' }
        });
        
        if (!result1.state || result1.state.step !== 1) {
          throw new Error('State setting failed');
        }
        
        // Verify state persistence
        const result2 = await agent1.execute({});
        
        if (!result2.state || result2.state.step !== 1) {
          throw new Error('State persistence failed');
        }
      }
    },
    
    {
      name: 'Agent Performance Monitoring',
      description: 'Test agent performance tracking',
      test: async () => {
        const agent = new MockAgent('perf-agent', 'generation');
        const metrics: any[] = [];
        
        // Wrap agent execution with performance monitoring
        const originalExecute = agent.execute.bind(agent);
        agent.execute = async function(input: any) {
          const startTime = Date.now();
          const startMemory = process.memoryUsage().heapUsed;
          
          try {
            const result = await originalExecute(input);
            
            metrics.push({
              duration: Date.now() - startTime,
              memoryUsed: process.memoryUsage().heapUsed - startMemory,
              success: true
            });
            
            return result;
          } catch (error) {
            metrics.push({
              duration: Date.now() - startTime,
              memoryUsed: process.memoryUsage().heapUsed - startMemory,
              success: false,
              error: error.message
            });
            throw error;
          }
        };
        
        // Execute multiple times
        for (let i = 0; i < 5; i++) {
          await agent.execute({ iteration: i });
        }
        
        // Verify metrics collection
        if (metrics.length !== 5) {
          throw new Error(`Expected 5 metrics, got ${metrics.length}`);
        }
        
        const avgDuration = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length;
        
        if (avgDuration <= 0) {
          throw new Error('Invalid performance metrics');
        }
      }
    }
  ]
};