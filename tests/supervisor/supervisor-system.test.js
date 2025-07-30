const { SupervisorAgent } = require('../../backend/src/agents/supervisor/supervisor-agent.js');
const { DecisionEngine } = require('../../backend/src/agents/supervisor/decision-engine.js');
const { ExecutionTracker } = require('../../backend/src/workflow/execution-tracker.js');

describe('Task 1.2: SupervisorAgent 시스템 구현', () => {
  describe('SupervisorAgent', () => {
    let supervisor;

    beforeEach(() => {
      supervisor = new SupervisorAgent();
    });

    test('should analyze request and create workflow plan', async () => {
      const request = {
        description: 'Implement user authentication with code and test',
        type: 'development'
      };

      const workflow = await supervisor.analyzeRequest(request);

      expect(workflow).toBeDefined();
      expect(workflow.id).toMatch(/^workflow-\d+$/);
      expect(workflow.steps).toHaveLength(2);
      expect(workflow.steps[0].agents).toContain('code-agent');
      expect(workflow.steps[1].agents).toContain('test-agent');
    });

    test('should extract intent from request', async () => {
      const request = {
        description: 'This is a complex task that requires multiple steps and careful planning',
        type: 'complex'
      };

      const intent = await supervisor.extractIntent(request);

      expect(intent.description).toBe(request.description);
      expect(intent.type).toBe('complex');
      expect(intent.complexity).toBe(0.8); // Long description
    });

    test('should determine appropriate agents', async () => {
      const intent = {
        description: 'Create design mockups and implement code',
        type: 'development',
        complexity: 0.6
      };

      const agents = await supervisor.determineAgents(intent);

      expect(agents).toContain('design-agent');
      expect(agents).toContain('code-agent');
    });

    test('should execute workflow with sequential steps', async () => {
      const workflow = {
        id: 'test-workflow',
        steps: [
          {
            id: 'step-1',
            name: 'Execute code-agent',
            agents: ['code-agent'],
            parallel: false,
            task: { type: 'code' }
          },
          {
            id: 'step-2',
            name: 'Execute test-agent',
            agents: ['test-agent'],
            parallel: false,
            task: { type: 'test' }
          }
        ],
        estimatedDuration: 120000
      };

      const results = await supervisor.executeWorkflow(workflow);

      expect(results).toBeDefined();
      expect(results['Execute code-agent']).toHaveLength(1);
      expect(results['Execute test-agent']).toHaveLength(1);
      expect(results['Execute code-agent'][0].agentName).toBe('code-agent');
    });

    test('should execute workflow with parallel steps', async () => {
      const workflow = {
        id: 'parallel-workflow',
        steps: [
          {
            id: 'parallel-step',
            name: 'Parallel execution',
            agents: ['code-agent', 'test-agent'],
            parallel: true,
            task: { type: 'parallel' }
          }
        ],
        estimatedDuration: 60000
      };

      const results = await supervisor.executeWorkflow(workflow);

      expect(results['Parallel execution']).toHaveLength(2);
      expect(results['Parallel execution'][0].success).toBe(true);
      expect(results['Parallel execution'][1].success).toBe(true);
    });

    test('should handle default agent when no specific agents match', async () => {
      const intent = {
        description: 'Generic task with no specific keywords',
        type: 'general',
        complexity: 0.2
      };

      const agents = await supervisor.determineAgents(intent);

      expect(agents).toEqual(['default-agent']);
    });
  });

  describe('DecisionEngine', () => {
    let decisionEngine;

    beforeEach(() => {
      decisionEngine = new DecisionEngine();
    });

    test('should determine agents based on rules', async () => {
      const intent = {
        description: 'Implement secure authentication code',
        type: 'development',
        complexity: 0.7
      };

      const decisions = await decisionEngine.determineAgents(intent);

      expect(decisions).toBeDefined();
      expect(decisions.length).toBeGreaterThan(0);
      
      const codeAgent = decisions.find(d => d.agentName === 'CodeAgent');
      const securityAgent = decisions.find(d => d.agentName === 'SecurityAgent');
      
      expect(codeAgent).toBeDefined();
      expect(securityAgent).toBeDefined();
      expect(codeAgent.confidence).toBe(0.8);
    });

    test('should match by rules correctly', () => {
      const intent = {
        description: 'Design and architect the system',
        type: 'architecture',
        complexity: 0.5
      };

      const ruleBasedAgents = decisionEngine.matchByRules(intent);

      expect(ruleBasedAgents).toHaveLength(1);
      expect(ruleBasedAgents[0].agentName).toBe('DesignAgent');
      expect(ruleBasedAgents[0].reasoning).toContain('Rule-based match');
    });

    test('should predict agents for complex tasks', async () => {
      const intent = {
        description: 'Very complex multi-step process',
        type: 'complex',
        complexity: 0.8
      };

      const predictions = await decisionEngine.predictAgents(intent);

      expect(predictions).toHaveLength(1);
      expect(predictions[0].agentName).toBe('ComplexTaskAgent');
      expect(predictions[0].confidence).toBe(0.7);
    });

    test('should combine decisions and remove duplicates', () => {
      const ruleBasedAgents = [
        { agentName: 'CodeAgent', confidence: 0.8, reasoning: 'Rule match' }
      ];
      const mlPredictions = [
        { agentName: 'CodeAgent', confidence: 0.9, reasoning: 'ML prediction' }
      ];
      const historicalPatterns = [
        { agentName: 'TestAgent', confidence: 0.6, reasoning: 'History' }
      ];

      const combined = decisionEngine.combineDecisions(
        ruleBasedAgents,
        mlPredictions,
        historicalPatterns
      );

      expect(combined).toHaveLength(2);
      expect(combined[0].agentName).toBe('CodeAgent');
      expect(combined[0].confidence).toBe(0.9); // Higher confidence kept
      expect(combined[1].agentName).toBe('TestAgent');
    });

    test('should record and use decision history', () => {
      const intent = { type: 'test-type', description: 'test', complexity: 0.5 };
      const decision = { agentName: 'TestAgent', confidence: 0.9, reasoning: 'Test' };

      decisionEngine.recordDecision(intent, decision);

      const historicalPatterns = decisionEngine.analyzeHistory(intent);
      expect(historicalPatterns).toHaveLength(1);
      expect(historicalPatterns[0].agentName).toBe('TestAgent');
    });
  });

  describe('ExecutionTracker', () => {
    let tracker;

    beforeEach(() => {
      tracker = new ExecutionTracker();
    });

    test('should track workflow execution', async () => {
      const workflowId = 'test-workflow-123';
      const workflow = {
        id: workflowId,
        steps: [
          { id: 'step-1', name: 'First step', agents: ['agent-1'] }
        ]
      };

      await tracker.trackExecution(workflowId, workflow);

      const state = tracker.getExecutionState(workflowId);
      expect(state).toBeDefined();
      expect(state.workflowId).toBe(workflowId);
      expect(state.status).toBe('pending');
      expect(state.currentStep).toBe('step-1');
    });

    test('should update step progress', async () => {
      const workflowId = 'progress-test';
      const workflow = { id: workflowId, steps: [{ id: 'step-1' }] };

      await tracker.trackExecution(workflowId, workflow);
      await tracker.updateStepProgress(workflowId, 'step-1', 50);

      const state = tracker.getExecutionState(workflowId);
      expect(state.progress).toBe(50);
      expect(state.status).toBe('running');
      expect(state.currentStep).toBe('step-1');
    });

    test('should complete step with result', async () => {
      const workflowId = 'complete-test';
      const workflow = { id: workflowId, steps: [{ id: 'step-1' }] };
      const result = { success: true, data: 'test result' };

      await tracker.trackExecution(workflowId, workflow);
      await tracker.completeStep(workflowId, 'step-1', result);

      const state = tracker.getExecutionState(workflowId);
      expect(state.results.get('step-1')).toEqual(result);
    });

    test('should handle step failure', async () => {
      const workflowId = 'fail-test';
      const workflow = { id: workflowId, steps: [{ id: 'step-1' }] };
      const error = new Error('Test error');

      await tracker.trackExecution(workflowId, workflow);
      await tracker.failStep(workflowId, 'step-1', error);

      const state = tracker.getExecutionState(workflowId);
      expect(state.status).toBe('failed');
      expect(state.errors).toHaveLength(1);
      expect(state.errors[0].message).toBe('Test error');
    });

    test('should complete workflow', async () => {
      const workflowId = 'completion-test';
      const workflow = { id: workflowId, steps: [{ id: 'step-1' }] };

      await tracker.trackExecution(workflowId, workflow);
      await tracker.completeWorkflow(workflowId);

      const state = tracker.getExecutionState(workflowId);
      expect(state.status).toBe('completed');
      expect(state.progress).toBe(100);
      expect(state.endTime).toBeDefined();
    });

    test('should emit state updates', (done) => {
      const workflowId = 'emit-test';
      const workflow = { id: workflowId, steps: [{ id: 'step-1' }] };

      tracker.on('stateUpdate', (update) => {
        expect(update.workflowId).toBe(workflowId);
        expect(update.state.status).toBe('pending');
        done();
      });

      tracker.trackExecution(workflowId, workflow);
    });

    test('should get all executions', async () => {
      const workflow1 = { id: 'wf-1', steps: [{ id: 'step-1' }] };
      const workflow2 = { id: 'wf-2', steps: [{ id: 'step-1' }] };

      await tracker.trackExecution('wf-1', workflow1);
      await tracker.trackExecution('wf-2', workflow2);

      const allExecutions = tracker.getAllExecutions();
      expect(allExecutions).toHaveLength(2);
      expect(allExecutions.map(e => e.workflowId)).toContain('wf-1');
      expect(allExecutions.map(e => e.workflowId)).toContain('wf-2');
    });
  });

  describe('Integration Tests', () => {
    test('should integrate supervisor with decision engine', async () => {
      const supervisor = new SupervisorAgent();
      const decisionEngine = new DecisionEngine();

      const intent = {
        description: 'Implement and test security features',
        type: 'security',
        complexity: 0.8
      };

      const decisions = await decisionEngine.determineAgents(intent);
      expect(decisions.length).toBeGreaterThan(0);

      const agents = await supervisor.determineAgents(intent);
      expect(agents.length).toBeGreaterThan(0);
    });

    test('should integrate supervisor with execution tracker', async () => {
      const supervisor = new SupervisorAgent();
      const tracker = new ExecutionTracker();

      const request = {
        description: 'Create code and run tests',
        type: 'development'
      };

      const workflow = await supervisor.analyzeRequest(request);
      await tracker.trackExecution(workflow.id, workflow);

      const state = tracker.getExecutionState(workflow.id);
      expect(state.workflowId).toBe(workflow.id);

      const results = await supervisor.executeWorkflow(workflow);
      expect(results).toBeDefined();
    });

    test('should handle complete workflow lifecycle', async () => {
      const supervisor = new SupervisorAgent();
      const tracker = new ExecutionTracker();
      const decisionEngine = new DecisionEngine();

      // 1. Analyze request
      const request = {
        description: 'Design, implement, and test a new feature',
        type: 'feature'
      };

      const workflow = await supervisor.analyzeRequest(request);
      expect(workflow.steps.length).toBeGreaterThanOrEqual(2); // implement and test detected

      // 2. Track execution
      await tracker.trackExecution(workflow.id, workflow);

      // 3. Execute workflow
      const results = await supervisor.executeWorkflow(workflow);
      expect(Object.keys(results).length).toBeGreaterThanOrEqual(2);

      // 4. Complete tracking
      await tracker.completeWorkflow(workflow.id);
      const finalState = tracker.getExecutionState(workflow.id);
      expect(finalState.status).toBe('completed');
    });
  });
});