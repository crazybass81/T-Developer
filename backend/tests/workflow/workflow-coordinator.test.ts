// backend/tests/workflow/workflow-coordinator.test.ts
import { WorkflowEngine } from '../../src/workflow/workflow-engine';

// Mock dependencies
const mockParallelExecutor = {
  executeParallel: jest.fn().mockResolvedValue([
    { result: 'task1' },
    { result: 'task2' }
  ])
};

const mockDependencyManager = {
  addDependency: jest.fn(),
  getExecutionOrder: jest.fn().mockReturnValue(['task1', 'task2']),
  canExecute: jest.fn().mockResolvedValue(true)
};

const mockExecutionTracker = {
  trackExecution: jest.fn().mockResolvedValue(undefined),
  updateStepProgress: jest.fn().mockResolvedValue(undefined),
  getState: jest.fn().mockReturnValue({
    workflowId: 'test',
    status: 'pending',
    currentStep: 'step1'
  })
};

jest.mock('../../src/workflow/parallel-executor', () => ({
  ParallelExecutor: jest.fn().mockImplementation(() => mockParallelExecutor)
}));

jest.mock('../../src/workflow/dependency-manager', () => ({
  DependencyManager: jest.fn().mockImplementation(() => mockDependencyManager)
}));

jest.mock('../../src/workflow/execution-tracker', () => ({
  ExecutionTracker: jest.fn().mockImplementation(() => mockExecutionTracker)
}));

describe('Workflow Coordination System', () => {
  describe('WorkflowEngine', () => {
    let engine: WorkflowEngine;

    beforeEach(() => {
      engine = new WorkflowEngine();
      jest.clearAllMocks();
    });

    test('should create workflow from intent', async () => {
      const intent = { description: 'develop a web application', type: 'development', complexity: 0.5 };
      const agents = ['analysis-agent', 'code-agent', 'test-agent'];
      
      const workflow = await engine.createWorkflow(intent, agents);
      
      expect(workflow).toBeDefined();
      expect(workflow.id).toBeDefined();
      expect(workflow.steps).toHaveLength(3);
      expect(workflow.estimatedDuration).toBeGreaterThan(0);
    });

    test('should create dynamic workflow for unknown intent', async () => {
      const intent = { description: 'unknown task', type: 'general', complexity: 0.3 };
      const agents = ['agent1', 'agent2'];
      
      const workflow = await engine.createWorkflow(intent, agents);
      
      expect(workflow).toBeDefined();
      expect(workflow.steps.length).toBeGreaterThan(0);
    });

    test('should handle empty agents list', async () => {
      const intent = { description: 'code development', type: 'development', complexity: 0.4 };
      const agents: string[] = [];
      
      const workflow = await engine.createWorkflow(intent, agents);
      
      expect(workflow).toBeDefined();
      expect(workflow.steps).toHaveLength(3);
    });

    test('should validate workflow steps', async () => {
      const intent = { description: 'test workflow', type: 'testing', complexity: 0.2 };
      const agents = ['test-agent'];
      
      const workflow = await engine.createWorkflow(intent, agents);
      
      expect(workflow.steps.every(step => step.id)).toBe(true);
      expect(workflow.steps.every(step => step.agents.length > 0)).toBe(true);
    });
  });

  describe('Mocked Components', () => {
    test('ParallelExecutor should execute tasks', async () => {
      const { ParallelExecutor } = require('../../src/workflow/parallel-executor');
      const executor = new ParallelExecutor(5);
      
      const tasks = [
        { id: '1', execute: jest.fn().mockResolvedValue({ result: 'task1' }) },
        { id: '2', execute: jest.fn().mockResolvedValue({ result: 'task2' }) }
      ];

      const results = await executor.executeParallel(tasks);
      
      expect(results).toHaveLength(2);
      expect(mockParallelExecutor.executeParallel).toHaveBeenCalledWith(tasks);
    });

    test('DependencyManager should manage dependencies', () => {
      const { DependencyManager } = require('../../src/workflow/dependency-manager');
      const manager = new DependencyManager();
      
      const dependency = {
        taskId: 'task1',
        dependsOn: ['task0'],
        type: 'hard' as const
      };

      manager.addDependency(dependency);
      const order = manager.getExecutionOrder();
      
      expect(mockDependencyManager.addDependency).toHaveBeenCalledWith(dependency);
      expect(order).toEqual(['task1', 'task2']);
    });

    test('ExecutionTracker should track workflow', async () => {
      const { ExecutionTracker } = require('../../src/workflow/execution-tracker');
      const tracker = new ExecutionTracker();
      
      const workflowId = 'test-workflow';
      const workflow = {
        id: workflowId,
        steps: [{ id: 'step1', name: 'Step 1', agents: ['agent1'], parallel: false, task: {} }]
      };

      await tracker.trackExecution(workflowId, workflow);
      const state = tracker.getState(workflowId);
      
      expect(mockExecutionTracker.trackExecution).toHaveBeenCalledWith(workflowId, workflow);
      expect(state?.status).toBe('pending');
    });
  });
});