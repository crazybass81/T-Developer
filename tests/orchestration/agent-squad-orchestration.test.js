const { BaseOrchestrator } = require('../../backend/src/orchestration/base-orchestrator.js');
const { AgentSquad, SupervisorAgent } = require('../../backend/src/orchestration/agent-squad.js');
const { AgentRegistry } = require('../../backend/src/orchestration/agent-registry.js');

describe('Task 1.1: Agent Squad 오케스트레이션 설정', () => {
  describe('AgentSquad', () => {
    let agentSquad;

    beforeEach(() => {
      agentSquad = new AgentSquad({
        maxConcurrentAgents: 50,
        timeout: 300000,
        storage: 'dynamodb'
      });
    });

    test('should initialize successfully', async () => {
      await agentSquad.initialize();
      expect(agentSquad.agents).toBeDefined();
      expect(agentSquad.activeExecutions).toBeDefined();
    });

    test('should add agents to squad', async () => {
      const testAgent = {
        name: 'test-agent',
        execute: async (task) => ({ result: 'test completed' })
      };

      await agentSquad.addAgent(testAgent);

      expect(agentSquad.agents.has('test-agent')).toBe(true);
      expect(agentSquad.getAgent('test-agent')).toEqual(testAgent);
    });

    test('should classify task complexity', async () => {
      const simpleTask = 'Simple task';
      const complexTask = 'This is a very complex task that requires multiple steps and careful consideration of various factors and dependencies';

      const simpleClassification = await agentSquad.classify(simpleTask);
      const complexClassification = await agentSquad.classify(complexTask);

      expect(simpleClassification.complexity).toBe(0.3);
      expect(complexClassification.complexity).toBe(0.8);
      expect(simpleClassification.confidence).toBe(0.85);
    });

    test('should select appropriate agents based on description', () => {
      const codeTask = 'Develop a new feature with code';
      const testTask = 'Run tests for the application';
      const uiTask = 'Design user interface components';
      const generalTask = 'General administrative task';

      expect(agentSquad.selectAgents(codeTask)).toContain('generation-agent');
      expect(agentSquad.selectAgents(testTask)).toContain('test-agent');
      expect(agentSquad.selectAgents(uiTask)).toContain('ui-agent');
      expect(agentSquad.selectAgents(generalTask)).toEqual(['nl-input-agent']);
    });

    test('should handle multiple agent selection', () => {
      const multiTask = 'Develop code and create tests with UI interface';
      const selectedAgents = agentSquad.selectAgents(multiTask);

      expect(selectedAgents).toContain('generation-agent');
      expect(selectedAgents).toContain('test-agent');
      expect(selectedAgents).toContain('ui-agent');
    });
  });

  describe('BaseOrchestrator', () => {
    let orchestrator;

    beforeEach(async () => {
      orchestrator = new BaseOrchestrator();
      await orchestrator.initialize();
    });

    test('should initialize with default agents', async () => {
      const agents = orchestrator.getRegisteredAgents();

      expect(agents).toContain('default-agent');
      expect(agents).toContain('code-agent');
      expect(agents).toContain('test-agent');
      expect(agents.length).toBe(3);
    });

    test('should register new agents', async () => {
      const customAgent = {
        name: 'custom-agent',
        execute: async (task) => ({ result: 'custom processing', task })
      };

      await orchestrator.registerAgent('custom-agent', customAgent);

      const agents = orchestrator.getRegisteredAgents();
      expect(agents).toContain('custom-agent');
      expect(orchestrator.getAgent('custom-agent')).toEqual(customAgent);
    });

    test('should route tasks to appropriate agents', async () => {
      const codeTask = {
        id: 'task-1',
        type: 'code',
        description: 'Generate authentication code'
      };

      const testTask = {
        id: 'task-2',
        type: 'test',
        description: 'Run unit tests'
      };

      const codeResult = await orchestrator.routeTask(codeTask);
      const testResult = await orchestrator.routeTask(testTask);

      expect(codeResult.routing.selectedAgent).toBe('code-agent');
      expect(codeResult.result).toBe('Code generated successfully');
      expect(codeResult.generatedCode).toBeDefined();

      expect(testResult.routing.selectedAgent).toBe('test-agent');
      expect(testResult.result).toBe('Tests executed successfully');
      expect(testResult.testResults).toBeDefined();
    });

    test('should handle unknown task types with default agent', async () => {
      const unknownTask = {
        id: 'task-3',
        type: 'unknown',
        description: 'Some unknown task'
      };

      const result = await orchestrator.routeTask(unknownTask);

      expect(result.routing.selectedAgent).toBe('default-agent');
      expect(result.result).toBe('processed');
    });

    test('should track metrics', async () => {
      const task = {
        id: 'metrics-task',
        type: 'code',
        description: 'Test metrics tracking'
      };

      await orchestrator.routeTask(task);
      const metrics = await orchestrator.getMetrics();

      expect(metrics.totalRequests).toBeGreaterThan(0);
      expect(metrics.successfulRequests).toBeGreaterThan(0);
      expect(metrics.successRate).toBeGreaterThan(0);
      expect(metrics.registeredAgents).toBe(3);
    });

    test('should handle task execution errors', async () => {
      const errorAgent = {
        name: 'error-agent',
        execute: async () => {
          throw new Error('Simulated agent error');
        }
      };

      await orchestrator.registerAgent('error-agent', errorAgent);

      const errorTask = {
        id: 'error-task',
        type: 'error',
        description: 'Task that will fail'
      };

      // Override determineAgent for this test
      const originalDetermineAgent = orchestrator.determineAgent;
      orchestrator.determineAgent = () => 'error-agent';

      await expect(orchestrator.routeTask(errorTask)).rejects.toThrow('Simulated agent error');

      const metrics = await orchestrator.getMetrics();
      expect(metrics.failedRequests).toBeGreaterThan(0);

      // Restore original method
      orchestrator.determineAgent = originalDetermineAgent;
    });

    test('should perform health check', async () => {
      const health = await orchestrator.healthCheck();

      expect(health.status).toBe('healthy');
      expect(health.timestamp).toBeDefined();
      expect(health.services.orchestrator).toBe('running');
      expect(health.services.agentSquad).toBe('running');
    });

    test('should manage sessions', async () => {
      const sessionId = await orchestrator.createSession('user-123');
      
      expect(sessionId).toMatch(/^session-\d+-[a-z0-9]+$/);
      
      const session = orchestrator.getSession(sessionId);
      expect(session.userId).toBe('user-123');
      expect(session.createdAt).toBeDefined();
      expect(session.tasks).toEqual([]);
    });

    test('should execute tasks within sessions', async () => {
      const sessionId = await orchestrator.createSession('user-456');
      const task = {
        id: 'session-task',
        type: 'code',
        description: 'Task within session'
      };

      const result = await orchestrator.executeWithSession(sessionId, task);

      expect(result.routing.selectedAgent).toBe('code-agent');
      
      const session = orchestrator.getSession(sessionId);
      expect(session.tasks).toHaveLength(1);
      expect(session.tasks[0]).toEqual(task);
    });
  });

  describe('AgentRegistry', () => {
    let registry;

    beforeEach(() => {
      registry = new AgentRegistry();
    });

    test('should register agent metadata', async () => {
      const metadata = {
        name: 'test-agent',
        version: '1.0.0',
        capabilities: ['testing', 'validation'],
        maxConcurrent: 5,
        timeout: 30000
      };

      await registry.register(metadata);

      const agents = registry.listAgents();
      expect(agents).toHaveLength(1);
      expect(agents[0]).toEqual(metadata);
    });

    test('should instantiate agents on demand', async () => {
      const metadata = {
        name: 'lazy-agent',
        version: '1.0.0',
        capabilities: ['lazy-loading']
      };

      await registry.register(metadata);
      const agent = await registry.getAgent('lazy-agent');

      expect(agent.name).toBe('lazy-agent');
      expect(agent.metadata).toEqual(metadata);
      expect(typeof agent.execute).toBe('function');
    });

    test('should track agent usage statistics', async () => {
      const metadata = {
        name: 'stats-agent',
        version: '1.0.0',
        capabilities: ['statistics']
      };

      await registry.register(metadata);
      
      // Use agent multiple times
      await registry.getAgent('stats-agent');
      await registry.getAgent('stats-agent');
      await registry.getAgent('stats-agent');

      const agentMetadata = registry.getAgentMetadata('stats-agent');
      expect(agentMetadata.usageCount).toBe(3);
      expect(agentMetadata.lastUsed).toBeDefined();
    });

    test('should unregister agents', async () => {
      const metadata = {
        name: 'temp-agent',
        version: '1.0.0',
        capabilities: ['temporary']
      };

      await registry.register(metadata);
      expect(registry.listAgents()).toHaveLength(1);

      await registry.unregister('temp-agent');
      expect(registry.listAgents()).toHaveLength(0);
    });

    test('should provide registry statistics', async () => {
      const metadata1 = { name: 'agent-1', version: '1.0.0' };
      const metadata2 = { name: 'agent-2', version: '1.0.0' };

      await registry.register(metadata1);
      await registry.register(metadata2);
      await registry.getAgent('agent-1');

      const stats = registry.getStats();
      expect(stats.totalAgents).toBe(2);
      expect(stats.activeInstances).toBe(1);
      expect(stats.agentUsage).toHaveLength(2);
    });
  });

  describe('SupervisorAgent', () => {
    let supervisor;

    beforeEach(() => {
      supervisor = new SupervisorAgent({
        name: 'test-supervisor',
        maxConcurrency: 10
      });
    });

    test('should evaluate components', async () => {
      const requirement = {
        name: 'authentication',
        type: 'security'
      };

      const candidates = [
        { name: 'passport.js', score: 0.9 },
        { name: 'auth0', score: 0.8 },
        { name: 'firebase-auth', score: 0.7 }
      ];

      const evaluation = await supervisor.evaluateComponent(requirement, candidates);

      expect(evaluation.recommended_component).toEqual(candidates[0]);
      expect(evaluation.alternatives).toEqual(candidates.slice(1));
      expect(evaluation.confidence).toBe(0.8);
    });

    test('should create integration plans', async () => {
      const components = [
        { name: 'database' },
        { name: 'api-server' },
        { name: 'frontend' }
      ];

      const architecture = {
        type: 'microservices'
      };

      const plan = await supervisor.createIntegrationPlan(components, architecture);

      expect(plan.steps).toHaveLength(3);
      expect(plan.steps[0].name).toBe('Configure database');
      expect(plan.steps[1].dependencies).toEqual(['step-0']);
      expect(plan.estimated_duration).toBe(90); // 3 * 30 minutes
    });
  });

  describe('Integration Tests', () => {
    test('should integrate orchestrator with agent squad', async () => {
      const orchestrator = new BaseOrchestrator();
      await orchestrator.initialize();

      const task = {
        id: 'integration-task',
        type: 'code',
        description: 'Integration test task'
      };

      const result = await orchestrator.routeTask(task);
      expect(result.routing.selectedAgent).toBe('code-agent');
      expect(result.result).toBe('Code generated successfully');
    });

    test('should handle complex workflow with multiple agents', async () => {
      const orchestrator = new BaseOrchestrator();
      await orchestrator.initialize();

      const tasks = [
        { id: 'task-1', type: 'code', description: 'Generate code' },
        { id: 'task-2', type: 'test', description: 'Run tests' },
        { id: 'task-3', type: 'general', description: 'Documentation' }
      ];

      const results = await Promise.all(
        tasks.map(task => orchestrator.routeTask(task))
      );

      expect(results[0].routing.selectedAgent).toBe('code-agent');
      expect(results[1].routing.selectedAgent).toBe('test-agent');
      expect(results[2].routing.selectedAgent).toBe('default-agent');

      const metrics = await orchestrator.getMetrics();
      expect(metrics.totalRequests).toBe(3);
      expect(metrics.successfulRequests).toBe(3);
    });
  });
});