import { EventEmitter } from 'events';

interface WorkflowStep {
  id: string;
  name: string;
  type: 'sequential' | 'parallel' | 'conditional';
  agents: string[];
  dependencies: string[];
  condition?: string;
  timeout: number;
}

interface WorkflowPlan {
  id: string;
  steps: WorkflowStep[];
  metadata: Record<string, any>;
}

interface Intent {
  description: string;
  type: string;
  priority: number;
  requirements: string[];
}

interface AgentTask {
  id: string;
  type: string;
  input: any;
  timeout: number;
}

export abstract class SupervisorAgent extends EventEmitter {
  protected subAgents: Map<string, any> = new Map();
  protected workflowEngine: WorkflowEngine;
  protected decisionEngine: DecisionEngine;
  protected executionHistory: Map<string, any> = new Map();

  constructor() {
    super();
    this.workflowEngine = new WorkflowEngine();
    this.decisionEngine = new DecisionEngine();
  }

  abstract extractIntent(request: Record<string, any>): Promise<Intent>;

  async analyzeRequest(request: Record<string, any>): Promise<WorkflowPlan> {
    const intent = await this.extractIntent(request);
    const requiredAgents = await this.decisionEngine.determineAgents(intent);
    const workflow = await this.workflowEngine.createWorkflow(intent, requiredAgents);
    
    this.emit('workflow-created', { workflow, intent });
    return workflow;
  }

  async executeWorkflow(workflow: WorkflowPlan): Promise<Record<string, any>> {
    const results: Record<string, any> = {};
    
    this.emit('workflow-started', { workflowId: workflow.id });
    
    try {
      for (const step of workflow.steps) {
        const stepResult = await this.executeStep(step);
        results[step.name] = stepResult;
        this.emit('step-completed', { stepId: step.id, result: stepResult });
      }
      
      this.emit('workflow-completed', { workflowId: workflow.id, results });
      return results;
    } catch (error) {
      this.emit('workflow-failed', { workflowId: workflow.id, error: error.message });
      throw error;
    }
  }

  private async executeStep(step: WorkflowStep): Promise<any> {
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

  protected async executeAgentTask(agentName: string, task: AgentTask): Promise<any> {
    const agent = this.subAgents.get(agentName);
    if (!agent) {
      throw new Error(`Agent ${agentName} not found`);
    }

    const startTime = Date.now();
    
    try {
      const result = await Promise.race([
        agent.execute(task),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Task timeout')), task.timeout)
        )
      ]);
      
      const duration = Date.now() - startTime;
      this.recordExecution(agentName, task, result, duration);
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.recordExecution(agentName, task, null, duration, error);
      throw error;
    }
  }

  private recordExecution(
    agentName: string, 
    task: AgentTask, 
    result: any, 
    duration: number, 
    error?: Error
  ): void {
    const execution = {
      agentName,
      taskId: task.id,
      duration,
      success: !error,
      error: error?.message,
      timestamp: new Date().toISOString()
    };
    
    this.executionHistory.set(task.id, execution);
    this.emit('task-executed', execution);
  }

  registerAgent(name: string, agent: any): void {
    this.subAgents.set(name, agent);
    this.emit('agent-registered', { name, agent });
  }

  getExecutionHistory(): Record<string, any>[] {
    return Array.from(this.executionHistory.values());
  }
}

class WorkflowEngine {
  private templates: Map<string, any> = new Map();

  async createWorkflow(intent: Intent, agents: string[]): Promise<WorkflowPlan> {
    const template = this.selectTemplate(intent);
    
    if (template) {
      return this.applyTemplate(template, agents);
    }
    
    return this.createDynamicWorkflow(intent, agents);
  }

  private selectTemplate(intent: Intent): any {
    return this.templates.get(intent.type);
  }

  private applyTemplate(template: any, agents: string[]): WorkflowPlan {
    return {
      id: `workflow-${Date.now()}`,
      steps: template.steps.map((step: any, index: number) => ({
        ...step,
        id: `step-${index}`,
        agents: agents.slice(0, step.agentCount || 1)
      })),
      metadata: { template: template.name }
    };
  }

  private createDynamicWorkflow(intent: Intent, agents: string[]): WorkflowPlan {
    const steps: WorkflowStep[] = [];
    
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
  private rules: Array<{ pattern: RegExp; agents: string[] }> = [
    { pattern: /code|implement|develop/i, agents: ['CodeAgent'] },
    { pattern: /test|verify|validate/i, agents: ['TestAgent'] },
    { pattern: /design|architect/i, agents: ['DesignAgent'] },
    { pattern: /security|vulnerabilit/i, agents: ['SecurityAgent'] }
  ];

  async determineAgents(intent: Intent): Promise<string[]> {
    const matchedAgents = new Set<string>();
    
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