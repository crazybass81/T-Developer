import { WorkflowEngine, StepType } from '../../src/workflow/workflow_engine';
import { Intent } from '../../src/agents/supervisor/types';

describe('WorkflowEngine', () => {
  let engine: WorkflowEngine;

  beforeEach(() => {
    engine = new WorkflowEngine();
  });

  describe('createWorkflow', () => {
    it('should create dynamic workflow for development intent', async () => {
      const intent: Intent = {
        type: 'development',
        description: 'Create a web application',
        confidence: 0.9,
        entities: { projectType: 'web' },
        context: {}
      };

      const agents = ['CodeAgent', 'UIAgent', 'TestAgent'];
      const workflow = await engine.createWorkflow(intent, agents);

      expect(workflow.id).toBeDefined();
      expect(workflow.name).toContain('Dynamic workflow');
      expect(workflow.steps.length).toBeGreaterThan(0);
      expect(workflow.estimatedDuration).toBeGreaterThan(0);
    });

    it('should use template for known intent types', async () => {
      const intent: Intent = {
        type: 'test',
        description: 'Run tests',
        confidence: 0.95,
        entities: {},
        context: {}
      };

      const agents = ['TestAgent', 'SecurityAgent'];
      const workflow = await engine.createWorkflow(intent, agents);

      expect(workflow.name).toContain('Testing Workflow');
      expect(workflow.steps.some(s => s.name.includes('Unit Testing'))).toBe(true);
    });

    it('should handle agent dependencies correctly', async () => {
      const intent: Intent = {
        type: 'development',
        description: 'Full development cycle',
        confidence: 0.8,
        entities: {},
        context: {}
      };

      const agents = ['CodeAgent', 'UIAgent', 'TestAgent', 'DeploymentAgent'];
      const workflow = await engine.createWorkflow(intent, agents);

      // TestAgent should come after CodeAgent and UIAgent
      const testStepIndex = workflow.steps.findIndex(s => s.agents.includes('TestAgent'));
      const codeStepIndex = workflow.steps.findIndex(s => s.agents.includes('CodeAgent'));
      
      expect(testStepIndex).toBeGreaterThan(codeStepIndex);
    });

    it('should optimize workflow by merging parallelizable steps', async () => {
      const intent: Intent = {
        type: 'development',
        description: 'Complex project',
        confidence: 0.7,
        entities: {},
        context: {}
      };

      const agents = ['CodeAgent', 'UIAgent', 'APIAgent'];
      const workflow = await engine.createWorkflow(intent, agents);

      // Should have parallel steps for independent agents
      const hasParallelSteps = workflow.steps.some(s => s.type === StepType.PARALLEL);
      expect(hasParallelSteps).toBe(true);
    });
  });

  describe('workflow validation', () => {
    it('should detect circular dependencies', async () => {
      const invalidWorkflow = {
        id: 'invalid',
        name: 'Invalid',
        steps: [
          {
            id: 'step1',
            name: 'Step 1',
            type: StepType.SEQUENTIAL,
            agents: ['CodeAgent'],
            dependencies: ['step2'],
            timeout: 300
          },
          {
            id: 'step2',
            name: 'Step 2',
            type: StepType.SEQUENTIAL,
            agents: ['TestAgent'],
            dependencies: ['step1'],
            timeout: 300
          }
        ],
        estimatedDuration: 600,
        createdAt: new Date()
      };

      const validator = new (engine as any).validator.constructor();
      
      await expect(validator.validate(invalidWorkflow))
        .rejects.toThrow('Circular dependency detected');
    });

    it('should detect missing dependencies', async () => {
      const invalidWorkflow = {
        id: 'invalid',
        name: 'Invalid',
        steps: [
          {
            id: 'step1',
            name: 'Step 1',
            type: StepType.SEQUENTIAL,
            agents: ['CodeAgent'],
            dependencies: ['nonexistent'],
            timeout: 300
          }
        ],
        estimatedDuration: 300,
        createdAt: new Date()
      };

      const validator = new (engine as any).validator.constructor();
      
      await expect(validator.validate(invalidWorkflow))
        .rejects.toThrow('depends on non-existent step');
    });

    it('should detect invalid agents', async () => {
      const invalidWorkflow = {
        id: 'invalid',
        name: 'Invalid',
        steps: [
          {
            id: 'step1',
            name: 'Step 1',
            type: StepType.SEQUENTIAL,
            agents: ['InvalidAgent'],
            dependencies: [],
            timeout: 300
          }
        ],
        estimatedDuration: 300,
        createdAt: new Date()
      };

      const validator = new (engine as any).validator.constructor();
      
      await expect(validator.validate(invalidWorkflow))
        .rejects.toThrow('Invalid agent');
    });
  });

  describe('workflow optimization', () => {
    it('should calculate correct estimated duration', async () => {
      const intent: Intent = {
        type: 'development',
        description: 'Simple project',
        confidence: 0.9,
        entities: {},
        context: {}
      };

      const workflow = await engine.createWorkflow(intent, ['CodeAgent']);
      
      expect(workflow.estimatedDuration).toBeGreaterThan(0);
      expect(typeof workflow.estimatedDuration).toBe('number');
    });

    it('should remove redundant dependencies', async () => {
      const intent: Intent = {
        type: 'development',
        description: 'Multi-step project',
        confidence: 0.8,
        entities: {},
        context: {}
      };

      const agents = ['CodeAgent', 'UIAgent', 'TestAgent', 'DeploymentAgent'];
      const workflow = await engine.createWorkflow(intent, agents);

      // Check that no step has redundant transitive dependencies
      workflow.steps.forEach(step => {
        const directDeps = step.dependencies;
        const indirectDeps = directDeps.flatMap(depId => {
          const depStep = workflow.steps.find(s => s.id === depId);
          return depStep ? depStep.dependencies : [];
        });

        // No dependency should appear in both direct and indirect
        const overlap = directDeps.filter(dep => indirectDeps.includes(dep));
        expect(overlap.length).toBe(0);
      });
    });
  });
});