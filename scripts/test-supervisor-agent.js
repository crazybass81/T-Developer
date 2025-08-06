#!/usr/bin/env node

const path = require('path');

// Mock agent for testing
class MockAgent {
  constructor(name) {
    this.name = name;
  }

  async execute(task) {
    console.log(`${this.name} executing task: ${task.id}`);
    await new Promise(resolve => setTimeout(resolve, 100)); // Simulate work
    return { success: true, result: `${this.name} completed task ${task.id}` };
  }
}

// Test SupervisorAgent implementation
class TestSupervisorAgent {
  constructor() {
    this.subAgents = new Map();
    this.workflowEngine = new WorkflowEngine();
    this.decisionEngine = new DecisionEngine();
    this.executionHistory = new Map();
  }

  async extractIntent(request) {
    return {
      description: request.description || 'Default task',
      type: request.type || 'general',
      priority: request.priority || 1,
      requirements: request.requirements || []
    };
  }

  async analyzeRequest(request) {
    const intent = await this.extractIntent(request);
    const requiredAgents = await this.decisionEngine.determineAgents(intent);
    const workflow = await this.workflowEngine.createWorkflow(intent, requiredAgents);
    
    console.log('✅ Workflow created:', workflow.id);
    return workflow;
  }

  async executeWorkflow(workflow) {
    const results = {};
    
    console.log('🚀 Starting workflow execution:', workflow.id);
    
    for (const step of workflow.steps) {
      const stepResult = await this.executeStep(step);
      results[step.name] = stepResult;
      console.log(`✅ Step completed: ${step.name}`);
    }
    
    console.log('🎉 Workflow completed:', workflow.id);
    return results;
  }

  async executeStep(step) {
    if (step.type === 'parallel') {
      const tasks = step.agents.map(agentName => 
        this.executeAgentTask(agentName, {
          id: `${step.id}-${agentName}`,
          type: step.name,
          input: {},
          timeout: step.timeout
        })
      );
      return Promise.all(tasks);
    } else {
      const results = [];
      for (const agentName of step.agents) {
        const result = await this.executeAgentTask(agentName, {
          id: `${step.id}-${agentName}`,
          type: step.name,
          input: {},
          timeout: step.timeout
        });
        results.push(result);
      }
      return results;
    }
  }

  async executeAgentTask(agentName, task) {
    const agent = this.subAgents.get(agentName);
    if (!agent) {
      throw new Error(`Agent ${agentName} not found`);
    }

    const startTime = Date.now();
    
    try {
      const result = await agent.execute(task);
      const duration = Date.now() - startTime;
      this.recordExecution(agentName, task, result, duration);
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.recordExecution(agentName, task, null, duration, error);
      throw error;
    }
  }

  recordExecution(agentName, task, result, duration, error) {
    const execution = {
      agentName,
      taskId: task.id,
      duration,
      success: !error,
      error: error?.message,
      timestamp: new Date().toISOString()
    };
    
    this.executionHistory.set(task.id, execution);
  }

  registerAgent(name, agent) {
    this.subAgents.set(name, agent);
    console.log(`📝 Agent registered: ${name}`);
  }
}

class WorkflowEngine {
  constructor() {
    this.templates = new Map();
  }

  async createWorkflow(intent, agents) {
    return this.createDynamicWorkflow(intent, agents);
  }

  createDynamicWorkflow(intent, agents) {
    const steps = [];
    
    agents.forEach((agent, index) => {
      steps.push({
        id: `step-${index}`,
        name: `Execute ${agent}`,
        type: 'sequential',
        agents: [agent],
        dependencies: index > 0 ? [`step-${index - 1}`] : [],
        timeout: 300000
      });
    });
    
    return {
      id: `workflow-${Date.now()}`,
      steps,
      metadata: { type: 'dynamic', intent: intent.type }
    };
  }
}

class DecisionEngine {
  constructor() {
    this.rules = [
      { pattern: /code|implement|develop/i, agents: ['CodeAgent'] },
      { pattern: /test|verify|validate/i, agents: ['TestAgent'] },
      { pattern: /design|architect/i, agents: ['DesignAgent'] },
      { pattern: /security|vulnerabilit/i, agents: ['SecurityAgent'] }
    ];
  }

  async determineAgents(intent) {
    const matchedAgents = new Set();
    
    for (const rule of this.rules) {
      if (rule.pattern.test(intent.description)) {
        rule.agents.forEach(agent => matchedAgents.add(agent));
      }
    }
    
    if (matchedAgents.size === 0) {
      matchedAgents.add('GeneralAgent');
    }
    
    return Array.from(matchedAgents);
  }
}

async function testSupervisorAgent() {
  console.log('🧪 Testing SupervisorAgent Architecture...\n');

  const supervisor = new TestSupervisorAgent();

  // Register mock agents
  supervisor.registerAgent('CodeAgent', new MockAgent('CodeAgent'));
  supervisor.registerAgent('TestAgent', new MockAgent('TestAgent'));
  supervisor.registerAgent('DesignAgent', new MockAgent('DesignAgent'));
  supervisor.registerAgent('SecurityAgent', new MockAgent('SecurityAgent'));
  supervisor.registerAgent('GeneralAgent', new MockAgent('GeneralAgent'));

  // Test 1: Code development request
  console.log('📋 Test 1: Code development request');
  const codeRequest = {
    description: 'Implement a REST API for user management',
    type: 'development',
    priority: 1,
    requirements: ['authentication', 'CRUD operations']
  };

  const workflow1 = await supervisor.analyzeRequest(codeRequest);
  const result1 = await supervisor.executeWorkflow(workflow1);
  console.log('Result:', result1);
  console.log('');

  // Test 2: Security review request
  console.log('📋 Test 2: Security review request');
  const securityRequest = {
    description: 'Review application for security vulnerabilities',
    type: 'security',
    priority: 2,
    requirements: ['vulnerability scan', 'code review']
  };

  const workflow2 = await supervisor.analyzeRequest(securityRequest);
  const result2 = await supervisor.executeWorkflow(workflow2);
  console.log('Result:', result2);
  console.log('');

  // Test 3: General request (fallback)
  console.log('📋 Test 3: General request (fallback)');
  const generalRequest = {
    description: 'Help me with project planning',
    type: 'general',
    priority: 1
  };

  const workflow3 = await supervisor.analyzeRequest(generalRequest);
  const result3 = await supervisor.executeWorkflow(workflow3);
  console.log('Result:', result3);
  console.log('');

  console.log('✅ All SupervisorAgent tests completed successfully!');
  
  // Show execution history
  console.log('\n📊 Execution History:');
  const history = Array.from(supervisor.executionHistory.values());
  history.forEach(exec => {
    console.log(`- ${exec.agentName}: ${exec.taskId} (${exec.duration}ms) ${exec.success ? '✅' : '❌'}`);
  });
}

// Run tests
testSupervisorAgent().catch(console.error);