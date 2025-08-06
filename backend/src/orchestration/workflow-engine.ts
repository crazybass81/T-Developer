export enum StepType {
  SEQUENTIAL = 'sequential',
  PARALLEL = 'parallel',
  CONDITIONAL = 'conditional'
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: StepType;
  agents: string[];
  dependencies: string[];
  condition?: string;
  timeout: number;
}

export interface WorkflowPlan {
  id: string;
  name: string;
  steps: WorkflowStep[];
  estimatedDuration: number;
}

export interface Intent {
  description: string;
  type: string;
  priority: number;
  context: Record<string, any>;
}

export class WorkflowEngine {
  private templates: Map<string, WorkflowPlan> = new Map();

  constructor() {
    this.loadWorkflowTemplates();
  }

  async createWorkflow(intent: Intent, agents: string[]): Promise<WorkflowPlan> {
    // 1. Select template based on intent
    const template = this.selectTemplate(intent);
    
    // 2. Create workflow from template or dynamically
    const workflow: WorkflowPlan = template || this.createDynamicWorkflow(intent, agents);
    
    // 3. Validate workflow
    await this.validateWorkflow(workflow);
    
    // 4. Optimize workflow
    return this.optimizeWorkflow(workflow);
  }

  private selectTemplate(intent: Intent): WorkflowPlan | null {
    // Simple template matching
    if (intent.type === 'project-creation') {
      return this.templates.get('project-creation');
    }
    return null;
  }

  private createDynamicWorkflow(intent: Intent, agents: string[]): WorkflowPlan {
    const steps: WorkflowStep[] = agents.map((agent, index) => ({
      id: `step-${index + 1}`,
      name: `Execute ${agent}`,
      type: StepType.SEQUENTIAL,
      agents: [agent],
      dependencies: index > 0 ? [`step-${index}`] : [],
      timeout: 300
    }));

    return {
      id: `workflow-${Date.now()}`,
      name: `Dynamic workflow for ${intent.type}`,
      steps,
      estimatedDuration: steps.length * 300
    };
  }

  private async validateWorkflow(workflow: WorkflowPlan): Promise<void> {
    // Check for circular dependencies
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    for (const step of workflow.steps) {
      if (!visited.has(step.id)) {
        if (this.hasCycle(step, workflow.steps, visited, recursionStack)) {
          throw new Error('Circular dependency detected in workflow');
        }
      }
    }
  }

  private hasCycle(
    step: WorkflowStep,
    allSteps: WorkflowStep[],
    visited: Set<string>,
    recursionStack: Set<string>
  ): boolean {
    visited.add(step.id);
    recursionStack.add(step.id);

    for (const depId of step.dependencies) {
      const depStep = allSteps.find(s => s.id === depId);
      if (!depStep) continue;

      if (!visited.has(depId)) {
        if (this.hasCycle(depStep, allSteps, visited, recursionStack)) {
          return true;
        }
      } else if (recursionStack.has(depId)) {
        return true;
      }
    }

    recursionStack.delete(step.id);
    return false;
  }

  private optimizeWorkflow(workflow: WorkflowPlan): WorkflowPlan {
    // Identify parallel execution opportunities
    const optimizedSteps = workflow.steps.map(step => {
      if (step.dependencies.length === 0 && step.type === StepType.SEQUENTIAL) {
        // Steps with no dependencies can potentially run in parallel
        return { ...step, type: StepType.PARALLEL };
      }
      return step;
    });

    return {
      ...workflow,
      steps: optimizedSteps,
      estimatedDuration: Math.max(...optimizedSteps.map(s => s.timeout))
    };
  }

  private loadWorkflowTemplates(): void {
    // Load predefined workflow templates
    const projectCreationTemplate: WorkflowPlan = {
      id: 'project-creation',
      name: 'Project Creation Workflow',
      steps: [
        {
          id: 'step-1',
          name: 'Analyze Requirements',
          type: StepType.SEQUENTIAL,
          agents: ['NLInputAgent', 'ParserAgent'],
          dependencies: [],
          timeout: 300
        },
        {
          id: 'step-2',
          name: 'Select Components',
          type: StepType.PARALLEL,
          agents: ['ComponentDecisionAgent', 'MatchRateAgent', 'SearchAgent'],
          dependencies: ['step-1'],
          timeout: 600
        },
        {
          id: 'step-3',
          name: 'Generate and Assemble',
          type: StepType.SEQUENTIAL,
          agents: ['GenerationAgent', 'AssemblyAgent'],
          dependencies: ['step-2'],
          timeout: 900
        },
        {
          id: 'step-4',
          name: 'Package and Download',
          type: StepType.SEQUENTIAL,
          agents: ['DownloadAgent'],
          dependencies: ['step-3'],
          timeout: 300
        }
      ],
      estimatedDuration: 2100
    };

    this.templates.set('project-creation', projectCreationTemplate);
  }
}