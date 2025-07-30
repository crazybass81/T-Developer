const { AgentSquad } = require('./agent-squad.js');

class BaseOrchestrator {
  constructor() {
    this.squad = new AgentSquad({
      maxConcurrentAgents: 50,
      timeout: 300000,
      storage: 'dynamodb'
    });
    
    this.agentRegistry = new Map();
    this.activeSessions = new Map();
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageLatency: 0
    };
  }
  
  async initialize() {
    await this.squad.initialize();
    await this.registerDefaultAgents();
    console.log('✅ BaseOrchestrator initialized');
  }
  
  async registerAgent(name, agent) {
    this.agentRegistry.set(name, agent);
    await this.squad.addAgent(agent);
    console.log(`✅ Agent registered: ${name}`);
  }
  
  async routeTask(task) {
    const startTime = Date.now();
    this.metrics.totalRequests++;
    
    try {
      const taskObj = {
        id: task.id || `task-${Date.now()}`,
        type: task.type || 'general',
        description: task.description || '',
        priority: task.priority || 3,
        createdAt: new Date()
      };
      
      const agentName = this.determineAgent(taskObj);
      const agent = this.agentRegistry.get(agentName);
      
      if (!agent) {
        throw new Error(`No agent found for task: ${JSON.stringify(task)}`);
      }
      
      const result = await agent.execute(task);
      
      const latency = Date.now() - startTime;
      this.updateMetrics(latency, true);
      
      return {
        ...result,
        routing: {
          selectedAgent: agentName,
          routingLatency: latency,
          totalLatency: latency
        }
      };
      
    } catch (error) {
      const latency = Date.now() - startTime;
      this.updateMetrics(latency, false);
      throw error;
    }
  }
  
  determineAgent(task) {
    if (task.type === 'code') return 'code-agent';
    if (task.type === 'test') return 'test-agent';
    return 'default-agent';
  }
  
  async registerDefaultAgents() {
    const defaultAgent = {
      name: 'default-agent',
      execute: async (task) => ({ result: 'processed', task })
    };
    
    const codeAgent = {
      name: 'code-agent',
      execute: async (task) => ({ 
        result: 'Code generated successfully', 
        task,
        generatedCode: 'function example() { return "Hello World"; }'
      })
    };
    
    const testAgent = {
      name: 'test-agent',
      execute: async (task) => ({ 
        result: 'Tests executed successfully', 
        task,
        testResults: { passed: 5, failed: 0 }
      })
    };
    
    await this.registerAgent('default-agent', defaultAgent);
    await this.registerAgent('code-agent', codeAgent);
    await this.registerAgent('test-agent', testAgent);
  }
  
  updateMetrics(latency, success) {
    if (success) {
      this.metrics.successfulRequests++;
    } else {
      this.metrics.failedRequests++;
    }
    
    // Simple moving average
    const totalRequests = this.metrics.successfulRequests + this.metrics.failedRequests;
    this.metrics.averageLatency = 
      (this.metrics.averageLatency * (totalRequests - 1) + latency) / totalRequests;
  }
  
  async getMetrics() {
    return {
      ...this.metrics,
      successRate: this.metrics.totalRequests > 0 
        ? this.metrics.successfulRequests / this.metrics.totalRequests 
        : 0,
      registeredAgents: this.agentRegistry.size,
      activeSessions: this.activeSessions.size
    };
  }
  
  async healthCheck() {
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        orchestrator: 'running',
        agentSquad: 'running',
        agentRegistry: `${this.agentRegistry.size} agents`
      }
    };
  }
  
  getRegisteredAgents() {
    return Array.from(this.agentRegistry.keys());
  }
  
  getAgent(name) {
    return this.agentRegistry.get(name);
  }
  
  async createSession(userId) {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const session = {
      id: sessionId,
      userId,
      createdAt: new Date(),
      lastActivity: new Date(),
      tasks: []
    };
    
    this.activeSessions.set(sessionId, session);
    return sessionId;
  }
  
  getSession(sessionId) {
    return this.activeSessions.get(sessionId);
  }
  
  async executeWithSession(sessionId, task) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }
    
    session.lastActivity = new Date();
    session.tasks.push(task);
    
    return await this.routeTask(task);
  }
}

module.exports = { BaseOrchestrator };